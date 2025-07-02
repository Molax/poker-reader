import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import json

class TemplatePreviewViewer:
    def __init__(self, parent, templates_dict):
        self.parent = parent
        self.templates = templates_dict
        
        self.window = tk.Toplevel(parent)
        self.window.title("Template Previews")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        self.setup_ui()
        self.load_previews()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Saved Template Previews", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        close_btn = ttk.Button(
            header_frame, 
            text="Close", 
            command=self.window.destroy
        )
        close_btn.pack(side=tk.RIGHT)
        
        self.preview_frame = ttk.Frame(main_frame)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas_frame = ttk.Frame(self.preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar_v = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_h = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.content_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(0, 0, anchor=tk.NW, window=self.content_frame)
        
        self.content_frame.bind('<Configure>', self._on_frame_configure)
        
    def load_previews(self):
        preview_dir = os.path.join("templates", "previews")
        
        if not os.path.exists(preview_dir):
            no_preview_label = ttk.Label(
                self.content_frame, 
                text="No template previews found.\nCreate templates to see previews here.",
                font=('Arial', 12),
                justify=tk.CENTER
            )
            no_preview_label.pack(expand=True, pady=50)
            return
        
        row = 0
        col = 0
        max_cols = 2
        
        for site, template_data in self.templates.items():
            if site == 'yaya' and 'player_count' in template_data:
                preview_filename = f"{site}_{template_data['player_count']}p_preview.png"
            else:
                preview_filename = f"{site}_preview.png"
                
            preview_path = os.path.join(preview_dir, preview_filename)
            
            if os.path.exists(preview_path):
                self._create_preview_card(row, col, site, template_data, preview_path)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        if row == 0 and col == 0:
            no_preview_label = ttk.Label(
                self.content_frame, 
                text="No preview images found.\nRe-save templates to generate previews.",
                font=('Arial', 12),
                justify=tk.CENTER
            )
            no_preview_label.pack(expand=True, pady=50)
            
    def _create_preview_card(self, row, col, site, template_data, preview_path):
        card_frame = ttk.LabelFrame(
            self.content_frame, 
            text=f"{site.upper()} Template",
            padding=10
        )
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        try:
            image = Image.open(preview_path)
            image.thumbnail((350, 250), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            image_label = ttk.Label(card_frame, image=photo)
            image_label.image = photo
            image_label.pack()
            
            info_frame = ttk.Frame(card_frame)
            info_frame.pack(fill=tk.X, pady=(10, 0))
            
            regions_count = len(template_data.get('regions', {}))
            created_date = template_data.get('created', 'Unknown')
            
            info_text = f"Regions: {regions_count}"
            if site == 'yaya' and 'player_count' in template_data:
                info_text += f" | Players: {template_data['player_count']}"
            
            info_label = ttk.Label(info_frame, text=info_text, font=('Arial', 10))
            info_label.pack()
            
            if created_date != 'Unknown':
                try:
                    from datetime import datetime
                    created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    created_str = created_dt.strftime("%Y-%m-%d %H:%M")
                    date_label = ttk.Label(info_frame, text=f"Created: {created_str}", font=('Arial', 9))
                    date_label.pack()
                except:
                    pass
                    
        except Exception as e:
            error_label = ttk.Label(
                card_frame, 
                text=f"Error loading preview:\n{str(e)}", 
                foreground='red'
            )
            error_label.pack()
            
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))