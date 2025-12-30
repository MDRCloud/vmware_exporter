# VMware Exporter for Windows

This directory contains the necessary configuration to build and deploy `vmware_exporter` as a Windows Service.

## Prerequisites

### Build Machine
1. **Python 3.x** (Ensure "Add Python to PATH" is selected).
2. **WiX Toolset v3.11** (or compatible v4). Add `candle.exe` and `light.exe` to your PATH.
3. **Git** (optional, to clone repo).

### Python Dependencies
Install the required packages:
```powershell
pip install -r requirements.txt
pip install pyinstaller
```

*Note on AntiGravity*: This project requires the `AntiGravity` module. Ensure it is installed in your Python environment (`pip install ...` or `setup.py install`) before running the build. PyInstaller is configured to bundle it automatically.

## Building the Installer

We provide a PowerShell script to automate the process.

1. Open PowerShell as Administrator (optional but recommended for pip installs).
2. Run the build script:
   ```powershell
   .\build.ps1
   ```

### Manual Steps
If you prefer to run steps manually:
1. **Freeze the Application**:
   ```bash
   pyinstaller vmware_exporter.spec --clean
   ```
   This creates `dist\vmware_exporter.exe`.

2. **Compile MSI**:
   ```bash
   candle installer.wxs
   light installer.wixobj -out vmware_exporter.msi
   ```

## Installation & Usage

1. Copy `vmware_exporter.msi` to the target Windows Server.
2. Run the MSI. Steps through the wizard to install.
3. **Configuration**:
   The service uses Environment Variables for configuration by default (as per `service.py` logic). You may need to set these System Environment Variables before starting the service:
   - `VMWARE_EXPORTER_PORT` (default: 9272)
   - `VSPHERE_HOST`
   - `VSPHERE_USER`
   - `VSPHERE_PASSWORD`
   - `VSPHERE_IGNORE_SSL` (True/False)
   - *See `README.md` for full list of vars.*

4. **Service Management**:
   The installer registers a service named "VMware Exporter" (`VMwareExporter`).
   - Start/Stop via `services.msc`.
   - Logs are currently written to the installation directory (`vmware_exporter.log`) or standard event logs if configured.

## Troubleshooting

- **Service fails to start**: Check `vmware_exporter.log` in the install folder (typically `C:\Program Files (x86)\VMware Exporter`).
- **Missing AntiGravity**: If you see `ModuleNotFoundError: No module named 'AntiGravity'`, verify that the module was present during the build phase. You can check the `dist` folder content to see if it was collected.
- **Port Conflicts**: Ensure port 9272 is not in use.

## Validation Checklist

- [ ] Installer completes without error.
- [ ] "VMware Exporter" service appears in `services.msc`.
- [ ] Service starts automatically (or manually) without error.
- [ ] `http://localhost:9272/metrics` is accessible.
- [ ] `vmware_exporter.exe` is running in Task Manager.
