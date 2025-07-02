"""
Template Data Manager

Handles all template data operations including region storage,
player count management, and template serialization.

Author: PokerAnalyzer Team
"""

from datetime import datetime
from config.regions_definitions import get_regions_for_site, get_sorted_regions


class TemplateDataManager:
    """
    Manages template data and coordinates with region definitions.
    
    This class handles:
    - Region storage and retrieval
    - Player count management for YAYA tables
    - Template data serialization
    - State change notifications
    """
    
    def __init__(self, poker_site, player_count=6):
        """
        Initialize template data manager.
        
        Args:
            poker_site: Poker site identifier
            player_count: Number of players (for YAYA only)
        """
        self.poker_site = poker_site
        self.player_count = player_count if poker_site == 'yaya' else None
        self.regions = {}
        self.image_size = None
        self.update_callback = None
        
        self._update_region_definitions()
        
    def _update_region_definitions(self):
        """Update region definitions based on current settings."""
        if self.poker_site == 'yaya' and self.player_count:
            self.region_definitions = get_regions_for_site(self.poker_site, self.player_count)
            self.sorted_regions = get_sorted_regions(self.poker_site, self.player_count)
        else:
            self.region_definitions = get_regions_for_site(self.poker_site)
            self.sorted_regions = get_sorted_regions(self.poker_site)
            
    def set_update_callback(self, callback):
        """
        Set callback function for state updates.
        
        Args:
            callback: Function to call when data changes
        """
        self.update_callback = callback
        
    def _notify_update(self):
        """Notify listeners of data changes."""
        if self.update_callback:
            self.update_callback()
            
    def set_player_count(self, count):
        """
        Set player count and update region definitions.
        
        Args:
            count: Number of players (2-11 for YAYA)
        """
        if self.poker_site == 'yaya' and 2 <= count <= 11:
            self.player_count = count
            self.regions.clear()  # Clear existing regions
            self._update_region_definitions()
            self._notify_update()
        else:
            raise ValueError(f"Invalid player count {count} for {self.poker_site}")
            
    def set_image_size(self, size):
        """
        Set the source image dimensions.
        
        Args:
            size: Tuple of (width, height)
        """
        self.image_size = size
        
    def add_region(self, region_key, display_name, coordinates):
        """
        Add or update a region definition.
        
        Args:
            region_key: Unique identifier for the region
            display_name: Human-readable region name
            coordinates: Dict with x, y, width, height
        """
        self.regions[region_key] = {
            'type': region_key,
            'display_name': display_name,
            'coordinates': coordinates,
            'created_at': datetime.now().isoformat()
        }
        self._notify_update()
        
    def remove_region(self, region_key):
        """
        Remove a region definition.
        
        Args:
            region_key: Key of region to remove
        """
        if region_key in self.regions:
            del self.regions[region_key]
            self._notify_update()
            
    def clear_regions(self):
        """Clear all region definitions."""
        self.regions.clear()
        self._notify_update()
        
    def has_regions(self):
        """
        Check if any regions are defined.
        
        Returns:
            bool: True if regions exist
        """
        return len(self.regions) > 0
        
    def get_regions(self):
        """
        Get all defined regions.
        
        Returns:
            dict: All region definitions
        """
        return self.regions.copy()
        
    def get_region_definitions(self):
        """
        Get available region definitions for current configuration.
        
        Returns:
            dict: Available region definitions
        """
        return self.region_definitions
        
    def get_sorted_regions(self):
        """
        Get regions sorted by priority.
        
        Returns:
            list: Sorted region tuples (key, data)
        """
        return self.sorted_regions
        
    def is_region_defined(self, region_key):
        """
        Check if a specific region is defined.
        
        Args:
            region_key: Region identifier
            
        Returns:
            bool: True if region is defined
        """
        return region_key in self.regions
        
    def get_completion_stats(self):
        """
        Get template completion statistics.
        
        Returns:
            dict: Completion statistics
        """
        total_regions = len(self.region_definitions)
        defined_regions = len(self.regions)
        
        return {
            'total_regions': total_regions,
            'defined_regions': defined_regions,
            'completion_percentage': (defined_regions / total_regions * 100) if total_regions > 0 else 0,
            'missing_regions': total_regions - defined_regions
        }
        
    def get_template_data(self):
        """
        Get complete template data for serialization.
        
        Returns:
            dict: Complete template data structure
        """
        template_data = {
            'site': self.poker_site,
            'created': datetime.now().isoformat(),
            'regions': self.regions,
            'metadata': {
                'total_regions_available': len(self.region_definitions),
                'regions_defined': len(self.regions)
            }
        }
        
        if self.poker_site == 'yaya':
            template_data['player_count'] = self.player_count
            
        if self.image_size:
            template_data['image_size'] = {
                'width': self.image_size[0],
                'height': self.image_size[1]
            }
            
        return template_data
        
    def load_template_data(self, template_data):
        """
        Load template data from saved configuration.
        
        Args:
            template_data: Dictionary containing template configuration
        """
        self.regions = template_data.get('regions', {})
        
        if self.poker_site == 'yaya':
            self.player_count = template_data.get('player_count', 6)
            self._update_region_definitions()
            
        if 'image_size' in template_data:
            size_data = template_data['image_size']
            self.image_size = (size_data['width'], size_data['height'])
            
        self._notify_update()