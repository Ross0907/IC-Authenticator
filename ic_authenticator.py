"""
IC Authentication System - Main Application
Advanced AOI-based system for detecting counterfeit integrated circuits
"""

import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTextEdit, QTabWidget, QCheckBox, QGroupBox,
                             QProgressBar, QComboBox, QLineEdit, QSpinBox,
                             QMessageBox, QSplitter, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
import json
from datetime import datetime

from image_processor import ImageProcessor
from ocr_engine import OCREngine
from web_scraper import DatasheetScraper
from verification_engine import VerificationEngine
from database_manager import DatabaseManager


class ProcessingThread(QThread):
    """Background thread for image processing"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    result = pyqtSignal(dict)
    debug_images = pyqtSignal(dict)
    
    def __init__(self, image_path, settings):
        super().__init__()
        self.image_path = image_path
        self.settings = settings
        self.image_processor = ImageProcessor()
        self.ocr_engine = OCREngine()
        self.scraper = DatasheetScraper()
        self.verifier = VerificationEngine()
        
    def run(self):
        try:
            # Step 1: Load and preprocess image
            self.status.emit("Loading image...")
            self.progress.emit(10)
            image = cv2.imread(self.image_path)
            if image is None:
                raise ValueError("Failed to load image")
            
            # Step 2: Image preprocessing and enhancement
            self.status.emit("Preprocessing image...")
            self.progress.emit(20)
            processed_images = self.image_processor.process_image(image)
            self.debug_images.emit(processed_images)
            
            # Step 3: IC Detection
            self.status.emit("Detecting IC component...")
            self.progress.emit(30)
            ic_regions = self.image_processor.detect_ic_regions(
                processed_images['enhanced']
            )
            
            # Step 4: Extract markings
            self.status.emit("Extracting markings...")
            self.progress.emit(40)
            marking_regions = self.image_processor.extract_marking_regions(
                ic_regions
            )
            
            # Step 5: OCR on markings using YOLO-OCR system
            self.status.emit("Performing advanced YOLO-OCR...")
            self.progress.emit(50)
            
            # Use direct YOLO-OCR integration for better results
            print(f"🔍 Using OCR method: {self.settings.get('ocr_method', 'yolo')}")
            
            extracted_result = self.ocr_engine.extract_text(
                marking_regions,
                method=self.settings.get('ocr_method', 'yolo')
            )
            
            # Extract the text and confidence
            extracted_text = extracted_result.get('text', '')
            ocr_confidence = extracted_result.get('confidence', 0.0)
            
            print(f"📝 OCR extracted: '{extracted_text}' (confidence: {ocr_confidence:.3f})")
            
            # Step 6: Parse marking information using advanced pattern recognition
            self.status.emit("Parsing IC marking structure...")
            self.progress.emit(60)
            parsed_data = self.ocr_engine.parse_marking_structure(extracted_text)
            
            # Add OCR confidence to parsed data
            parsed_data['ocr_confidence'] = ocr_confidence
            parsed_data['ocr_method'] = self.settings.get('ocr_method', 'yolo')
            
            # Step 7: Search for datasheet online
            self.status.emit("Searching for datasheet...")
            self.progress.emit(70)
            datasheet_info = self.scraper.search_component_datasheet(
                parsed_data.get('part_number', ''),
                parsed_data.get('manufacturer', '')
            )
            
            # Step 8: Extract marking specifications from datasheet
            self.status.emit("Analyzing datasheet...")
            self.progress.emit(80)
            official_markings = self.scraper.extract_marking_specifications(
                datasheet_info
            )
            
            # Step 9: Verify authenticity
            self.status.emit("Verifying authenticity...")
            self.progress.emit(90)
            verification_result = self.verifier.verify_component(
                parsed_data,
                official_markings,
                processed_images
            )
            
            # Step 10: Compile results
            self.status.emit("Compilation results...")
            self.progress.emit(95)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'image_path': self.image_path,
                'extracted_markings': parsed_data,
                'official_markings': official_markings,
                'verification': verification_result,
                'datasheet_sources': datasheet_info,
                'confidence_score': verification_result.get('confidence', 0),
                'is_authentic': verification_result.get('is_authentic', False),
                'anomalies': verification_result.get('anomalies', []),
                'recommendation': verification_result.get('recommendation', ''),
                'ocr_details': {
                    'method': self.settings.get('ocr_method', 'yolo'),
                    'raw_text': extracted_text,
                    'ocr_confidence': ocr_confidence,
                    'regions_detected': extracted_result.get('regions_detected', 0)
                }
            }
            
            self.progress.emit(100)
            self.status.emit("Analysis complete!")
            self.result.emit(result)
            
        except Exception as e:
            self.status.emit(f"Error: {str(e)}")
            self.result.emit({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })


class ICAuthenticatorGUI(QMainWindow):
    """Main GUI Application for IC Authentication System"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.current_results = None
        self.debug_images = {}
        self.db_manager = DatabaseManager()
        
        self.init_ui()
        self.apply_stylesheet()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("IC Authentication System - AOI Platform")
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
        
        # Image Selection Group
        image_group = QGroupBox("Image Input")
        image_layout = QVBoxLayout()
        
        self.load_btn = QPushButton("📁 Load IC Image")
        self.load_btn.clicked.connect(self.load_image)
        image_layout.addWidget(self.load_btn)
        
        self.capture_btn = QPushButton("📷 Capture from Camera")
        self.capture_btn.clicked.connect(self.capture_from_camera)
        image_layout.addWidget(self.capture_btn)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # OCR Settings Group
        ocr_group = QGroupBox("OCR Settings")
        ocr_layout = QVBoxLayout()
        
        ocr_label = QLabel("OCR Method:")
        ocr_layout.addWidget(ocr_label)
        
        self.ocr_combo = QComboBox()
        self.ocr_combo.addItems(['YOLO-OCR (Recommended)', 'Ensemble (All)', 'EasyOCR', 
                                 'Tesseract', 'Auto-Select'])
        ocr_layout.addWidget(self.ocr_combo)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # Debug Options Group
        debug_group = QGroupBox("Debug Visualization")
        debug_layout = QVBoxLayout()
        
        self.show_preprocessing = QCheckBox("Show Preprocessing Steps")
        self.show_preprocessing.setChecked(True)
        debug_layout.addWidget(self.show_preprocessing)
        
        self.show_detection = QCheckBox("Show IC Detection")
        self.show_detection.setChecked(True)
        debug_layout.addWidget(self.show_detection)
        
        self.show_segmentation = QCheckBox("Show Text Segmentation")
        self.show_segmentation.setChecked(True)
        debug_layout.addWidget(self.show_segmentation)
        
        self.show_features = QCheckBox("Show Feature Analysis")
        self.show_features.setChecked(True)
        debug_layout.addWidget(self.show_features)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        # Analysis Button
        self.analyze_btn = QPushButton("🔍 Analyze IC")
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.analyze_ic)
        self.analyze_btn.setMinimumHeight(50)
        self.analyze_btn.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.analyze_btn)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Additional Options
        options_group = QGroupBox("Additional Options")
        options_layout = QVBoxLayout()
        
        self.batch_btn = QPushButton("📦 Batch Processing")
        self.batch_btn.clicked.connect(self.batch_processing)
        options_layout.addWidget(self.batch_btn)
        
        self.history_btn = QPushButton("📊 View History")
        self.history_btn.clicked.connect(self.view_history)
        options_layout.addWidget(self.history_btn)
        
        self.export_btn = QPushButton("💾 Export Report")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)
        options_layout.addWidget(self.export_btn)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
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
        
        # Debug Layers Tab
        debug_tab = self.create_debug_tab()
        self.tab_widget.addTab(debug_tab, "🔧 Debug Layers")
        
        # Results Tab
        results_tab = self.create_results_tab()
        self.tab_widget.addTab(results_tab, "📋 Results")
        
        # Verification Tab
        verification_tab = self.create_verification_tab()
        self.tab_widget.addTab(verification_tab, "✓ Verification")
        
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
        self.image_label.setStyleSheet("border: 2px solid #cccccc; background-color: #f0f0f0;")
        
        scroll = QScrollArea()
        scroll.setWidget(self.image_label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Image info
        self.image_info_label = QLabel("Image Info: -")
        layout.addWidget(self.image_info_label)
        
        return tab
    
    def create_debug_tab(self):
        """Create debug visualization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Debug layer selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Debug Layer:"))
        
        self.debug_combo = QComboBox()
        self.debug_combo.addItems([
            'Original', 'Grayscale', 'Denoised', 'Enhanced',
            'Edge Detection', 'IC Detection', 'ROI Extraction',
            'Text Segmentation', 'Feature Analysis'
        ])
        self.debug_combo.currentTextChanged.connect(self.display_debug_layer)
        selector_layout.addWidget(self.debug_combo)
        selector_layout.addStretch()
        
        layout.addLayout(selector_layout)
        
        # Debug image display
        self.debug_image_label = QLabel("No debug data available")
        self.debug_image_label.setAlignment(Qt.AlignCenter)
        self.debug_image_label.setMinimumSize(800, 600)
        self.debug_image_label.setStyleSheet("border: 2px solid #cccccc; background-color: #f0f0f0;")
        
        scroll = QScrollArea()
        scroll.setWidget(self.debug_image_label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
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
        
        # Authenticity Result
        self.auth_label = QLabel("Authenticity: Not Analyzed")
        self.auth_label.setAlignment(Qt.AlignCenter)
        self.auth_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.auth_label.setMinimumHeight(80)
        layout.addWidget(self.auth_label)
        
        # Confidence Score
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Confidence Score:"))
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setMinimumHeight(30)
        confidence_layout.addWidget(self.confidence_bar)
        layout.addLayout(confidence_layout)
        
        # Detailed verification info
        self.verification_text = QTextEdit()
        self.verification_text.setReadOnly(True)
        layout.addWidget(self.verification_text)
        
        return tab
    
    def apply_stylesheet(self):
        """Apply custom stylesheet to the application"""
        stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
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
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QProgressBar {
            border: 2px solid #cccccc;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
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
    
    def display_image(self, image_path):
        """Display image in the image tab"""
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
        # Update image info
        image = cv2.imread(image_path)
        h, w = image.shape[:2]
        self.image_info_label.setText(
            f"Image Info: {w}x{h} pixels | {os.path.basename(image_path)}"
        )
    
    def capture_from_camera(self):
        """Capture image from camera"""
        QMessageBox.information(
            self,
            "Camera Capture",
            "Camera capture feature will be implemented.\nPlease use 'Load IC Image' for now."
        )
    
    def analyze_ic(self):
        """Start IC analysis process"""
        if not self.current_image_path:
            return
        
        # Get selected method and convert to proper format
        selected_method = self.ocr_combo.currentText()
        if 'YOLO-OCR' in selected_method:
            ocr_method = 'yolo'
        elif 'Ensemble' in selected_method:
            ocr_method = 'ensemble'
        elif 'EasyOCR' in selected_method:
            ocr_method = 'easyocr'
        elif 'Tesseract' in selected_method:
            ocr_method = 'tesseract'
        else:
            ocr_method = 'yolo'  # Default to YOLO-OCR
        
        settings = {
            'ocr_method': ocr_method,
            'show_debug': True,
            'confidence_threshold': 0.5
        }
        
        print(f"🔍 Starting IC analysis with OCR method: {ocr_method}")
        
        # Create and start processing thread
        self.processing_thread = ProcessingThread(
            self.current_image_path,
            settings
        )
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.status.connect(self.update_status)
        self.processing_thread.result.connect(self.display_results)
        self.processing_thread.debug_images.connect(self.store_debug_images)
        
        # Disable analyze button during processing
        self.analyze_btn.setEnabled(False)
        self.processing_thread.start()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)
    
    def store_debug_images(self, images):
        """Store debug images for visualization"""
        self.debug_images = images
    
    def display_debug_layer(self, layer_name):
        """Display selected debug layer"""
        if not self.debug_images:
            return
        
        layer_map = {
            'Original': 'original',
            'Grayscale': 'grayscale',
            'Denoised': 'denoised',
            'Enhanced': 'enhanced',
            'Edge Detection': 'edges',
            'IC Detection': 'ic_detected',
            'ROI Extraction': 'roi',
            'Text Segmentation': 'text_regions',
            'Feature Analysis': 'features'
        }
        
        layer_key = layer_map.get(layer_name)
        if layer_key and layer_key in self.debug_images:
            image = self.debug_images[layer_key]
            self.display_cv_image(image, self.debug_image_label)
    
    def display_cv_image(self, cv_image, label):
        """Display OpenCV image in QLabel"""
        if len(cv_image.shape) == 2:
            height, width = cv_image.shape
            bytes_per_line = width
            q_image = QImage(
                cv_image.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_Grayscale8
            )
        else:
            height, width, channel = cv_image.shape
            bytes_per_line = 3 * width
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            q_image = QImage(
                rgb_image.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_RGB888
            )
        
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
    
    def _convert_to_serializable(self, obj):
        """Convert numpy types to native Python types for JSON serialization"""
        if isinstance(obj, dict):
            return {key: self._convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return obj
    
    def display_results(self, results):
        """Display analysis results"""
        self.current_results = results
        self.analyze_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        if 'error' in results:
            self.results_text.setText(f"Error: {results['error']}")
            return
        
        # Display in results tab
        results_text = self.format_results(results)
        self.results_text.setText(results_text)
        
        # Display in verification tab
        self.display_verification(results)
        
        # Save to database
        self.db_manager.save_analysis(results)
        
        # Switch to results tab
        self.tab_widget.setCurrentIndex(2)
    
    def format_results(self, results):
        """Format results for display"""
        text = "=" * 80 + "\n"
        text += "IC AUTHENTICATION ANALYSIS REPORT\n"
        text += "=" * 80 + "\n\n"
        
        text += f"Timestamp: {results.get('timestamp', 'N/A')}\n"
        text += f"Image: {os.path.basename(results.get('image_path', 'N/A'))}\n\n"
        
        text += "-" * 80 + "\n"
        text += "EXTRACTED MARKINGS\n"
        text += "-" * 80 + "\n"
        extracted = results.get('extracted_markings', {})
        for key, value in extracted.items():
            text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        text += "\n" + "-" * 80 + "\n"
        text += "OFFICIAL MARKINGS (from Datasheet)\n"
        text += "-" * 80 + "\n"
        official = results.get('official_markings', {})
        for key, value in official.items():
            text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        text += "\n" + "-" * 80 + "\n"
        text += "VERIFICATION RESULTS\n"
        text += "-" * 80 + "\n"
        verification = results.get('verification', {})
        text += f"Authentic: {results.get('is_authentic', 'Unknown')}\n"
        text += f"Confidence: {results.get('confidence_score', 0):.2f}%\n"
        text += f"\nRecommendation:\n{results.get('recommendation', 'N/A')}\n"
        
        if results.get('anomalies'):
            text += "\n" + "-" * 80 + "\n"
            text += "DETECTED ANOMALIES\n"
            text += "-" * 80 + "\n"
            for i, anomaly in enumerate(results['anomalies'], 1):
                text += f"{i}. {anomaly}\n"
        
        text += "\n" + "=" * 80 + "\n"
        
        return text
    
    def display_verification(self, results):
        """Display verification results"""
        is_authentic = results.get('is_authentic', False)
        confidence = results.get('confidence_score', 0)
        
        if is_authentic:
            self.auth_label.setText("✓ AUTHENTIC")
            self.auth_label.setStyleSheet(
                "background-color: #4CAF50; color: white; border-radius: 10px;"
            )
        else:
            self.auth_label.setText("✗ COUNTERFEIT SUSPECTED")
            self.auth_label.setStyleSheet(
                "background-color: #f44336; color: white; border-radius: 10px;"
            )
        
        self.confidence_bar.setValue(int(confidence))
        
        # Detailed verification info
        verification = results.get('verification', {})
        # Convert numpy types to native Python types for JSON serialization
        details = json.dumps(self._convert_to_serializable(verification), indent=2)
        self.verification_text.setText(details)
    
    def batch_processing(self):
        """Batch process multiple images"""
        QMessageBox.information(
            self,
            "Batch Processing",
            "Batch processing feature will open a separate dialog.\nSelect multiple images for analysis."
        )
    
    def view_history(self):
        """View analysis history"""
        QMessageBox.information(
            self,
            "Analysis History",
            "History viewer will show all previous analyses.\nFeature coming soon."
        )
    
    def export_report(self):
        """Export analysis report"""
        if not self.current_results:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            f"IC_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;PDF Files (*.pdf);;Text Files (*.txt)"
        )
        
        if file_path:
            if file_path.endswith('.json'):
                with open(file_path, 'w') as f:
                    json.dump(self.current_results, f, indent=2)
            elif file_path.endswith('.txt'):
                with open(file_path, 'w') as f:
                    f.write(self.format_results(self.current_results))
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Report exported to:\n{file_path}"
            )


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, Qt.black)
    app.setPalette(palette)
    
    window = ICAuthenticatorGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
