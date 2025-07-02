import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from PIL import Image, ImageTk
import yaml
import json
from datetime import datetime

from regions.utils.tooltip import ToolTip

class PokerAnalyzerUI:
    def __init__(self, root, ocr_available, analysis_engine, config_class, results_viewer_class, results_browser_class):
        self.root = root
        self.ocr_available = ocr_available
        self.analysis_engine = analysis_engine
        self.config_class = config_class
        self.results_viewer_class = results_viewer_class
        self.results_browser_class = results_browser_class
        
        self.current_image_path = None
        self.current_image = None
        self.poker_site = None
        self.extracted_data = {}
        self.templates = {}
        
        self.setup_directories()
        self.setup_ui()
        self.load_existing_templates()
        
    def setup_directories(self):
        os.makedirs("results", exist_ok=True)
        os.makedirs("templates", exist_ok=True)
        os.makedirs("templates/previews", exist_ok=True)
        
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
        
        buttons_frame2 = ttk.Frame(controls_frame)
        buttons_frame2.pack(fill=tk.X, pady=(10, 0))
        
        self.view_results_btn = ttk.Button(buttons_frame2, text="View Last Results", 
                                          command=self.view_last_results, 
                                          state=tk.DISABLED, width=20)
        self.view_results_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.view_results_btn, "View detailed results from last analysis")
        
        self.browse_results_btn = ttk.Button(buttons_frame2, text="Browse All Results", 
                                            command=self.browse_all_results, width=20)
        self.browse_results_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.browse_results_btn, "Browse all saved analysis results")
        
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
        
        configurator = self.config_class(self.root, self.current_image_path, self.poker_site)
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
        
        configurator = self.config_class(
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
            
            auto_save_path = self.auto_save_results(analysis_results)
            
            summary = analysis_results['analysis_summary']
            self.log_message(f"✓ OCR Analysis completed!")
            self.log_message(f"  → Results auto-saved: {os.path.basename(auto_save_path)}")
            self.log_message(f"  → Successful extractions: {summary['successful_extractions']}/{summary['successful_extractions'] + summary['failed_extractions']}")
            self.log_message(f"  → Average confidence: {summary['average_confidence']:.1f}%")
            self.log_message(f"  → High confidence results: {summary['high_confidence_count']}")
            
            self._log_extraction_details()
            
            self.status_label.config(text="Analysis complete - Results saved", foreground='green')
            self.export_btn.config(state=tk.NORMAL)
            self.view_results_btn.config(state=tk.NORMAL)
                                    
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.log_message(f"✗ {error_msg}", "ERROR")
            self.status_label.config(text="Analysis failed", foreground='red')
            messagebox.showerror("Analysis Error", error_msg)
    
    def auto_save_results(self, analysis_results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.poker_site == 'yaya' and 'player_count' in analysis_results.get('template_info', {}):
            player_count = analysis_results['template_info']['player_count']
            filename = f"{self.poker_site}_{player_count}p_analysis_{timestamp}.yml"
        else:
            filename = f"{self.poker_site}_analysis_{timestamp}.yml"
        
        filepath = os.path.join("results", filename)
        
        with open(filepath, 'w') as f:
            yaml.dump(analysis_results, f, default_flow_style=False, 
                     sort_keys=False, allow_unicode=True)
        
        return filepath
    
    def view_last_results(self):
        if not self.extracted_data:
            messagebox.showwarning("Warning", "No analysis results available")
            return
        
        self.results_viewer_class(self.root, self.extracted_data)
    
    def browse_all_results(self):
        results_dir = "results"
        if not os.path.exists(results_dir) or not os.listdir(results_dir):
            messagebox.showinfo("Info", "No saved results found")
            return
        
        self.results_browser_class(self.root, self.results_viewer_class)
            
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
            initialfile=default_name,
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