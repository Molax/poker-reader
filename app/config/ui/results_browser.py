import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import yaml
from datetime import datetime

class ResultsBrowser:
    def __init__(self, parent, results_viewer_class):
        self.parent = parent
        self.results_viewer_class = results_viewer_class
        
        self.browser = tk.Toplevel(parent)
        self.browser.title("Results Browser")
        self.browser.geometry("800x600")
        
        self.setup_ui()
        self.load_results()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.browser)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text="Saved Analysis Results", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('File', 'Site', 'Date', 'Success Rate', 'Avg Confidence')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('File', width=200)
        self.tree.column('Site', width=80)
        self.tree.column('Date', width=150)
        self.tree.column('Success Rate', width=100)
        self.tree.column('Avg Confidence', width=120)
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.bind('<Double-1>', self.on_double_click)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(button_frame, text="Double-click to view detailed results", 
                 font=('Arial', 10), foreground='gray').pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Refresh", command=self.load_results).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Close", command=self.browser.destroy).pack(side=tk.RIGHT)
    
    def load_results(self):
        results_dir = "results"
        if not os.path.exists(results_dir):
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        results_files = []
        for filename in os.listdir(results_dir):
            if filename.endswith(('.yml', '.yaml', '.json')):
                try:
                    filepath = os.path.join(results_dir, filename)
                    with open(filepath, 'r') as f:
                        if filename.endswith('.json'):
                            data = json.load(f)
                        else:
                            data = yaml.safe_load(f)
                    
                    summary = data.get('analysis_summary', {})
                    successful = summary.get('successful_extractions', 0)
                    failed = summary.get('failed_extractions', 0)
                    total = successful + failed
                    success_rate = f"{(successful/total*100) if total > 0 else 0:.1f}%"
                    avg_confidence = f"{summary.get('average_confidence', 0):.1f}%"
                    
                    timestamp = data.get('timestamp', '')
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            date_str = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            date_str = timestamp
                    else:
                        date_str = "Unknown"
                    
                    results_files.append((filename, data, success_rate, avg_confidence, date_str))
                    
                except Exception as e:
                    continue
        
        results_files.sort(key=lambda x: x[4], reverse=True)
        
        for filename, data, success_rate, avg_confidence, date_str in results_files:
            self.tree.insert('', tk.END, values=(
                filename,
                data.get('site', 'Unknown').upper(),
                date_str,
                success_rate,
                avg_confidence
            ))
    
    def on_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            filename = item['values'][0]
            
            try:
                filepath = os.path.join("results", filename)
                with open(filepath, 'r') as f:
                    if filename.endswith('.json'):
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f)
                
                self.results_viewer_class(self.browser, data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load results: {str(e)}")