import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import json
from datetime import datetime

from config.region_definitions import get_regions_for_site, get_sorted_regions

class TemplateConfigurator:
    def __init__(self, parent, image_path, poker_site):
        self.template_saved = False
        self.image_path = image_path
        self.poker_site = poker_site
        self.regions = {}
        self.current_image = None
        self.display_image = None
        self.photo = None
        self.scale_factor = 1.0
        
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        
        self.region_definitions = get_regions_for_site(poker_site)
        self.sorted_regions = get_sorted_regions(poker_site)
        
        self.setup_window(parent)
        self.load_image()
        
    def setup_window(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Template Configurator - {self.poker_site.upper()}")
        self.window.geometry("1400x900")
        self.window.resizable(True, True)
        
        self.setup_toolbar()
        self.setup_main_area()
        
    def setup_toolbar(self):
        toolbar_frame = ttk.Frame(self.window)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_frame = ttk.Frame(toolbar_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text=f"Template Setup for {self.poker_site.upper()}", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text=f"Define {len(self.region_definitions)} regions by clicking and dragging", 
                 foreground='blue').pack(side=tk.RIGHT)
        
        controls_frame = ttk.Frame(toolbar_frame)
        controls_frame.pack(fill=tk.X)
        
        # Region selection area
        selection_frame = ttk.LabelFrame(controls_frame, text="Current Region to Select", padding=10)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Region selector
        selector_frame = ttk.Frame(selection_frame)
        selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(selector_frame, text="Select region:", 
                 font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        
        region_list = [f"{i+1}. {data['display_name']}" for i, (key, data) in enumerate(self.sorted_regions)]
        
        self.region_var = tk.StringVar()
        if self.sorted_regions:
            self.region_var.set(region_list[0])
            
        self.region_combo = ttk.Combobox(selector_frame, textvariable=self.region_var,
                                        values=region_list, width=35, 
                                        state="readonly", font=('Arial', 10))
        self.region_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.region_combo.bind('<<ComboboxSelected>>', self.on_region_selected)
        
        # Current region info display
        info_frame = ttk.Frame(selection_frame)
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text="📍 What to select:", 
                 font=('Arial', 10, 'bold'), foreground='blue').pack(anchor=tk.W)
        
        self.tooltip_label = ttk.Label(info_frame, text="", 
                                      font=('Arial', 10), foreground='darkgreen',
                                      wraplength=800)
        self.tooltip_label.pack(anchor=tk.W, pady=(2, 5))
        
        ttk.Label(info_frame, text="💡 Example text:", 
                 font=('Arial', 10, 'bold'), foreground='purple').pack(anchor=tk.W)
        
        self.example_label = ttk.Label(info_frame, text="", 
                                      font=('Arial', 10, 'italic'), foreground='purple')
        self.example_label.pack(anchor=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Clear All Regions", 
                  command=self.clear_regions).pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = ttk.Button(button_frame, text="💾 Save Template", 
                             command=self.save_template)
        save_btn.pack(side=tk.LEFT)
        
        # Instructions
        instruction_frame = ttk.Frame(controls_frame)
        instruction_frame.pack(fill=tk.X, pady=(10, 0))
        
        instruction_text = "🖱️ Instructions: Read the blue text above, then click and drag on the image to select that region"
        ttk.Label(instruction_frame, text=instruction_text, 
                 font=('Arial', 11, 'bold'), foreground='darkblue').pack()
        
        self.update_current_region_info()
        
    def setup_main_area(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        canvas_frame = ttk.LabelFrame(main_frame, text="Poker Image - Click and drag to select regions", 
                                     padding=10)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self.setup_regions_list(right_panel)
        self.setup_help_panel(right_panel)
        
    def setup_regions_list(self, parent):
        regions_frame = ttk.LabelFrame(parent, text="Defined Regions", padding=10, width=350)
        regions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        regions_frame.pack_propagate(False)
        
        self.regions_tree = ttk.Treeview(regions_frame, columns=('status',), show='tree headings', height=15)
        self.regions_tree.heading('#0', text='Region')
        self.regions_tree.heading('status', text='Status')
        
        self.regions_tree.column('#0', width=250)
        self.regions_tree.column('status', width=80)
        
        tree_scroll = ttk.Scrollbar(regions_frame, orient=tk.VERTICAL, command=self.regions_tree.yview)
        self.regions_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.regions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        list_controls = ttk.Frame(regions_frame)
        list_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(list_controls, text="Delete Selected", 
                  command=self.delete_selected_region).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(list_controls, text="Jump to Region", 
                  command=self.jump_to_region).pack(fill=tk.X)
        
        self.populate_regions_tree()
        
    def setup_help_panel(self, parent):
        help_frame = ttk.LabelFrame(parent, text="Current Region Help", padding=10, width=350)
        help_frame.pack(fill=tk.X)
        help_frame.pack_propagate(False)
        
        self.help_text = tk.Text(help_frame, height=8, width=40, wrap=tk.WORD, 
                                font=('Arial', 9), state=tk.DISABLED)
        self.help_text.pack(fill=tk.BOTH, expand=True)
        
    def on_region_selected(self, event=None):
        self.update_current_region_info()
        self.update_help_text()
        
    def update_current_region_info(self):
        selection = self.region_var.get()
        if not selection:
            return
            
        try:
            index = int(selection.split('.')[0]) - 1
            if 0 <= index < len(self.sorted_regions):
                region_key, region_data = self.sorted_regions[index]
                
                # Update tooltip and example labels
                tooltip_text = region_data.get('tooltip', '')
                example_text = region_data.get('example', '')
                
                self.tooltip_label.config(text=tooltip_text)
                self.example_label.config(text=f'"{example_text}"')
                
                # Update status in the region list
                is_completed = region_key in self.regions
                
                # Find the corresponding item in the tree and update it
                for item in self.regions_tree.get_children():
                    item_text = self.regions_tree.item(item, 'text')
                    if region_data['display_name'] in item_text:
                        self.regions_tree.set(item, 'status', "✅ Done" if is_completed else "⏳ Pending")
                        break
                        
        except Exception as e:
            print(f"Error updating region info: {e}")
            
    def update_help_text(self):
        selection = self.region_var.get()
        if not selection:
            return
            
        try:
            index = int(selection.split('.')[0]) - 1
            if 0 <= index < len(self.sorted_regions):
                region_key, region_data = self.sorted_regions[index]
                
                help_content = f"Region: {region_data['display_name']}\n\n"
                help_content += f"Description:\n{region_data['description']}\n\n"
                help_content += f"What to select:\n{region_data['tooltip']}\n\n"
                help_content += f"Example text:\n'{region_data['example']}'"
                
                self.help_text.config(state=tk.NORMAL)
                self.help_text.delete(1.0, tk.END)
                self.help_text.insert(1.0, help_content)
                self.help_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error updating help text: {e}")
            
    def populate_regions_tree(self):
        self.regions_tree.delete(*self.regions_tree.get_children())
        
        for i, (region_key, region_data) in enumerate(self.sorted_regions):
            display_name = f"{i+1}. {region_data['display_name']}"
            is_completed = region_key in self.regions
            status = "✅ Done" if is_completed else "⏳ Pending"
            
            item = self.regions_tree.insert('', tk.END, text=display_name, values=(status,))
            
            # Color completed items differently
            if is_completed:
                self.regions_tree.set(item, 'status', '✅ Done')
            else:
                self.regions_tree.set(item, 'status', '⏳ Pending')
                
    def jump_to_region(self):
        selection = self.regions_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a region from the list")
            return
            
        item = selection[0]
        region_text = self.regions_tree.item(item, 'text')
        
        for i, option in enumerate([f"{j+1}. {data['display_name']}" for j, (key, data) in enumerate(self.sorted_regions)]):
            if option == region_text:
                self.region_combo.current(i)
                self.update_current_region_info()
                self.update_help_text()
                break
                
    def load_image(self):
        try:
            self.current_image = Image.open(self.image_path)
            self.display_image_on_canvas()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.window.destroy()
            
    def display_image_on_canvas(self):
        canvas_width = 900
        canvas_height = 700
        
        self.display_image = self.current_image.copy()
        
        img_width, img_height = self.display_image.size
        self.scale_factor = min(canvas_width / img_width, canvas_height / img_height, 1.0)
        
        if self.scale_factor < 1.0:
            new_width = int(img_width * self.scale_factor)
            new_height = int(img_height * self.scale_factor)
            self.display_image = self.display_image.resize((new_width, new_height), 
                                                          Image.Resampling.LANCZOS)
        
        self.photo = ImageTk.PhotoImage(self.display_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        self.redraw_regions()
        
    def start_selection(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.drawing = True
        
    def update_selection(self, event):
        if not self.drawing:
            return
            
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=3, fill='', stipple='gray25'
        )
        
    def end_selection(self, event):
        if not self.drawing:
            return
            
        self.drawing = False
        
        if abs(event.x - self.start_x) < 10 or abs(event.y - self.start_y) < 10:
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None
            return
            
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        
        original_coords = self.canvas_to_original_coords(x1, y1, x2, y2)
        
        selection = self.region_var.get()
        if selection:
            try:
                index = int(selection.split('.')[0]) - 1
                if 0 <= index < len(self.sorted_regions):
                    region_key, region_data = self.sorted_regions[index]
                    self.add_region(region_key, region_data['display_name'], original_coords)
                    
                    # Auto-advance to next uncompleted region
                    self.auto_advance_to_next_region()
            except Exception as e:
                print(f"Error processing selection: {e}")
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            
    def auto_advance_to_next_region(self):
        """Automatically advance to the next uncompleted region"""
        current_selection = self.region_var.get()
        try:
            current_index = int(current_selection.split('.')[0]) - 1
            
            # Look for next uncompleted region
            for i in range(current_index + 1, len(self.sorted_regions)):
                region_key, region_data = self.sorted_regions[i]
                if region_key not in self.regions:
                    # Found next uncompleted region
                    next_selection = f"{i+1}. {region_data['display_name']}"
                    self.region_var.set(next_selection)
                    self.region_combo.set(next_selection)
                    self.update_current_region_info()
                    self.update_help_text()
                    return
                    
            # If no uncompleted regions found, show completion message
            completed_count = len(self.regions)
            total_count = len(self.sorted_regions)
            if completed_count == total_count:
                messagebox.showinfo("All Regions Complete!", 
                                  f"🎉 Excellent! You've defined all {total_count} regions.\n\n"
                                  f"Click 'Save Template' to finish.")
        except Exception as e:
            print(f"Error in auto advance: {e}")
            
    def canvas_to_original_coords(self, x1, y1, x2, y2):
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
        
    def original_to_canvas_coords(self, coords):
        x1 = coords['x'] * self.scale_factor
        y1 = coords['y'] * self.scale_factor
        x2 = (coords['x'] + coords['width']) * self.scale_factor
        y2 = (coords['y'] + coords['height']) * self.scale_factor
        return x1, y1, x2, y2
        
    def add_region(self, region_key, display_name, coords):
        self.regions[region_key] = {
            'type': region_key,
            'display_name': display_name,
            'coordinates': coords
        }
        
        self.populate_regions_tree()
        self.redraw_regions()
        
    def redraw_regions(self):
        self.canvas.delete("region")
        
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'cyan', 'magenta']
        color_index = 0
        
        for region_key, region in self.regions.items():
            coords = region['coordinates']
            x1, y1, x2, y2 = self.original_to_canvas_coords(coords)
            
            color = colors[color_index % len(colors)]
            
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                       outline=color, width=2, tags="region")
            
            self.canvas.create_text(x1 + 5, y1 + 5, text=region['display_name'], anchor=tk.NW,
                                  fill=color, font=('Arial', 9, 'bold'), tags="region")
            
            color_index += 1
            
    def delete_selected_region(self):
        selection = self.regions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a region to delete")
            return
            
        item = selection[0]
        region_text = self.regions_tree.item(item, 'text')
        
        for region_key, region_data in self.regions.items():
            if region_data['display_name'] in region_text:
                del self.regions[region_key]
                break
                
        self.populate_regions_tree()
        self.redraw_regions()
        
    def clear_regions(self):
        if messagebox.askyesno("Clear All", "Delete all defined regions?"):
            self.regions.clear()
            self.populate_regions_tree()
            self.redraw_regions()
            
    def save_template(self):
        if not self.regions:
            messagebox.showwarning("Warning", "Please define at least one region")
            return
            
        template_data = {
            'site': self.poker_site,
            'created': datetime.now().isoformat(),
            'image_size': {
                'width': self.current_image.size[0],
                'height': self.current_image.size[1]
            },
            'regions': self.regions
        }
        
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            
        filename = f"{self.poker_site}_template.json"
        filepath = os.path.join(templates_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(template_data, f, indent=2)
                
            self.template_saved = True
            
            total_regions = len(self.region_definitions)
            defined_regions = len(self.regions)
            
            messagebox.showinfo("Template Saved!", 
                              f"Template saved successfully!\n\n"
                              f"File: {filename}\n"
                              f"Regions defined: {defined_regions}/{total_regions}\n"
                              f"Coverage: {(defined_regions/total_regions)*100:.1f}%")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {str(e)}")