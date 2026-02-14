# Building PDX Mod Translator as EXE

This guide explains how to build the PDX Mod Translator application into a standalone executable file.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- All project dependencies installed

## Quick Start

### Windows

1. Open Command Prompt or PowerShell
2. Navigate to the `pdx translation tool` folder:
   ```cmd
   cd "pdx translation tool"
   ```
3. Run the build script:
   ```cmd
   build_exe.bat
   ```
4. The executable will be created at: `dist\PDX_Mod_Translator.exe`

### Linux / macOS

1. Open Terminal
2. Navigate to the `pdx translation tool` folder:
   ```bash
   cd "pdx translation tool"
   ```
3. Run the build script:
   ```bash
   ./build_exe.sh
   ```
4. The executable will be created at: `dist/PDX_Mod_Translator`

## Manual Build Process

If you prefer to build manually or need more control:

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Build the Executable

Run PyInstaller with the provided spec file:

```bash
pyinstaller build_exe.spec --clean
```

### Step 3: Locate the Output

The executable will be created in the `dist` folder:
- Windows: `dist\PDX_Mod_Translator.exe`
- Linux/Mac: `dist/PDX_Mod_Translator`

## Build Configuration

The build is configured using the `build_exe.spec` file. Key settings:

- **Name**: PDX_Mod_Translator
- **Console**: False (GUI application, no console window)
- **One File**: True (single executable file)
- **Icon**: Can be customized by adding `icon='path/to/icon.ico'` to the EXE section

### Included Dependencies

The following packages are automatically bundled:
- customtkinter (GUI framework)
- google-generativeai (API client)
- PyYAML (YAML file handling)
- All translator_app modules

## Troubleshooting

### Build Fails

1. Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Clear previous build artifacts:
   ```bash
   # Delete build and dist folders
   rm -rf build dist
   # Windows: rmdir /s /q build dist
   ```

3. Try rebuilding with the `--clean` flag

### Executable Doesn't Run

1. Check antivirus software - it may block the executable
2. Try running from command line to see error messages
3. Ensure the executable has permission to run

### Missing Modules

If you get "ModuleNotFoundError" when running the executable:

1. Add the missing module to `hiddenimports` in `build_exe.spec`
2. Rebuild the executable

## Customization

### Adding an Icon

1. Create or obtain an `.ico` file (Windows) or `.icns` file (macOS)
2. Edit `build_exe.spec` and add to the EXE section:
   ```python
   icon='path/to/your/icon.ico'
   ```

### Including Additional Files

To include extra data files, edit the `datas` list in `build_exe.spec`:

```python
datas=[
    ('translator_app', 'translator_app'),
    ('your_file.txt', '.'),  # Add your file here
],
```

### Build Options

Common PyInstaller options you can add to the spec file:

- `console=True` - Show console window (useful for debugging)
- `onefile=False` - Create a folder instead of a single file
- `upx=False` - Disable UPX compression (may help with antivirus issues)

## Distribution

### Windows

The `PDX_Mod_Translator.exe` file can be distributed as-is. Users can run it directly without installing Python.

**Note**: First-time users may see a Windows SmartScreen warning. This is normal for unsigned executables.

### Linux / macOS

The executable may need to be marked as executable:

```bash
chmod +x PDX_Mod_Translator
```

## File Size Optimization

The executable may be large (50-200 MB) due to bundled dependencies. To reduce size:

1. Remove unused libraries from your code
2. Use virtual environments to ensure only necessary packages are included
3. Consider using UPX compression (enabled by default)

## Building for Different Platforms

**Important**: PyInstaller creates platform-specific executables. To build for:

- **Windows**: Build on a Windows machine
- **macOS**: Build on a macOS machine
- **Linux**: Build on a Linux machine

Cross-compilation is not supported.

## Advanced Configuration

For advanced PyInstaller configuration options, see the [PyInstaller documentation](https://pyinstaller.readthedocs.io/).

## Support

If you encounter issues during the build process:

1. Check the PyInstaller logs in the `build` folder
2. Open an issue on GitHub with the error message
3. Include your Python version and operating system

---

**Happy Building! 🚀**
