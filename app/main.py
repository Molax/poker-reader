import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from PIL import Image, ImageTk
import yaml
import json
from datetime import datetime

from config.template_configurator import TemplateConfigurator
from regions.utils.tooltip import ToolTip

try:
    import cv2
    import numpy as np
    import pytesseract
    import easyocr
    
    class OCREngine:
        def __init__(self):
            self.easyocr_reader = easyocr.Reader(['en'])
            self.tesseract_configs = {
                'default': '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,/:- ',
                'numbers': '--psm 8 -c tessedit_char_whitelist=0123456789.,',
                'currency': '--psm 8 -c tessedit_char_whitelist=0123456789$.,',
                'tournament': '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,/:- '
            }

    class ImageProcessor:
        @staticmethod
        def preprocess_region(image, region_type):
            processed_images = []
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            processed_images.append(gray)
            
            binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            processed_images.append(binary)
            
            inv_binary = cv2.bitwise_not(binary)
            processed_images.append(inv_binary)
            
            contrast_enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
            processed_images.append(contrast_enhanced)
            
            return processed_images

    class TextExtractor:
        def __init__(self):
            self.ocr_engine = OCREngine()
            self.image_processor = ImageProcessor()
            
        def extract_text_from_region(self, image, coordinates, region_type):
            x, y, width, height = coordinates['x'], coordinates['y'], coordinates['width'], coordinates['height']
            region = image.crop((x, y, x + width, y + height))
            region_np = np.array(region)
            
            processed_images = self.image_processor.preprocess_region(region_np, region_type)
            results = []
            
            for i, processed_img in enumerate(processed_images):
                pil_img = Image.fromarray(processed_img)
                
                tesseract_result = self._extract_with_tesseract(pil_img, region_type)
                if tesseract_result['confidence'] > 30:
                    results.append({
                        'method': f'tesseract_v{i}',
                        'text': tesseract_result['text'],
                        'confidence': tesseract_result['confidence']
                    })
                
                try:
                    easyocr_results = self.ocr_engine.easyocr_reader.readtext(processed_img)
                    if easyocr_results:
                        combined_text = ' '.join([result[1] for result in easyocr_results])
                        avg_confidence = sum([result[2] for result in easyocr_results]) / len(easyocr_results)
                        if avg_confidence > 0.3:
                            results.append({
                                'method': f'easyocr_v{i}',
                                'text': combined_text.strip(),
                                'confidence': avg_confidence * 100
                            })
                except:
                    pass
            
            best_result = self._select_best_result(results, region_type)
            
            return {
                'text': best_result['text'] if best_result else '',
                'confidence': best_result['confidence'] if best_result else 0,
                'method': best_result['method'] if best_result else 'none',
                'region_type': region_type,
                'coordinates': coordinates
            }
        
        def _extract_with_tesseract(self, image, region_type):
            config_map = {
                'tournament_header': 'tournament',
                'position_stats': 'default',
                'hand_history': 'numbers',
                'pot_info': 'currency',
                'hero_info': 'default'
            }
            
            config_key = config_map.get(region_type, 'default')
            if region_type.startswith('seat_'):
                config_key = 'default'
            
            config = self.ocr_engine.tesseract_configs[config_key]
            
            try:
                text = pytesseract.image_to_string(image, config=config).strip()
                data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                return {'text': text, 'confidence': avg_confidence}
            except:
                return {'text': '', 'confidence': 0}
        
        def _select_best_result(self, results, region_type):
            if not results:
                return None
            
            valid_results = [r for r in results if r['text'] and len(r['text'].strip()) > 0]
            if not valid_results:
                return None
            
            scored_results = []
            for result in valid_results:
                score = result['confidence'] + min(len(result['text']) * 2, 20)
                
                if region_type == 'tournament_header' and '$' in result['text']:
                    score += 30
                elif region_type == 'pot_info' and 'BB' in result['text']:
                    score += 25
                elif 'easyocr' in result['method']:
                    score += 5
                
                scored_results.append((score, result))
            
            scored_results.sort(key=lambda x: x[0], reverse=True)
            return scored_results[0][1]

    class PokerAnalysisEngine:
        def __init__(self):
            self.text_extractor = TextExtractor()
            
        def analyze_poker_image(self, image_path, template):
            try:
                image = Image.open(image_path)
                regions = template.get('regions', {})
                
                analysis_results = {
                    'site': template.get('site', 'unknown'),
                    'timestamp': None,
                    'image_file': os.path.basename(image_path),
                    'image_size': {'width': image.width, 'height': image.height},
                    'template_info': {
                        'total_regions': len(regions),
                        'player_count': template.get('player_count')
                    },
                    'extracted_data': {},
                    'analysis_summary': {
                        'successful_extractions': 0,
                        'failed_extractions': 0,
                        'average_confidence': 0,
                        'high_confidence_count': 0
                    }
                }
                
                confidences = []
                successful = 0
                failed = 0
                
                for region_key, region_data in regions.items():
                    try:
                        coordinates = region_data['coordinates']
                        region_type = region_data['type']
                        
                        extraction_result = self.text_extractor.extract_text_from_region(
                            image, coordinates, region_type
                        )
                        
                        analysis_results['extracted_data'][region_key] = {
                            'display_name': region_data.get('display_name', region_key),
                            'type': region_type,
                            'coordinates': coordinates,
                            'text': extraction_result['text'],
                            'confidence': extraction_result['confidence'],
                            'method': extraction_result['method'],
                            'success': bool(extraction_result['text'] and extraction_result['confidence'] > 30)
                        }
                        
                        if extraction_result['text'] and extraction_result['confidence'] > 30:
                            successful += 1
                            confidences.append(extraction_result['confidence'])
                            if extraction_result['confidence'] > 70:
                                analysis_results['analysis_summary']['high_confidence_count'] += 1
                        else:
                            failed += 1
                            
                    except Exception as e:
                        analysis_results['extracted_data'][region_key] = {
                            'display_name': region_data.get('display_name', region_key),
                            'type': region_data.get('type', 'unknown'),
                            'coordinates': region_data.get('coordinates', {}),
                            'text': '',
                            'confidence': 0,
                            'method': 'error',
                            'success': False,
                            'error': str(e)
                        }
                        failed += 1
                
                analysis_results['analysis_summary']['successful_extractions'] = successful
                analysis_results['analysis_summary']['failed_extractions'] = failed
                analysis_results['analysis_summary']['average_confidence'] = (
                    sum(confidences) / len(confidences) if confidences else 0
                )
                
                return analysis_results
                
            except Exception as e:
                return {
                    'error': f"Analysis failed: {str(e)}",
                    'site': template.get('site', 'unknown'),
                    'image_file': os.path.basename(image_path) if image_path else 'unknown'
                }

    OCR_AVAILABLE = True
    
except ImportError as e:
    OCR_AVAILABLE = False
    PokerAnalysisEngine = None

class PokeAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PokeAnalyzer - Poker Hand Analysis")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        self.current_image_path = None
        self.current_image = None
        self.poker_site = None
        self.extracted_data = {}
        self.templates = {}
        self.analysis_engine = PokerAnalysisEngine() if OCR_AVAILABLE else None
        
        self.setup_ui()
        self.load_existing_templates()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.setup_header(main_frame)
        self.setup_main_section(main_frame)
        self.setup_log_section(main_frame)
        
    def setup_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="PokeAnalyzer", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(header_frame, text="Ready - Upload an image to start", 
                                     font=('Arial', 12), foreground='green')
        self.status_label.pack(side=tk.RIGHT)
        
    def setup_main_section(self, parent):
        main_section = ttk.Frame(parent)
        main_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.setup_controls(main_section)
        self.setup_image_display(main_section)
        
    def setup_controls(self, parent):
        controls_frame = ttk.LabelFrame(parent, text="Controls", padding=15)
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X)
        
        self.upload_btn = ttk.Button(buttons_frame, text="1. Upload Poker Image", 
                                    command=self.upload_image, width=25)
        self.upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.upload_btn, "Upload a poker screenshot\nFilename should contain site name: image_yaya.png")
        
        self.configure_btn = ttk.Button(buttons_frame, text="2. Configure Template", 
                                       command=self.configure_template, 
                                       state=tk.DISABLED, width=25)
        self.configure_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.configure_btn, "Define regions to extract text from\nClick and drag to select areas")
        
        self.edit_template_btn = ttk.Button(buttons_frame, text="Edit Template", 
                                           command=self.edit_existing_template, 
                                           state=tk.DISABLED, width=20)
        self.edit_template_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.edit_template_btn, "Edit existing template configuration")
        
        self.analyze_btn = ttk.Button(buttons_frame, text="3. Analyze Image", 
                                     command=self.analyze_image, 
                                     state=tk.DISABLED, width=25)
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.analyze_btn, "Extract text from all defined regions\nRequires template to be configured first")
        
        info_frame = ttk.Frame(controls_frame)
        info_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(info_frame, text="Site:").pack(side=tk.LEFT)
        self.site_label = ttk.Label(info_frame, text="None", font=('Arial', 10, 'bold'))
        self.site_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(info_frame, text="Template:").pack(side=tk.LEFT)
        self.template_label = ttk.Label(info_frame, text="Not configured", foreground='red')
        self.template_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(info_frame, text="OCR Status:").pack(side=tk.LEFT)
        ocr_status = "Ready" if self.analysis_engine else "Not Available"
        ocr_color = "green" if self.analysis_engine else "red"
        self.ocr_label = ttk.Label(info_frame, text=ocr_status, foreground=ocr_color)
        self.ocr_label.pack(side=tk.LEFT, padx=(5, 0))
        
    def setup_image_display(self, parent):
        image_frame = ttk.LabelFrame(parent, text="Image Preview", padding=10)
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_canvas = tk.Canvas(image_frame, bg='#f0f0f0', height=300)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        canvas_label = ttk.Label(image_frame, text="Upload a poker screenshot to begin", 
                               foreground='gray')
        self.image_canvas.create_window(400, 150, window=canvas_label)
        
    def setup_log_section(self, parent):
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding=10)
        log_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, 
                                                 font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, pady=(10, 0))
        
        clear_btn = ttk.Button(log_controls, text="Clear Log", command=self.clear_log)
        clear_btn.pack(side=tk.LEFT)
        ToolTip(clear_btn, "Clear the activity log")
        
        self.export_btn = ttk.Button(log_controls, text="Export Results", 
                                    command=self.export_results, state=tk.DISABLED)
        self.export_btn.pack(side=tk.RIGHT)
        ToolTip(self.export_btn, "Export extracted data as YAML or JSON file")
        
    def upload_image(self):
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Poker Screenshot",
            filetypes=file_types
        )
        
        if file_path:
            self.current_image_path = file_path
            self.detect_poker_site()
            self.display_image()
            self.check_template_status()
            self.update_ui_state()
            
            filename = os.path.basename(file_path)
            self.log_message(f"✓ Image uploaded: {filename}")
            self.log_message(f"✓ Detected site: {self.poker_site.upper()}")
            
    def detect_poker_site(self):
        if not self.current_image_path:
            return
            
        filename = os.path.basename(self.current_image_path).lower()
        
        if '_yaya' in filename or '_yapoker' in filename:
            self.poker_site = 'yaya'
        elif '_pokerstars' in filename:
            self.poker_site = 'pokerstars'
        elif '_ggpoker' in filename:
            self.poker_site = 'ggpoker'
        elif '_888poker' in filename:
            self.poker_site = '888poker'
        else:
            self.poker_site = 'unknown'
            
        self.site_label.config(text=self.poker_site.upper())
        
    def display_image(self):
        if not self.current_image_path:
            return
            
        try:
            image = Image.open(self.current_image_path)
            
            canvas_width = 780
            canvas_height = 300
            
            image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(image)
            
            self.image_canvas.delete("all")
            self.image_canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                anchor=tk.CENTER, image=self.photo
            )
            
        except Exception as e:
            self.log_message(f"✗ Error displaying image: {str(e)}", "ERROR")
            
    def check_template_status(self):
        if self.poker_site in self.templates:
            template = self.templates[self.poker_site]
            region_count = len(template.get('regions', {}))
            self.template_label.config(text=f"Ready ({region_count} regions) ✓", foreground='green')
            self.log_message(f"✓ Template found for {self.poker_site} with {region_count} regions")
        else:
            self.template_label.config(text="Not configured", foreground='red')
            self.log_message(f"⚠ No template found for {self.poker_site} - Configure template first")
            
    def update_ui_state(self):
        if self.current_image_path:
            self.configure_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"Image loaded - {self.poker_site.upper()}")
            
            if self.poker_site in self.templates:
                self.edit_template_btn.config(state=tk.NORMAL)
                if self.analysis_engine:
                    self.analyze_btn.config(state=tk.NORMAL)
            else:
                self.edit_template_btn.config(state=tk.DISABLED)
                self.analyze_btn.config(state=tk.DISABLED)
        else:
            self.configure_btn.config(state=tk.DISABLED)
            self.edit_template_btn.config(state=tk.DISABLED)
            self.analyze_btn.config(state=tk.DISABLED)
            
    def configure_template(self):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please upload an image first")
            return
            
        self.log_message(f"🔧 Opening template configurator for {self.poker_site}...")
        
        configurator = TemplateConfigurator(self.root, self.current_image_path, self.poker_site)
        self.root.wait_window(configurator.window)
        
        if configurator.template_saved:
            self.load_existing_templates()
            self.check_template_status()
            self.update_ui_state()
            self.log_message(f"✓ Template configured and saved for {self.poker_site}")
        else:
            self.log_message("Template configuration cancelled")
            
    def edit_existing_template(self):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please upload an image first")
            return
            
        if self.poker_site not in self.templates:
            messagebox.showwarning("Warning", "No template exists for this site")
            return
            
        self.log_message(f"✏️ Opening template editor for {self.poker_site}...")
        
        configurator = TemplateConfigurator(
            self.root, 
            self.current_image_path, 
            self.poker_site, 
            existing_template=self.templates[self.poker_site]
        )
        self.root.wait_window(configurator.window)
        
        if configurator.template_saved:
            self.load_existing_templates()
            self.check_template_status()
            self.update_ui_state()
            self.log_message(f"✓ Template updated for {self.poker_site}")
        else:
            self.log_message("Template editing cancelled")
            
    def analyze_image(self):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please upload an image first")
            return
            
        if self.poker_site not in self.templates:
            messagebox.showwarning("Warning", "Please configure template first")
            return
            
        if not self.analysis_engine:
            messagebox.showerror("Error", "OCR engine not available. Please check dependencies.")
            return
            
        self.log_message(f"🔍 Starting OCR analysis using {self.poker_site} template...")
        self.status_label.config(text="Analyzing... Please wait", foreground='orange')
        self.root.update()
        
        try:
            template = self.templates[self.poker_site]
            regions = template.get('regions', {})
            
            self.log_message(f"  → Processing {len(regions)} regions with OCR engines...")
            
            analysis_results = self.analysis_engine.analyze_poker_image(
                self.current_image_path, template
            )
            
            if 'error' in analysis_results:
                self.log_message(f"✗ Analysis failed: {analysis_results['error']}", "ERROR")
                self.status_label.config(text="Analysis failed", foreground='red')
                return
            
            analysis_results['timestamp'] = datetime.now().isoformat()
            self.extracted_data = analysis_results
            
            summary = analysis_results['analysis_summary']
            self.log_message(f"✓ OCR Analysis completed!")
            self.log_message(f"  → Successful extractions: {summary['successful_extractions']}/{summary['successful_extractions'] + summary['failed_extractions']}")
            self.log_message(f"  → Average confidence: {summary['average_confidence']:.1f}%")
            self.log_message(f"  → High confidence results: {summary['high_confidence_count']}")
            
            self._log_extraction_details()
            
            self.status_label.config(text="Analysis complete - Ready to export", foreground='green')
            self.export_btn.config(state=tk.NORMAL)
                                    
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.log_message(f"✗ {error_msg}", "ERROR")
            self.status_label.config(text="Analysis failed", foreground='red')
            messagebox.showerror("Analysis Error", error_msg)
            
    def _log_extraction_details(self):
        if not self.extracted_data or 'extracted_data' not in self.extracted_data:
            return
            
        self.log_message("📊 Extraction Results:")
        
        for region_key, result in self.extracted_data['extracted_data'].items():
            status = "✓" if result['success'] else "✗"
            confidence = result['confidence']
            text_preview = result['text'][:50] + "..." if len(result['text']) > 50 else result['text']
            
            if result['success']:
                self.log_message(f"  {status} {result['display_name']}: '{text_preview}' ({confidence:.1f}%)")
            else:
                self.log_message(f"  {status} {result['display_name']}: Failed extraction", "ERROR")
                
    def export_results(self):
        if not self.extracted_data:
            messagebox.showwarning("Warning", "No analysis data to export")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.poker_site == 'yaya' and 'player_count' in self.extracted_data.get('template_info', {}):
            player_count = self.extracted_data['template_info']['player_count']
            default_name = f"{self.poker_site}_{player_count}p_analysis_{timestamp}.yml"
        else:
            default_name = f"{self.poker_site}_analysis_{timestamp}.yml"
        
        file_path = filedialog.asksaveasfilename(
            title="Export Analysis Results",
            defaultextension=".yml",
            initialname=default_name,
            filetypes=[("YAML files", "*.yml"), ("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w') as f:
                        json.dump(self.extracted_data, f, indent=2)
                else:
                    with open(file_path, 'w') as f:
                        yaml.dump(self.extracted_data, f, default_flow_style=False, 
                                 sort_keys=False, allow_unicode=True)
                        
                self.log_message(f"✓ Results exported: {os.path.basename(file_path)}")
                
                success_count = self.extracted_data.get('analysis_summary', {}).get('successful_extractions', 0)
                total_count = success_count + self.extracted_data.get('analysis_summary', {}).get('failed_extractions', 0)
                avg_confidence = self.extracted_data.get('analysis_summary', {}).get('average_confidence', 0)
                
                messagebox.showinfo("Export Complete", 
                    f"Analysis results exported successfully!\n\n"
                    f"Successful extractions: {success_count}/{total_count}\n"
                    f"Average confidence: {avg_confidence:.1f}%\n\n"
                    f"File: {os.path.basename(file_path)}")
                
            except Exception as e:
                error_msg = f"Export failed: {str(e)}"
                self.log_message(f"✗ {error_msg}", "ERROR")
                messagebox.showerror("Export Error", error_msg)
                
    def load_existing_templates(self):
        templates_dir = "templates"
        
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            self.log_message("Created templates directory")
            
        for filename in os.listdir(templates_dir):
            if filename.endswith('_template.json'):
                try:
                    with open(os.path.join(templates_dir, filename), 'r') as f:
                        template_data = json.load(f)
                        site = template_data.get('site', 'unknown')
                        self.templates[site] = template_data
                        self.log_message(f"✓ Loaded template: {filename}")
                except Exception as e:
                    self.log_message(f"✗ Failed to load {filename}: {str(e)}", "ERROR")
                    
    def log_message(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
        if level == "ERROR":
            self.log_text.tag_add("error", "end-2l", "end-1l")
            self.log_text.tag_config("error", foreground="red")
            
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
        
    def run(self):
        self.log_message("🚀 PokeAnalyzer started")
        
        if not OCR_AVAILABLE:
            self.log_message("⚠ OCR engine not available - install dependencies: pytesseract, easyocr, opencv-python", "ERROR")
        else:
            self.log_message("✓ OCR engine initialized successfully")
            
        self.log_message("📁 Looking for existing templates...")
        if self.templates:
            sites = ", ".join(self.templates.keys())
            self.log_message(f"✓ Found templates for: {sites}")
        else:
            self.log_message("⚠ No templates found - you'll need to configure templates first")
        self.root.mainloop()

if __name__ == "__main__":
    app = PokeAnalyzer()
    app.run()