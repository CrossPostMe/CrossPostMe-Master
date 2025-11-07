# EXE Installer Guide

## For Backend (Python/FastAPI)

### Using PyInstaller

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Create a PyInstaller spec file or run:
   ```bash
   pyinstaller --onefile app/backend/server.py --name CrossPostMeBackend
   ```

   - This will generate a single EXE in `dist/CrossPostMeBackend.exe`.
   - You may need to bundle dependencies and static files; see PyInstaller docs for advanced config.
3. Distribute the EXE to Windows users. They must have MongoDB and Python dependencies available, or you can bundle them with the EXE.

### Notes

- For a true Windows service, consider packaging with NSSM or creating a Windows installer with NSIS/Inno Setup.
- For cross-platform, use Docker or package as a standalone binary for each OS.

## For Frontend (React)

### Using Electron + NSIS

1. Wrap your React build in an Electron app:
   - Install Electron:
     ```bash
     npm install --save-dev electron
     ```
   - Create `main.js` to launch your React build in Electron.
2. Build the Electron app:
   ```bash
   npm run build
   electron-packager . CrossPostMeFrontend --platform=win32 --arch=x64
   ```
3. Create an installer with NSIS:
   - Install NSIS ([Download here](https://nsis.sourceforge.io/Download))
   - Use a script to package the Electron app into an installer.

### References

- [PyInstaller Docs](https://pyinstaller.org/en/stable/)
- [Electron Packager](https://github.com/electron/electron-packager)
- [NSIS](https://nsis.sourceforge.io/Main_Page)

---

**Summary:**

- Use PyInstaller for backend EXE, Electron+NSIS for frontend installer.
- For production, prefer Docker or cloud deployment unless a desktop app is required.
