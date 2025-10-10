"""
IC Authentication System - Professional Classic GUI
Production-ready interface with comprehensive details display
"""

import sys
import webbrowser
import os
import cv2
import torch
import ctypes
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTextEdit, QTextBrowser, QTabWidget, QGroupBox, QScrollArea, 
                             QMessageBox, QProgressBar, QGridLayout, QSplitter,
                             QCheckBox, QDialog, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPalette, QTextCursor, QIcon

# Try to import ultimate authenticator, fallback to fresh YOLO
try:
    from smart_ic_authenticator import SmartICAuthenticator as Authenticator
    USING_ULTIMATE = True
except ImportError:
    from fresh_yolo_authenticator import FreshYOLOAuthenticator as Authenticator
    USING_ULTIMATE = False

from datetime import datetime


class ProcessingThread(QThread):
    """Background thread for image processing"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    result = pyqtSignal(dict)
    
    def __init__(self, image_path, authenticator):
        super().__init__()
        self.image_path = image_path
        self.authenticator = authenticator
    
    def run(self):
        """Run the authentication process"""
        try:
            self.status.emit("🚀 Starting analysis...")
            self.progress.emit(10)
            
            self.status.emit("📝 Extracting text...")
            self.progress.emit(40)
            
            self.status.emit("🔍 Detecting part numbers...")
            self.progress.emit(60)
            
            self.status.emit("� Validating datasheets...")
            self.progress.emit(80)
            
            self.status.emit("✅ Finalizing...")
            self.progress.emit(95)
            
            # Run authentication using provided authenticator instance
            result = self.authenticator.authenticate(self.image_path)
            
            self.progress.emit(100)
            self.status.emit("✅ Analysis complete!")
            
            # Emit result
            self.result.emit(result)
            
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.status.emit(f"❌ {str(e)}")
            self.result.emit({'success': False, 'error': error_msg})


class BatchProcessingThread(QThread):
    """Background thread for batch processing multiple images"""
    progress = pyqtSignal(int, int, str)  # current, total, filename
    status = pyqtSignal(str)
    batch_result = pyqtSignal(dict)  # Single image result
    complete = pyqtSignal(dict)  # Final summary
    
    def __init__(self, image_paths, authenticator):
        super().__init__()
        self.image_paths = image_paths
        self.authenticator = authenticator
        self.results = []
    
    def run(self):
        """Process multiple images"""
        try:
            self.status.emit(f"🚀 Starting batch processing of {len(self.image_paths)} images...")
            
            # Use provided authenticator instance (models already loaded)
            total = len(self.image_paths)
            
            # Create debug_output folder
            os.makedirs('debug_output', exist_ok=True)
            
            authentic_count = 0
            likely_authentic_count = 0
            suspicious_count = 0
            counterfeit_count = 0
            error_count = 0
            
            for idx, image_path in enumerate(self.image_paths, 1):
                filename = os.path.basename(image_path)
                self.status.emit(f"📝 Processing {idx}/{total}: {filename}")
                self.progress.emit(idx, total, filename)
                
                try:
                    result = self.authenticator.authenticate(image_path)
                    result['filename'] = filename
                    result['filepath'] = image_path
                    result['success'] = True
                    
                    # Generate debug image
                    try:
                        debug_path = self.authenticator.save_debug_image(result)
                        result['debug_image_path'] = debug_path
                    except Exception as e:
                        result['debug_image_path'] = None
                    
                    self.results.append(result)
                    
                    # Emit individual result
                    self.batch_result.emit(result)
                    
                    # Count results based on verdict
                    verdict = result.get('verdict', 'ERROR')
                    if verdict == 'AUTHENTIC':
                        authentic_count += 1
                    elif verdict == 'LIKELY AUTHENTIC':
                        likely_authentic_count += 1
                    elif verdict == 'SUSPICIOUS':
                        suspicious_count += 1
                    elif verdict in ['COUNTERFEIT', 'LIKELY COUNTERFEIT']:
                        counterfeit_count += 1
                    else:
                        error_count += 1
                    
                except Exception as e:
                    error_count += 1
                    error_result = {
                        'filename': filename,
                        'filepath': image_path,
                        'success': False,
                        'error': str(e),
                        'verdict': 'ERROR',
                        'is_authentic': False,
                        'confidence': 0
                    }
                    self.results.append(error_result)
                    self.batch_result.emit(error_result)
            
            # Emit final summary
            summary = {
                'total': total,
                'authentic': authentic_count,
                'likely_authentic': likely_authentic_count,
                'suspicious': suspicious_count,
                'counterfeit': counterfeit_count,
                'errors': error_count,
                'results': self.results
            }
            
            self.status.emit(f"✅ Batch processing complete! {authentic_count} authentic, {likely_authentic_count} likely authentic, {suspicious_count} suspicious, {counterfeit_count} counterfeit, {error_count} errors")
            self.complete.emit(summary)
            
        except Exception as e:
            import traceback
            error_msg = f"Batch processing error: {str(e)}\n{traceback.format_exc()}"
            self.status.emit(f"❌ {str(e)}")
            self.complete.emit({'success': False, 'error': error_msg})


class ClickableImageLabel(QLabel):
    """QLabel that can be clicked to show full-size image with zoom"""
    clicked = pyqtSignal(QPixmap, str)
    
    def __init__(self, pixmap=None, title=""):
        super().__init__()
        self.full_pixmap = pixmap
        self.image_title = title
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Click to view full size and zoom")
    
    def set_image(self, pixmap, title=""):
        """Set the image and title"""
        self.full_pixmap = pixmap
        self.image_title = title
    
    def mousePressEvent(self, event):
        """Handle click event"""
        if self.full_pixmap and not self.full_pixmap.isNull():
            self.clicked.emit(self.full_pixmap, self.image_title)


class ImageViewerDialog(QMessageBox):
    """Dialog for viewing and zooming images"""
    def __init__(self, pixmap, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(f"{title}\n\nUse mouse wheel to zoom. Click and drag to pan.")
        self.setIcon(QMessageBox.NoIcon)
        
        # Create scroll area for zooming
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setMinimumSize(1000, 800)
        
        # Image label
        self.img_label = QLabel()
        self.img_label.setPixmap(pixmap)
        self.img_label.setAlignment(Qt.AlignCenter)
        scroll.setWidget(self.img_label)
        
        # Add scroll area to dialog
        self.layout().addWidget(scroll, 1, 0, 1, self.layout().columnCount())
        
        # Zoom controls
        self.zoom_factor = 1.0
        self.original_pixmap = pixmap
        
        # Install event filter for mouse wheel
        scroll.viewport().installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle mouse wheel for zooming"""
        if event.type() == event.Wheel:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_factor *= 1.1
            else:
                self.zoom_factor /= 1.1
            
            # Limit zoom
            self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))
            
            # Scale image
            scaled = self.original_pixmap.scaled(
                self.original_pixmap.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.img_label.setPixmap(scaled)
            self.img_label.resize(scaled.size())
            
            return True
        
        return super().eventFilter(obj, event)


class ICAuthenticatorGUI(QMainWindow):
    """Main GUI Application for IC Authentication System"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.current_results = None
        self.dark_mode = True
        self.processing_thread = None
        self.batch_results = []  # Store batch processing results
        self.app_icon = None  # Store icon reference globally
        
        # Initialize authenticator once and reuse it (prevents reloading YOLO/EasyOCR models)
        self.statusBar().showMessage("🚀 Loading models... Please wait...")
        QApplication.processEvents()  # Update UI immediately
        self.authenticator = Authenticator()
        
        self.init_ui()
        self.apply_theme()
    
    def showEvent(self, event):
        """Override showEvent to force icon refresh when window becomes visible"""
        super().showEvent(event)
        # Force icon update after window is shown (Windows taskbar fix)
        if self.app_icon and not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)
            QApplication.instance().setWindowIcon(self.app_icon)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("IC Authentication System - Professional Edition")
        self.setGeometry(50, 50, 1800, 1000)
        self.setMinimumSize(1400, 800)
        
        # Set window icon with absolute path - store reference to prevent garbage collection
        try:
            # Try ICO file first (preferred for Windows)
            icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icon.ico'))
            if os.path.exists(icon_path):
                self.app_icon = QIcon(icon_path)
                if not self.app_icon.isNull():
                    self.setWindowIcon(self.app_icon)
                    print(f"✓ Window icon set from: {icon_path}")
                else:
                    # Try PNG as fallback
                    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icon.png'))
                    if os.path.exists(icon_path):
                        self.app_icon = QIcon(icon_path)
                        self.setWindowIcon(self.app_icon)
                        print(f"✓ Window icon set from PNG: {icon_path}")
        except Exception as e:
            print(f"Could not set window icon: {e}")
        
        # Enable dark title bar on Windows 10/11
        if sys.platform == 'win32':
            try:
                hwnd = int(self.winId())
                # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                value = ctypes.c_int(2)  # 2 = force dark mode
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
                )
            except Exception as e:
                print(f"Could not set dark title bar: {e}")
        
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
        
        # Buttons container
        buttons_layout = QHBoxLayout()
        
        # Authenticate button
        self.auth_btn = QPushButton("🔍 Authenticate IC")
        self.auth_btn.setFixedHeight(50)
        self.auth_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.auth_btn.setEnabled(False)
        self.auth_btn.clicked.connect(self.authenticate)
        buttons_layout.addWidget(self.auth_btn, 2)
        
        # Batch process button
        self.batch_btn = QPushButton("📁 Batch Process")
        self.batch_btn.setFixedHeight(50)
        self.batch_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.batch_btn.clicked.connect(self.batch_process)
        self.batch_btn.setToolTip("Process multiple images at once")
        buttons_layout.addWidget(self.batch_btn, 1)
        
        layout.addLayout(buttons_layout)
        
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
        info_grid.setSpacing(8)
        info_grid.setColumnStretch(1, 2)  # GPU column gets more space
        info_grid.setColumnStretch(3, 1)  # Other columns get less space
        
        # GPU status
        gpu_label = QLabel("GPU:")
        gpu_label.setStyleSheet("font-weight: bold; font-size: 9pt;")
        self.gpu_status = QLabel("Detecting...")
        self.gpu_status.setStyleSheet("font-size: 9pt;")
        self.gpu_status.setWordWrap(True)
        self.gpu_status.setMinimumWidth(200)
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
                self.gpu_status.setText(f"✅ {gpu_name}")
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
        
        # Image Display Section (NEW)
        image_group = QGroupBox("IC Image Preview (Click to Zoom)")
        image_layout = QVBoxLayout()
        
        self.result_image_label = ClickableImageLabel()
        self.result_image_label.setAlignment(Qt.AlignCenter)
        self.result_image_label.setMinimumHeight(200)
        self.result_image_label.setMaximumHeight(300)
        self.result_image_label.setStyleSheet("border: 1px solid #444; background-color: #1a1a1a;")
        self.result_image_label.setScaledContents(False)
        self.result_image_label.clicked.connect(self.show_zoomed_image)
        
        image_layout.addWidget(self.result_image_label)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
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
        
        self.datasheet_text = QTextBrowser()  # Changed from QTextEdit
        self.datasheet_text.setReadOnly(True)
        self.datasheet_text.setOpenExternalLinks(True)  # Make URLs clickable
        datasheet_layout.addWidget(self.datasheet_text)
        
        datasheet_group.setLayout(datasheet_layout)
        splitter.addWidget(datasheet_group)
        
        # OCR Details (larger - contains detailed extraction info)
        ocr_group = QGroupBox("OCR Extraction Details")
        ocr_layout = QVBoxLayout()
        
        self.ocr_text = QTextBrowser()  # Changed from QTextEdit
        self.ocr_text.setReadOnly(True)
        self.ocr_text.setOpenExternalLinks(True)  # Make URLs clickable
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
        """Create debug images tab with organized sections and export"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Export buttons at top
        export_layout = QHBoxLayout()
        
        self.export_debug_btn = QPushButton("💾 Export Debug Images")
        self.export_debug_btn.clicked.connect(self.export_debug_images)
        self.export_debug_btn.setEnabled(False)
        self.export_debug_btn.setToolTip("Export all debug images to a folder")
        export_layout.addWidget(self.export_debug_btn)
        
        self.export_raw_btn = QPushButton("💾 Export Raw Data")
        self.export_raw_btn.clicked.connect(self.export_raw_data)
        self.export_raw_btn.setEnabled(False)
        self.export_raw_btn.setToolTip("Export raw authentication data as JSON")
        export_layout.addWidget(self.export_raw_btn)
        
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
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
        
        # Section 1: OCR with text bounding boxes (FIRST)
        ocr_group = QGroupBox("📝 Text Detection (OCR with Bounding Boxes)")
        self.ocr_layout = QVBoxLayout()
        ocr_group.setLayout(self.ocr_layout)
        ocr_group.setVisible(False)
        container_layout.addWidget(ocr_group)
        self.ocr_group = ocr_group
        
        # Section 2: Preprocessing variants (SECOND)
        preprocessing_group = QGroupBox("🔧 Image Preprocessing Variants")
        self.preprocessing_layout = QVBoxLayout()
        preprocessing_group.setLayout(self.preprocessing_layout)
        preprocessing_group.setVisible(False)
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
        
        # Start processing thread with reusable authenticator instance
        self.processing_thread = ProcessingThread(self.current_image_path, self.authenticator)
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
        
        # Update variants count display
        if 'variants_count' in results:
            count = results['variants_count']
            self.variants_used.setText(str(count) if count > 0 else "None (direct)")
        elif 'debug_variants' in results and results['debug_variants']:
            # Count from debug_variants
            self.variants_used.setText(str(len(results['debug_variants'])))
        elif 'ocr_details' in results:
            # Count unique variants from OCR details
            variants = set(d.get('variant', '') for d in results['ocr_details'])
            variants.discard('')  # Remove empty strings
            count = len(variants)
            self.variants_used.setText(str(count) if count > 0 else "None (direct)")
        else:
            self.variants_used.setText("None (direct)")
        
        # Update Summary Tab
        is_authentic = results.get('is_authentic', False)
        confidence = results.get('confidence', 0)
        verdict = results.get('verdict', 'UNKNOWN')
        
        # Load and display image with debug annotations
        if self.current_image_path and os.path.exists(self.current_image_path):
            # Generate debug image using the existing authenticator instance
            try:
                debug_path = self.authenticator.save_debug_image(results)
                
                # Load debug image
                if debug_path and os.path.exists(debug_path):
                    pixmap = QPixmap(debug_path)
                else:
                    pixmap = QPixmap(self.current_image_path)
                    
                if not pixmap.isNull():
                    # Scale to fit the preview area
                    scaled_pixmap = pixmap.scaled(600, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.result_image_label.setPixmap(scaled_pixmap)
                    self.result_image_label.full_pixmap = pixmap  # Store full size for zoom
            except Exception as e:
                print(f"Error loading image: {e}")
        
        # Map verdict to display text and color
        if verdict == 'AUTHENTIC':
            verdict_text = f"✅ AUTHENTIC\nConfidence: {confidence}%"
            verdict_color = "#2d5016"
        elif verdict == 'LIKELY AUTHENTIC':
            verdict_text = f"✅ LIKELY AUTHENTIC\nConfidence: {confidence}%"
            verdict_color = "#3d6020"
        elif verdict == 'SUSPICIOUS':
            verdict_text = f"⚠️ SUSPICIOUS\nConfidence: {confidence}%"
            verdict_color = "#6b5416"
        elif verdict == 'LIKELY COUNTERFEIT':
            verdict_text = f"❌ LIKELY COUNTERFEIT\nConfidence: {confidence}%"
            verdict_color = "#5c1010"
        elif verdict == 'COUNTERFEIT':
            verdict_text = f"❌ COUNTERFEIT\nConfidence: {confidence}%"
            verdict_color = "#4c0000"
        else:
            verdict_text = f"❓ {verdict}\nConfidence: {confidence}%"
            verdict_color = "#444444"
            
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
    
    def batch_process(self):
        """Start batch processing of multiple images"""
        # Open file dialog for multiple images
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.tiff)")
        
        if file_dialog.exec_():
            image_paths = file_dialog.selectedFiles()
            
            if not image_paths:
                return
            
            # Confirm batch processing
            reply = QMessageBox.question(
                self,
                'Batch Processing',
                f'Process {len(image_paths)} images?\n\nThis may take several minutes.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
            
            # Clear previous batch results
            self.batch_results = []
            
            # Disable buttons during processing
            self.auth_btn.setEnabled(False)
            self.select_btn.setEnabled(False)
            self.batch_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(image_paths))
            
            # Start batch processing thread with reusable authenticator instance
            self.batch_thread = BatchProcessingThread(image_paths, self.authenticator)
            self.batch_thread.progress.connect(self.update_batch_progress)
            self.batch_thread.status.connect(self.update_status)
            self.batch_thread.batch_result.connect(self.handle_batch_result)
            self.batch_thread.complete.connect(self.batch_complete)
            self.batch_thread.start()
    
    def update_batch_progress(self, current, total, filename):
        """Update progress bar for batch processing"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Processing {current}/{total}: {filename}")
    
    def handle_batch_result(self, result):
        """Handle individual result from batch processing - OPTIMIZED for memory"""
        # MEMORY FIX: Save debug images to disk immediately and replace with file paths
        # This prevents storing large numpy arrays in memory
        
        image_path = result.get('image_path', '')
        image_name = Path(image_path).stem if image_path else f"image_{len(self.batch_results)}"
        
        # Save debug OCR image to disk if present
        if result.get('debug_ocr_image') is not None:
            ocr_image_path = f"debug_output/debug_{image_name}_ocr.png"
            Path("debug_output").mkdir(exist_ok=True)
            cv2.imwrite(ocr_image_path, result['debug_ocr_image'])
            result['debug_ocr_image_path'] = ocr_image_path  # Store file path instead
            del result['debug_ocr_image']  # Remove numpy array from memory
        
        # Save debug variant images to disk if present
        if result.get('debug_variants'):
            variant_paths = []
            for idx, (name, img) in enumerate(result['debug_variants']):
                variant_path = f"debug_output/debug_{image_name}_variant_{idx}_{name.replace(' ', '_')}.png"
                cv2.imwrite(variant_path, img)
                variant_paths.append((name, variant_path))
            result['debug_variant_paths'] = variant_paths  # Store file paths
            del result['debug_variants']  # Remove numpy arrays from memory
        
        # Save preprocessing images to disk if present
        if result.get('preprocessing_images'):
            for preproc in result['preprocessing_images']:
                if 'image' in preproc:
                    del preproc['image']  # Remove numpy arrays
            del result['preprocessing_images']  # Clean up
        
        # Store result with file paths only (minimal memory usage)
        self.batch_results.append(result)
        
        # Force garbage collection to free memory immediately
        import gc
        gc.collect()
    
    def batch_complete(self, summary):
        """Handle completion of batch processing"""
        self.auth_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.batch_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if not summary.get('success', True):
            QMessageBox.critical(self, "Error", summary.get('error', 'Batch processing failed'))
            return
        
        # Store batch results for individual viewing
        self.batch_results = summary.get('results', [])
        
        # Display summary
        total = summary['total']
        authentic = summary.get('authentic', 0)
        likely_authentic = summary.get('likely_authentic', 0)
        suspicious = summary.get('suspicious', 0)
        counterfeit = summary.get('counterfeit', 0)
        errors = summary.get('errors', 0)
        
        # Create dialog with table widget
        dialog = QDialog(self)
        dialog.setWindowTitle("Batch Processing Complete")
        dialog.setMinimumSize(1400, 900)  # Much larger window
        
        layout = QVBoxLayout(dialog)
        
        # Summary label
        summary_label = QLabel(f"✅ Successfully processed {total} images!\n"
                              f"✅ {authentic} Authentic  |  ⚠️ {counterfeit} Counterfeit  |  ⚠️ {errors} Errors\n"
                              f"Click 'View' button to see detailed results and debug images")
        summary_label.setStyleSheet("font-size: 12pt; font-weight: bold; padding: 10px;")
        layout.addWidget(summary_label)
        
        # Create table widget
        table = QTableWidget()
        table.setRowCount(len(self.batch_results))
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(['', 'Filename', 'Verdict', 'Confidence', 'Part Number', 'Datasheet', 'Action'])
        
        # Set column widths - make them wider to prevent cutoff
        table.setColumnWidth(0, 40)   # Icon
        table.setColumnWidth(1, 300)  # Filename (increased)
        table.setColumnWidth(2, 150)  # Verdict (increased)
        table.setColumnWidth(3, 90)   # Confidence
        table.setColumnWidth(4, 180)  # Part Number (increased)
        table.setColumnWidth(5, 120)  # Datasheet (increased)
        table.setColumnWidth(6, 100)  # Action
        
        # Make table resize to fit contents
        table.horizontalHeader().setStretchLastSection(True)
        table.setWordWrap(False)
        table.resizeRowsToContents()
        
        # Configure table
        table.horizontalHeader().setStretchLastSection(False)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(False)  # Disable alternating colors for uniform appearance
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set uniform dark background for all rows
        table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                gridline-color: #444;
                color: white;
            }
            QTableWidget::item {
                background-color: #2a2a2a;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3a3a3a;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: white;
                padding: 5px;
                border: 1px solid #444;
                font-weight: bold;
            }
        """)
        
        # Populate table
        for idx, result in enumerate(self.batch_results):
            filename = result.get('filename', 'Unknown')
            verdict = result.get('verdict', 'ERROR')
            confidence = result.get('confidence', 0)
            part_number = result.get('normalized_part_number') or result.get('part_number') or 'N/A'
            
            # Icon cell with proper color coding
            if verdict == 'AUTHENTIC':
                icon_text = '✅'
                verdict_color = QColor(76, 175, 80)  # Green
            elif verdict == 'LIKELY AUTHENTIC':
                icon_text = '✅'
                verdict_color = QColor(156, 204, 101)  # Light Green
            elif verdict == 'SUSPICIOUS':
                icon_text = '⚠️'
                verdict_color = QColor(255, 167, 38)  # Orange
            elif verdict in ['COUNTERFEIT', 'LIKELY COUNTERFEIT']:
                icon_text = '❌'
                verdict_color = QColor(244, 67, 54)  # Red
            else:
                icon_text = '⚠️'
                verdict_color = QColor(255, 167, 38)  # Orange
            
            icon_item = QTableWidgetItem(icon_text)
            icon_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(idx, 0, icon_item)
            
            # Filename
            filename_item = QTableWidgetItem(filename)
            table.setItem(idx, 1, filename_item)
            
            # Verdict
            verdict_item = QTableWidgetItem(verdict)
            verdict_item.setForeground(verdict_color)
            verdict_item.setFont(QFont('Arial', 10, QFont.Bold))
            table.setItem(idx, 2, verdict_item)
            
            # Confidence
            confidence_item = QTableWidgetItem(f"{confidence}%")
            table.setItem(idx, 3, confidence_item)
            
            # Part Number
            part_item = QTableWidgetItem(part_number)
            table.setItem(idx, 4, part_item)
            
            # Datasheet status - make it a clickable button if found
            datasheet_found = result.get('datasheet_found', False)
            
            if datasheet_found and result.get('datasheet_url'):
                # Create clickable button for found datasheets
                datasheet_btn = QPushButton("✅ Found")
                datasheet_url = result['datasheet_url']
                datasheet_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #4CAF50;
                        border: none;
                        padding: 5px;
                        font-weight: bold;
                        text-decoration: underline;
                    }
                    QPushButton:hover {
                        color: #66BB6A;
                        background-color: #3a3a3a;
                    }
                """)
                datasheet_btn.setCursor(Qt.PointingHandCursor)
                datasheet_btn.clicked.connect(lambda checked, url=datasheet_url: webbrowser.open(url))
                datasheet_btn.setToolTip(f"Click to open datasheet:\n{datasheet_url}")
                table.setCellWidget(idx, 5, datasheet_btn)
            else:
                # Regular text item for not found
                datasheet_item = QTableWidgetItem("❌ Not Found")
                datasheet_item.setForeground(QColor(244, 67, 54))
                datasheet_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(idx, 5, datasheet_item)
            
            # View button - always shows result details dialog
            view_btn = QPushButton("🔍 View")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4A9EFF;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #357ABD;
                }
            """)
            view_btn.clicked.connect(lambda checked, i=idx: self.view_batch_result_by_index(i))
            view_btn.setToolTip("View detailed results")
            table.setCellWidget(idx, 6, view_btn)
        
        layout.addWidget(table)
        
        # Button row
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Report")
        save_btn.clicked.connect(lambda: self.save_batch_report_table())
        button_layout.addWidget(save_btn)
        
        export_btn = QPushButton("📦 Export All Debug Data")
        export_btn.clicked.connect(self.export_all_batch_debug_data)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def save_batch_report_table(self):
        """Save batch processing report to HTML file"""
        if not self.batch_results:
            return
        
        # Generate HTML report
        total = len(self.batch_results)
        authentic = sum(1 for r in self.batch_results if r.get('verdict') == 'AUTHENTIC')
        counterfeit = sum(1 for r in self.batch_results if r.get('verdict') == 'COUNTERFEIT')
        errors = sum(1 for r in self.batch_results if r.get('verdict') == 'ERROR')
        
        report = f"""
<html>
<head>
<style>
    body {{ font-family: Arial; font-size: 11pt; }}
    h2 {{ color: #4A9EFF; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    th {{ background: #2a2a2a; padding: 8px; text-align: left; border: 1px solid #444; color: white; }}
    td {{ padding: 6px; border: 1px solid #444; }}
    .authentic {{ color: #4CAF50; font-weight: bold; }}
    .counterfeit {{ color: #F44336; font-weight: bold; }}
    .error {{ color: #FFA726; font-weight: bold; }}
</style>
</head>
<body>
<h2>📊 Batch Processing Results</h2>
<p><b>Total Images:</b> {total}</p>
<p><b>✅ Authentic:</b> {authentic} ({authentic/total*100:.1f}%)</p>
<p><b>❌ Counterfeit:</b> {counterfeit} ({counterfeit/total*100:.1f}%)</p>
<p><b>⚠️ Errors:</b> {errors} ({errors/total*100:.1f}%)</p>

<h3>Individual Results:</h3>
<table>
<tr>
    <th></th>
    <th>Filename</th>
    <th>Verdict</th>
    <th>Confidence</th>
    <th>Part Number</th>
</tr>
"""
        
        for result in self.batch_results:
            filename = result.get('filename', 'Unknown')
            verdict = result.get('verdict', 'ERROR')
            confidence = result.get('confidence', 0)
            part_number = result.get('normalized_part_number') or result.get('part_number') or 'N/A'
            
            if verdict == 'AUTHENTIC':
                verdict_class = 'authentic'
                verdict_symbol = '✅'
            elif verdict == 'COUNTERFEIT':
                verdict_class = 'counterfeit'
                verdict_symbol = '❌'
            else:
                verdict_class = 'error'
                verdict_symbol = '⚠️'
            
            report += f"""
<tr>
    <td style="text-align: center;">{verdict_symbol}</td>
    <td>{filename}</td>
    <td class="{verdict_class}">{verdict}</td>
    <td>{confidence}%</td>
    <td>{part_number}</td>
</tr>
"""
        
        report += """
</table>
</body>
</html>
"""
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Batch Report",
            f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML Files (*.html)"
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                QMessageBox.information(self, "Success", f"Report saved to:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report:\n{str(e)}")
    
    def export_all_batch_debug_data(self):
        """Export all batch processing debug data to organized folders"""
        if not self.batch_results:
            QMessageBox.warning(self, "No Data", "No batch results available to export.")
            return
        
        # Choose export directory
        export_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly
        )
        
        if not export_dir:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_dir = os.path.join(export_dir, f"batch_export_{timestamp}")
            os.makedirs(base_dir, exist_ok=True)
            
            # Create main folders: debug_images and raw_data
            debug_images_dir = os.path.join(base_dir, "debug_images")
            raw_data_dir = os.path.join(base_dir, "raw_data")
            
            os.makedirs(debug_images_dir, exist_ok=True)
            os.makedirs(raw_data_dir, exist_ok=True)
            
            # Create subdirectories under debug_images
            ocr_dir = os.path.join(debug_images_dir, "ocr_detection")
            preprocessing_dir = os.path.join(debug_images_dir, "preprocessing_variants")
            
            os.makedirs(ocr_dir, exist_ok=True)
            os.makedirs(preprocessing_dir, exist_ok=True)
            
            # Create subdirectories under raw_data
            raw_text_dir = os.path.join(raw_data_dir, "text_files")
            json_dir = os.path.join(raw_data_dir, "json_files")
            
            os.makedirs(raw_text_dir, exist_ok=True)
            os.makedirs(json_dir, exist_ok=True)
            
            exported_count = 0
            
            for idx, result in enumerate(self.batch_results):
                filename = result.get('filename', f'image_{idx}')
                base_name = os.path.splitext(filename)[0]
                
                # Export OCR bounding box image
                if result.get('debug_ocr_image') is not None:
                    ocr_path = os.path.join(ocr_dir, f"{base_name}_ocr_detection.png")
                    cv2.imwrite(ocr_path, result['debug_ocr_image'])
                
                # Export preprocessing variants
                if result.get('debug_variants'):
                    variant_subdir = os.path.join(preprocessing_dir, base_name)
                    os.makedirs(variant_subdir, exist_ok=True)
                    
                    # Handle both dict and list formats for debug_variants
                    debug_variants = result['debug_variants']
                    if isinstance(debug_variants, dict):
                        # Dict format: {variant_name: variant_img}
                        for variant_name, variant_img in debug_variants.items():
                            variant_path = os.path.join(variant_subdir, f"{variant_name}.png")
                            cv2.imwrite(variant_path, variant_img)
                    elif isinstance(debug_variants, list):
                        # List format: [(variant_name, variant_img), ...]
                        for item in debug_variants:
                            if isinstance(item, tuple) and len(item) == 2:
                                variant_name, variant_img = item
                                variant_path = os.path.join(variant_subdir, f"{variant_name}.png")
                                cv2.imwrite(variant_path, variant_img)
                
                # Export raw text
                raw_text_path = os.path.join(raw_text_dir, f"{base_name}_text.txt")
                with open(raw_text_path, 'w', encoding='utf-8') as f:
                    f.write(f"Filename: {filename}\n")
                    f.write(f"Verdict: {result.get('verdict', 'N/A')}\n")
                    f.write(f"Confidence: {result.get('confidence', 0)}%\n")
                    f.write(f"Part Number: {result.get('normalized_part_number', 'N/A')}\n")
                    f.write(f"Manufacturer: {result.get('manufacturer', 'N/A')}\n")
                    f.write(f"Date Codes: {', '.join(result.get('date_codes', []))}\n")
                    f.write(f"\n{'='*50}\n")
                    f.write(f"OCR Confidence: {result.get('ocr_confidence', 0)}%\n")
                    f.write(f"\nFull OCR Text:\n{'-'*50}\n")
                    f.write(result.get('full_text', 'N/A'))
                    f.write(f"\n\n{'='*50}\n")
                    f.write(f"Authentication Reasons:\n{'-'*50}\n")
                    for reason in result.get('reasons', []):
                        f.write(f"  {reason}\n")
                    
                    # Add validation issues if any
                    issues = result.get('validation_issues', [])
                    if issues:
                        f.write(f"\n{'='*50}\n")
                        f.write(f"Validation Issues:\n{'-'*50}\n")
                        for issue in issues:
                            f.write(f"  [{issue.get('severity', 'INFO')}] {issue.get('message', '')}\n")
                
                # Export raw JSON
                json_path = os.path.join(json_dir, f"{base_name}_data.json")
                import json
                import numpy as np
                
                class NumpyEncoder(json.JSONEncoder):
                    def default(self, obj):
                        if isinstance(obj, (np.integer, np.int32, np.int64)):
                            return int(obj)
                        elif isinstance(obj, (np.floating, np.float32, np.float64)):
                            return float(obj)
                        elif isinstance(obj, np.ndarray):
                            return obj.tolist()
                        return super().default(obj)
                
                # Filter out non-serializable items
                filtered_result = {
                    k: v for k, v in result.items()
                    if k not in ['debug_variants', 'debug_ocr_image', 'preprocessed_image', 
                                'original_image', 'marking_validation', 'datasheet_details']
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(filtered_result, f, indent=2, cls=NumpyEncoder)
                
                exported_count += 1
            
            # Create summary file
            summary_path = os.path.join(base_dir, "EXPORT_SUMMARY.txt")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"Batch Processing Export Summary\n")
                f.write(f"{'='*60}\n\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Results Exported: {exported_count}\n\n")
                f.write(f"Export Structure:\n")
                f.write(f"  📁 {os.path.basename(base_dir)}/\n")
                f.write(f"     ├─ 📁 debug_images/\n")
                f.write(f"     │  ├─ 📁 ocr_detection/       (OCR bounding box images)\n")
                f.write(f"     │  └─ 📁 preprocessing_variants/ (All preprocessing stages)\n")
                f.write(f"     ├─ 📁 raw_data/\n")
                f.write(f"     │  ├─ 📁 text_files/          (Complete text details)\n")
                f.write(f"     │  └─ 📁 json_files/          (Machine-readable JSON)\n")
                f.write(f"     └─ 📄 EXPORT_SUMMARY.txt      (This file)\n\n")
                
                # Add result summary
                authentic_count = sum(1 for r in self.batch_results if r.get('verdict') == 'AUTHENTIC')
                counterfeit_count = sum(1 for r in self.batch_results if r.get('verdict') == 'COUNTERFEIT')
                error_count = sum(1 for r in self.batch_results if r.get('verdict') == 'ERROR')
                
                f.write(f"Results Summary:\n")
                f.write(f"  ✅ Authentic: {authentic_count}\n")
                f.write(f"  ❌ Counterfeit: {counterfeit_count}\n")
                f.write(f"  ⚠️  Errors: {error_count}\n\n")
                
                f.write(f"Individual Results:\n")
                f.write(f"{'-'*60}\n")
                for result in self.batch_results:
                    verdict = result.get('verdict', 'N/A')
                    confidence = result.get('confidence', 0)
                    filename = result.get('filename', 'Unknown')
                    part_number = result.get('normalized_part_number', 'N/A')
                    f.write(f"  {filename}\n")
                    f.write(f"    Verdict: {verdict} ({confidence}%)\n")
                    f.write(f"    Part Number: {part_number}\n\n")
            
            # Show success message
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Export Complete")
            msg.setText(f"Successfully exported {exported_count} results!")
            msg.setInformativeText(f"Export location:\n{base_dir}")
            msg.setDetailedText(
                f"Exported Data:\n\n"
                f"📁 debug_images/\n"
                f"  • OCR Detection: {ocr_dir}\n"
                f"  • Preprocessing Variants: {preprocessing_dir}\n\n"
                f"📁 raw_data/\n"
                f"  • Text Files: {raw_text_dir}\n"
                f"  • JSON Files: {json_dir}\n\n"
                f"📄 Summary: {summary_path}"
            )
            
            # Add button to open folder
            open_btn = msg.addButton("📁 Open Folder", QMessageBox.ActionRole)
            msg.addButton(QMessageBox.Ok)
            
            msg.exec_()
            
            if msg.clickedButton() == open_btn:
                # Use os.startfile for reliable Windows folder opening
                try:
                    os.startfile(base_dir)
                except:
                    # Fallback to explorer command
                    import subprocess
                    subprocess.Popen(['explorer', base_dir])
        
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export batch data:\n{str(e)}\n\n{traceback.format_exc()}"
            )
    
    def view_batch_result(self, url_str):
        """View individual result from batch processing"""
        if not url_str.startswith('view_result:'):
            return
        
        try:
            idx = int(url_str.split(':')[1])
            if 0 <= idx < len(self.batch_results):
                result = self.batch_results[idx]
                
                # Create detailed view dialog
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Batch Result: {result.get('filename', 'Unknown')}")
                dialog.setMinimumSize(1600, 900)
                
                layout = QVBoxLayout(dialog)
                
                # Header with verdict
                verdict = result.get('verdict', 'ERROR')
                confidence = result.get('confidence', 0)
                
                if verdict == 'AUTHENTIC':
                    header_text = f"✅ AUTHENTIC - Confidence: {confidence}%"
                    header_color = "#4CAF50"
                elif verdict == 'COUNTERFEIT':
                    header_text = f"❌ COUNTERFEIT - Confidence: {confidence}%"
                    header_color = "#F44336"
                else:
                    header_text = f"⚠️ ERROR - Confidence: {confidence}%"
                    header_color = "#FFA726"
                
                header_label = QLabel(header_text)
                header_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {header_color}; padding: 10px;")
                layout.addWidget(header_label)
                
                # Create tabs for detailed view
                tabs = QTabWidget()
                
                # Summary tab
                summary_text = self.create_summary_html(result)
                summary_browser = QTextBrowser()
                summary_browser.setHtml(summary_text)
                summary_browser.setOpenExternalLinks(True)
                tabs.addTab(summary_browser, "📋 Summary")
                
                # Details tab
                details_text = self.create_details_html(result)
                details_browser = QTextBrowser()
                details_browser.setHtml(details_text)
                details_browser.setOpenExternalLinks(True)
                tabs.addTab(details_browser, "📊 Details")
                
                # Debug Images tab
                if result.get('debug_variants') or result.get('debug_ocr_image'):
                    debug_widget = self.create_debug_images_widget(result)
                    tabs.addTab(debug_widget, "🔍 Debug Images")
                
                # Raw Data tab
                raw_text = self.create_raw_data_text(result)
                raw_browser = QTextBrowser()
                raw_browser.setPlainText(raw_text)
                tabs.addTab(raw_browser, "📄 Raw Data")
                
                layout.addWidget(tabs)
                
                # Close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.exec_()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view result:\n{str(e)}")
    
    def view_raw_data_by_index(self, idx):
        """View raw data for individual result from batch processing"""
        try:
            if 0 <= idx < len(self.batch_results):
                result = self.batch_results[idx]
                
                # Create raw data dialog
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Raw Data: {result.get('filename', 'Unknown')}")
                dialog.setMinimumSize(800, 600)
                
                layout = QVBoxLayout(dialog)
                
                # Raw data browser
                raw_browser = QTextBrowser()
                raw_text = self.create_raw_data_text(result)
                raw_browser.setPlainText(raw_text)
                raw_browser.setFont(QFont("Consolas", 9))
                layout.addWidget(raw_browser)
                
                # Close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.exec_()
                
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", f"Failed to view raw data:\n{str(e)}\n\n{traceback.format_exc()}")
    
    def view_batch_result_by_index(self, idx):
        """View individual result from batch processing by index"""
        try:
            if 0 <= idx < len(self.batch_results):
                result = self.batch_results[idx]
                
                # Create detailed view dialog
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Batch Result: {result.get('filename', 'Unknown')}")
                dialog.setMinimumSize(1600, 900)
                
                layout = QVBoxLayout(dialog)
                
                # Header with verdict
                verdict = result.get('verdict', 'ERROR')
                confidence = result.get('confidence', 0)
                
                if verdict == 'AUTHENTIC':
                    header_text = f"✅ AUTHENTIC - Confidence: {confidence}%"
                    header_color = "#4CAF50"
                elif verdict == 'LIKELY AUTHENTIC':
                    header_text = f"✅ LIKELY AUTHENTIC - Confidence: {confidence}%"
                    header_color = "#9CCC65"
                elif verdict == 'SUSPICIOUS':
                    header_text = f"⚠️ SUSPICIOUS - Confidence: {confidence}%"
                    header_color = "#FFA726"
                elif verdict in ['COUNTERFEIT', 'LIKELY COUNTERFEIT']:
                    header_text = f"❌ {verdict} - Confidence: {confidence}%"
                    header_color = "#F44336"
                else:
                    header_text = f"⚠️ ERROR - Confidence: {confidence}%"
                    header_color = "#FFA726"
                
                header_label = QLabel(header_text)
                header_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {header_color}; padding: 10px;")
                layout.addWidget(header_label)
                
                # Create tabs for detailed view
                tabs = QTabWidget()
                
                # Summary tab
                summary_text = self.create_summary_html(result)
                summary_browser = QTextBrowser()
                summary_browser.setHtml(summary_text)
                summary_browser.setOpenExternalLinks(True)
                tabs.addTab(summary_browser, "📋 Summary")
                
                # Details tab
                details_text = self.create_details_html(result)
                details_browser = QTextBrowser()
                details_browser.setHtml(details_text)
                details_browser.setOpenExternalLinks(True)
                tabs.addTab(details_browser, "📊 Details")
                
                # Debug Images tab
                debug_image_path = result.get('debug_image_path')
                if debug_image_path and os.path.exists(debug_image_path):
                    debug_widget = QWidget()
                    debug_layout = QVBoxLayout(debug_widget)
                    
                    # Add debug image
                    debug_label = QLabel("Debug Image with OCR Bounding Boxes (Click to Zoom):")
                    debug_label.setStyleSheet("font-weight: bold; font-size: 11pt; padding: 5px;")
                    debug_layout.addWidget(debug_label)
                    
                    # Load and display debug image - make it clickable
                    pixmap = QPixmap(debug_image_path)
                    if not pixmap.isNull():
                        # Create clickable image label
                        img_label = ClickableImageLabel()
                        img_label.full_pixmap = pixmap
                        img_label.image_title = f"Debug: {result.get('filename', 'Unknown')}"
                        img_label.clicked.connect(self.show_zoomed_image)
                        
                        # Scale image to fit
                        scaled_pixmap = pixmap.scaled(1400, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img_label.setPixmap(scaled_pixmap)
                        img_label.setAlignment(Qt.AlignCenter)
                        img_label.setCursor(Qt.PointingHandCursor)
                        img_label.setToolTip("Click to view full size and zoom")
                        
                        # Add to scroll area
                        scroll = QScrollArea()
                        scroll.setWidget(img_label)
                        scroll.setWidgetResizable(True)
                        debug_layout.addWidget(scroll)
                    
                    tabs.addTab(debug_widget, "🔍 Debug Images")
                elif result.get('debug_variants') or result.get('debug_ocr_image') is not None:
                    debug_widget = self.create_debug_images_widget(result)
                    tabs.addTab(debug_widget, "🔍 Debug Images")
                
                # Raw Data tab
                raw_text = self.create_raw_data_text(result)
                raw_browser = QTextBrowser()
                raw_browser.setPlainText(raw_text)
                raw_browser.setFont(QFont("Consolas", 9))
                tabs.addTab(raw_browser, "📄 Raw Data")
                
                layout.addWidget(tabs)
                
                # Close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.exec_()
                
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", f"Failed to view result:\n{str(e)}\n\n{traceback.format_exc()}")
    
    def create_summary_html(self, result):
        """Create summary HTML for batch result"""
        verdict = result.get('verdict', 'ERROR')
        confidence = result.get('confidence', 0)
        part_number = result.get('normalized_part_number') or result.get('part_number', 'N/A')
        manufacturer = result.get('manufacturer', 'N/A')
        date_codes = ', '.join(result.get('date_codes', [])) or 'None'
        datasheet_url = result.get('datasheet_url', '')
        
        html = f"""
<html>
<head>
<style>
    body {{ font-family: Arial; font-size: 11pt; padding: 10px; }}
    h3 {{ color: #4A9EFF; }}
    .info-row {{ margin: 8px 0; }}
    .label {{ font-weight: bold; color: #888; }}
    .value {{ color: #fff; }}
</style>
</head>
<body>
<h3>Authentication Summary</h3>
<div class="info-row"><span class="label">Filename:</span> <span class="value">{result.get('filename', 'Unknown')}</span></div>
<div class="info-row"><span class="label">Part Number:</span> <span class="value">{part_number}</span></div>
<div class="info-row"><span class="label">Manufacturer:</span> <span class="value">{manufacturer}</span></div>
<div class="info-row"><span class="label">Date Codes:</span> <span class="value">{date_codes}</span></div>
<div class="info-row"><span class="label">Confidence:</span> <span class="value">{confidence}%</span></div>
<div class="info-row"><span class="label">Datasheet:</span> <span class="value">{'<a href="' + datasheet_url + '">View Datasheet</a>' if datasheet_url else 'Not Found'}</span></div>

<h3>Authentication Details</h3>
"""
        
        # Add reasons
        reasons = result.get('reasons', [])
        if reasons:
            html += "<ul>"
            for reason in reasons:
                html += f"<li>{reason}</li>"
            html += "</ul>"
        
        # Add validation issues
        issues = result.get('validation_issues', [])
        if issues:
            html += "<h3>Validation Issues</h3><ul>"
            for issue in issues:
                severity = issue.get('severity', 'INFO')
                message = issue.get('message', '')
                if severity == 'CRITICAL':
                    color = '#F44336'
                elif severity == 'MAJOR':
                    color = '#FFA726'
                else:
                    color = '#888'
                html += f"<li style='color: {color}'>[{severity}] {message}</li>"
            html += "</ul>"
        
        html += "</body></html>"
        return html
    
    def create_details_html(self, result):
        """Create detailed HTML for batch result"""
        ocr_confidence = result.get('ocr_confidence', 0)
        full_text = result.get('full_text', 'N/A')
        processing_time = result.get('processing_time', 0)
        
        html = f"""
<html>
<head>
<style>
    body {{ font-family: Arial; font-size: 11pt; padding: 10px; }}
    h3 {{ color: #4A9EFF; }}
    .info-row {{ margin: 8px 0; }}
    .label {{ font-weight: bold; color: #888; }}
    .value {{ color: #fff; }}
    pre {{ background: #2a2a2a; padding: 10px; border-radius: 5px; }}
</style>
</head>
<body>
<h3>OCR Results</h3>
<div class="info-row"><span class="label">OCR Confidence:</span> <span class="value">{ocr_confidence}%</span></div>
<div class="info-row"><span class="label">Full Text:</span></div>
<pre>{full_text}</pre>

<h3>Processing Details</h3>
<div class="info-row"><span class="label">Processing Time:</span> <span class="value">{processing_time:.2f}s</span></div>
<div class="info-row"><span class="label">GPU Used:</span> <span class="value">{result.get('gpu_used', False)}</span></div>
<div class="info-row"><span class="label">Timestamp:</span> <span class="value">{result.get('timestamp', 'N/A')}</span></div>
</body>
</html>
"""
        return html
    
    def create_debug_images_widget(self, result):
        """Create widget showing debug images for batch result"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content = QWidget()
        grid = QGridLayout(content)
        grid.setSpacing(10)
        
        row = 0
        col = 0
        
        # Show OCR detection image first - LOAD FROM DISK to save memory
        if result.get('debug_ocr_image_path'):
            label = QLabel("OCR Text Detection")
            label.setStyleSheet("font-weight: bold; color: #4A9EFF; font-size: 12pt;")
            grid.addWidget(label, row, 0, 1, 3)
            row += 1
            
            # Load image from disk (not from memory)
            ocr_img = cv2.imread(result['debug_ocr_image_path'])
            
            if ocr_img is not None:
                # Convert cv2 image to QPixmap
                if len(ocr_img.shape) == 2:  # Grayscale
                    height, width = ocr_img.shape
                    bytes_per_line = width
                    q_img = QImage(ocr_img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
                else:  # Color
                    height, width, channel = ocr_img.shape
                    bytes_per_line = 3 * width
                    q_img = QImage(ocr_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                
                pixmap = QPixmap.fromImage(q_img)
                
                # Scale to reasonable size for display
                scaled_pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                img_label = QLabel()
                img_label.setPixmap(scaled_pixmap)
                img_label.setAlignment(Qt.AlignCenter)
                img_label.setStyleSheet("border: 2px solid #4A9EFF; background-color: #1a1a1a;")
                img_label.setCursor(Qt.PointingHandCursor)
                img_label.setToolTip("Click to zoom")
                
                # Make clickable for zoom
                img_label.mousePressEvent = lambda event, p=pixmap: self.show_zoomed_image(p, "OCR Text Detection")
                
                grid.addWidget(img_label, row, 0, 1, 3)
                row += 1
                
                # Clean up loaded image
                del ocr_img
        # Fallback: check if debug_ocr_image exists (old format - shouldn't happen with new code)
        elif result.get('debug_ocr_image') is not None:
            label = QLabel("OCR Text Detection")
            label.setStyleSheet("font-weight: bold; color: #4A9EFF; font-size: 12pt;")
            grid.addWidget(label, row, 0, 1, 3)
            row += 1
            
            # Convert cv2 image to QPixmap
            ocr_img = result['debug_ocr_image']
            if len(ocr_img.shape) == 2:  # Grayscale
                height, width = ocr_img.shape
                bytes_per_line = width
                q_img = QImage(ocr_img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            else:  # Color
                height, width, channel = ocr_img.shape
                bytes_per_line = 3 * width
                q_img = QImage(ocr_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            
            pixmap = QPixmap.fromImage(q_img)
            
            # Scale to reasonable size for display
            scaled_pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            img_label = QLabel()
            img_label.setPixmap(scaled_pixmap)
            img_label.setAlignment(Qt.AlignCenter)
            img_label.setStyleSheet("border: 2px solid #4A9EFF; background-color: #1a1a1a;")
            img_label.setCursor(Qt.PointingHandCursor)
            img_label.setToolTip("Click to zoom")
            
            # Make clickable for zoom
            img_label.mousePressEvent = lambda event, p=pixmap: self.show_zoomed_image(p, "OCR Text Detection")
            
            grid.addWidget(img_label, row, 0, 1, 3)
            row += 1
        
        # Show preprocessing variants
        if result.get('debug_variants'):
            variants_label = QLabel("Preprocessing Variants")
            variants_label.setStyleSheet("font-weight: bold; color: #4A9EFF; margin-top: 10px; font-size: 12pt;")
            grid.addWidget(variants_label, row, 0, 1, 3)
            row += 1
            
            col = 0
            debug_variants = result['debug_variants']
            
            # Handle both dict and list formats
            if isinstance(debug_variants, dict):
                # Dict format: {variant_name: variant_img}
                for variant_name, variant_img in debug_variants.items():
                    var_label = QLabel(variant_name)
                    var_label.setAlignment(Qt.AlignCenter)
                    var_label.setStyleSheet("color: white; font-weight: bold;")
                    grid.addWidget(var_label, row, col)
                    
                    # Convert cv2 image to QPixmap
                    if len(variant_img.shape) == 2:  # Grayscale
                        height, width = variant_img.shape
                        bytes_per_line = width
                        q_img = QImage(variant_img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
                    else:  # Color
                        height, width, channel = variant_img.shape
                        bytes_per_line = 3 * width
                        q_img = QImage(variant_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                    
                    pixmap = QPixmap.fromImage(q_img)
                    scaled_pixmap = pixmap.scaled(350, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    img_label = QLabel()
                    img_label.setPixmap(scaled_pixmap)
                    img_label.setAlignment(Qt.AlignCenter)
                    img_label.setStyleSheet("border: 1px solid #444; background-color: #1a1a1a; padding: 5px;")
                    img_label.setCursor(Qt.PointingHandCursor)
                    img_label.setToolTip(f"Click to zoom - {variant_name}")
                    
                    # Make clickable for zoom
                    img_label.mousePressEvent = lambda event, p=pixmap, n=variant_name: self.show_zoomed_image(p, n)
                    
                    grid.addWidget(img_label, row + 1, col)
                    
                    col += 1
                    if col >= 3:
                        col = 0
                        row += 2
                        
            elif isinstance(debug_variants, list):
                # List format: [(variant_name, variant_img), ...]
                for item in debug_variants:
                    if isinstance(item, tuple) and len(item) == 2:
                        variant_name, variant_img = item
                        var_label = QLabel(variant_name)
                        var_label.setAlignment(Qt.AlignCenter)
                        var_label.setStyleSheet("color: white; font-weight: bold;")
                        grid.addWidget(var_label, row, col)
                        
                        # Convert cv2 image to QPixmap
                        if len(variant_img.shape) == 2:  # Grayscale
                            height, width = variant_img.shape
                            bytes_per_line = width
                            q_img = QImage(variant_img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
                        else:  # Color
                            height, width, channel = variant_img.shape
                            bytes_per_line = 3 * width
                            q_img = QImage(variant_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                        
                        pixmap = QPixmap.fromImage(q_img)
                        scaled_pixmap = pixmap.scaled(350, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        
                        img_label = QLabel()
                        img_label.setPixmap(scaled_pixmap)
                        img_label.setAlignment(Qt.AlignCenter)
                        img_label.setStyleSheet("border: 1px solid #444; background-color: #1a1a1a; padding: 5px;")
                        img_label.setCursor(Qt.PointingHandCursor)
                        img_label.setToolTip(f"Click to zoom - {variant_name}")
                        
                        # Make clickable for zoom
                        img_label.mousePressEvent = lambda event, p=pixmap, n=variant_name: self.show_zoomed_image(p, n)
                        
                        grid.addWidget(img_label, row + 1, col)
                        
                        col += 1
                        if col >= 3:
                            col = 0
                            row += 2
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return widget
    
    def show_zoomed_image(self, pixmap, title):
        """Show image in zoom dialog"""
        dialog = ImageViewerDialog(pixmap, title, self)
        dialog.exec_()
    
    def create_raw_data_text(self, result):
        """Create raw JSON text for batch result"""
        import json
        import numpy as np
        
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.integer, np.int32, np.int64)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float32, np.float64)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)
        
        # Filter out non-serializable items
        filtered = {
            k: v for k, v in result.items()
            if k not in ['debug_variants', 'debug_ocr_image', 'preprocessed_image', 
                        'original_image', 'marking_validation', 'datasheet_details']
        }
        
        return json.dumps(filtered, indent=2, cls=NumpyEncoder)
        
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
        """Update debug tab with organized sections: OCR first, then preprocessing"""
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
        
        # Enable export buttons
        self.export_debug_btn.setEnabled(True)
        self.export_raw_btn.setEnabled(True)
        
        # SECTION 1: OCR with text bounding boxes (FIRST)
        if self.show_bboxes_cb.isChecked() and 'debug_ocr_image' in results:
            self.ocr_group.setVisible(True)
            
            ocr_label = QLabel("Original image with detected text regions highlighted:")
            ocr_label.setStyleSheet("font-weight: bold; font-size: 10pt; padding: 5px; color: #4A9EFF;")
            self.ocr_layout.addWidget(ocr_label)
            
            # Display OCR image with clickable zoom
            img = results['debug_ocr_image']
            img_label = ClickableImageLabel()
            img_label.setAlignment(Qt.AlignCenter)
            
            # Convert to QPixmap
            if len(img.shape) == 2:
                h, w = img.shape
                q_image = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
            else:
                h, w, ch = img.shape
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                q_image = QImage(rgb.data, w, h, w * ch, QImage.Format_RGB888)
            
            full_pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = full_pixmap.scaled(700, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(scaled_pixmap)
            img_label.set_image(full_pixmap, "OCR Text Detection")
            img_label.clicked.connect(self.show_image_viewer)
            img_label.setStyleSheet("border: 2px solid #4A9EFF; padding: 5px; background: #2b2b2b;")
            
            self.ocr_layout.addWidget(img_label)
        else:
            self.ocr_group.setVisible(False)
        
        # SECTION 2: Preprocessing variants (SECOND)
        if self.show_preprocessed_cb.isChecked():
            self.preprocessing_group.setVisible(True)
            
            # Check if preprocessing variants exist
            if 'debug_variants' in results and results['debug_variants']:
                variants = results['debug_variants']
                
                # Add subtitle
                subtitle = QLabel(f"Showing {len(variants[:8])} preprocessing variants used for text extraction:")
                subtitle.setStyleSheet("font-size: 9pt; padding: 5px; color: #888; font-style: italic;")
                self.preprocessing_layout.addWidget(subtitle)
                
                # Create grid for variants
                grid_container = QWidget()
                grid_layout = QGridLayout(grid_container)
                grid_layout.setSpacing(10)
                
                row, col = 0, 0
                max_cols = 3
                
                for idx, (name, img) in enumerate(variants[:8]):  # Show first 8 variants
                    # Container for each variant
                    variant_widget = QWidget()
                    variant_layout = QVBoxLayout(variant_widget)
                    variant_layout.setSpacing(2)
                    
                    # Variant name label
                    name_label = QLabel(f"{idx+1}. {name}")
                    name_label.setStyleSheet("font-weight: bold; font-size: 9pt; padding: 3px; color: #FFA726;")
                    name_label.setAlignment(Qt.AlignCenter)
                    variant_layout.addWidget(name_label)
                    
                    # Convert and display image with clickable zoom
                    img_label = ClickableImageLabel()
                    img_label.setAlignment(Qt.AlignCenter)
                    
                    # Convert image to QPixmap
                    if len(img.shape) == 2:  # Grayscale
                        h, w = img.shape
                        q_image = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
                    else:  # BGR
                        h, w, ch = img.shape
                        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        q_image = QImage(rgb.data, w, h, w * ch, QImage.Format_RGB888)
                    
                    # Scale to thumbnail size
                    full_pixmap = QPixmap.fromImage(q_image)
                    scaled_pixmap = full_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    img_label.setPixmap(scaled_pixmap)
                    img_label.set_image(full_pixmap, f"Preprocessing: {name}")
                    img_label.clicked.connect(self.show_image_viewer)
                    img_label.setStyleSheet("border: 1px solid #444; padding: 3px; background: #2b2b2b;")
                    
                    variant_layout.addWidget(img_label)
                    
                    # Add to grid
                    grid_layout.addWidget(variant_widget, row, col)
                    
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                
                self.preprocessing_layout.addWidget(grid_container)
            else:
                # Show message when no preprocessing was needed
                no_preprocessing_label = QLabel("✅ No preprocessing needed - image quality was sufficient for direct text extraction")
                no_preprocessing_label.setStyleSheet("font-size: 11pt; padding: 20px; color: #4CAF50; font-weight: bold;")
                no_preprocessing_label.setAlignment(Qt.AlignCenter)
                no_preprocessing_label.setWordWrap(True)
                self.preprocessing_layout.addWidget(no_preprocessing_label)
        else:
            self.preprocessing_group.setVisible(False)
        
        # If neither checkbox is checked, show info message
        if not self.show_preprocessed_cb.isChecked() and not self.show_bboxes_cb.isChecked():
            self.debug_info.setText("Enable debug options (Show Text Boxes / Show Preprocessing) to view debug images")
            self.debug_info.setVisible(True)
            self.export_debug_btn.setEnabled(False)
    
    def on_debug_option_changed(self):
        """Called when debug checkboxes are toggled"""
        if self.current_results:
            self.update_debug_tab(self.current_results)
    
    def show_image_viewer(self, pixmap, title):
        """Show image viewer dialog with zoom capability"""
        viewer = ImageViewerDialog(pixmap, title, self)
        viewer.exec_()
    
    def export_debug_images(self):
        """Export all debug images to a folder"""
        if not self.current_results:
            QMessageBox.warning(self, "No Data", "No debug images available to export.")
            return
        
        # Select folder
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder for Debug Images",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not folder:
            return
        
        try:
            # Create subfolder with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_name = os.path.splitext(os.path.basename(self.current_image_path))[0] if self.current_image_path else "unknown"
            debug_folder = os.path.join(folder, f"debug_{image_name}_{timestamp}")
            os.makedirs(debug_folder, exist_ok=True)
            
            saved_count = 0
            
            # Export OCR image
            if 'debug_ocr_image' in self.current_results:
                ocr_img = self.current_results['debug_ocr_image']
                ocr_path = os.path.join(debug_folder, "01_ocr_text_detection.png")
                cv2.imwrite(ocr_path, ocr_img)
                saved_count += 1
            
            # Export preprocessing variants
            if 'debug_variants' in self.current_results:
                for idx, (name, img) in enumerate(self.current_results['debug_variants'], start=2):
                    # Sanitize filename
                    safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
                    variant_path = os.path.join(debug_folder, f"{idx:02d}_preprocessing_{safe_name}.png")
                    cv2.imwrite(variant_path, img)
                    saved_count += 1
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"Successfully exported {saved_count} debug images to:\n{debug_folder}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export images:\n{str(e)}")
    
    def export_raw_data(self):
        """Export raw authentication data as JSON"""
        if not self.current_results:
            QMessageBox.warning(self, "No Data", "No authentication data available to export.")
            return
        
        # Select save location
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_name = os.path.splitext(os.path.basename(self.current_image_path))[0] if self.current_image_path else "unknown"
        default_name = f"auth_data_{image_name}_{timestamp}.json"
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Raw Data",
            default_name,
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not save_path:
            return
        
        try:
            import json
            import numpy as np
            
            # Custom encoder for numpy types
            class NumpyEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, (np.integer, np.int32, np.int64)):
                        return int(obj)
                    elif isinstance(obj, (np.floating, np.float32, np.float64)):
                        return float(obj)
                    elif isinstance(obj, np.ndarray):
                        return obj.tolist()
                    elif isinstance(obj, bytes):
                        return obj.decode('utf-8', errors='ignore')
                    return super().default(obj)
            
            # Filter out non-serializable items
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'image_path': self.current_image_path,
                'verdict': self.current_results.get('verdict', 'UNKNOWN'),
                'is_authentic': self.current_results.get('is_authentic', False),
                'confidence': self.current_results.get('confidence', 0),
                'normalized_part_number': self.current_results.get('normalized_part_number', ''),
                'full_text': self.current_results.get('full_text', ''),
                'ocr_confidence': self.current_results.get('ocr_confidence', 0),
                'date_codes': self.current_results.get('date_codes', []),
                'logo': self.current_results.get('logo', ''),
                'datasheet_found': self.current_results.get('datasheet_found', False),
                'datasheet_source': self.current_results.get('datasheet_source', ''),
                'datasheet_url': self.current_results.get('datasheet_url', ''),
                'marking_validation': self.current_results.get('marking_validation', {}),
                'validation_issues': self.current_results.get('validation_issues', []),
                'processing_time': self.current_results.get('processing_time', 0),
            }
            
            # Add OCR details if available
            if 'ocr_details' in self.current_results:
                export_data['ocr_details'] = [
                    {
                        'text': d.get('text', ''),
                        'confidence': float(d.get('confidence', 0)),
                        'variant': d.get('variant', ''),
                        'bbox': d.get('bbox', [])
                    }
                    for d in self.current_results['ocr_details']
                ]
            
            # Write to file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False, cls=NumpyEncoder)
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"Raw data exported successfully to:\n{save_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{str(e)}")
        
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
    # Set App User Model ID BEFORE creating QApplication (Windows only)
    if sys.platform == 'win32':
        try:
            myappid = 'Ross0907.ICAuthenticator.ProductionGUI.v3.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            print(f"✓ App User Model ID set: {myappid}")
        except Exception as e:
            print(f"✗ Could not set App User Model ID: {e}")
    
    app = QApplication(sys.argv)
    app.setApplicationName("IC Authentication System")
    app.setOrganizationName("Ross0907")
    app.setOrganizationDomain("icauthenticator.local")
    
    # Set application icon with ABSOLUTE path - critical for Windows taskbar
    app_icon = None
    icon_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'icon.ico')),
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'icon.png')),
        os.path.abspath('icon.ico'),
        os.path.abspath('icon.png'),
    ]
    
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            try:
                app_icon = QIcon(icon_path)
                if not app_icon.isNull():
                    # Set on QApplication - this is the KEY for taskbar icon
                    app.setWindowIcon(app_icon)
                    # Also set as default for all widgets
                    QApplication.setWindowIcon(app_icon)
                    
                    print(f"✓ Application icon set from: {icon_path}")
                    print(f"  Icon size: {app_icon.availableSizes()}")
                    break
            except Exception as e:
                print(f"✗ Failed to load icon from {icon_path}: {e}")
    
    if not app_icon or app_icon.isNull():
        print(f"✗ Could not set application icon - tried paths:")
        for p in icon_paths:
            print(f"  - {p} (exists: {os.path.exists(p)})")
    
    gui = ICAuthenticatorGUI()
    # Pass the icon reference to the GUI
    if app_icon and not app_icon.isNull():
        gui.app_icon = app_icon
    
    gui.show()
    
    # Force icon refresh after showing (Windows taskbar workaround)
    if sys.platform == 'win32' and app_icon and not app_icon.isNull():
        gui.setWindowIcon(app_icon)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
