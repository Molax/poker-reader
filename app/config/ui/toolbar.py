"""
Toolbar Manager

Manages the template configurator toolbar including region selection,
player count controls, and action buttons.

Author: PokerAnalyzer Team
"""

import tkinter as tk
from tkinter import ttk


class ToolbarManager:
    """
    Manages the toolbar UI and user interactions.
    
    Handles:
    - Region selection dropdown
    - Player count selection (YAYA only)
    - Action buttons (save, clear)
    - Current region information display
    """
    
    def __init__(self, parent, poker_site, template_data, region_selector, 
                 on_save_callback, on_clear_callback, on_player_count_changed):
        """
        Initialize toolbar manager.
        
        Args:
            parent: Parent tkinter widget
            poker_site: Poker site identifier
            template_data: TemplateDataManager instance
            region_selector: RegionSelectorManager instance
            on_save_callback: Function to call for template save
            on_clear_callback: Function to call for clearing regions
            on_player_count_changed: Function to call when player count changes
        """
        self.parent = parent
        self.poker_site = poker_site
        self.template_data = template_data
        self.region_selector = region_selector
        self.on_save_callback = on_save_callback
        self.on_clear_callback = on_clear_callback
        self.on_player_count_changed = on_player_count_changed
        
        self.region_update_callback = None
        
        self._setup_ui()
        self.update_display()
        
    def _setup_ui(self):
        """Setup the toolbar UI components."""
        self.toolbar_frame = ttk.Frame(self.parent)
        self.toolbar_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self._setup_title_section()
        self._setup_controls_section()
        self._setup_region_info_section()
        self._setup_instructions_section()
        
    def _setup_title_section(self):
        """Setup the title and player count section."""
        title_frame = ttk.Frame(self.toolbar_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            title_frame, 
            text=f"Template Setup for {self.poker_site.upper()}", 
            font=('Arial', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Player count selector (YAYA only)
        if self.poker_site == 'yaya':
            self._setup_player_count_selector(title_frame)
            
    def _setup_player_count_selector(self, parent):
        """Setup player count selection for YAYA tables."""
        player_frame = ttk.Frame(parent)
        player_frame.pack(side=tk.RIGHT)
        
        ttk.Label(
            player_frame, 
            text="Players at table:", 
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT)
        
        self.player_count_var = tk.StringVar(value=str(self.template_data.player_count))
        player_combo = ttk.Combobox(
            player_frame, 
            textvariable=self.player_count_var,
            values=[str(i) for i in range(2, 12)], 
            width=5, 
            state="readonly"
        )
        player_combo.pack(side=tk.LEFT, padx=(5, 0))
        player_combo.bind('<<ComboboxSelected>>', self._on_player_count_changed_internal)
        
    def _setup_controls_section(self):
        """Setup the main controls section."""
        controls_frame = ttk.Frame(self.toolbar_frame)
        controls_frame.pack(fill=tk.X)
        
        # Region selection frame
        selection_frame = ttk.LabelFrame(
            controls_frame, 
            text="Current Region to Select", 
            padding=10
        )
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._setup_region_selector(selection_frame)
        
        # Action buttons
        self._setup_action_buttons(controls_frame)
        
    def _setup_region_selector(self, parent):
        """Setup region selection dropdown and info."""
        selector_frame = ttk.Frame(parent)
        selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            selector_frame, 
            text="Select region:", 
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT)
        
        # Region dropdown
        self.region_var = tk.StringVar()
        self.region_combo = ttk.Combobox(
            selector_frame, 
            textvariable=self.region_var,
            width=40, 
            state="readonly", 
            font=('Arial', 10)
        )
        self.region_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.region_combo.bind('<<ComboboxSelected>>', self._on_region_selected)
        
        self.update_region_selector()
        
    def _setup_region_info_section(self):
        """Setup the region information display section."""
        # This will be part of the selection frame created above
        selection_frame = self.toolbar_frame.winfo_children()[-2]  # Get selection frame
        
        info_frame = ttk.Frame(selection_frame)
        info_frame.pack(fill=tk.X)
        
        # What to select label
        ttk.Label(
            info_frame, 
            text="📍 What to select:", 
            font=('Arial', 10, 'bold'), 
            foreground='blue'
        ).pack(anchor=tk.W)
        
        # Tooltip text
        self.tooltip_label = ttk.Label(
            info_frame, 
            text="", 
            font=('Arial', 10), 
            foreground='darkgreen',
            wraplength=900
        )
        self.tooltip_label.pack(anchor=tk.W, pady=(2, 5))
        
        # Example label
        ttk.Label(
            info_frame, 
            text="💡 Example text:", 
            font=('Arial', 10, 'bold'), 
            foreground='purple'
        ).pack(anchor=tk.W)
        
        self.example_label = ttk.Label(
            info_frame, 
            text="", 
            font=('Arial', 10, 'italic'), 
            foreground='purple'
        )
        self.example_label.pack(anchor=tk.W)
        
    def _setup_action_buttons(self, parent):
        """Setup action buttons (save, clear)."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame, 
            text="Clear All Regions", 
            command=self.on_clear_callback
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="💾 Save Template", 
            command=self.on_save_callback
        ).pack(side=tk.LEFT)
        
    def _setup_instructions_section(self):
        """Setup instructions display."""
        instruction_frame = ttk.Frame(self.toolbar_frame)
        instruction_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.instruction_label = ttk.Label(
            instruction_frame, 
            text="", 
            font=('Arial', 11, 'bold'), 
            foreground='darkblue'
        )
        self.instruction_label.pack()
        
    def _on_player_count_changed_internal(self, event=None):
        """Handle player count change from UI."""
        new_count = int(self.player_count_var.get())
        old_count = self.template_data.player_count
        
        if new_count != old_count:
            success = self.on_player_count_changed(new_count)
            if not success:
                # Revert if change was cancelled
                self.player_count_var.set(str(old_count))
            else:
                self.update_region_selector()
                self.update_display()
                
    def _on_region_selected(self, event=None):
        """Handle region selection from dropdown."""
        selection = self.region_var.get()
        if selection:
            try:
                index = int(selection.split('.')[0]) - 1
                self.region_selector.set_current_region_index(index)
                self.update_region_info()
                
                if self.region_update_callback:
                    self.region_update_callback()
            except ValueError:
                pass
                
    def set_region_update_callback(self, callback):
        """Set callback for region updates."""
        self.region_update_callback = callback
        
    def update_region_selector(self):
        """Update the region selection dropdown."""
        region_list = self.region_selector.get_region_list_for_display()
        self.region_combo['values'] = region_list
        
        if region_list:
            current_index = self.region_selector.get_current_region_index()
            if current_index < len(region_list):
                self.region_var.set(region_list[current_index])
            else:
                self.region_var.set(region_list[0])
                self.region_selector.set_current_region_index(0)
                
    def update_region_info(self):
        """Update the region information display."""
        current_info = self.region_selector.get_current_region_info()
        
        if current_info:
            self.tooltip_label.config(text=current_info['tooltip'])
            self.example_label.config(text=f'"{current_info["example"]}"')
        else:
            self.tooltip_label.config(text="")
            self.example_label.config(text="")
            
    def update_instructions(self):
        """Update the instructions text."""
        stats = self.template_data.get_completion_stats()
        
        instruction_text = (
            f"🖱️ Instructions: Define {stats['total_regions']} regions "
            f"by clicking and dragging on the image"
        )
        
        if self.poker_site == 'yaya':
            instruction_text += f" ({self.template_data.player_count} players selected)"
            
        if stats['defined_regions'] > 0:
            instruction_text += f" | Progress: {stats['defined_regions']}/{stats['total_regions']}"
            
        self.instruction_label.config(text=instruction_text)
        
    def update_display(self):
        """Update all toolbar components."""
        self.update_region_selector()
        self.update_region_info()
        self.update_instructions()