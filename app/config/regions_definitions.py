"""
Optimized region definitions for different poker sites
"""

YAYA_BASE_REGIONS = {
    "tournament_header": {
        "display_name": "Tournament Header",
        "description": "Complete tournament info: '$215 - Sunday Special - $100,000 GTD, Table 46 - No Limit - 35,000/70,000, Ante 9,000'",
        "tooltip": "Select the entire top bar containing tournament name, buy-in, table info, and blinds",
        "example": "$215 - Sunday Special - $100,000 GTD, Table 46 - No Limit - 35,000/70,000, Ante 9,000",
        "priority": 1,
        "required": True
    },
    
    "position_stats": {
        "display_name": "Position & Statistics",
        "description": "Right panel: Position, average stack, prize pool, first place",
        "tooltip": "Select the entire right panel with position and tournament stats",
        "example": "Your Position: 11 of 33, Avg Stack: 27.18 BB, Prize Pool: $125,600, 1st Place: $25,953.40",
        "priority": 2,
        "required": True
    },
    
    "hand_history": {
        "display_name": "Hand Numbers",
        "description": "Current and previous hand numbers from left panel",
        "tooltip": "Select the hand number area on the left side",
        "example": "Current: 2492611261, Previous: 2492610659",
        "priority": 3,
        "required": True
    },
    
    "pot_info": {
        "display_name": "Pot Information",
        "description": "Center table pot amounts: total and current betting round",
        "tooltip": "Select the pot area in center of table showing total and current pot",
        "example": "Total: 34.19 BB, Pot: 0.9 BB",
        "priority": 4,
        "required": True
    },
    
    "hero_info": {
        "display_name": "Hero (Your) Information",
        "description": "Your cards, stack, and time bank at bottom center",
        "tooltip": "Select your cards, stack amount, and timer area at bottom",
        "example": "5♠ 5♦, 0 BB, 35s",
        "priority": 5,
        "required": True
    }
}

YAYA_PLAYER_POSITIONS = {
    2: ["seat_1", "seat_6"],
    3: ["seat_1", "seat_4", "seat_6"],
    4: ["seat_1", "seat_3", "seat_4", "seat_6"],
    5: ["seat_1", "seat_2", "seat_3", "seat_4", "seat_6"],
    6: ["seat_1", "seat_2", "seat_3", "seat_4", "seat_5", "seat_6"],
    7: ["seat_1", "seat_2", "seat_3", "seat_4", "seat_5", "seat_6", "seat_7"],
    8: ["seat_1", "seat_2", "seat_3", "seat_4", "seat_5", "seat_6", "seat_7", "seat_8"],
    9: ["seat_1", "seat_2", "seat_3", "seat_4", "seat_5", "seat_6", "seat_7", "seat_8", "seat_9"],
    10: ["seat_1", "seat_2", "seat_3", "seat_4", "seat_5", "seat_6", "seat_7", "seat_8", "seat_9", "seat_10"],
    11: ["seat_1", "seat_2", "seat_3", "seat_4", "seat_5", "seat_6", "seat_7", "seat_8", "seat_9", "seat_10", "seat_11"]
}

YAYA_SEAT_DEFINITIONS = {
    "seat_1": {
        "display_name": "Player 1 (Top Left)",
        "description": "Top left player position",
        "tooltip": "Select the top left player area (name, stack, bet)",
        "example": "USAWasteland, 13.07 BB, 1 BB",
        "position": "top_left"
    },
    "seat_2": {
        "display_name": "Player 2 (Top Right)",
        "description": "Top right player position",
        "tooltip": "Select the top right player area (name, stack, bet)",
        "example": "campana17, 19.04 BB",
        "position": "top_right"
    },
    "seat_3": {
        "display_name": "Player 3 (Left)",
        "description": "Left side player position",
        "tooltip": "Select the left side player area (name, stack)",
        "example": "GodsWay, 7.17 BB",
        "position": "left"
    },
    "seat_4": {
        "display_name": "Player 4 (Right)",
        "description": "Right side player position",
        "tooltip": "Select the right side player area (name, stack)",
        "example": "Chiliquaro, 17.07 BB",
        "position": "right"
    },
    "seat_5": {
        "display_name": "Player 5 (Bottom Left)",
        "description": "Bottom left player position",
        "tooltip": "Select the bottom left player area (name, stack)",
        "example": "Skrimples, 17.81 BB",
        "position": "bottom_left"
    },
    "seat_6": {
        "display_name": "Player 6 (Bottom Right)",
        "description": "Bottom right player position",
        "tooltip": "Select the bottom right player area (name, stack)",
        "example": "Push0rdie, 34.72 BB",
        "position": "bottom_right"
    },
    "seat_7": {
        "display_name": "Player 7 (Top Center)",
        "description": "Top center player position",
        "tooltip": "Select the top center player area",
        "example": "Player7, XX.XX BB",
        "position": "top_center"
    },
    "seat_8": {
        "display_name": "Player 8 (Center Left)",
        "description": "Center left player position",
        "tooltip": "Select the center left player area",
        "example": "Player8, XX.XX BB",
        "position": "center_left"
    },
    "seat_9": {
        "display_name": "Player 9 (Center Right)",
        "description": "Center right player position",
        "tooltip": "Select the center right player area",
        "example": "Player9, XX.XX BB",
        "position": "center_right"
    },
    "seat_10": {
        "display_name": "Player 10 (Bottom Center)",
        "description": "Bottom center player position",
        "tooltip": "Select the bottom center player area",
        "example": "Player10, XX.XX BB",
        "position": "bottom_center"
    },
    "seat_11": {
        "display_name": "Player 11 (Extra)",
        "description": "Additional player position",
        "tooltip": "Select additional player area",
        "example": "Player11, XX.XX BB",
        "position": "extra"
    }
}

POKERSTARS_REGIONS = {
    "tournament_header": {
        "display_name": "Tournament Header",
        "description": "Tournament name and details",
        "tooltip": "Select the tournament information at the top",
        "example": "Sunday Million - $215 Buy-in",
        "priority": 1
    },
    "table_info": {
        "display_name": "Table Information",
        "description": "Table number and blind levels",
        "tooltip": "Select table number and current blinds",
        "example": "Table 123 - 1000/2000",
        "priority": 2
    }
}

def get_yaya_regions_for_player_count(player_count):
    if player_count < 2 or player_count > 11:
        raise ValueError("YAYA supports 2-11 players")
    
    regions = YAYA_BASE_REGIONS.copy()
    
    active_seats = YAYA_PLAYER_POSITIONS[player_count]
    priority = 6
    
    for seat in active_seats:
        seat_def = YAYA_SEAT_DEFINITIONS[seat]
        regions[seat] = {
            **seat_def,
            "priority": priority,
            "required": False
        }
        priority += 1
    
    return regions

def get_regions_for_site(site, player_count=None):
    site_regions = {
        'yaya': get_yaya_regions_for_player_count(player_count) if player_count else YAYA_BASE_REGIONS,
        'pokerstars': POKERSTARS_REGIONS,
        'ggpoker': {},
        '888poker': {}
    }
    return site_regions.get(site, {})

def get_sorted_regions(site, player_count=None):
    regions = get_regions_for_site(site, player_count)
    return sorted(regions.items(), key=lambda x: x[1].get('priority', 999))