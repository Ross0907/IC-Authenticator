"""
Create ICAuthenticator.exe wrapper
This creates a simple executable that launches the Python application
"""

import os
import sys
import subprocess

# Create a simple Python launcher script with better error handling
launcher_code = '''
import os
import sys
import subprocess
import ctypes

# Set Windows App User Model ID for proper taskbar icon (before anything else)
if sys.platform == 'win32':
    try:
        myappid = 'Ross0907.ICAuthenticator.ProductionGUI.v3.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

def show_error(title, message):
    """Show error message box"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
    except:
        # Fallback to Windows API
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)

def show_info(title, message):
    """Show info message box"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(title, message)
    except:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)

def show_question(title, message):
    """Show yes/no question"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        return messagebox.askyesno(title, message)
    except:
        # Fallback to Windows API (MB_YESNO)
        result = ctypes.windll.user32.MessageBoxW(0, message, title, 0x04)
        return result == 6  # IDYES

# Get the directory where the executable is located
app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(app_dir)

# Check Python with multiple methods
python_found = False
python_cmd = None

# Method 1: Check if python is in PATH
for cmd in ['python', 'python3', 'py']:
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            python_found = True
            python_cmd = cmd
            break
    except:
        continue

# Method 2: Check common installation paths
if not python_found:
    common_paths = [
        r"C:\\Program Files\\Python311\\python.exe",
        r"C:\\Program Files\\Python310\\python.exe",
        r"C:\\Python311\\python.exe",
        r"C:\\Python310\\python.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Python\\Python311\\python.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Python\\Python310\\python.exe"),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    python_found = True
                    python_cmd = path
                    break
            except:
                continue

if not python_found:
    show_error("Python Not Found", 
               "Python is not installed or not in PATH.\\n\\n"
               "Please install Python 3.11 or later from:\\n"
               "https://www.python.org\\n\\n"
               "Make sure to check 'Add Python to PATH' during installation.")
    sys.exit(1)

# Check critical dependencies
missing_deps = []
critical_packages = ['PyQt5', 'cv2', 'torch', 'easyocr']

for package in critical_packages:
    try:
        result = subprocess.run([python_cmd, '-c', f'import {package}'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            missing_deps.append(package)
    except:
        missing_deps.append(package)

if missing_deps:
    # Offer to install dependencies
    response = show_question("Install Dependencies", 
                            f"The following dependencies are missing:\\n"
                            f"{', '.join(missing_deps)}\\n\\n"
                            f"Would you like to install them now?\\n"
                            f"(This will take 10-20 minutes)")
    
    if response:
        # Run the dependency installer
        try:
            subprocess.Popen([python_cmd, 'install_dependencies.py'], 
                           cwd=app_dir,
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            show_info("Installing", 
                     "Dependencies are being installed in a new window.\\n\\n"
                     "Please wait for installation to complete,\\n"
                     "then restart IC Authenticator.")
            sys.exit(0)
        except Exception as e:
            show_error("Installation Error", 
                      f"Failed to start dependency installer:\\n\\n{e}")
            sys.exit(1)
    else:
        sys.exit(1)

# Launch the application with pythonw (no console window)
try:
    # Try pythonw first (windowed mode)
    pythonw_cmd = python_cmd.replace('python.exe', 'pythonw.exe')
    if os.path.exists(pythonw_cmd):
        subprocess.Popen([pythonw_cmd, 'gui_classic_production.py'], cwd=app_dir)
    else:
        # Fallback to regular python
        subprocess.Popen([python_cmd, 'gui_classic_production.py'], cwd=app_dir)
except Exception as e:
    show_error("Launch Error", f"Failed to launch application:\\n\\n{e}")
    sys.exit(1)
'''

# Save the launcher script
with open('launcher.py', 'w') as f:
    f.write(launcher_code)

print("Created launcher.py")
print("\nNow creating ICAuthenticator.exe...")
print("Running: python -m PyInstaller with advanced icon settings...")

# Create the executable with PyInstaller with more specific settings
result = subprocess.run([
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--windowed',
    '--icon=icon.ico',
    '--name=ICAuthenticator',
    '--add-data=icon.ico;.',  # Include icon in the bundle
    '--add-data=icon.png;.',  # Include PNG icon too
    'launcher.py'
], capture_output=True, text=True)

if result.returncode == 0:
    print("\n✓ Successfully created ICAuthenticator.exe")
    print("\nLocation: dist\\ICAuthenticator.exe")
    
    # Copy the exe to the current directory
    import shutil
    if os.path.exists('dist\\ICAuthenticator.exe'):
        shutil.copy2('dist\\ICAuthenticator.exe', 'ICAuthenticator.exe')
        print("\n✓ Copied to current directory")
        
        # Clean up build files
        if os.path.exists('launcher.py'):
            os.remove('launcher.py')
        if os.path.exists('ICAuthenticator.spec'):
            os.remove('ICAuthenticator.spec')
            
        print("\nICAuthenticator.exe is ready for the installer!")
else:
    print("\n✗ Failed to create executable")
    print(result.stderr)
    sys.exit(1)
