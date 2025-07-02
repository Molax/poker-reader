"""
Region definitions for different poker sites
"""

YAYA_REGIONS = {
    "tournament_title": {
        "display_name": "Tournament Title",
        "description": "Top bar: '$215 - Sunday Special - $100,000 GTD'",
        "tooltip": "Select the tournament name and buy-in information at the very top",
        "example": "$215 - Sunday Special - $100,000 GTD",
        "priority": 1
    },
    "table_info": {
        "display_name": "Table & Blinds Info", 
        "description": "Table number, blinds, ante: 'Table 46 - No Limit - 35,000/70,000, Ante 9,000'",
        "tooltip": "Select the table number, limit type, and blind levels",
        "example": "Table 46 - No Limit - 35,000 / 70,000, Ante 9,000",
        "priority": 2
    },
    "position_info": {
        "display_name": "Your Position",
        "description": "Top right: Position and remaining players",
        "tooltip": "Select 'Your Position: 11 of 33' area",
        "example": "Your Position: 11 of 33",
        "priority": 3
    },
    "avg_stack": {
        "display_name": "Average Stack",
        "description": "Average stack in big blinds",
        "tooltip": "Select 'Avg Stack: 27.18 BB' area",
        "example": "Avg Stack: 27.18 BB",
        "priority": 4
    },
    "prize_pool": {
        "display_name": "Prize Pool",
        "description": "Total prize pool amount",
        "tooltip": "Select 'Prize Pool: $125,600' area",
        "example": "Prize Pool: $125,600",
        "priority": 5
    },
    "first_place": {
        "display_name": "1st Place Prize",
        "description": "First place prize amount",
        "tooltip": "Select '1st Place: $25,953.40' area",
        "example": "1st Place: $25,953.40",
        "priority": 6
    },
    "hand_current": {
        "display_name": "Current Hand #",
        "description": "Current hand number",
        "tooltip": "Select 'Current: 2492611261' area on the left",
        "example": "Current: 2492611261",
        "priority": 7
    },
    "hand_previous": {
        "display_name": "Previous Hand #",
        "description": "Previous hand number",
        "tooltip": "Select 'Previous: 2492610659' area on the left",
        "example": "Previous: 2492610659",
        "priority": 8
    },
    "pot_total": {
        "display_name": "Total Pot",
        "description": "Center pot amount in BB",
        "tooltip": "Select 'Total: 34.19 BB' in the center of table",
        "example": "Total: 34.19 BB",
        "priority": 9
    },
    "pot_current": {
        "display_name": "Current Pot",
        "description": "Current betting round pot",
        "tooltip": "Select 'Pot: 0.9 BB' below the total pot",
        "example": "Pot: 0.9 BB",
        "priority": 10
    },
    "hero_cards": {
        "display_name": "Your Cards",
        "description": "Your hole cards at bottom center",
        "tooltip": "Select your two cards (5♠ 5♦) at bottom center",
        "example": "5♠ 5♦",
        "priority": 11
    },
    "hero_stack": {
        "display_name": "Your Stack",
        "description": "Your chip stack amount",
        "tooltip": "Select your stack amount below your cards",
        "example": "0 BB",
        "priority": 12
    },
    "time_bank": {
        "display_name": "Time Bank",
        "description": "Remaining time for your action",
        "tooltip": "Select the timer showing remaining seconds",
        "example": "35",
        "priority": 13
    },
    "player_1_name": {
        "display_name": "Player 1 Name (Top Left)",
        "description": "USAWasteland - Top left position",
        "tooltip": "Select player name at top left of table",
        "example": "USAWasteland",
        "priority": 14
    },
    "player_1_stack": {
        "display_name": "Player 1 Stack",
        "description": "Stack amount for top left player",
        "tooltip": "Select stack amount below player 1 name",
        "example": "13.07 BB",
        "priority": 15
    },
    "player_1_bet": {
        "display_name": "Player 1 Bet",
        "description": "Current bet amount for player 1",
        "tooltip": "Select bet amount near player 1 (1 BB)",
        "example": "1 BB",
        "priority": 16
    },
    "player_2_name": {
        "display_name": "Player 2 Name (Top Right)",
        "description": "campana17 - Top right position",
        "tooltip": "Select player name at top right (marked as friend)",
        "example": "campana17",
        "priority": 17
    },
    "player_2_stack": {
        "display_name": "Player 2 Stack",
        "description": "Stack amount for top right player",
        "tooltip": "Select stack amount below player 2 name",
        "example": "19.04 BB",
        "priority": 18
    },
    "player_3_name": {
        "display_name": "Player 3 Name (Left)",
        "description": "GodsWay - Left position",
        "tooltip": "Select player name on the left side",
        "example": "GodsWay",
        "priority": 19
    },
    "player_3_stack": {
        "display_name": "Player 3 Stack",
        "description": "Stack amount for left player",
        "tooltip": "Select stack amount below player 3 name",
        "example": "7.17 BB",
        "priority": 20
    },
    "player_4_name": {
        "display_name": "Player 4 Name (Right)",
        "description": "Chiliquaro - Right position",
        "tooltip": "Select player name on the right side",
        "example": "Chiliquaro",
        "priority": 21
    },
    "player_4_stack": {
        "display_name": "Player 4 Stack",
        "description": "Stack amount for right player",
        "tooltip": "Select stack amount below player 4 name",
        "example": "17.07 BB",
        "priority": 22
    },
    "player_5_name": {
        "display_name": "Player 5 Name (Bottom Left)",
        "description": "Skrimples - Bottom left position",
        "tooltip": "Select player name at bottom left",
        "example": "Skrimples",
        "priority": 23
    },
    "player_5_stack": {
        "display_name": "Player 5 Stack",
        "description": "Stack amount for bottom left player",
        "tooltip": "Select stack amount below player 5 name",
        "example": "17.81 BB",
        "priority": 24
    },
    "player_6_name": {
        "display_name": "Player 6 Name (Bottom Right)",
        "description": "Push0rdie - Bottom right position",
        "tooltip": "Select player name at bottom right",
        "example": "Push0rdie",
        "priority": 25
    },
    "player_6_stack": {
        "display_name": "Player 6 Stack",
        "description": "Stack amount for bottom right player",
        "tooltip": "Select stack amount below player 6 name",
        "example": "34.72 BB",
        "priority": 26
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

def get_regions_for_site(site):
    """Get region definitions for specific poker site"""
    site_regions = {
        'yaya': YAYA_REGIONS,
        'pokerstars': POKERSTARS_REGIONS,
        'ggpoker': {},
        '888poker': {}
    }
    return site_regions.get(site, {})

def get_sorted_regions(site):
    """Get regions sorted by priority for easier selection"""
    regions = get_regions_for_site(site)
    return sorted(regions.items(), key=lambda x: x[1].get('priority', 999))