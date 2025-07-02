import tkinter as tk
from datetime import datetime

from config.template_configurator import TemplateConfigurator

try:
    import cv2
    import numpy as np
    import pytesseract
    import easyocr
    from ocr.analysis_engine import PokerAnalysisEngine
    OCR_AVAILABLE = True
except ImportError as e:
    OCR_AVAILABLE = False
    PokerAnalysisEngine = None

from ui.poker_analyzer_ui import PokerAnalyzerUI
from ui.results_viewer import ResultsViewer
from ui.results_browser import ResultsBrowser

class PokeAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PokeAnalyzer - Poker Hand Analysis")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        self.analysis_engine = PokerAnalysisEngine() if OCR_AVAILABLE else None
        
        self.ui = PokerAnalyzerUI(
            self.root,
            OCR_AVAILABLE,
            self.analysis_engine,
            TemplateConfigurator,
            ResultsViewer,
            ResultsBrowser
        )
        
    def run(self):
        self.ui.log_message("🚀 PokeAnalyzer started")
        
        if not OCR_AVAILABLE:
            self.ui.log_message("⚠ OCR engine not available - install dependencies: pytesseract, easyocr, opencv-python", "ERROR")
        else:
            self.ui.log_message("✓ OCR engine initialized successfully")
            
        self.ui.log_message("📁 Looking for existing templates...")
        if self.ui.templates:
            sites = ", ".join(self.ui.templates.keys())
            self.ui.log_message(f"✓ Found templates for: {sites}")
        else:
            self.ui.log_message("⚠ No templates found - you'll need to configure templates first")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = PokeAnalyzer()
    app.run()