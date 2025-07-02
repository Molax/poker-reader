"""
OCR Configuration Settings
"""

class OCRConfig:
    
    TESSERACT_CONFIGS = {
        'default': '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,/:- ',
        'numbers_only': '--psm 8 -c tessedit_char_whitelist=0123456789',
        'currency': '--psm 8 -c tessedit_char_whitelist=0123456789$.,BB ',
        'currency_precise': '--psm 7 -c tessedit_char_whitelist=0123456789.BB ',
        'currency_with_total': '--psm 7 -c tessedit_char_whitelist=Total:0123456789.BB ',
        'currency_with_pot': '--psm 7 -c tessedit_char_whitelist=Pot:0123456789.BB ',
        'tournament': '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,/:- ',
        'tournament_enhanced': '--psm 7 -c tessedit_char_whitelist=0123456789$ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,- ',
        'player_name': '--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        'cards': '--psm 8 -c tessedit_char_whitelist=0123456789AKQJT♠♥♦♣',
        'hand_numbers': '--psm 7 -c tessedit_char_whitelist=0123456789:',
        'blinds_ante': '--psm 6 -c tessedit_char_whitelist=NoLimitAnte0123456789,/- '
    }
    
    REGION_CONFIG_MAP = {
        'tournament_header': 'tournament_enhanced',
        'blinds_info': 'blinds_ante',
        'position_stats': 'default',
        'hand_history': 'hand_numbers',
        'total_pot': 'currency_with_total',
        'current_pot': 'currency_with_pot',
        'hero_cards': 'cards',
        'hero_stack': 'currency_precise',
        'hero_name': 'player_name'
    }
    
    @classmethod
    def get_config_for_region(cls, region_type):
        if '_name' in region_type:
            return cls.TESSERACT_CONFIGS['player_name']
        elif '_stack' in region_type:
            return cls.TESSERACT_CONFIGS['currency_precise']
        elif '_bet' in region_type:
            return cls.TESSERACT_CONFIGS['currency_precise']
        elif region_type.startswith('seat_'):
            return cls.TESSERACT_CONFIGS['default']
        
        config_key = cls.REGION_CONFIG_MAP.get(region_type, 'default')
        return cls.TESSERACT_CONFIGS[config_key]
    
    CONFIDENCE_THRESHOLDS = {
        'minimum_success': 30,
        'high_confidence': 70,
        'excellent_confidence': 90
    }
    
    PREPROCESSING_PROFILES = {
        'currency_amounts': ['high_contrast', 'binary_threshold', 'morphological_cleanup'],
        'player_names': ['enhanced_contrast', 'denoising', 'sharpening'],
        'card_symbols': ['ultra_high_contrast', 'edge_enhancement', 'sharpening'],
        'hand_numbers': ['binary_threshold', 'morphological_operations'],
        'tournament_info': ['moderate_contrast', 'denoising'],
        'default': ['basic_contrast', 'binary_threshold']
    }