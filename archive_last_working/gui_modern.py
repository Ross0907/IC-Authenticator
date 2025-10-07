"""
MODERN GUI FOR IC AUTHENTICATOR
Professional production-ready interface with light/dark mode
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
from production_ic_authenticator import ProductionICAuthenticator


class ModernICAuthenticatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth = ProductionICAuthenticator()
        self.dark_mode = False
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("IC Authenticator Pro - Modern Interface")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area (splitter)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Image and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([500, 900])
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Apply initial theme
        self.apply_theme()
    
    def create_header(self):
        header = QWidget()
        layout = QHBoxLayout()
        header.setLayout(layout)
        
        # Title
        title = QLabel("🔬 IC Authenticator Pro")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Theme toggle
        theme_btn = QPushButton("🌙 Dark Mode")
        theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_btn)
        self.theme_btn = theme_btn
        
        header.setFixedHeight(60)
        return header
    
    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Image display
        image_group = QGroupBox("IC Image")
        image_layout = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setStyleSheet("border: 2px dashed #ccc; background: #f5f5f5;")
        self.image_label.setText("No image loaded\n\nClick 'Load Image' to start")
        image_layout.addWidget(self.image_label)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # Controls
        controls_group = QGroupBox("Actions")
        controls_layout = QVBoxLayout()
        
        load_btn = QPushButton("📁 Load Image")
        load_btn.clicked.connect(self.load_image)
        controls_layout.addWidget(load_btn)
        
        analyze_btn = QPushButton("🔬 Analyze IC")
        analyze_btn.clicked.connect(self.analyze_ic)
        controls_layout.addWidget(analyze_btn)
        self.analyze_btn = analyze_btn
        self.analyze_btn.setEnabled(False)
        
        batch_btn = QPushButton("📂 Batch Analysis")
        batch_btn.clicked.connect(self.batch_analysis)
        controls_layout.addWidget(batch_btn)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        return panel
    
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Results tabs
        tabs = QTabWidget()
        
        # Tab 1: Analysis Results
        results_tab = self.create_results_tab()
        tabs.addTab(results_tab, "📊 Analysis Results")
        
        # Tab 2: Extracted Data
        data_tab = self.create_data_tab()
        tabs.addTab(data_tab, "📝 Extracted Data")
        
        # Tab 3: Validation Details
        validation_tab = self.create_validation_tab()
        tabs.addTab(validation_tab, "✅ Validation")
        
        # Tab 4: History
        history_tab = self.create_history_tab()
        tabs.addTab(history_tab, "📜 History")
        
        layout.addWidget(tabs)
        
        return panel
    
    def create_results_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Verdict display
        self.verdict_label = QLabel("No analysis yet")
        self.verdict_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            padding: 20px;
            border: 2px solid #ccc;
            border-radius: 5px;
            background: #f9f9f9;
        """)
        self.verdict_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.verdict_label)
        
        # Confidence meter
        conf_group = QGroupBox("Confidence Score")
        conf_layout = QVBoxLayout()
        
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        conf_layout.addWidget(self.confidence_bar)
        
        conf_group.setLayout(conf_layout)
        layout.addWidget(conf_group)
        
        # Recommendation
        rec_group = QGroupBox("Recommendation")
        rec_layout = QVBoxLayout()
        
        self.recommendation_text = QTextEdit()
        self.recommendation_text.setReadOnly(True)
        self.recommendation_text.setMaximumHeight(100)
        rec_layout.addWidget(self.recommendation_text)
        
        rec_group.setLayout(rec_layout)
        layout.addWidget(rec_group)
        
        # Issues/Warnings
        issues_group = QGroupBox("Issues & Warnings")
        issues_layout = QVBoxLayout()
        
        self.issues_list = QListWidget()
        issues_layout.addWidget(self.issues_list)
        
        issues_group.setLayout(issues_layout)
        layout.addWidget(issues_group)
        
        layout.addStretch()
        
        return widget
    
    def create_data_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        self.data_text = QTextEdit()
        self.data_text.setReadOnly(True)
        self.data_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.data_text)
        
        return widget
    
    def create_validation_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.validation_text)
        
        return widget
    
    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh History")
        refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(refresh_btn)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Timestamp", "Part Number", "Manufacturer", "Result", "Confidence"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.history_table)
        
        return widget
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.theme_btn.setText("☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode")
    
    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #555;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QPushButton {
                    background-color: #0d47a1;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:disabled {
                    background-color: #555;
                }
                QTextEdit, QListWidget, QTableWidget {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QGroupBox {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
                QTextEdit, QListWidget, QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                }
            """)
    
    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select IC Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if filename:
            self.current_image = filename
            pixmap = QPixmap(filename)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.analyze_btn.setEnabled(True)
            self.statusBar().showMessage(f"Loaded: {os.path.basename(filename)}")
    
    def analyze_ic(self):
        if not hasattr(self, 'current_image'):
            return
        
        # Show progress dialog
        progress = QProgressDialog("Analyzing IC...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()
        
        try:
            # Run analysis
            result = self.auth.analyze_ic(self.current_image)
            
            # Update UI with results
            self.display_results(result)
            
            self.statusBar().showMessage("Analysis complete")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")
        finally:
            progress.close()
    
    def display_results(self, result):
        # Verdict
        if result['is_authentic']:
            verdict_text = "✅ AUTHENTIC IC"
            verdict_color = "#4CAF50"
        else:
            verdict_text = "❌ COUNTERFEIT/SUSPECT"
            verdict_color = "#f44336"
        
        self.verdict_label.setText(verdict_text)
        self.verdict_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            padding: 20px;
            border: 3px solid {verdict_color};
            border-radius: 5px;
            background: {'#e8f5e9' if result['is_authentic'] else '#ffebee'};
            color: {verdict_color};
        """)
        
        # Confidence
        conf_percent = int(result['confidence_score'] * 100)
        self.confidence_bar.setValue(conf_percent)
        
        # Recommendation
        self.recommendation_text.setText(result['recommendation'])
        
        # Issues
        self.issues_list.clear()
        for issue in result.get('issues', []):
            item = QListWidgetItem(f"[{issue['severity']}] {issue['message']}")
            self.issues_list.addItem(item)
        
        for warning in result.get('warnings', []):
            msg = warning if isinstance(warning, str) else warning.get('message', str(warning))
            item = QListWidgetItem(f"[WARNING] {msg}")
            self.issues_list.addItem(item)
        
        # Extracted data
        extracted = result['extracted_markings']
        data_text = f"""
EXTRACTED MARKINGS:
==================
Part Number: {extracted.get('part_number', 'N/A')}
Manufacturer: {extracted.get('manufacturer', 'N/A')}
Date Codes: {', '.join(extracted.get('date_codes', [])) or 'None'}
Lot Codes: {', '.join(extracted.get('lot_codes', [])) or 'None'}
Country Codes: {', '.join(extracted.get('country_codes', [])) or 'None'}

All Text Found:
{', '.join(extracted.get('all_text_found', [])[:20])}
        """
        self.data_text.setText(data_text.strip())
        
        # Validation details
        verification = result.get('verification', {})
        val_text = f"""
VALIDATION RESULTS:
==================
Manufacturer: {verification.get('manufacturer', 'N/A')}
Validation Passed: {'YES' if verification.get('validation_passed') else 'NO'}

Date Validation:
{self.format_dict(verification.get('date_validation', {}))}

DATASHEET VERIFICATION:
=====================
{self.format_dict(result.get('official_markings', {}))}
        """
        self.validation_text.setText(val_text.strip())
    
    def format_dict(self, d, indent=0):
        lines = []
        for k, v in d.items():
            if isinstance(v, dict):
                lines.append("  " * indent + f"{k}:")
                lines.append(self.format_dict(v, indent + 1))
            else:
                lines.append("  " * indent + f"{k}: {v}")
        return "\n".join(lines)
    
    def batch_analysis(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with IC Images")
        if not folder:
            return
        
        # Get all images
        images = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
        ]
        
        if not images:
            QMessageBox.warning(self, "No Images", "No images found in selected folder")
            return
        
        # Show progress
        progress = QProgressDialog(f"Analyzing {len(images)} images...", "Cancel", 0, len(images), self)
        progress.setWindowModality(Qt.WindowModal)
        
        results = []
        for i, img_path in enumerate(images):
            if progress.wasCanceled():
                break
            
            progress.setValue(i)
            progress.setLabelText(f"Analyzing {os.path.basename(img_path)}...")
            QApplication.processEvents()
            
            try:
                result = self.auth.analyze_ic(img_path)
                results.append((img_path, result))
            except Exception as e:
                print(f"Error analyzing {img_path}: {e}")
        
        progress.setValue(len(images))
        
        # Show summary
        authentic = sum(1 for _, r in results if r['is_authentic'])
        msg = f"""
Batch Analysis Complete

Total Images: {len(results)}
Authentic: {authentic}
Counterfeit/Suspect: {len(results) - authentic}
        """
        QMessageBox.information(self, "Batch Analysis Complete", msg.strip())
        
        self.load_history()
    
    def load_history(self):
        history = self.auth.db.get_history(limit=100)
        
        self.history_table.setRowCount(len(history))
        
        for i, entry in enumerate(history):
            self.history_table.setItem(i, 0, QTableWidgetItem(entry['timestamp']))
            self.history_table.setItem(i, 1, QTableWidgetItem(entry.get('part_number', 'N/A')))
            self.history_table.setItem(i, 2, QTableWidgetItem(entry.get('manufacturer', 'N/A')))
            
            result_text = "✅ Authentic" if entry['is_authentic'] else "❌ Counterfeit"
            self.history_table.setItem(i, 3, QTableWidgetItem(result_text))
            
            self.history_table.setItem(i, 4, QTableWidgetItem(f"{entry['confidence']:.1%}"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernICAuthenticatorGUI()
    window.show()
    sys.exit(app.exec_())
