import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk, ImageDraw
import json
from datetime import datetime

from config.regions_definitions import get_regions_for_site, get_sorted_regions
from config.ui.toolbar import ToolbarManager
from config.ui.canvas import CanvasManager
from config.ui.regions_panel import RegionsPanelManager
from config.core.template_data import TemplateDataManager
from config.core.region_selector import RegionSelectorManager

class TemplateConfigurator:
    def __init__(self, parent, image_path, poker_site, existing_template=None):
        self.parent = parent
        self.image_path = image_path
        self.poker_site = poker_site
        self.template_saved = False
        self.existing_template = existing_template
        
        self.template_data = TemplateDataManager(poker_site)
        self.region_selector = RegionSelectorManager(self.template_data)
        
        self.toolbar = None
        self.canvas_manager = None
        self.regions_panel = None
        
        self._setup_window()
        self._initialize_ui_components()
        self._load_image()
        
        if existing_template:
            self._load_existing_template()
        
    def _setup_window(self):
        self.window = tk.Toplevel(self.parent)
        window_title = f"Template Configurator - {self.poker_site.upper()}"
        if self.existing_template:
            window_title += " (Editing)"
        self.window.title(window_title)
        self.window.geometry("1500x950")
        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
    def _initialize_ui_components(self):
        self.toolbar = ToolbarManager(
            self.window, 
            self.poker_site,
            self.template_data,
            self.region_selector,
            on_save_callback=self.save_template,
            on_clear_callback=self.clear_regions,
            on_player_count_changed=self._on_player_count_changed
        )
        
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.canvas_manager = CanvasManager(
            main_frame,
            on_region_selected=self._on_region_drawn
        )
        
        self.regions_panel = RegionsPanelManager(
            main_frame,
            self.template_data,
            self.region_selector,
            on_region_jump=self._on_region_jump,
            on_region_delete=self._on_region_delete
        )
        
        self._connect_components()
        
    def _connect_components(self):
        self.toolbar.set_region_update_callback(self._update_all_components)
        self.template_data.set_update_callback(self._update_all_components)
        
    def _load_image(self):
        try:
            image = Image.open(self.image_path)
            self.canvas_manager.set_image(image)
            self.template_data.set_image_size(image.size)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.window.destroy()
            
    def _load_existing_template(self):
        try:
            if self.poker_site == 'yaya' and 'player_count' in self.existing_template:
                player_count = self.existing_template['player_count']
                self.template_data.set_player_count(player_count)
            
            regions = self.existing_template.get('regions', {})
            for region_key, region_data in regions.items():
                display_name = region_data.get('display_name', region_key)
                coordinates = region_data.get('coordinates', {})
                self.template_data.add_region(region_key, display_name, coordinates)
            
            self.region_selector.update_regions()
            self._update_all_components()
            
            messagebox.showinfo(
                "Template Loaded", 
                f"Loaded existing template with {len(regions)} regions.\n"
                f"You can now edit the regions or add new ones."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load existing template: {str(e)}")
            
    def _on_player_count_changed(self, new_count):
        if self.template_data.has_regions():
            if not messagebox.askyesno(
                "Change Player Count", 
                f"Changing player count will clear all regions. Continue?"
            ):
                return False
                
        self.template_data.set_player_count(new_count)
        self.region_selector.update_regions()
        self._update_all_components()
        
        messagebox.showinfo(
            "Player Count Updated", 
            f"Template updated for {new_count} players.\n"
            f"Total regions to define: {len(self.template_data.get_region_definitions())}"
        )
        return True
        
    def _on_region_drawn(self, coordinates):
        current_region = self.region_selector.get_current_region()
        if current_region:
            region_key, region_data = current_region
            self.template_data.add_region(region_key, region_data['display_name'], coordinates)
            self.region_selector.advance_to_next_region()
            self._update_all_components()
            
    def _on_region_jump(self, region_index):
        self.region_selector.set_current_region_index(region_index)
        self.toolbar.update_region_selector()
        
    def _on_region_delete(self, region_key):
        self.template_data.remove_region(region_key)
        self._update_all_components()
        
    def _update_all_components(self):
        self.toolbar.update_display()
        self.canvas_manager.redraw_regions(self.template_data.get_regions())
        self.regions_panel.update_display()
        
    def clear_regions(self):
        if messagebox.askyesno("Clear All", "Delete all defined regions?"):
            self.template_data.clear_regions()
            self._update_all_components()
            
    def save_template(self):
        if not self.template_data.has_regions():
            messagebox.showwarning("Warning", "Please define at least one region")
            return
            
        try:
            template_data = self.template_data.get_template_data()
            filepath = self._get_template_filepath()
            
            with open(filepath, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            self._save_template_preview()
            
            self.template_saved = True
            self._show_save_success_message(filepath)
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {str(e)}")
            
    def _get_template_filepath(self):
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            
        if self.poker_site == 'yaya':
            filename = f"{self.poker_site}_{self.template_data.player_count}p_template.json"
        else:
            filename = f"{self.poker_site}_template.json"
            
        return os.path.join(templates_dir, filename)
        
    def _save_template_preview(self):
        try:
            preview_dir = os.path.join("templates", "previews")
            if not os.path.exists(preview_dir):
                os.makedirs(preview_dir)
            
            image = Image.open(self.image_path).copy()
            draw = ImageDraw.Draw(image)
            
            regions = self.template_data.get_regions()
            colors = [
                'red', 'blue', 'green', 'orange', 'purple', 
                'brown', 'pink', 'cyan', 'magenta', 'yellow'
            ]
            
            color_index = 0
            for region_key, region_data in regions.items():
                coords = region_data['coordinates']
                x1, y1 = coords['x'], coords['y']
                x2, y2 = x1 + coords['width'], y1 + coords['height']
                
                color = colors[color_index % len(colors)]
                
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                
                display_name = region_data.get('display_name', region_key)
                draw.text((x1 + 5, y1 + 5), display_name, fill=color)
                
                color_index += 1
            
            if self.poker_site == 'yaya':
                preview_filename = f"{self.poker_site}_{self.template_data.player_count}p_preview.png"
            else:
                preview_filename = f"{self.poker_site}_preview.png"
                
            preview_path = os.path.join(preview_dir, preview_filename)
            image.save(preview_path)
            
        except Exception as e:
            print(f"Warning: Failed to save template preview: {str(e)}")
        
    def _show_save_success_message(self, filepath):
        total_regions = len(self.template_data.get_region_definitions())
        defined_regions = len(self.template_data.get_regions())
        
        message = (
            f"Template saved successfully!\n\n"
            f"File: {os.path.basename(filepath)}\n"
            f"Site: {self.poker_site.upper()}\n"
        )
        
        if self.poker_site == 'yaya':
            message += f"Players: {self.template_data.player_count}\n"
            
        message += (
            f"Regions defined: {defined_regions}/{total_regions}\n"
            f"Coverage: {(defined_regions/total_regions)*100:.1f}%\n\n"
            f"Preview image saved to templates/previews/"
        )
        
        messagebox.showinfo("Template Saved!", message)
        
    def _on_window_close(self):
        if self.template_data.has_regions() and not self.template_saved:
            if messagebox.askyesno(
                "Unsaved Changes", 
                "You have unsaved regions. Close without saving?"
            ):
                self.window.destroy()
        else:
            self.window.destroy()