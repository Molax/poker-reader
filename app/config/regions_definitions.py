"""
Enhanced region definitions for better OCR accuracy
"""

YAYA_BASE_REGIONS = {
    "tournament_header": {
        "display_name": "Tournament Header",
        "description": "Tournament name, buy-in, and table info only",
        "tooltip": "Select only the top tournament bar - exclude blinds/ante info",
        "example": "$215 - Sunday Special - $100,000 GTD, Table 46",
        "priority": 1,
        "required": True
    },
    
    "blinds_info": {
        "display_name": "Blinds & Ante",
        "description": "Current blinds and ante information",
        "tooltip": "Select the blinds/ante area separately from tournament header",
        "example": "No Limit - 35,000/70,000, Ante 9,000",
        "priority": 2,
        "required": True
    },
    
    "position_stats": {
        "display_name": "Position & Statistics", 
        "description": "Right panel: Position, average stack, prize pool, first place",
        "tooltip": "Select the entire right panel with position and tournament stats",
        "example": "Your Position: 11 of 33, Avg Stack: 27.18 BB, Prize Pool: $125,600, 1st Place: $25,953.40",
        "priority": 3,
        "required": True
    },
    
    "hand_history": {
        "display_name": "Hand Numbers",
        "description": "Current and previous hand numbers from left panel", 
        "tooltip": "Select the hand number area on the left side",
        "example": "Current: 2492611261, Previous: 2492610659",
        "priority": 4,
        "required": True
    },
    
    "total_pot": {
        "display_name": "Total Pot",
        "description": "Total pot amount only (top display)",
        "tooltip": "Select only the 'Total: XX.XX BB' area at top of table",
        "example": "Total: 34.19 BB",
        "priority": 5,
        "required": True
    },
    
    "current_pot": {
        "display_name": "Current Betting Round Pot",
        "description": "Current betting round pot amount only",
        "tooltip": "Select only the 'Pot: X.X BB' area in center of table",
        "example": "Pot: 0.9 BB", 
        "priority": 6,
        "required": True
    },
    
    "hero_cards": {
        "display_name": "Hero Cards",
        "description": "Your hole cards only",
        "tooltip": "Select only the card area - exclude stack and name",
        "example": "5♠ 5♦",
        "priority": 7,
        "required": True
    },
    
    "hero_stack": {
        "display_name": "Hero Stack",
        "description": "Your stack amount and time bank",
        "tooltip": "Select your stack amount and timer area separately",
        "example": "31.79 BB, 35s",
        "priority": 8,
        "required": True
    },
    
    "hero_name": {
        "display_name": "Hero Name",
        "description": "Your player name only",
        "tooltip": "Select only your username area",
        "example": "BelezIIAAa",
        "priority": 9,
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
        "display_name": "Player 1 - Name",
        "description": "Top left player name only",
        "tooltip": "Select only the player name area",
        "example": "USAWasteland",
        "position": "top_left"
    },
    "seat_1_stack": {
        "display_name": "Player 1 - Stack",
        "description": "Top left player stack amount",
        "tooltip": "Select only the stack amount area",
        "example": "13.07 BB",
        "position": "top_left"
    },
    "seat_1_bet": {
        "display_name": "Player 1 - Bet",
        "description": "Top left player current bet",
        "tooltip": "Select the current bet area if visible",
        "example": "1 BB",
        "position": "top_left"
    },
    "seat_2": {
        "display_name": "Player 2 - Name",
        "description": "Top right player name only",
        "tooltip": "Select only the player name area",
        "example": "campana17",
        "position": "top_right"
    },
    "seat_2_stack": {
        "display_name": "Player 2 - Stack",
        "description": "Top right player stack amount",
        "tooltip": "Select only the stack amount area",
        "example": "19.04 BB",
        "position": "top_right"
    },
    "seat_3": {
        "display_name": "Player 3 - Name",
        "description": "Left side player name only",
        "tooltip": "Select only the player name area",
        "example": "GodsWay",
        "position": "left"
    },
    "seat_3_stack": {
        "display_name": "Player 3 - Stack", 
        "description": "Left side player stack amount",
        "tooltip": "Select only the stack amount area",
        "example": "7.17 BB",
        "position": "left"
    },
    "seat_4": {
        "display_name": "Player 4 - Name",
        "description": "Right side player name only",
        "tooltip": "Select only the player name area",
        "example": "Chiliquaro",
        "position": "right"
    },
    "seat_4_stack": {
        "display_name": "Player 4 - Stack",
        "description": "Right side player stack amount", 
        "tooltip": "Select only the stack amount area",
        "example": "17.07 BB",
        "position": "right"
    },
    "seat_5": {
        "display_name": "Player 5 - Name",
        "description": "Bottom left player name only",
        "tooltip": "Select only the player name area",
        "example": "Skrimples",
        "position": "bottom_left"
    },
    "seat_5_stack": {
        "display_name": "Player 5 - Stack",
        "description": "Bottom left player stack amount",
        "tooltip": "Select only the stack amount area", 
        "example": "17.81 BB",
        "position": "bottom_left"
    },
    "seat_6": {
        "display_name": "Player 6 - Name",
        "description": "Bottom right player name only",
        "tooltip": "Select only the player name area",
        "example": "Push0rdie",
        "position": "bottom_right"
    },
    "seat_6_stack": {
        "display_name": "Player 6 - Stack",
        "description": "Bottom right player stack amount",
        "tooltip": "Select only the stack amount area",
        "example": "34.72 BB", 
        "position": "bottom_right"
    }
}

def get_yaya_regions_for_player_count(player_count):
    if player_count < 2 or player_count > 11:
        raise ValueError("YAYA supports 2-11 players")
    
    regions = YAYA_BASE_REGIONS.copy()
    
    active_seats = YAYA_PLAYER_POSITIONS[player_count]
    priority = 10
    
    for seat in active_seats:
        seat_def = YAYA_SEAT_DEFINITIONS[seat]
        regions[seat] = {
            **seat_def,
            "priority": priority,
            "required": False
        }
        priority += 1
        
        # Add stack region for each player
        stack_key = f"{seat}_stack"
        if stack_key in YAYA_SEAT_DEFINITIONS:
            stack_def = YAYA_SEAT_DEFINITIONS[stack_key]
            regions[stack_key] = {
                **stack_def,
                "priority": priority,
                "required": False
            }
            priority += 1
        
        # Add bet region for active players if betting
        bet_key = f"{seat}_bet"
        if bet_key in YAYA_SEAT_DEFINITIONS:
            bet_def = YAYA_SEAT_DEFINITIONS[bet_key]
            regions[bet_key] = {
                **bet_def,
                "priority": priority,
                "required": False
            }
            priority += 1
    
    return regions

def get_regions_for_site(site, player_count=None):
    site_regions = {
        'yaya': get_yaya_regions_for_player_count(player_count) if player_count else YAYA_BASE_REGIONS,
        'pokerstars': {},
        'ggpoker': {},
        '888poker': {}
    }
    return site_regions.get(site, {})

def get_sorted_regions(site, player_count=None):
    regions = get_regions_for_site(site, player_count)
    return sorted(regions.items(), key=lambda x: x[1].get('priority', 999))