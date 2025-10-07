"""
IC Authentication System - Professional Classic GUI
Production-ready interface with comprehensive details display
"""

import sys
import os
import cv2
import torch
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTextEdit, QTabWidget, QGroupBox, QScrollArea, 
                             QMessageBox, QProgressBar, QGridLayout, QSplitter,
                             QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPalette, QTextCursor
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
            
            # Run authentication
            result = authenticator.authenticate(self.image_path)
            
            self.progress.emit(100)
            self.status.emit("✅ Analysis complete!")
            
            # Emit result
            self.result.emit(result)
            
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.status.emit(f"❌ {str(e)}")
            self.result.emit({'success': False, 'error': error_msg})


class ICAuthenticatorGUI(QMainWindow):
    """Main GUI Application for IC Authentication System"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.current_results = None
        self.dark_mode = True
        self.processing_thread = None
        
        self.init_ui()
        self.apply_theme()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("IC Authentication System - Professional Edition")
        self.setGeometry(50, 50, 1800, 1000)
        self.setMinimumSize(1400, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Compact header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Control and image
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([600, 1200])
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("Ready")
        
    def create_header(self):
        """Create compact header with title"""
        header = QWidget()
        header.setFixedHeight(50)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 5, 20, 5)
        
        # Compact title
        title = QLabel("🔬 IC Authentication System")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        return header
        
    def create_left_panel(self):
        """Create compact left panel with controls and image"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Full-width button layout
        select_layout = QHBoxLayout()
        select_layout.setSpacing(5)
        select_layout.setContentsMargins(0, 0, 0, 0)
        
        self.select_btn = QPushButton("📁 Select Image")
        self.select_btn.setFixedHeight(40)
        self.select_btn.setFont(QFont("Arial", 10))
        self.select_btn.clicked.connect(self.select_image)
        select_layout.addWidget(self.select_btn, stretch=1)  # Takes 50% space
        
        # Theme toggle - takes other 50% space
        self.theme_btn = QPushButton("🌙 Light Mode")
        self.theme_btn.setFixedHeight(40)
        self.theme_btn.setFont(QFont("Arial", 10))
        self.theme_btn.clicked.connect(self.toggle_theme)
        select_layout.addWidget(self.theme_btn, stretch=1)  # Takes 50% space
        
        layout.addLayout(select_layout)
        
        # Compact file path display
        self.image_path_label = QLabel("No image selected")
        self.image_path_label.setWordWrap(True)
        self.image_path_label.setMaximumHeight(35)
        self.image_path_label.setStyleSheet("padding: 5px; border: 1px solid #444; font-size: 9pt;")
        layout.addWidget(self.image_path_label)
        
        # Image display - larger now
        display_group = QGroupBox("Image Preview")
        display_layout = QVBoxLayout()
        display_layout.setContentsMargins(5, 5, 5, 5)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(450, 450)
        self.image_label.setStyleSheet("border: 2px solid #444; background: #2b2b2b;")
        self.image_label.setText("No Image Loaded")
        
        display_layout.addWidget(self.image_label)
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Debug options - better spacing
        debug_group = QGroupBox("Debug Options")
        debug_layout = QHBoxLayout()
        debug_layout.setSpacing(15)
        debug_layout.setContentsMargins(10, 10, 10, 10)
        
        self.show_preprocessed_cb = QCheckBox("Show Preprocessing")
        self.show_preprocessed_cb.setStyleSheet("font-size: 10pt;")
        self.show_preprocessed_cb.setToolTip("Show preprocessed image layers")
        self.show_preprocessed_cb.toggled.connect(self.on_debug_option_changed)
        debug_layout.addWidget(self.show_preprocessed_cb)
        
        self.show_bboxes_cb = QCheckBox("Show Text Boxes")
        self.show_bboxes_cb.setStyleSheet("font-size: 10pt;")
        self.show_bboxes_cb.setToolTip("Show OCR bounding boxes")
        self.show_bboxes_cb.toggled.connect(self.on_debug_option_changed)
        debug_layout.addWidget(self.show_bboxes_cb)
        
        debug_layout.addStretch()  # Push checkboxes to left
        
        debug_group.setLayout(debug_layout)
        debug_group.setMaximumHeight(65)  # Slightly taller for better spacing
        layout.addWidget(debug_group)
        
        # Authenticate button
        self.auth_btn = QPushButton("🔍 Authenticate IC")
        self.auth_btn.setFixedHeight(50)
        self.auth_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.auth_btn.setEnabled(False)
        self.auth_btn.clicked.connect(self.authenticate)
        layout.addWidget(self.auth_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status and info section
        status_group = QGroupBox("Status & Information")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        
        self.status_label = QLabel("Ready - Select an image to begin")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 8px; border: 1px solid #444; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        # Additional info grid
        info_grid = QGridLayout()
        info_grid.setSpacing(3)
        
        # GPU status
        gpu_label = QLabel("GPU:")
        gpu_label.setStyleSheet("font-weight: bold; font-size: 9pt;")
        self.gpu_status = QLabel("Detecting...")
        self.gpu_status.setStyleSheet("font-size: 9pt;")
        info_grid.addWidget(gpu_label, 0, 0)
        info_grid.addWidget(self.gpu_status, 0, 1)
        
        # Processing time
        time_label = QLabel("Time:")
        time_label.setStyleSheet("font-weight: bold; font-size: 9pt;")
        self.process_time = QLabel("-")
        self.process_time.setStyleSheet("font-size: 9pt;")
        info_grid.addWidget(time_label, 0, 2)
        info_grid.addWidget(self.process_time, 0, 3)
        
        # Image size
        size_label = QLabel("Size:")
        size_label.setStyleSheet("font-weight: bold; font-size: 9pt;")
        self.image_size = QLabel("-")
        self.image_size.setStyleSheet("font-size: 9pt;")
        info_grid.addWidget(size_label, 1, 0)
        info_grid.addWidget(self.image_size, 1, 1)
        
        # Variants used
        var_label = QLabel("Variants:")
        var_label.setStyleSheet("font-weight: bold; font-size: 9pt;")
        self.variants_used = QLabel("-")
        self.variants_used.setStyleSheet("font-size: 9pt;")
        info_grid.addWidget(var_label, 1, 2)
        info_grid.addWidget(self.variants_used, 1, 3)
        
        status_layout.addLayout(info_grid)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Detect GPU on startup
        self.detect_gpu()
        
        return panel
    
    def detect_gpu(self):
        """Detect GPU availability"""
        try:
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                self.gpu_status.setText(f"✅ {gpu_name[:20]}")
                self.gpu_status.setStyleSheet("font-size: 9pt; color: #4CAF50;")
            else:
                self.gpu_status.setText("❌ CPU Only")
                self.gpu_status.setStyleSheet("font-size: 9pt; color: #FFA726;")
        except:
            self.gpu_status.setText("❌ CPU Only")
            self.gpu_status.setStyleSheet("font-size: 9pt; color: #FFA726;")
        
    def create_results_panel(self):
        """Create right panel for displaying results"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Results tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Summary
        self.summary_tab = self.create_summary_tab()
        self.tabs.addTab(self.summary_tab, "📊 Summary")
        
        # Tab 2: Detailed Analysis
        self.details_tab = self.create_details_tab()
        self.tabs.addTab(self.details_tab, "🔬 Detailed Analysis")
        
        # Tab 3: Debug Images
        self.debug_tab = self.create_debug_tab()
        self.tabs.addTab(self.debug_tab, "🐛 Debug Images")
        
        # Tab 4: Raw Data
        self.raw_tab = self.create_raw_tab()
        self.tabs.addTab(self.raw_tab, "📝 Raw Data")
        
        layout.addWidget(self.tabs)
        
        return panel
        
    def create_summary_tab(self):
        """Create summary results tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Verdict display
        self.verdict_label = QLabel("Awaiting Analysis...")
        self.verdict_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.verdict_label.setAlignment(Qt.AlignCenter)
        self.verdict_label.setMinimumHeight(80)
        self.verdict_label.setStyleSheet("padding: 20px; border: 2px solid #444; border-radius: 5px;")
        layout.addWidget(self.verdict_label)
        
        # Key Information Grid
        info_group = QGroupBox("Key Information")
        info_layout = QGridLayout()
        
        labels = [
            ("Part Number:", 0, 0),
            ("Manufacturer:", 1, 0),
            ("Date Code:", 2, 0),
            ("Confidence Score:", 3, 0),
            ("OCR Confidence:", 4, 0),
            ("Datasheet:", 5, 0),
        ]
        
        self.info_values = {}
        for text, row, col in labels:
            label = QLabel(text)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            info_layout.addWidget(label, row, col)
            
            value = QLabel("-")
            value.setFont(QFont("Arial", 10))
            info_layout.addWidget(value, row, col + 1)
            self.info_values[text] = value
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Scoring Breakdown
        score_group = QGroupBox("Authentication Breakdown")
        score_layout = QVBoxLayout()
        
        self.score_text = QTextEdit()
        self.score_text.setReadOnly(True)
        self.score_text.setMaximumHeight(200)
        score_layout.addWidget(self.score_text)
        
        score_group.setLayout(score_layout)
        layout.addWidget(score_group)
        
        layout.addStretch()
        
        return tab
        
    def create_details_tab(self):
        """Create detailed analysis tab with dynamic sizing"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use splitter for dynamic resizing
        splitter = QSplitter(Qt.Vertical)
        
        # Marking Validation (smaller - typically just pass/fail)
        marking_group = QGroupBox("Marking Validation")
        marking_layout = QVBoxLayout()
        
        self.marking_text = QTextEdit()
        self.marking_text.setReadOnly(True)
        marking_layout.addWidget(self.marking_text)
        
        marking_group.setLayout(marking_layout)
        splitter.addWidget(marking_group)
        
        # Datasheet Information
        datasheet_group = QGroupBox("Datasheet Information")
        datasheet_layout = QVBoxLayout()
        
        self.datasheet_text = QTextEdit()
        self.datasheet_text.setReadOnly(True)
        datasheet_layout.addWidget(self.datasheet_text)
        
        datasheet_group.setLayout(datasheet_layout)
        splitter.addWidget(datasheet_group)
        
        # OCR Details (larger - contains detailed extraction info)
        ocr_group = QGroupBox("OCR Extraction Details")
        ocr_layout = QVBoxLayout()
        
        self.ocr_text = QTextEdit()
        self.ocr_text.setReadOnly(True)
        ocr_layout.addWidget(self.ocr_text)
        
        ocr_group.setLayout(ocr_layout)
        splitter.addWidget(ocr_group)
        
        # Set initial sizes (marking:datasheet:ocr = 1:2:3 ratio)
        splitter.setSizes([150, 200, 400])
        splitter.setStretchFactor(0, 1)  # Marking - least stretch
        splitter.setStretchFactor(1, 2)  # Datasheet - medium stretch
        splitter.setStretchFactor(2, 3)  # OCR - most stretch
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_debug_tab(self):
        """Create debug images tab with preprocessing, OCR, and text boxes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area for debug images
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container for images
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Info label
        self.debug_info = QLabel("Debug images will appear here after authentication")
        self.debug_info.setAlignment(Qt.AlignCenter)
        self.debug_info.setStyleSheet("padding: 20px; font-size: 11pt; color: #888;")
        container_layout.addWidget(self.debug_info)
        
        # OCR with bounding boxes section (moved above preprocessing)
        ocr_group = QGroupBox("OCR with Text Bounding Boxes")
        self.ocr_layout = QVBoxLayout()
        ocr_group.setLayout(self.ocr_layout)
        ocr_group.setVisible(False)  # Hidden until we have images
        container_layout.addWidget(ocr_group)
        self.ocr_group = ocr_group
        
        # Preprocessing variants section (moved below OCR)
        preprocessing_group = QGroupBox("Preprocessing Variants")
        self.preprocessing_layout = QVBoxLayout()
        preprocessing_group.setLayout(self.preprocessing_layout)
        preprocessing_group.setVisible(False)  # Hidden until we have images
        container_layout.addWidget(preprocessing_group)
        self.preprocessing_group = preprocessing_group
        
        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        return tab
        
    def create_raw_tab(self):
        """Create raw data tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        self.raw_text.setFont(QFont("Courier New", 9))
        layout.addWidget(self.raw_text)
        
        return tab
        
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
            self.image_path_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.display_image(file_path)
            self.auth_btn.setEnabled(True)
            self.statusBar.showMessage(f"Image loaded: {os.path.basename(file_path)}")
            
            # Clear previous results
            self.clear_results()
            
    def display_image(self, image_path):
        """Display the selected image"""
        try:
            image = cv2.imread(image_path)
            original_h, original_w = image.shape[:2]
            
            # Update image size info
            self.image_size.setText(f"{original_w}×{original_h}")
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            h, w, ch = image.shape
            bytes_per_line = ch * w
            
            # Scale image to fit label
            max_size = 500
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
            self.image_label.setScaledContents(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            
    def authenticate(self):
        """Start authentication process"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please select an image first!")
            return
            
        # Disable button during processing
        self.auth_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start processing thread
        self.processing_thread = ProcessingThread(self.current_image_path)
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.status.connect(self.update_status)
        self.processing_thread.result.connect(self.display_results)
        self.processing_thread.start()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
    def update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)
        self.statusBar.showMessage(message)
        
    def display_results(self, results):
        """Display authentication results"""
        self.auth_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if not results.get('success', False):
            QMessageBox.critical(self, "Error", results.get('error', 'Unknown error'))
            return
            
        self.current_results = results
        
        # Update status information
        if 'processing_time' in results:
            self.process_time.setText(f"{results['processing_time']:.2f}s")
        
        if 'variants_count' in results:
            self.variants_used.setText(str(results['variants_count']))
        elif 'ocr_details' in results:
            # Count unique variants
            variants = set(d.get('variant', '') for d in results['ocr_details'])
            self.variants_used.setText(str(len(variants)))
        
        # Update Summary Tab
        is_authentic = results.get('is_authentic', False)
        confidence = results.get('confidence', 0)
        
        if is_authentic:
            verdict_text = f"✅ AUTHENTIC\nConfidence: {confidence}%"
            verdict_color = "#2d5016"
        else:
            verdict_text = f"❌ COUNTERFEIT/SUSPICIOUS\nConfidence: {confidence}%"
            verdict_color = "#5c1010"
            
        self.verdict_label.setText(verdict_text)
        self.verdict_label.setStyleSheet(f"padding: 20px; border: 2px solid #444; border-radius: 5px; background-color: {verdict_color};")
        
        # Update key information
        self.info_values["Part Number:"].setText(results.get('part_number', 'Unknown'))
        self.info_values["Manufacturer:"].setText(results.get('manufacturer', 'Unknown'))
        self.info_values["Date Code:"].setText(', '.join(results.get('date_codes', [])) if results.get('date_codes') else 'None')
        self.info_values["Confidence Score:"].setText(f"{confidence}%")
        self.info_values["OCR Confidence:"].setText(f"{results.get('ocr_confidence', 0):.1f}%")
        self.info_values["Datasheet:"].setText("✅ Found" if results.get('datasheet_found', False) else "❌ Not Found")
        
        # Update scoring breakdown
        score_html = "<h3>Scoring Breakdown:</h3><ul>"
        for reason in results.get('reasons', []):
            score_html += f"<li>{reason}</li>"
        score_html += "</ul>"
        self.score_text.setHtml(score_html)
        
        # Update Details Tab
        self.update_details_tab(results)
        
        # Update Debug Tab
        self.update_debug_tab(results)
        
        # Update Raw Data Tab
        self.update_raw_tab(results)
        
        self.statusBar.showMessage(f"Analysis complete: {'AUTHENTIC' if is_authentic else 'COUNTERFEIT/SUSPICIOUS'}")
        
    def update_details_tab(self, results):
        """Update detailed analysis tab"""
        # Marking validation
        marking_html = "<h3>Marking Validation:</h3>"
        marking = results.get('marking_validation', {})
        marking_html += f"<p><b>Manufacturer:</b> {results.get('manufacturer', 'Unknown')}</p>"
        marking_html += f"<p><b>Validation Status:</b> {'✅ PASSED' if marking.get('validation_passed', False) else '❌ FAILED'}</p>"
        
        if marking.get('issues'):
            marking_html += "<p><b>Issues Found:</b></p><ul>"
            for issue in marking['issues']:
                emoji = "🔴" if issue['severity'] == 'CRITICAL' else "🟡" if issue['severity'] == 'MAJOR' else "🔵"
                marking_html += f"<li>{emoji} [{issue['severity']}] {issue['message']}</li>"
            marking_html += "</ul>"
        else:
            marking_html += "<p style='color: green;'>✅ No issues found - markings are valid</p>"
            
        self.marking_text.setHtml(marking_html)
        
        # Datasheet information
        datasheet_html = "<h3>Datasheet Verification:</h3>"
        if results.get('datasheet_found', False):
            datasheet_html += f"<p><b>Status:</b> ✅ Datasheet Found</p>"
            datasheet_html += f"<p><b>Source:</b> {results.get('datasheet_source', 'Unknown')}</p>"
            if results.get('datasheet_url'):
                url = results['datasheet_url']
                datasheet_html += f"<p><b>URL:</b> <a href='{url}' style='color: #4A9EFF;'>{url}</a></p>"
        else:
            datasheet_html += "<p><b>Status:</b> ❌ Datasheet Not Found</p>"
            datasheet_html += "<p>This could indicate a rare/obsolete part or potentially counterfeit IC</p>"
            
        self.datasheet_text.setHtml(datasheet_html)
        
        # OCR details
        ocr_html = "<h3>OCR Extraction:</h3>"
        
        # Format full text with better readability
        full_text = results.get('full_text', '')
        if full_text:
            # Split into words and format nicely
            words = full_text.split()
            formatted_text = '<br>'.join([' '.join(words[i:i+8]) for i in range(0, len(words), 8)])
            ocr_html += f"<p><b>Full Text:</b><br><span style='font-family: Courier New; font-size: 10pt; background: #1a1a1a; padding: 10px; display: block; border: 1px solid #444; border-radius: 3px;'>{formatted_text}</span></p>"
        else:
            ocr_html += f"<p><b>Full Text:</b> <i>No text detected</i></p>"
        
        ocr_html += f"<p><b>Overall Confidence:</b> {results.get('ocr_confidence', 0):.1f}%</p>"
        
        if results.get('ocr_details'):
            ocr_html += "<p><b>Individual Detections:</b></p><table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>"
            ocr_html += "<tr style='background: #2a2a2a;'><th>Text</th><th>Confidence</th><th>Variant</th></tr>"
            
            for detail in results['ocr_details'][:20]:  # Limit to 20 entries
                text = detail.get('text', '')
                conf = detail.get('confidence', 0) * 100
                variant = detail.get('variant', '')
                ocr_html += f"<tr><td>{text}</td><td>{conf:.1f}%</td><td>{variant}</td></tr>"
            
            if len(results['ocr_details']) > 20:
                ocr_html += f"<tr><td colspan='3' style='text-align: center; font-style: italic;'>... and {len(results['ocr_details']) - 20} more</td></tr>"
            
            ocr_html += "</table>"
            
        self.ocr_text.setHtml(ocr_html)
        
    def update_raw_tab(self, results):
        """Update raw data tab with JSON-like output"""
        import json
        import numpy as np
        
        # Custom JSON encoder for numpy types
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.integer, np.int32, np.int64)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float32, np.float64)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)
        
        # Filter out non-serializable items and debug arrays
        filtered_results = {
            k: v for k, v in results.items()
            if k not in ['marking_validation', 'datasheet_details', 'debug_variants', 
                        'debug_ocr_image', 'preprocessed_image', 'original_image']
        }
        
        # Add simplified versions
        if 'marking_validation' in results:
            filtered_results['marking_validation_summary'] = {
                'passed': results['marking_validation'].get('validation_passed', False),
                'manufacturer': results['marking_validation'].get('manufacturer', 'Unknown'),
                'issues_count': len(results['marking_validation'].get('issues', []))
            }
        
        # Clean up OCR details to be more readable
        if 'ocr_details' in filtered_results:
            cleaned_details = []
            for detail in filtered_results['ocr_details']:
                cleaned_detail = {
                    'text': detail.get('text', ''),
                    'confidence': f"{float(detail.get('confidence', 0))*100:.2f}%",
                    'variant': detail.get('variant', ''),
                    'bbox': [[int(x), int(y)] for x, y in detail.get('bbox', [])]
                }
                cleaned_details.append(cleaned_detail)
            filtered_results['ocr_details'] = cleaned_details
        
        # Format validation issues if present
        if 'validation_issues' in filtered_results:
            issues = filtered_results['validation_issues']
            filtered_results['validation_issues'] = [
                {
                    'type': issue.get('type', ''),
                    'severity': issue.get('severity', ''),
                    'message': issue.get('message', '')
                }
                for issue in issues
            ]
        
        # Clean numeric values
        for key in ['ocr_confidence', 'confidence', 'processing_time']:
            if key in filtered_results and isinstance(filtered_results[key], (np.floating, np.float32, np.float64, float)):
                filtered_results[key] = round(float(filtered_results[key]), 2)
        
        try:
            # Use custom encoder and add more indentation for readability
            raw_text = json.dumps(filtered_results, indent=4, ensure_ascii=False, cls=NumpyEncoder)
        except Exception as e:
            # Fallback: convert to string representation
            raw_text = f"Error formatting data: {str(e)}\n\n{str(filtered_results)}"
            
        self.raw_text.setPlainText(raw_text)
    
    def update_debug_tab(self, results):
        """Update debug tab with preprocessing variants and OCR visualizations"""
        # Clear previous debug images
        while self.preprocessing_layout.count():
            child = self.preprocessing_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        while self.ocr_layout.count():
            child = self.ocr_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Hide info label
        self.debug_info.setVisible(False)
        
        # Show preprocessing variants if checkbox is checked
        if self.show_preprocessed_cb.isChecked() and 'debug_variants' in results:
            self.preprocessing_group.setVisible(True)
            variants = results['debug_variants']
            
            for name, img in variants[:6]:  # Show first 6 variants
                # Create label for variant name
                name_label = QLabel(f"Variant: {name}")
                name_label.setStyleSheet("font-weight: bold; font-size: 10pt; padding: 5px;")
                self.preprocessing_layout.addWidget(name_label)
                
                # Convert and display image
                img_label = QLabel()
                img_label.setAlignment(Qt.AlignCenter)
                
                # Convert image to QPixmap
                if len(img.shape) == 2:  # Grayscale
                    h, w = img.shape
                    q_image = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
                else:  # BGR
                    h, w, ch = img.shape
                    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    q_image = QImage(rgb.data, w, h, w * ch, QImage.Format_RGB888)
                
                # Scale to reasonable size
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label.setPixmap(scaled_pixmap)
                img_label.setStyleSheet("border: 1px solid #444; padding: 5px; background: #2b2b2b;")
                
                self.preprocessing_layout.addWidget(img_label)
        else:
            self.preprocessing_group.setVisible(False)
        
        # Show OCR visualization if checkbox is checked
        if self.show_bboxes_cb.isChecked() and 'debug_ocr_image' in results:
            self.ocr_group.setVisible(True)
            
            ocr_label = QLabel("Original image with OCR detections:")
            ocr_label.setStyleSheet("font-weight: bold; font-size: 10pt; padding: 5px;")
            self.ocr_layout.addWidget(ocr_label)
            
            # Display OCR image
            img = results['debug_ocr_image']
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            
            # Convert to QPixmap
            if len(img.shape) == 2:
                h, w = img.shape
                q_image = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
            else:
                h, w, ch = img.shape
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                q_image = QImage(rgb.data, w, h, w * ch, QImage.Format_RGB888)
            
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(scaled_pixmap)
            img_label.setStyleSheet("border: 1px solid #444; padding: 5px; background: #2b2b2b;")
            
            self.ocr_layout.addWidget(img_label)
        else:
            self.ocr_group.setVisible(False)
        
        # If neither checkbox is checked, show info message
        if not self.show_preprocessed_cb.isChecked() and not self.show_bboxes_cb.isChecked():
            self.debug_info.setText("Enable debug options (Show Preprocessing / Show Text Boxes) to view debug images")
            self.debug_info.setVisible(True)
    
    def on_debug_option_changed(self):
        """Called when debug checkboxes are toggled"""
        if self.current_results:
            self.update_debug_tab(self.current_results)
        
    def clear_results(self):
        """Clear all result displays"""
        self.verdict_label.setText("Awaiting Analysis...")
        self.verdict_label.setStyleSheet("padding: 20px; border: 2px solid #444; border-radius: 5px;")
        
        for key, label in self.info_values.items():
            label.setText("-")
            
        self.score_text.clear()
        self.marking_text.clear()
        self.datasheet_text.clear()
        self.ocr_text.clear()
        self.raw_text.clear()
        
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        
    def apply_theme(self):
        """Apply dark or light theme"""
        if self.dark_mode:
            self.theme_btn.setText("☀️ Light Mode")
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }
                QGroupBox {
                    border: 2px solid #444;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QPushButton {
                    background-color: #0d47a1;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:pressed {
                    background-color: #0a3d91;
                }
                QPushButton:disabled {
                    background-color: #424242;
                    color: #888;
                }
                QTextEdit, QLabel {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    border: 1px solid #444;
                    padding: 5px;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                }
                QTabBar::tab {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    padding: 10px 20px;
                    border: 1px solid #444;
                }
                QTabBar::tab:selected {
                    background-color: #0d47a1;
                }
                QProgressBar {
                    border: 1px solid #444;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #2b2b2b;
                }
                QProgressBar::chunk {
                    background-color: #0d47a1;
                }
                QStatusBar {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QScrollBar:vertical {
                    background-color: #2b2b2b;
                    width: 14px;
                    border: 1px solid #444;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical {
                    background-color: #0d47a1;
                    border-radius: 6px;
                    min-height: 30px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #1565c0;
                }
                QScrollBar::handle:vertical:pressed {
                    background-color: #0a3d91;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                QScrollBar:horizontal {
                    background-color: #2b2b2b;
                    height: 14px;
                    border: 1px solid #444;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #0d47a1;
                    border-radius: 6px;
                    min-width: 30px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #1565c0;
                }
                QScrollBar::handle:horizontal:pressed {
                    background-color: #0a3d91;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
            """)
        else:
            self.theme_btn.setText("🌙 Dark Mode")
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: #212121;
                }
                QGroupBox {
                    border: 2px solid #ccc;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QPushButton {
                    background-color: #1976d2;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2196f3;
                }
                QPushButton:pressed {
                    background-color: #1565c0;
                }
                QPushButton:disabled {
                    background-color: #e0e0e0;
                    color: #9e9e9e;
                }
                QTextEdit, QLabel {
                    background-color: white;
                    color: #212121;
                    border: 1px solid #ccc;
                    padding: 5px;
                }
                QTabWidget::pane {
                    border: 1px solid #ccc;
                }
                QTabBar::tab {
                    background-color: #e0e0e0;
                    color: #212121;
                    padding: 10px 20px;
                    border: 1px solid #ccc;
                }
                QTabBar::tab:selected {
                    background-color: #1976d2;
                    color: white;
                }
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                    background-color: white;
                }
                QProgressBar::chunk {
                    background-color: #1976d2;
                }
                QStatusBar {
                    background-color: #e0e0e0;
                    color: #212121;
                }
                QScrollBar:vertical {
                    background-color: #f5f5f5;
                    width: 14px;
                    border: 1px solid #ccc;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical {
                    background-color: #1976d2;
                    border-radius: 6px;
                    min-height: 30px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #2196f3;
                }
                QScrollBar::handle:vertical:pressed {
                    background-color: #1565c0;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                QScrollBar:horizontal {
                    background-color: #f5f5f5;
                    height: 14px;
                    border: 1px solid #ccc;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #1976d2;
                    border-radius: 6px;
                    min-width: 30px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #2196f3;
                }
                QScrollBar::handle:horizontal:pressed {
                    background-color: #1565c0;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
            """)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("IC Authentication System")
    
    gui = ICAuthenticatorGUI()
    gui.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
