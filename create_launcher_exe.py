"""
Create ICAuthenticator.exe wrapper
This creates a simple executable that launches the Python application
"""

import os
import sys
import subprocess

# Create a simple Python launcher script
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

# Get the directory where the executable is located
app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(app_dir)

# Check Python
try:
    result = subprocess.run(['python', '--version'], capture_output=True, text=True)
    if result.returncode != 0:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Python Not Found", 
                           "Python is not installed or not in PATH.\\n\\n"
                           "Please install Python 3.11 or later from:\\n"
                           "https://www.python.org")
        sys.exit(1)
except Exception as e:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", f"Failed to check Python: {e}")
    sys.exit(1)

# Check dependencies
try:
    result = subprocess.run(['python', '-c', 'import PyQt5'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        # Dependencies not installed, try to install
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        response = messagebox.askyesno("Install Dependencies", 
                                      "Required dependencies are not installed.\\n\\n"
                                      "Would you like to install them now?\\n"
                                      "(This will take a few minutes)")
        if response:
            # Show progress window
            progress_window = tk.Toplevel()
            progress_window.title("Installing Dependencies")
            progress_window.geometry("400x100")
            label = tk.Label(progress_window, 
                           text="Installing dependencies...\\nThis may take several minutes.\\nPlease wait...")
            label.pack(expand=True)
            progress_window.update()
            
            # Install dependencies
            subprocess.run(['python', '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         capture_output=True)
            result = subprocess.run(['python', '-m', 'pip', 'install', '-r', 
                                   'requirements_production.txt'], 
                                  capture_output=True, text=True)
            
            progress_window.destroy()
            
            if result.returncode != 0:
                messagebox.showerror("Installation Failed", 
                                   f"Failed to install dependencies:\\n\\n{result.stderr}")
                sys.exit(1)
            else:
                messagebox.showinfo("Success", "Dependencies installed successfully!")
        else:
            sys.exit(1)
except Exception as e:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", f"Failed to check dependencies: {e}")
    sys.exit(1)

# Launch the application
try:
    subprocess.Popen(['pythonw', 'gui_classic_production.py'], 
                    cwd=app_dir)
except Exception as e:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Launch Error", 
                       f"Failed to launch application:\\n\\n{e}")
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
