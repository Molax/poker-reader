"""
Template Configurator Main Controller

This module provides the main interface for configuring poker site templates.
It orchestrates the UI components and handles template creation workflow.

Author: PokerAnalyzer Team
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import json
from datetime import datetime

from config.regions_definitions import get_regions_for_site, get_sorted_regions
from config.ui.toolbar import ToolbarManager
from config.ui.canvas import CanvasManager
from config.ui.regions_panel import RegionsPanelManager
from config.core.template_data import TemplateDataManager
from config.core.region_selector import RegionSelectorManager


class TemplateConfigurator:
    """
    Main template configurator window controller.
    
    Manages the overall template configuration workflow including:
    - UI component coordination
    - Template data management
    - User interaction handling
    - Template saving/loading
    """
    
    def __init__(self, parent, image_path, poker_site):
        """
        Initialize the template configurator.
        
        Args:
            parent: Parent tkinter window
            image_path: Path to poker screenshot image
            poker_site: Poker site identifier ('yaya', 'pokerstars', etc.)
        """
        self.parent = parent
        self.image_path = image_path
        self.poker_site = poker_site
        self.template_saved = False
        
        # Initialize core managers
        self.template_data = TemplateDataManager(poker_site)
        self.region_selector = RegionSelectorManager(self.template_data)
        
        # UI will be initialized after window setup
        self.toolbar = None
        self.canvas_manager = None
        self.regions_panel = None
        
        self._setup_window()
        self._initialize_ui_components()
        self._load_image()
        
    def _setup_window(self):
        """Configure the main window properties."""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Template Configurator - {self.poker_site.upper()}")
        self.window.geometry("1500x950")
        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
    def _initialize_ui_components(self):
        """Initialize and setup all UI component managers."""
        # Initialize toolbar
        self.toolbar = ToolbarManager(
            self.window, 
            self.poker_site,
            self.template_data,
            self.region_selector,
            on_save_callback=self.save_template,
            on_clear_callback=self.clear_regions,
            on_player_count_changed=self._on_player_count_changed
        )
        
        # Setup main content area
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Initialize canvas manager
        self.canvas_manager = CanvasManager(
            main_frame,
            on_region_selected=self._on_region_drawn
        )
        
        # Initialize regions panel
        self.regions_panel = RegionsPanelManager(
            main_frame,
            self.template_data,
            self.region_selector,
            on_region_jump=self._on_region_jump,
            on_region_delete=self._on_region_delete
        )
        
        # Connect components
        self._connect_components()
        
    def _connect_components(self):
        """Connect UI components for coordinated updates."""
        self.toolbar.set_region_update_callback(self._update_all_components)
        self.template_data.set_update_callback(self._update_all_components)
        
    def _load_image(self):
        """Load and display the poker screenshot image."""
        try:
            image = Image.open(self.image_path)
            self.canvas_manager.set_image(image)
            self.template_data.set_image_size(image.size)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.window.destroy()
            
    def _on_player_count_changed(self, new_count):
        """
        Handle player count changes for YAYA tables.
        
        Args:
            new_count: New number of players (2-11)
        """
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
        """
        Handle new region selection from canvas.
        
        Args:
            coordinates: Dictionary with x, y, width, height
        """
        current_region = self.region_selector.get_current_region()
        if current_region:
            region_key, region_data = current_region
            self.template_data.add_region(region_key, region_data['display_name'], coordinates)
            self.region_selector.advance_to_next_region()
            self._update_all_components()
            
    def _on_region_jump(self, region_index):
        """
        Handle jumping to a specific region in the selector.
        
        Args:
            region_index: Index of region to jump to
        """
        self.region_selector.set_current_region_index(region_index)
        self.toolbar.update_region_selector()
        
    def _on_region_delete(self, region_key):
        """
        Handle region deletion request.
        
        Args:
            region_key: Key of region to delete
        """
        self.template_data.remove_region(region_key)
        self._update_all_components()
        
    def _update_all_components(self):
        """Update all UI components to reflect current state."""
        self.toolbar.update_display()
        self.canvas_manager.redraw_regions(self.template_data.get_regions())
        self.regions_panel.update_display()
        
    def clear_regions(self):
        """Clear all defined regions after confirmation."""
        if messagebox.askyesno("Clear All", "Delete all defined regions?"):
            self.template_data.clear_regions()
            self._update_all_components()
            
    def save_template(self):
        """Save the current template configuration."""
        if not self.template_data.has_regions():
            messagebox.showwarning("Warning", "Please define at least one region")
            return
            
        try:
            template_data = self.template_data.get_template_data()
            filepath = self._get_template_filepath()
            
            with open(filepath, 'w') as f:
                json.dump(template_data, f, indent=2)
                
            self.template_saved = True
            self._show_save_success_message(filepath)
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {str(e)}")
            
    def _get_template_filepath(self):
        """Generate the template file path."""
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            
        if self.poker_site == 'yaya':
            filename = f"{self.poker_site}_{self.template_data.player_count}p_template.json"
        else:
            filename = f"{self.poker_site}_template.json"
            
        return os.path.join(templates_dir, filename)
        
    def _show_save_success_message(self, filepath):
        """Show template save success message with details."""
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
            f"Coverage: {(defined_regions/total_regions)*100:.1f}%"
        )
        
        messagebox.showinfo("Template Saved!", message)
        
    def _on_window_close(self):
        """Handle window close event."""
        if self.template_data.has_regions() and not self.template_saved:
            if messagebox.askyesno(
                "Unsaved Changes", 
                "You have unsaved regions. Close without saving?"
            ):
                self.window.destroy()
        else:
            self.window.destroy()