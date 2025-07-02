"""
Canvas Manager

Handles image display and region selection drawing on the canvas.

Author: PokerAnalyzer Team
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class CanvasManager:
    """
    Manages canvas operations for template configuration.
    
    Handles:
    - Image display and scaling
    - Region selection drawing
    - Mouse interaction for region definition
    - Visual feedback for defined regions
    """
    
    def __init__(self, parent, on_region_selected):
        """
        Initialize canvas manager.
        
        Args:
            parent: Parent tkinter widget
            on_region_selected: Callback function for new region selection
        """
        self.parent = parent
        self.on_region_selected = on_region_selected
        
        self.current_image = None
        self.display_image = None
        self.photo = None
        self.scale_factor = 1.0
        
        # Drawing state
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the canvas UI."""
        canvas_frame = ttk.LabelFrame(
            self.parent, 
            text="Poker Image - Click and drag to select regions", 
            padding=10
        )
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self._start_selection)
        self.canvas.bind("<B1-Motion>", self._update_selection)
        self.canvas.bind("<ButtonRelease-1>", self._end_selection)
        
    def set_image(self, image):
        """
        Set and display the poker screenshot image.
        
        Args:
            image: PIL Image object
        """
        self.current_image = image
        self._display_image()
        
    def _display_image(self):
        """Display the image on canvas with appropriate scaling."""
        if not self.current_image:
            return
            
        # Get canvas dimensions (with fallback defaults)
        canvas_width = max(self.canvas.winfo_width(), 1000)
        canvas_height = max(self.canvas.winfo_height(), 750)
        
        # Create display copy
        self.display_image = self.current_image.copy()
        
        # Calculate scaling
        img_width, img_height = self.display_image.size
        self.scale_factor = min(
            canvas_width / img_width, 
            canvas_height / img_height, 
            1.0
        )
        
        # Resize if needed
        if self.scale_factor < 1.0:
            new_width = int(img_width * self.scale_factor)
            new_height = int(img_height * self.scale_factor)
            self.display_image = self.display_image.resize(
                (new_width, new_height), 
                Image.Resampling.LANCZOS
            )
        
        # Create PhotoImage and display
        self.photo = ImageTk.PhotoImage(self.display_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
    def _start_selection(self, event):
        """Start region selection on mouse down."""
        self.start_x = event.x
        self.start_y = event.y
        self.drawing = True
        
    def _update_selection(self, event):
        """Update selection rectangle during mouse drag."""
        if not self.drawing:
            return
            
        # Remove previous rectangle
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            
        # Draw new rectangle
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=3, fill='', stipple='gray25'
        )
        
    def _end_selection(self, event):
        """Complete region selection on mouse release."""
        if not self.drawing:
            return
            
        self.drawing = False
        
        # Check for minimum selection size
        if abs(event.x - self.start_x) < 10 or abs(event.y - self.start_y) < 10:
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None
            return
            
        # Calculate coordinates
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        
        # Convert to original image coordinates
        original_coords = self._canvas_to_original_coords(x1, y1, x2, y2)
        
        # Notify parent of new region selection
        self.on_region_selected(original_coords)
        
        # Clean up selection rectangle
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            
    def _canvas_to_original_coords(self, x1, y1, x2, y2):
        """
        Convert canvas coordinates to original image coordinates.
        
        Args:
            x1, y1, x2, y2: Canvas coordinates
            
        Returns:
            dict: Original image coordinates
        """
        orig_x1 = int(x1 / self.scale_factor)
        orig_y1 = int(y1 / self.scale_factor)
        orig_x2 = int(x2 / self.scale_factor)
        orig_y2 = int(y2 / self.scale_factor)
        
        return {
            'x': orig_x1,
            'y': orig_y1,
            'width': orig_x2 - orig_x1,
            'height': orig_y2 - orig_y1
        }
        
    def _original_to_canvas_coords(self, coords):
        """
        Convert original image coordinates to canvas coordinates.
        
        Args:
            coords: Dictionary with x, y, width, height
            
        Returns:
            tuple: Canvas coordinates (x1, y1, x2, y2)
        """
        x1 = coords['x'] * self.scale_factor
        y1 = coords['y'] * self.scale_factor
        x2 = (coords['x'] + coords['width']) * self.scale_factor
        y2 = (coords['y'] + coords['height']) * self.scale_factor
        return x1, y1, x2, y2
        
    def redraw_regions(self, regions):
        """
        Redraw all defined regions on the canvas.
        
        Args:
            regions: Dictionary of region definitions
        """
        # Remove existing region overlays
        self.canvas.delete("region")
        
        if not regions:
            return
            
        # Color palette for regions
        colors = [
            'red', 'blue', 'green', 'orange', 'purple', 
            'brown', 'pink', 'cyan', 'magenta', 'yellow'
        ]
        color_index = 0
        
        for region_key, region in regions.items():
            coords = region['coordinates']
            x1, y1, x2, y2 = self._original_to_canvas_coords(coords)
            
            color = colors[color_index % len(colors)]
            
            # Draw region rectangle
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=color, width=2, tags="region"
            )
            
            # Draw region label
            self.canvas.create_text(
                x1 + 5, y1 + 5, 
                text=region['display_name'], 
                anchor=tk.NW,
                fill=color, 
                font=('Arial', 9, 'bold'), 
                tags="region"
            )
            
            color_index += 1
            
    def clear_regions(self):
        """Clear all region overlays from canvas."""
        self.canvas.delete("region")
        
    def highlight_region(self, region_key, regions):
        """
        Highlight a specific region on the canvas.
        
        Args:
            region_key: Key of region to highlight
            regions: Dictionary of all regions
        """
        if region_key not in regions:
            return
            
        coords = regions[region_key]['coordinates']
        x1, y1, x2, y2 = self._original_to_canvas_coords(coords)
        
        # Create highlight effect
        self.canvas.create_rectangle(
            x1-2, y1-2, x2+2, y2+2,
            outline='yellow', width=4, tags="highlight"
        )
        
        # Remove highlight after delay
        self.canvas.after(2000, lambda: self.canvas.delete("highlight"))