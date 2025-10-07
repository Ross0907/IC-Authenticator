"""
IC Authentication System - Classic GUI with Dark/Light Mode
Restored classic PyQt5 interface with modern dark mode toggle
"""

import sys
import os
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTextEdit, QTabWidget, QCheckBox, QGroupBox,
                             QProgressBar, QComboBox, QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont
from final_production_authenticator import FinalProductionAuthenticator
from datetime import datetime


class ProcessingThread(QThread):
    """Background thread for image processing"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    result = pyqtSignal(dict)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.authenticator = FinalProductionAuthenticator()
    
    def run(self):
        """Run the authentication process"""
        try:
            self.status.emit("Initializing authentication system...")
            self.progress.emit(10)
            
            self.status.emit("Processing image with GPU-accelerated OCR...")
            self.progress.emit(30)
            
            # Run authentication
            result = self.authenticator.authenticate(self.image_path)
            
            self.progress.emit(100)
            self.status.emit("Analysis complete!")
            
            # Emit result
            self.result.emit(result)
            
        except Exception as e:
            self.status.emit(f"Error: {str(e)}")
            self.result.emit({'error': str(e)})


class ICAuthenticatorGUI(QMainWindow):
    """Main GUI Application for IC Authentication System - Classic Edition"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.current_results = None
        self.dark_mode = True  # Default to dark mode
        
        self.init_ui()
        self.apply_theme()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("IC Authentication System - Classic Interface")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Control panel
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Display and results
        right_panel = self.create_display_panel()
        main_layout.addWidget(right_panel, 3)
        
    def create_control_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("IC Authentication\nControl Panel")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Theme Toggle
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout()
        
        self.theme_toggle_btn = QPushButton("🌙 Switch to Light Mode")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_toggle_btn)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Image Selection Group
        image_group = QGroupBox("Image Input")
        image_layout = QVBoxLayout()
        
        self.load_btn = QPushButton("📁 Load IC Image")
        self.load_btn.clicked.connect(self.load_image)
        image_layout.addWidget(self.load_btn)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # Analysis Button
        self.analyze_btn = QPushButton("🔍 Analyze IC")
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.analyze_ic)
        self.analyze_btn.setMinimumHeight(60)
        self.analyze_btn.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(self.analyze_btn)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)
        
        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Additional Options
        options_group = QGroupBox("Additional Options")
        options_layout = QVBoxLayout()
        
        self.export_btn = QPushButton("💾 Export Report")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)
        options_layout.addWidget(self.export_btn)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # System Info
        info_label = QLabel("✅ Final Production Authenticator\n96% accuracy on test set")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        return panel
    
    def create_display_panel(self):
        """Create the right display panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Image Display Tab
        image_tab = self.create_image_tab()
        self.tab_widget.addTab(image_tab, "📷 Image Analysis")
        
        # Results Tab
        results_tab = self.create_results_tab()
        self.tab_widget.addTab(results_tab, "📋 Detailed Results")
        
        # Verification Tab
        verification_tab = self.create_verification_tab()
        self.tab_widget.addTab(verification_tab, "✓ Authenticity")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def create_image_tab(self):
        """Create image display tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Image display
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(800, 600)
        
        scroll = QScrollArea()
        scroll.setWidget(self.image_label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Image info
        self.image_info_label = QLabel("Image Info: -")
        layout.addWidget(self.image_info_label)
        
        return tab
    
    def create_results_tab(self):
        """Create results display tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Results text display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier New", 10))
        layout.addWidget(self.results_text)
        
        return tab
    
    def create_verification_tab(self):
        """Create verification display tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Authenticity Result - BIG INDICATOR
        self.auth_label = QLabel("Not Analyzed Yet")
        self.auth_label.setAlignment(Qt.AlignCenter)
        self.auth_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.auth_label.setMinimumHeight(100)
        self.auth_label.setWordWrap(True)
        layout.addWidget(self.auth_label)
        
        # Confidence Score
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Confidence Score:"))
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setMinimumHeight(35)
        confidence_layout.addWidget(self.confidence_bar)
        self.confidence_label = QLabel("0%")
        self.confidence_label.setFont(QFont("Arial", 12, QFont.Bold))
        confidence_layout.addWidget(self.confidence_label)
        layout.addLayout(confidence_layout)
        
        # Detailed verification info
        self.verification_text = QTextEdit()
        self.verification_text.setReadOnly(True)
        self.verification_text.setFont(QFont("Courier New", 10))
        layout.addWidget(self.verification_text)
        
        return tab
    
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.theme_toggle_btn.setText("☀️ Switch to Light Mode")
        else:
            self.theme_toggle_btn.setText("🌙 Switch to Dark Mode")
        self.apply_theme()
    
    def apply_theme(self):
        """Apply dark or light theme"""
        if self.dark_mode:
            # Dark Mode
            stylesheet = """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #808080;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                text-align: center;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #0e639c;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #3c3c3c;
            }
            QTabBar::tab:selected {
                background-color: #0e639c;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                padding: 5px;
            }
            QScrollArea {
                border: 2px solid #3c3c3c;
                background-color: #2d2d2d;
            }
            """
        else:
            # Light Mode
            stylesheet = """
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #000000;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #000000;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #000000;
            }
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                background-color: #ffffff;
                color: #000000;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            QTextEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #f5f5f5;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #000000;
                padding: 8px 16px;
                border: 1px solid #cccccc;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QScrollArea {
                border: 2px solid #cccccc;
                background-color: #f0f0f0;
            }
            """
        
        self.setStyleSheet(stylesheet)
    
    def load_image(self):
        """Load an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select IC Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.analyze_btn.setEnabled(True)
            self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
            
            # Reset results
            self.current_results = None
            self.auth_label.setText("Not Analyzed Yet")
            self.confidence_bar.setValue(0)
            self.confidence_label.setText("0%")
            self.results_text.clear()
            self.verification_text.clear()
            self.export_btn.setEnabled(False)
    
    def display_image(self, image_path):
        """Display image in the image tab"""
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            800, 600,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
        # Update image info
        image = cv2.imread(image_path)
        if image is not None:
            h, w = image.shape[:2]
            self.image_info_label.setText(
                f"Image Info: {w}x{h} pixels | {os.path.basename(image_path)}"
            )
    
    def analyze_ic(self):
        """Start IC analysis process"""
        if not self.current_image_path:
            return
        
        # Create and start processing thread
        self.processing_thread = ProcessingThread(self.current_image_path)
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.status.connect(self.update_status)
        self.processing_thread.result.connect(self.display_results)
        
        # Disable analyze button during processing
        self.analyze_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        
        self.processing_thread.start()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)
    
    def display_results(self, result):
        """Display authentication results"""
        self.current_results = result
        
        # Re-enable buttons
        self.analyze_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        if 'error' in result:
            self.auth_label.setText(f"❌ ERROR")
            self.auth_label.setStyleSheet("background-color: #ff4444; padding: 20px; border-radius: 10px;")
            self.results_text.setText(f"Error occurred: {result['error']}")
            return
        
        # Extract key information
        is_authentic = result.get('is_authentic', False)
        confidence = result.get('confidence', 0)
        part_number = result.get('part_number', 'Unknown')
        manufacturer = result.get('manufacturer', 'Unknown')
        date_codes = result.get('date_codes', [])
        datasheet_url = result.get('datasheet_url', 'Not found')
        
        # Update BIG authenticity indicator
        if is_authentic:
            self.auth_label.setText(f"✅ AUTHENTIC\n{part_number}")
            self.auth_label.setStyleSheet("background-color: #4CAF50; padding: 20px; border-radius: 10px; color: white;")
        else:
            self.auth_label.setText(f"❌ COUNTERFEIT/SUSPICIOUS\n{part_number}")
            self.auth_label.setStyleSheet("background-color: #ff4444; padding: 20px; border-radius: 10px; color: white;")
        
        # Update confidence bar
        self.confidence_bar.setValue(confidence)
        self.confidence_label.setText(f"{confidence}%")
        
        if confidence >= 80:
            chunk_color = "#4CAF50"  # Green
        elif confidence >= 60:
            chunk_color = "#FFA500"  # Orange
        else:
            chunk_color = "#ff4444"  # Red
        
        self.confidence_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {chunk_color};
            }}
        """)
        
        # Display detailed results
        results_text = f"""
{'='*80}
IC AUTHENTICATION RESULTS
{'='*80}

PART INFORMATION:
  Part Number:     {part_number}
  Manufacturer:    {manufacturer}
  Date Codes:      {', '.join(date_codes) if date_codes else 'Not found'}

AUTHENTICATION:
  Status:          {'✅ AUTHENTIC' if is_authentic else '❌ COUNTERFEIT/SUSPICIOUS'}
  Confidence:      {confidence}%

VERIFICATION:
  Datasheet URL:   {datasheet_url}

OCR EXTRACTED TEXT:
"""
        
        # Add OCR text
        ocr_text = result.get('ocr_text', 'No text extracted')
        results_text += f"  {ocr_text}\n"
        
        # Add GPU info
        if result.get('gpu_used'):
            results_text += f"\n🚀 GPU Acceleration: ENABLED\n"
        
        self.results_text.setText(results_text)
        
        # Display verification details
        verification_text = f"""
{'='*80}
DETAILED VERIFICATION ANALYSIS
{'='*80}

"""
        
        # Add marking validation details
        marking_val = result.get('marking_validation', {})
        if marking_val:
            verification_text += f"MARKING VALIDATION:\n"
            verification_text += f"  Manufacturer: {marking_val.get('manufacturer', 'Unknown')}\n"
            verification_text += f"  Part Number Valid: {marking_val.get('part_number_valid', False)}\n"
            verification_text += f"  Date Code Valid: {marking_val.get('date_code_valid', False)}\n"
            
            issues = marking_val.get('issues', [])
            if issues:
                verification_text += f"\n  ISSUES FOUND:\n"
                for issue in issues:
                    severity = issue.get('severity', 'UNKNOWN')
                    message = issue.get('message', 'Unknown issue')
                    verification_text += f"    [{severity}] {message}\n"
            
            warnings = marking_val.get('warnings', [])
            if warnings:
                verification_text += f"\n  WARNINGS:\n"
                for warning in warnings:
                    if isinstance(warning, dict):
                        msg = warning.get('message', str(warning))
                    else:
                        msg = str(warning)
                    verification_text += f"    - {msg}\n"
        
        # Add reasons
        reasons = result.get('reasons', [])
        if reasons:
            verification_text += f"\nAUTHENTICATION REASONS:\n"
            for reason in reasons:
                verification_text += f"  • {reason}\n"
        
        self.verification_text.setText(verification_text)
        
        # Switch to verification tab to show results
        self.tab_widget.setCurrentIndex(2)
    
    def export_report(self):
        """Export analysis report"""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "No analysis results to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            f"ic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.toPlainText())
                    f.write("\n\n")
                    f.write(self.verification_text.toPlainText())
                
                QMessageBox.information(self, "Success", f"Report exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export report:\n{str(e)}")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    gui = ICAuthenticatorGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
