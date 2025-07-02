"""
Regions Panel Manager

Manages the right-side panel showing defined regions and help information.

Author: PokerAnalyzer Team
"""

import tkinter as tk
from tkinter import ttk, messagebox


class RegionsPanelManager:
    """
    Manages the regions list and help panel UI.
    
    Handles:
    - Region list display with completion status
    - Region deletion and navigation
    - Help text display for current region
    - Progress tracking
    """
    
    def __init__(self, parent, template_data, region_selector, 
                 on_region_jump, on_region_delete):
        """
        Initialize regions panel manager.
        
        Args:
            parent: Parent tkinter widget
            template_data: TemplateDataManager instance
            region_selector: RegionSelectorManager instance
            on_region_jump: Callback for jumping to region
            on_region_delete: Callback for deleting region
        """
        self.parent = parent
        self.template_data = template_data
        self.region_selector = region_selector
        self.on_region_jump = on_region_jump
        self.on_region_delete = on_region_delete
        
        self._setup_ui()
        self.update_display()
        
    def _setup_ui(self):
        """Setup the regions panel UI."""
        self.right_panel = ttk.Frame(self.parent)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self._setup_regions_list()
        self._setup_help_panel()
        
    def _setup_regions_list(self):
        """Setup the regions list treeview."""
        regions_frame = ttk.LabelFrame(
            self.right_panel, 
            text="Defined Regions", 
            padding=10, 
            width=380
        )
        regions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        regions_frame.pack_propagate(False)
        
        # Create treeview
        self.regions_tree = ttk.Treeview(
            regions_frame, 
            columns=('status', 'type'), 
            show='tree headings', 
            height=15
        )
        
        # Configure columns
        self.regions_tree.heading('#0', text='Region')
        self.regions_tree.heading('status', text='Status')
        self.regions_tree.heading('type', text='Type')
        
        self.regions_tree.column('#0', width=200)
        self.regions_tree.column('status', width=80)
        self.regions_tree.column('type', width=80)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(
            regions_frame, 
            orient=tk.VERTICAL, 
            command=self.regions_tree.yview
        )
        self.regions_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack treeview and scrollbar
        self.regions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add control buttons
        self._setup_list_controls(regions_frame)
        
        # Bind events
        self.regions_tree.bind('<Double-1>', self._on_region_double_click)
        
    def _setup_list_controls(self, parent):
        """Setup control buttons for the regions list."""
        list_controls = ttk.Frame(parent)
        list_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            list_controls, 
            text="Delete Selected", 
            command=self._delete_selected_region
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            list_controls, 
            text="Jump to Region", 
            command=self._jump_to_selected_region
        ).pack(fill=tk.X)
        
    def _setup_help_panel(self):
        """Setup the help and information panel."""
        help_frame = ttk.LabelFrame(
            self.right_panel, 
            text="Region Information", 
            padding=10, 
            width=380
        )
        help_frame.pack(fill=tk.X)
        help_frame.pack_propagate(False)
        
        # Player count info (for YAYA)
        if hasattr(self.template_data, 'player_count') and self.template_data.player_count:
            self.player_info_label = ttk.Label(
                help_frame, 
                text=f"Table Configuration: {self.template_data.player_count} players",
                font=('Arial', 10, 'bold'), 
                foreground='blue'
            )
            self.player_info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Progress info
        self.progress_label = ttk.Label(
            help_frame,
            text="",
            font=('Arial', 10, 'bold'),
            foreground='darkgreen'
        )
        self.progress_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Help text area
        self.help_text = tk.Text(
            help_frame, 
            height=12, 
            width=45, 
            wrap=tk.WORD, 
            font=('Arial', 9), 
            state=tk.DISABLED
        )
        self.help_text.pack(fill=tk.BOTH, expand=True)
        
    def _on_region_double_click(self, event):
        """Handle double-click on region list item."""
        self._jump_to_selected_region()
        
    def _delete_selected_region(self):
        """Delete the selected region after confirmation."""
        selection = self.regions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a region to delete")
            return
            
        item = selection[0]
        region_text = self.regions_tree.item(item, 'text')
        
        # Extract region key from display text
        region_key = self._extract_region_key_from_display(region_text)
        if not region_key:
            return
            
        # Confirm deletion
        if messagebox.askyesno(
            "Delete Region", 
            f"Delete region '{region_key}'?"
        ):
            self.on_region_delete(region_key)
            
    def _jump_to_selected_region(self):
        """Jump to the selected region in the selector."""
        selection = self.regions_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a region from the list")
            return
            
        item = selection[0]
        region_text = self.regions_tree.item(item, 'text')
        
        # Find region index
        region_index = self._find_region_index_from_display(region_text)
        if region_index >= 0:
            self.on_region_jump(region_index)
            
    def _extract_region_key_from_display(self, display_text):
        """Extract region key from display text."""
        sorted_regions = self.template_data.get_sorted_regions()
        
        for region_key, region_data in sorted_regions:
            if region_data['display_name'] in display_text:
                return region_key
        return None
        
    def _find_region_index_from_display(self, display_text):
        """Find region index from display text."""
        try:
            # Extract number from "1. Region Name" format
            index = int(display_text.split('.')[0]) - 1
            return index
        except (ValueError, IndexError):
            return -1
            
    def populate_regions_tree(self):
        """Populate the regions tree with current data."""
        # Clear existing items
        self.regions_tree.delete(*self.regions_tree.get_children())
        
        sorted_regions = self.template_data.get_sorted_regions()
        regions = self.template_data.get_regions()
        
        for i, (region_key, region_data) in enumerate(sorted_regions):
            display_name = f"{i+1}. {region_data['display_name']}"
            is_completed = region_key in regions
            status = "✅ Done" if is_completed else "⏳ Pending"
            region_type = "Required" if region_data.get('required', False) else "Optional"
            
            # Insert item
            item = self.regions_tree.insert(
                '', tk.END, 
                text=display_name, 
                values=(status, region_type)
            )
            
            # Apply styling based on completion
            if is_completed:
                self.regions_tree.set(item, 'status', '✅ Done')
            else:
                self.regions_tree.set(item, 'status', '⏳ Pending')
                
    def update_help_text(self):
        """Update the help text with current region information."""
        current_info = self.region_selector.get_current_region_info()
        
        if current_info:
            help_content = f"Region: {current_info['data']['display_name']}\n\n"
            help_content += f"Description:\n{current_info['data']['description']}\n\n"
            help_content += f"What to select:\n{current_info['data']['tooltip']}\n\n"
            help_content += f"Example text:\n'{current_info['data']['example']}'\n\n"
            
            if current_info['data'].get('required', False):
                help_content += "🔴 Required region\n"
            else:
                help_content += "🟡 Optional region\n"
                
            if 'position' in current_info['data']:
                help_content += f"Position: {current_info['data']['position']}\n"
                
            if current_info['completed']:
                help_content += "\n✅ This region is already defined"
            else:
                help_content += "\n⏳ This region needs to be defined"
        else:
            help_content = "No region selected"
            
        # Update help text
        self.help_text.config(state=tk.NORMAL)
        self.help_text.delete(1.0, tk.END)
        self.help_text.insert(1.0, help_content)
        self.help_text.config(state=tk.DISABLED)
        
    def update_progress_info(self):
        """Update the progress information display."""
        progress = self.region_selector.get_progress_summary()
        
        progress_text = (
            f"Progress: {progress['completed_regions']}/{progress['total_regions']} "
            f"({progress['completion_percentage']:.1f}%)"
        )
        
        if progress['is_complete']:
            progress_text += " ✅ Complete!"
            
        self.progress_label.config(text=progress_text)
        
        # Update player count if applicable
        if hasattr(self, 'player_info_label') and hasattr(self.template_data, 'player_count'):
            if self.template_data.player_count:
                self.player_info_label.config(
                    text=f"Table Configuration: {self.template_data.player_count} players"
                )
                
    def update_display(self):
        """Update all panel components."""
        self.populate_regions_tree()
        self.update_help_text()
        self.update_progress_info()