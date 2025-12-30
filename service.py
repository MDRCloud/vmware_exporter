import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import logging

# Add the current directory to sys.path to ensure we can import the package
sys.path.append(os.path.dirname(__file__))

# Import the application
from vmware_exporter.vmware_exporter import registerEndpoints
from twisted.internet import reactor, endpoints
from twisted.web.server import Site

class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = "VMwareExporter"
    _svc_display_name_ = "VMware Exporter"
    _svc_description_ = "Prometheus Exporter for VMware vCenter"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        logging.info('Stopping service...')
        # Stop the Twisted reactor safely from a different thread context
        reactor.callFromThread(reactor.stop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        # Configure logging - Windows Event Log or File? 
        # For simplicity, we stick to basic logging which typically goes to stdout/stderr (captured by service wrapper if configured)
        # or we could configure it to write to a file.
        logging.basicConfig(
            filename=os.path.join(os.getcwd(), 'vmware_exporter.log'),
            level=logging.INFO,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
        
        logging.info("VMware Exporter Service Starting...")

        # Configuration - simpler to read from ENV or default
        # In a real deployment, these would come from the registry or a config file
        # specified in the MSI.
        class Args:
            config_file = os.environ.get('VMWARE_EXPORTER_CONFIG', 'config.yml') 
            address = os.environ.get('VMWARE_EXPORTER_ADDRESS', '0.0.0.0')
            port = int(os.environ.get('VMWARE_EXPORTER_PORT', 9272))
            loglevel = 'INFO'

        # Check if config file exists, otherwise use defaults/env vars handled in registerEndpoints
        if not os.path.exists(Args.config_file):
            Args.config_file = None

        try:
            # Re-use the existing application logic
            # registerEndpoints returns the twisted Resource tree
            root = registerEndpoints(Args)
            
            # Setup the site
            factory = Site(root)
            endpoint = endpoints.TCP4ServerEndpoint(reactor, Args.port, interface=Args.address)
            endpoint.listen(factory)
            
            logging.info(f"Serving on {Args.address}:{Args.port}")
            
            # Run the reactor
            # installSignalHandlers=False is CRITICAL for running inside Windows Service
            reactor.run(installSignalHandlers=False)
        except Exception as e:
            logging.error(f"Service failed to start: {e}")
            self.SvcStop()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppService)
