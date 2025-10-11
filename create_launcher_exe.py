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
import datetime

# Set working directory to executable location FIRST (before any imports)
app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(app_dir)

# Create error log file for debugging
error_log = os.path.join(app_dir, 'launcher_error.log')

def log_message(message):
    """Log message to file for debugging"""
    try:
        with open(error_log, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {message}\\n")
    except:
        pass

log_message("=" * 60)
log_message("IC Authenticator Launcher Starting")
log_message(f"Working directory: {os.getcwd()}")
log_message(f"Executable location: {app_dir}")
log_message(f"Python version: {sys.version}")

# Set Windows App User Model ID for proper taskbar icon
if sys.platform == 'win32':
    try:
        myappid = 'Ross0907.ICAuthenticator.ProductionGUI.v3.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        log_message("Set Windows App User Model ID")
    except Exception as e:
        log_message(f"Failed to set App User Model ID: {e}")

def show_error(title, message):
    """Show error message box"""
    log_message(f"ERROR: {title} - {message}")
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
    except:
        pass

def show_info(title, message):
    """Show info message box"""
    log_message(f"INFO: {title} - {message}")
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
    except:
        pass

def show_question(title, message):
    """Show yes/no question"""
    log_message(f"QUESTION: {title} - {message}")
    try:
        result = ctypes.windll.user32.MessageBoxW(0, message, title, 0x04)
        return result == 6  # IDYES
    except:
        return False

# Check Python with multiple methods (no console output)
python_found = False
python_cmd = None

log_message("Searching for Python installation...")

# Method 1: Check if python is in PATH
for cmd in ['python', 'python3', 'py']:
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5, 
                              creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode == 0:
            python_found = True
            python_cmd = cmd
            log_message(f"Found Python via PATH: {cmd} - {result.stdout.strip()}")
            break
    except Exception as e:
        log_message(f"Failed to check {cmd}: {e}")
        continue

# Method 2: Check common installation paths
if not python_found:
    log_message("Python not in PATH, checking common locations...")
    common_paths = [
        r"C:\\Program Files\\Python311\\python.exe",
        r"C:\\Program Files\\Python310\\python.exe",
        r"C:\\Python311\\python.exe",
        r"C:\\Python310\\python.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Python\\Python311\\python.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Python\\Python310\\python.exe"),
    ]
    
    for path in common_paths:
        log_message(f"Checking: {path}")
        if os.path.exists(path):
            try:
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    python_found = True
                    python_cmd = path
                    log_message(f"Found Python: {path} - {result.stdout.strip()}")
                    break
            except Exception as e:
                log_message(f"Failed to check {path}: {e}")
                continue

if not python_found:
    show_error("Python Not Found", 
               "Python is not installed or not in PATH.\\n\\n"
               "Please install Python 3.11 or later from:\\n"
               "https://www.python.org\\n\\n"
               "Make sure to check 'Add Python to PATH' during installation.\\n\\n"
               f"Error log: {error_log}")
    sys.exit(1)

# Check critical dependencies (no console output)
log_message("Checking critical dependencies...")
missing_deps = []
critical_packages = ['PyQt5', 'cv2', 'torch', 'easyocr']

for package in critical_packages:
    try:
        result = subprocess.run([python_cmd, '-c', f'import {package}'], 
                              capture_output=True, text=True, timeout=10,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode != 0:
            missing_deps.append(package)
            log_message(f"Missing package: {package}")
        else:
            log_message(f"Found package: {package}")
    except Exception as e:
        missing_deps.append(package)
        log_message(f"Error checking {package}: {e}")

if missing_deps:
    # Offer to install dependencies
    response = show_question("Install Dependencies", 
                            f"The following dependencies are missing:\\n"
                            f"{', '.join(missing_deps)}\\n\\n"
                            f"Would you like to install them now?\\n"
                            f"(This will take 10-20 minutes)")
    
    if response:
        # Run the dependency installer in visible console
        try:
            subprocess.Popen([python_cmd, 'install_dependencies.py'], 
                           cwd=app_dir,
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            show_info("Installing", 
                     "Dependencies are being installed in a new window.\\n\\n"
                     "The window will close automatically when done.\\n\\n"
                     "Please restart IC Authenticator after installation completes.")
            sys.exit(0)
        except Exception as e:
            show_error("Installation Error", 
                      f"Failed to start dependency installer:\\n\\n{e}")
            sys.exit(1)
    else:
        sys.exit(1)

# Launch the application with pythonw (no console window)
try:
    log_message("Launching application...")
    
    # Use pythonw to launch without console
    pythonw_cmd = python_cmd.replace('python.exe', 'pythonw.exe')
    if not os.path.exists(pythonw_cmd):
        pythonw_cmd = python_cmd
        log_message(f"pythonw not found, using: {python_cmd}")
    else:
        log_message(f"Using pythonw: {pythonw_cmd}")
    
    # Check if GUI file exists
    gui_file = os.path.join(app_dir, 'gui_classic_production.py')
    log_message(f"Looking for GUI file: {gui_file}")
    
    if not os.path.exists(gui_file):
        show_error("Missing File", 
                  f"Cannot find gui_classic_production.py\\n\\n"
                  f"Expected location:\\n{gui_file}\\n\\n"
                  f"Please reinstall the application.\\n\\n"
                  f"Error log: {error_log}")
        sys.exit(1)
    
    log_message("GUI file found, launching...")
    
    # Launch with no console window
    process = subprocess.Popen([pythonw_cmd, gui_file], 
                              cwd=app_dir,
                              creationflags=subprocess.CREATE_NO_WINDOW,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE)
    
    log_message(f"Process started with PID: {process.pid}")
    
    # Wait a moment to check if it crashes immediately
    import time
    time.sleep(3)  # Increased from 2 to 3 seconds
    
    if process.poll() is not None:
        # Process exited, get error
        stderr = process.stderr.read().decode('utf-8', errors='ignore')
        stdout = process.stdout.read().decode('utf-8', errors='ignore')
        error_msg = stderr if stderr else stdout
        
        log_message(f"Process exited with code: {process.returncode}")
        log_message(f"STDERR: {stderr}")
        log_message(f"STDOUT: {stdout}")
        
        if error_msg:
            show_error("Application Error", 
                      f"The application failed to start:\\n\\n{error_msg[:500]}\\n\\n"
                      f"See error log for details:\\n{error_log}")
        else:
            show_error("Application Error", 
                      f"The application exited unexpectedly.\\n\\n"
                      f"Try running install_dependencies.py to reinstall packages.\\n\\n"
                      f"Error log: {error_log}")
        sys.exit(1)
    else:
        log_message("Application launched successfully")
    
except Exception as e:
    show_error("Launch Error", f"Failed to launch application:\\n\\n{e}\\n\\nError log: {error_log}")
    log_message(f"LAUNCH ERROR: {e}")
    import traceback
    log_message(traceback.format_exc())
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
    print("\n[OK] Successfully created ICAuthenticator.exe")
    print("\nLocation: dist\\ICAuthenticator.exe")
    
    # Copy the exe to the current directory
    import shutil
    if os.path.exists('dist\\ICAuthenticator.exe'):
        shutil.copy2('dist\\ICAuthenticator.exe', 'ICAuthenticator.exe')
        print("\n[OK] Copied to current directory")
        
        # Clean up build files
        if os.path.exists('launcher.py'):
            os.remove('launcher.py')
        if os.path.exists('ICAuthenticator.spec'):
            os.remove('ICAuthenticator.spec')
            
        print("\nICAuthenticator.exe is ready for the installer!")
else:
    print("\n[ERROR] Failed to create executable")
    print(result.stderr)
    sys.exit(1)
