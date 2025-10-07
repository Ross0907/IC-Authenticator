"""
IC Authentication System - Modern GUI
Sleek, professional interface with comprehensive analysis display
"""

import sys
import os
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTextEdit, QGroupBox, QScrollArea, QMessageBox, 
                             QProgressBar, QGridLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPalette, QLinearGradient, QPainter
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
    
    def run(self):
        """Run the authentication process"""
        try:
            self.status.emit("🚀 Initializing authentication system...")
            self.progress.emit(10)
            
            authenticator = FinalProductionAuthenticator()
            
            self.status.emit("📝 Extracting text with GPU-accelerated OCR...")
            self.progress.emit(30)
            
            self.status.emit("🔍 Analyzing markings and date codes...")
            self.progress.emit(50)
            
            self.status.emit("📚 Searching datasheets...")
            self.progress.emit(70)
            
            result = authenticator.authenticate(self.image_path)
            
            self.progress.emit(100)
            self.status.emit("✅ Analysis complete!")
            
            self.result.emit(result)
            
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.status.emit(f"❌ {str(e)}")
            self.result.emit({'success': False, 'error': error_msg})


class ModernCard(QGroupBox):
    """Modern card widget with shadow effect - using QGroupBox for stability"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid #444;
                border-radius: 10px;
                margin-top: 10px;
                padding: 15px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        # Create content layout
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setSpacing(10)
        
    def add_widget(self, widget):
        """Add a widget to the content area"""
        self.content_layout.addWidget(widget)
        
    def add_layout(self, child_layout):
        """Add a layout to the content area"""
        self.content_layout.addLayout(child_layout)


class ICAuthenticatorModernGUI(QMainWindow):
    """Modern GUI for IC Authentication System"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.current_results = None
        self.dark_mode = True
        self.processing_thread = None
        
        self.init_ui()
        self.apply_theme()
        
    def init_ui(self):
        """Initialize modern UI"""
        self.setWindowTitle("IC Authentication System - Modern Interface")
        self.setGeometry(50, 50, 1920, 1080)
        self.setMinimumSize(1600, 900)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Left column
        left_col = self.create_left_column()
        content_layout.addWidget(left_col, 1)
        
        # Middle column
        middle_col = self.create_middle_column()
        content_layout.addWidget(middle_col, 2)
        
        # Right column
        right_col = self.create_right_column()
        content_layout.addWidget(right_col, 1)
        
        main_layout.addWidget(content)
        
    def create_header(self):
        """Create compact modern header"""
        header = QWidget()
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 5, 20, 5)
        
        # Compact title
        title = QLabel("🔬 IC Authentication System")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Theme toggle
        self.theme_btn = QPushButton("🌙 Light Mode")
        self.theme_btn.setFixedSize(110, 30)
        self.theme_btn.setFont(QFont("Arial", 9))
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)
        
        return header
        
    def create_left_column(self):
        """Create left column with image and controls"""
        col = QWidget()
        layout = QVBoxLayout(col)
        layout.setSpacing(20)
        
        # Image card
        img_card = ModernCard("Image Preview")
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(500, 500)
        self.image_label.setStyleSheet("border: 2px dashed #444; background: #2b2b2b; border-radius: 10px;")
        self.image_label.setText("📷\n\nNo Image Loaded\n\nClick 'Select Image' to begin")
        self.image_label.setFont(QFont("Arial", 12))
        
        img_card.add_widget(self.image_label)
        layout.addWidget(img_card)
        
        # Control buttons
        btn_layout = QVBoxLayout()
        
        self.select_btn = QPushButton("📁 Select IC Image")
        self.select_btn.setFixedHeight(55)
        self.select_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.select_btn.clicked.connect(self.select_image)
        btn_layout.addWidget(self.select_btn)
        
        self.auth_btn = QPushButton("🔍 Authenticate IC")
        self.auth_btn.setFixedHeight(55)
        self.auth_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.auth_btn.setEnabled(False)
        self.auth_btn.clicked.connect(self.authenticate)
        btn_layout.addWidget(self.auth_btn)
        
        layout.addLayout(btn_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(30)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Ready - Select an image to begin analysis")
        self.status_label.setWordWrap(True)
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("padding: 15px; border: 1px solid #444; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return col
        
    def create_middle_column(self):
        """Create middle column with main results"""
        col = QWidget()
        layout = QVBoxLayout(col)
        layout.setSpacing(20)
        
        # Verdict card
        self.verdict_card = ModernCard()
        self.verdict_label = QLabel("Awaiting Analysis")
        self.verdict_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.verdict_label.setAlignment(Qt.AlignCenter)
        self.verdict_label.setMinimumHeight(120)
        self.verdict_label.setStyleSheet("padding: 30px; border: 3px solid #444; border-radius: 10px;")
        self.verdict_card.add_widget(self.verdict_label)
        layout.addWidget(self.verdict_card)
        
        # Key metrics
        metrics_card = ModernCard("Key Metrics")
        metrics_grid = QGridLayout()
        
        self.metrics = {}
        metric_data = [
            ("Confidence Score", "⭐", 0, 0),
            ("OCR Quality", "📝", 0, 1),
            ("Part Number", "🔧", 1, 0),
            ("Manufacturer", "🏭", 1, 1),
        ]
        
        for label, icon, row, col in metric_data:
            metric_widget = self.create_metric_widget(icon, label, "-")
            metrics_grid.addWidget(metric_widget, row, col)
            self.metrics[label] = metric_widget
        
        # Use add_layout method to add grid to card
        metrics_card.add_layout(metrics_grid)
        layout.addWidget(metrics_card)
        
        # Scoring breakdown
        score_card = ModernCard("Authentication Breakdown")
        self.score_text = QTextEdit()
        self.score_text.setReadOnly(True)
        self.score_text.setMaximumHeight(200)
        self.score_text.setFont(QFont("Arial", 10))
        score_card.add_widget(self.score_text)
        layout.addWidget(score_card)
        
        # Marking validation
        marking_card = ModernCard("Marking Validation")
        self.marking_text = QTextEdit()
        self.marking_text.setReadOnly(True)
        self.marking_text.setFont(QFont("Arial", 10))
        marking_card.add_widget(self.marking_text)
        layout.addWidget(marking_card)
        
        return col
        
    def create_right_column(self):
        """Create right column with detailed info"""
        col = QWidget()
        layout = QVBoxLayout(col)
        layout.setSpacing(20)
        
        # Datasheet info
        datasheet_card = ModernCard("Datasheet Information")
        self.datasheet_text = QTextEdit()
        self.datasheet_text.setReadOnly(True)
        self.datasheet_text.setFont(QFont("Arial", 10))
        self.datasheet_text.setMaximumHeight(250)
        datasheet_card.add_widget(self.datasheet_text)
        layout.addWidget(datasheet_card)
        
        # Date codes
        date_card = ModernCard("Date Codes & Lot Numbers")
        self.date_text = QTextEdit()
        self.date_text.setReadOnly(True)
        self.date_text.setFont(QFont("Arial", 10))
        self.date_text.setMaximumHeight(200)
        date_card.add_widget(self.date_text)
        layout.addWidget(date_card)
        
        # OCR details
        ocr_card = ModernCard("OCR Extraction Details")
        self.ocr_text = QTextEdit()
        self.ocr_text.setReadOnly(True)
        self.ocr_text.setFont(QFont("Arial", 9))
        ocr_card.add_widget(self.ocr_text)
        layout.addWidget(ocr_card)
        
        return col
        
    def create_metric_widget(self, icon, label, value):
        """Create a metric display widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName("metric_value")
        layout.addWidget(value_label)
        
        label_label = QLabel(label)
        label_label.setFont(QFont("Arial", 9))
        label_label.setAlignment(Qt.AlignCenter)
        label_label.setStyleSheet("color: #888;")
        layout.addWidget(label_label)
        
        widget.setStyleSheet("QWidget { border: 1px solid #444; border-radius: 8px; background: #2b2b2b; padding: 10px; }")
        
        return widget
        
    def update_metric(self, metric_name, value):
        """Update a metric value"""
        if metric_name in self.metrics:
            widget = self.metrics[metric_name]
            value_label = widget.findChild(QLabel, "metric_value")
            if value_label:
                value_label.setText(str(value))
                
    def select_image(self):
        """Select an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select IC Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp);;All Files (*.*)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.auth_btn.setEnabled(True)
            self.status_label.setText(f"✅ Image loaded: {os.path.basename(file_path)}")
            self.clear_results()
            
    def display_image(self, image_path):
        """Display the selected image"""
        try:
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            h, w, ch = image.shape
            bytes_per_line = ch * w
            
            # Scale image to fit
            max_size = 600
            scale = min(max_size / w, max_size / h)
            if scale < 1:
                new_w = int(w * scale)
                new_h = int(h * scale)
                image = cv2.resize(image, (new_w, new_h))
                h, w, ch = image.shape
                bytes_per_line = ch * w
            
            q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            self.image_label.setPixmap(pixmap)
            self.image_label.setStyleSheet("border: 2px solid #0d47a1; background: #2b2b2b; border-radius: 10px;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            
    def authenticate(self):
        """Start authentication"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please select an image first!")
            return
            
        self.auth_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.processing_thread = ProcessingThread(self.current_image_path)
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.status.connect(self.update_status)
        self.processing_thread.result.connect(self.display_results)
        self.processing_thread.start()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
    def update_status(self, message):
        """Update status"""
        self.status_label.setText(message)
        
    def display_results(self, results):
        """Display results"""
        self.auth_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if not results.get('success', False):
            QMessageBox.critical(self, "Error", results.get('error', 'Unknown error'))
            return
            
        self.current_results = results
        
        # Update verdict
        is_authentic = results.get('is_authentic', False)
        confidence = results.get('confidence', 0)
        
        if is_authentic:
            verdict_text = f"✅ AUTHENTIC\n{confidence}% Confidence"
            verdict_bg = "#1b5e20"
        else:
            verdict_text = f"❌ COUNTERFEIT\n{confidence}% Confidence"
            verdict_bg = "#b71c1c"
            
        self.verdict_label.setText(verdict_text)
        self.verdict_label.setStyleSheet(f"padding: 30px; border: 3px solid #444; border-radius: 10px; background-color: {verdict_bg};")
        
        # Update metrics
        self.update_metric("Confidence Score", f"{confidence}%")
        self.update_metric("OCR Quality", f"{results.get('ocr_confidence', 0):.1f}%")
        self.update_metric("Part Number", results.get('part_number', 'Unknown'))
        self.update_metric("Manufacturer", results.get('manufacturer', 'Unknown'))
        
        # Update scoring breakdown
        score_html = "<h3>Scoring Breakdown:</h3><ul style='font-size: 11pt;'>"
        for reason in results.get('reasons', []):
            score_html += f"<li>{reason}</li>"
        score_html += "</ul>"
        self.score_text.setHtml(score_html)
        
        # Update marking validation
        marking_html = "<h3>Marking Validation:</h3>"
        marking = results.get('marking_validation', {})
        marking_html += f"<p><b>Status:</b> {'✅ PASSED' if marking.get('validation_passed', False) else '❌ FAILED'}</p>"
        
        if marking.get('issues'):
            marking_html += "<p><b>Issues:</b></p><ul>"
            for issue in marking['issues']:
                emoji = "🔴" if issue['severity'] == 'CRITICAL' else "🟡"
                marking_html += f"<li>{emoji} [{issue['severity']}] {issue['message']}</li>"
            marking_html += "</ul>"
        else:
            marking_html += "<p style='color: #4caf50;'>✅ All markings valid</p>"
            
        self.marking_text.setHtml(marking_html)
        
        # Update datasheet info
        ds_html = "<h3>Datasheet Verification:</h3>"
        if results.get('datasheet_found', False):
            ds_html += "<p><b>Status:</b> ✅ Found</p>"
            ds_html += f"<p><b>Source:</b> {results.get('datasheet_source', 'Unknown')}</p>"
            if results.get('datasheet_url'):
                url = results['datasheet_url']
                ds_html += f"<p><b>URL:</b> <a href='{url}'>{url}</a></p>"
        else:
            ds_html += "<p><b>Status:</b> ❌ Not Found</p>"
            
        self.datasheet_text.setHtml(ds_html)
        
        # Update date codes
        date_html = "<h3>Extracted Codes:</h3>"
        date_codes = results.get('date_codes', [])
        if date_codes:
            date_html += "<ul>"
            for code in date_codes:
                date_html += f"<li>{code}</li>"
            date_html += "</ul>"
        else:
            date_html += "<p>No date codes found</p>"
            
        if results.get('logo_text'):
            date_html += f"<p><b>Logo:</b> {results['logo_text']}</p>"
            
        self.date_text.setHtml(date_html)
        
        # Update OCR details
        ocr_html = "<h3>Full Text:</h3>"
        ocr_html += f"<p>{results.get('full_text', '')}</p>"
        ocr_html += f"<p><b>Variants used:</b> {len(set(r['variant'] for r in results.get('ocr_details', [])))}</p>"
        
        self.ocr_text.setHtml(ocr_html)
        
        self.status_label.setText(f"✅ Analysis complete: {'AUTHENTIC' if is_authentic else 'COUNTERFEIT'}")
        
    def clear_results(self):
        """Clear all results"""
        self.verdict_label.setText("Awaiting Analysis")
        self.verdict_label.setStyleSheet("padding: 30px; border: 3px solid #444; border-radius: 10px;")
        
        for metric in self.metrics.values():
            value_label = metric.findChild(QLabel, "metric_value")
            if value_label:
                value_label.setText("-")
                
        self.score_text.clear()
        self.marking_text.clear()
        self.datasheet_text.clear()
        self.date_text.clear()
        self.ocr_text.clear()
        
    def toggle_theme(self):
        """Toggle theme"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        
    def apply_theme(self):
        """Apply theme"""
        if self.dark_mode:
            self.theme_btn.setText("☀️ Light Mode")
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                }
                QFrame {
                    background-color: #252525;
                    border-radius: 10px;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0d47a1, stop:1 #1565c0);
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1565c0, stop:1 #1976d2);
                }
                QPushButton:pressed {
                    background: #0a3d91;
                }
                QPushButton:disabled {
                    background-color: #333;
                    color: #666;
                }
                QTextEdit {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    border: 1px solid #444;
                    border-radius: 5px;
                    padding: 10px;
                }
                QProgressBar {
                    border: 2px solid #444;
                    border-radius: 8px;
                    text-align: center;
                    background-color: #2b2b2b;
                    color: white;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0d47a1, stop:1 #1976d2);
                    border-radius: 6px;
                }
            """)
        else:
            self.theme_btn.setText("🌙 Dark Mode")
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: #212121;
                }
                QFrame {
                    background-color: white;
                    border-radius: 10px;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1976d2, stop:1 #2196f3);
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196f3, stop:1 #42a5f5);
                }
                QPushButton:pressed {
                    background: #1565c0;
                }
                QPushButton:disabled {
                    background-color: #e0e0e0;
                    color: #9e9e9e;
                }
                QTextEdit {
                    background-color: white;
                    color: #212121;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 10px;
                }
                QProgressBar {
                    border: 2px solid #ccc;
                    border-radius: 8px;
                    text-align: center;
                    background-color: white;
                    color: #212121;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976d2, stop:1 #2196f3);
                    border-radius: 6px;
                }
            """)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("IC Authentication System - Modern")
    
    gui = ICAuthenticatorModernGUI()
    gui.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
