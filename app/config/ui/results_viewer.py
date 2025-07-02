import tkinter as tk
from tkinter import ttk
import yaml

class ResultsViewer:
    def __init__(self, parent, results_data):
        self.parent = parent
        self.results_data = results_data
        
        self.window = tk.Toplevel(parent)
        self.window.title("Analysis Results Viewer")
        self.window.geometry("1400x900")
        self.window.resizable(True, True)
        
        self.setup_ui()
        self.display_results()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text=f"Analysis Results - {self.results_data.get('site', 'Unknown').upper()}", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        close_btn = ttk.Button(header_frame, text="Close", command=self.window.destroy)
        close_btn.pack(side=tk.RIGHT)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.setup_summary_tab(notebook)
        self.setup_poker_insights_tab(notebook)
        self.setup_regions_tab(notebook)
        self.setup_raw_data_tab(notebook)
        
    def setup_summary_tab(self, notebook):
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="Summary")
        
        canvas = tk.Canvas(summary_frame)
        scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        summary = self.results_data.get('analysis_summary', {})
        template_info = self.results_data.get('template_info', {})
        performance = self.results_data.get('performance_metrics', {})
        
        info_frame = ttk.LabelFrame(scrollable_frame, text="Analysis Summary", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Image: {self.results_data.get('image_file', 'Unknown')}", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Site: {self.results_data.get('site', 'Unknown').upper()}", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Timestamp: {self.results_data.get('timestamp', 'Unknown')}", 
                 font=('Arial', 11)).pack(anchor=tk.W)
        
        if template_info.get('player_count'):
            ttk.Label(info_frame, text=f"Player Count: {template_info['player_count']}", 
                     font=('Arial', 11)).pack(anchor=tk.W)
        
        stats_frame = ttk.LabelFrame(scrollable_frame, text="Extraction Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        successful = summary.get('successful_extractions', 0)
        failed = summary.get('failed_extractions', 0)
        total = successful + failed
        avg_confidence = summary.get('average_confidence', 0)
        high_confidence = summary.get('high_confidence_count', 0)
        
        ttk.Label(stats_frame, text=f"Total Regions: {total}", font=('Arial', 11)).pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Successful Extractions: {successful} ({(successful/total*100) if total > 0 else 0:.1f}%)", 
                 font=('Arial', 11), foreground='green' if successful > 0 else 'red').pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Failed Extractions: {failed}", 
                 font=('Arial', 11), foreground='red' if failed > 0 else 'green').pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Average Confidence: {avg_confidence:.1f}%", 
                 font=('Arial', 11)).pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"High Confidence (>70%): {high_confidence}", 
                 font=('Arial', 11)).pack(anchor=tk.W)
        
        if performance:
            perf_frame = ttk.LabelFrame(scrollable_frame, text="Performance Metrics", padding=10)
            perf_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(perf_frame, text=f"Processing Time: {performance.get('processing_time', 0):.2f}s", 
                     font=('Arial', 11)).pack(anchor=tk.W)
            ttk.Label(perf_frame, text=f"Regions/Second: {performance.get('regions_per_second', 0):.1f}", 
                     font=('Arial', 11)).pack(anchor=tk.W)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_poker_insights_tab(self, notebook):
        insights_frame = ttk.Frame(notebook)
        notebook.add(insights_frame, text="Poker Insights")
        
        canvas = tk.Canvas(insights_frame)
        scrollbar = ttk.Scrollbar(insights_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        poker_insights = self.results_data.get('poker_insights', {})
        
        if 'pot_analysis' in poker_insights:
            pot_frame = ttk.LabelFrame(scrollable_frame, text="Pot Analysis", padding=10)
            pot_frame.pack(fill=tk.X, pady=(0, 10))
            
            pot_data = poker_insights['pot_analysis']
            if 'total_pot_bb' in pot_data:
                ttk.Label(pot_frame, text=f"Total Pot: {pot_data['total_pot_bb']} BB", 
                         font=('Arial', 12, 'bold')).pack(anchor=tk.W)
            if 'current_pot_bb' in pot_data:
                ttk.Label(pot_frame, text=f"Current Betting Round: {pot_data['current_pot_bb']} BB", 
                         font=('Arial', 12)).pack(anchor=tk.W)
        
        if 'player_info' in poker_insights:
            player_frame = ttk.LabelFrame(scrollable_frame, text="Player Information", padding=10)
            player_frame.pack(fill=tk.X, pady=(0, 10))
            
            player_data = poker_insights['player_info']
            if 'hero_name' in player_data:
                ttk.Label(player_frame, text=f"Hero: {player_data['hero_name']}", 
                         font=('Arial', 12, 'bold')).pack(anchor=tk.W)
            if 'hero_stack_bb' in player_data:
                ttk.Label(player_frame, text=f"Hero Stack: {player_data['hero_stack_bb']} BB", 
                         font=('Arial', 12)).pack(anchor=tk.W)
            if 'hero_cards' in player_data:
                ttk.Label(player_frame, text=f"Hero Cards: {player_data['hero_cards']}", 
                         font=('Arial', 12)).pack(anchor=tk.W)
            if 'player_count' in player_data:
                ttk.Label(player_frame, text=f"Active Players: {player_data['player_count']}", 
                         font=('Arial', 12)).pack(anchor=tk.W)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_regions_tab(self, notebook):
        regions_frame = ttk.Frame(notebook)
        notebook.add(regions_frame, text="Region Results")
        
        tree_frame = ttk.Frame(regions_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('Region', 'Success', 'Confidence', 'Method', 'Extracted Text')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            
        self.tree.column('Region', width=200)
        self.tree.column('Success', width=80)
        self.tree.column('Confidence', width=100)
        self.tree.column('Method', width=120)
        self.tree.column('Extracted Text', width=400)
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        extracted_data = self.results_data.get('extracted_data', {})
        for region_key, data in extracted_data.items():
            success = "✅ Yes" if data.get('success', False) else "❌ No"
            confidence = f"{data.get('confidence', 0):.1f}%"
            method = data.get('method', 'Unknown')
            text = data.get('text', '').replace('\n', ' ')[:100] + ('...' if len(data.get('text', '')) > 100 else '')
            
            self.tree.insert('', tk.END, values=(
                data.get('display_name', region_key),
                success,
                confidence,
                method,
                text
            ))
        
    def setup_raw_data_tab(self, notebook):
        raw_frame = ttk.Frame(notebook)
        notebook.add(raw_frame, text="Raw Data")
        
        text_widget = tk.Text(raw_frame, font=('Consolas', 10), wrap=tk.WORD)
        text_scroll = ttk.Scrollbar(raw_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scroll.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        formatted_data = yaml.dump(self.results_data, default_flow_style=False, sort_keys=False)
        text_widget.insert(tk.END, formatted_data)
        text_widget.config(state=tk.DISABLED)
        
    def display_results(self):
        pass