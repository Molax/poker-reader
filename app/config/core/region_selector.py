"""
Region Selector Manager

Handles region selection logic and navigation through
the template configuration workflow.

Author: PokerAnalyzer Team
"""


class RegionSelectorManager:
    """
    Manages region selection state and navigation logic.
    
    This class handles:
    - Current region tracking
    - Navigation through region list
    - Auto-advancement logic
    - Region completion status
    """
    
    def __init__(self, template_data_manager):
        """
        Initialize region selector.
        
        Args:
            template_data_manager: TemplateDataManager instance
        """
        self.template_data = template_data_manager
        self.current_region_index = 0
        
    def update_regions(self):
        """Update region list and reset selection."""
        self.current_region_index = 0
        
    def get_current_region(self):
        """
        Get currently selected region definition.
        
        Returns:
            tuple: (region_key, region_data) or None if invalid
        """
        sorted_regions = self.template_data.get_sorted_regions()
        
        if 0 <= self.current_region_index < len(sorted_regions):
            return sorted_regions[self.current_region_index]
        return None
        
    def get_current_region_index(self):
        """
        Get current region index.
        
        Returns:
            int: Current region index
        """
        return self.current_region_index
        
    def set_current_region_index(self, index):
        """
        Set current region index.
        
        Args:
            index: New region index
        """
        sorted_regions = self.template_data.get_sorted_regions()
        if 0 <= index < len(sorted_regions):
            self.current_region_index = index
            
    def advance_to_next_region(self):
        """
        Advance to next uncompleted region or show completion message.
        
        Returns:
            bool: True if advanced, False if all regions complete
        """
        sorted_regions = self.template_data.get_sorted_regions()
        
        # Look for next uncompleted region
        for i in range(self.current_region_index + 1, len(sorted_regions)):
            region_key, region_data = sorted_regions[i]
            if not self.template_data.is_region_defined(region_key):
                self.current_region_index = i
                return True
                
        # Check if all regions are complete
        stats = self.template_data.get_completion_stats()
        if stats['missing_regions'] == 0:
            # All regions complete
            return False
            
        # Still have incomplete regions, find first one
        for i, (region_key, region_data) in enumerate(sorted_regions):
            if not self.template_data.is_region_defined(region_key):
                self.current_region_index = i
                return True
                
        return False
        
    def get_region_list_for_display(self):
        """
        Get formatted region list for UI display.
        
        Returns:
            list: Formatted region names with numbers
        """
        sorted_regions = self.template_data.get_sorted_regions()
        return [
            f"{i+1}. {data['display_name']}" 
            for i, (key, data) in enumerate(sorted_regions)
        ]
        
    def get_region_completion_status(self):
        """
        Get completion status for all regions.
        
        Returns:
            list: List of completion status for each region
        """
        sorted_regions = self.template_data.get_sorted_regions()
        return [
            self.template_data.is_region_defined(key) 
            for key, data in sorted_regions
        ]
        
    def get_current_region_info(self):
        """
        Get detailed information about current region.
        
        Returns:
            dict: Current region information or None
        """
        current = self.get_current_region()
        if current:
            region_key, region_data = current
            is_completed = self.template_data.is_region_defined(region_key)
            
            return {
                'key': region_key,
                'data': region_data,
                'completed': is_completed,
                'index': self.current_region_index,
                'display_name': region_data.get('display_name', ''),
                'tooltip': region_data.get('tooltip', ''),
                'example': region_data.get('example', ''),
                'required': region_data.get('required', False)
            }
        return None
        
    def find_region_index_by_name(self, display_name):
        """
        Find region index by display name.
        
        Args:
            display_name: Region display name to search for
            
        Returns:
            int: Region index or -1 if not found
        """
        sorted_regions = self.template_data.get_sorted_regions()
        
        for i, (key, data) in enumerate(sorted_regions):
            if data.get('display_name') == display_name:
                return i
        return -1
        
    def get_progress_summary(self):
        """
        Get progress summary for UI display.
        
        Returns:
            dict: Progress information
        """
        stats = self.template_data.get_completion_stats()
        current_info = self.get_current_region_info()
        
        return {
            'current_region': current_info['display_name'] if current_info else 'None',
            'current_index': self.current_region_index + 1,
            'total_regions': stats['total_regions'],
            'completed_regions': stats['defined_regions'],
            'completion_percentage': stats['completion_percentage'],
            'is_complete': stats['missing_regions'] == 0
        }