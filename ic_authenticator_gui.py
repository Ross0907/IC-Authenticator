"""
IC Authentication GUI
Professional interface for IC authentication system
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import threading
from pathlib import Path
import sys
from datetime import datetime

# Import the authentication system
from final_production_authenticator import FinalProductionAuthenticator


class ICAuthenticatorGUI:
    """Professional GUI for IC Authentication System"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("IC Authentication System - v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize authenticator (will be done in thread)
        self.authenticator = None
        self.current_image_path = None
        self.current_result = None
        
        # Color scheme
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#4a9eff',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'panel': '#353535',
            'button': '#4a9eff',
            'button_hover': '#3a7fd5'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Setup UI
        self.setup_ui()
        
        # Initialize authenticator in background
        self.init_authenticator()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Title bar
        title_frame = tk.Frame(self.root, bg=self.colors['accent'], height=60)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🔬 IC Authentication System",
            font=("Arial", 20, "bold"),
            bg=self.colors['accent'],
            fg=self.colors['fg']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        subtitle = tk.Label(
            title_frame,
            text="Powered by AI & Computer Vision",
            font=("Arial", 10),
            bg=self.colors['accent'],
            fg=self.colors['fg']
        )
        subtitle.pack(side=tk.LEFT, padx=5)
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Image viewer
        left_panel = tk.Frame(main_container, bg=self.colors['panel'], relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Image controls
        controls_frame = tk.Frame(left_panel, bg=self.colors['panel'])
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.select_btn = tk.Button(
            controls_frame,
            text="📁 Select IC Image",
            command=self.select_image,
            bg=self.colors['button'],
            fg=self.colors['fg'],
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        self.authenticate_btn = tk.Button(
            controls_frame,
            text="🔍 Authenticate",
            command=self.authenticate_image,
            bg=self.colors['success'],
            fg=self.colors['fg'],
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.authenticate_btn.pack(side=tk.LEFT, padx=5)
        
        # Image display
        image_frame = tk.Frame(left_panel, bg='black', relief=tk.SUNKEN, bd=2)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_label = tk.Label(
            image_frame,
            text="No Image Selected\n\nClick 'Select IC Image' to begin",
            bg='black',
            fg='gray',
            font=("Arial", 14)
        )
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Results
        right_panel = tk.Frame(main_container, bg=self.colors['panel'], relief=tk.RAISED, bd=2, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        # Results header
        results_header = tk.Label(
            right_panel,
            text="📊 Authentication Results",
            font=("Arial", 14, "bold"),
            bg=self.colors['panel'],
            fg=self.colors['fg']
        )
        results_header.pack(pady=10)
        
        # BIG AUTHENTICITY INDICATOR
        self.auth_indicator_frame = tk.Frame(right_panel, bg=self.colors['panel'], height=120)
        self.auth_indicator_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.auth_indicator_frame.pack_propagate(False)
        
        self.auth_indicator = tk.Label(
            self.auth_indicator_frame,
            text="NOT ANALYZED",
            font=("Arial", 18, "bold"),
            bg=self.colors['bg'],
            fg='gray',
            relief=tk.RAISED,
            bd=3
        )
        self.auth_indicator.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Confidence bar
        confidence_frame = tk.Frame(right_panel, bg=self.colors['panel'])
        confidence_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        conf_label = tk.Label(
            confidence_frame,
            text="Confidence:",
            font=("Arial", 10, "bold"),
            bg=self.colors['panel'],
            fg=self.colors['fg']
        )
        conf_label.pack(side=tk.LEFT, padx=5)
        
        self.confidence_label = tk.Label(
            confidence_frame,
            text="0%",
            font=("Arial", 10, "bold"),
            bg=self.colors['panel'],
            fg=self.colors['fg']
        )
        self.confidence_label.pack(side=tk.RIGHT, padx=5)
        
        self.confidence_bar = ttk.Progressbar(
            confidence_frame,
            mode='determinate',
            length=200
        )
        self.confidence_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Results container with scrollbar
        results_container = tk.Frame(right_panel, bg=self.colors['panel'])
        results_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(results_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(
            results_container,
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=("Consolas", 10),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bg=self.colors['panel'],
            fg=self.colors['fg'],
            font=("Arial", 9),
            anchor=tk.W,
            relief=tk.SUNKEN
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial message
        self.update_results("Welcome to IC Authentication System\n\nSelect an image to begin authentication.")
    
    def init_authenticator(self):
        """Initialize the authenticator in background"""
        def init_thread():
            self.update_status("Initializing authentication engine...")
            try:
                self.authenticator = FinalProductionAuthenticator()
                self.root.after(0, lambda: self.update_status("✅ System Ready - GPU Accelerated"))
                self.root.after(0, lambda: self.select_btn.config(state=tk.NORMAL))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"❌ Initialization Error: {str(e)}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to initialize:\n{str(e)}"))
        
        thread = threading.Thread(target=init_thread, daemon=True)
        thread.start()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
    
    def update_results(self, text, clear=True):
        """Update results display"""
        self.results_text.config(state=tk.NORMAL)
        if clear:
            self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)
        self.results_text.see(tk.END)
    
    def select_image(self):
        """Select an IC image file"""
        file_path = filedialog.askopenfilename(
            title="Select IC Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.authenticate_btn.config(state=tk.NORMAL)
            self.update_status(f"Loaded: {Path(file_path).name}")
            self.update_results(f"Image loaded: {Path(file_path).name}\n\nClick 'Authenticate' to analyze.")
    
    def display_image(self, image_path):
        """Display the selected image"""
        try:
            # Load image
            image = Image.open(image_path)
            
            # Resize to fit panel (maintain aspect ratio)
            display_width = 600
            display_height = 600
            
            img_width, img_height = image.size
            ratio = min(display_width/img_width, display_height/img_height)
            new_size = (int(img_width*ratio), int(img_height*ratio))
            
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update label
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep reference
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
            self.update_status("Error loading image")
    
    def authenticate_image(self):
        """Authenticate the selected image"""
        if not self.current_image_path or not self.authenticator:
            return
        
        # Disable button during processing
        self.authenticate_btn.config(state=tk.DISABLED)
        self.update_status("Authenticating... Please wait...")
        self.update_results("🔄 Authentication in progress...\n\nThis may take a few seconds.")
        
        def auth_thread():
            try:
                # Run authentication
                result = self.authenticator.authenticate(self.current_image_path)
                self.current_result = result
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_results(result))
                
            except Exception as e:
                error_msg = f"Authentication failed:\n{str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.update_status("❌ Authentication failed"))
            finally:
                self.root.after(0, lambda: self.authenticate_btn.config(state=tk.NORMAL))
        
        thread = threading.Thread(target=auth_thread, daemon=True)
        thread.start()
    
    def display_results(self, result):
        """Display authentication results"""
        # Build results text
        confidence = result.get('confidence', 0)
        is_authentic = result.get('is_authentic', False)
        part_number = result.get('part_number', 'Unknown')
        manufacturer = result.get('manufacturer', 'Unknown')
        date_codes = result.get('date_codes', [])
        datasheet_found = result.get('datasheet_found', False)
        ocr_confidence = result.get('ocr_confidence', 0)
        
        # Determine status
        if is_authentic:
            status = "✅ AUTHENTIC"
            status_color = self.colors['success']
        else:
            status = "❌ COUNTERFEIT/SUSPICIOUS"
            status_color = self.colors['danger']
        
        # Update BIG authenticity indicator
        self.auth_indicator.config(
            text=f"{status}\n{part_number}",
            bg=status_color,
            fg='white'
        )
        
        # Update confidence bar and label
        self.confidence_bar['value'] = confidence
        self.confidence_label.config(text=f"{confidence}%")
        
        # Color code confidence bar
        style = ttk.Style()
        if confidence >= 80:
            style.configure("TProgressbar", background=self.colors['success'])
        elif confidence >= 60:
            style.configure("TProgressbar", background=self.colors['warning'])
        else:
            style.configure("TProgressbar", background=self.colors['danger'])
        
        # Build formatted output
        output = f"""
{'='*50}
{status}
Confidence: {confidence}%
{'='*50}

📦 PART INFORMATION
{'-'*50}
Part Number:    {part_number}
Manufacturer:   {manufacturer}
Date Codes:     {', '.join(date_codes) if date_codes else 'None'}

🔍 VERIFICATION RESULTS
{'-'*50}
OCR Confidence: {ocr_confidence:.1f}%
Datasheet:      {'✅ Found' if datasheet_found else '❌ Not Found'}

📝 VALIDATION DETAILS
{'-'*50}
"""
        
        # Add validation details
        marking_validation = result.get('marking_validation', {})
        if marking_validation:
            if marking_validation.get('validation_passed'):
                output += "✅ All manufacturer markings valid\n"
            else:
                output += "❌ Invalid or suspicious markings detected\n"
                issues = marking_validation.get('issues', [])
                if issues:
                    output += "\n⚠️ Issues Found:\n"
                    for issue in issues:
                        severity = issue.get('severity', 'UNKNOWN')
                        message = issue.get('message', 'Unknown issue')
                        output += f"  • [{severity}] {message}\n"
        
        output += f"\n{'='*50}\n"
        output += f"Analysis completed at {datetime.now().strftime('%H:%M:%S')}\n"
        output += f"{'='*50}\n"
        
        self.update_results(output)
        self.update_status(f"Analysis complete - {status}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ICAuthenticatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
