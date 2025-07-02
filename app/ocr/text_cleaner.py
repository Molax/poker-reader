import re
from typing import Dict, Any

class TextCleaner:
    
    @staticmethod
    def clean_text(text: str, region_type: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        
        if region_type in ['total_pot']:
            return TextCleaner._clean_total_pot(text)
        elif region_type in ['current_pot']:
            return TextCleaner._clean_current_pot(text)
        elif region_type in ['hero_stack'] or '_stack' in region_type:
            return TextCleaner._clean_stack_amount(text)
        elif region_type == 'hand_history':
            return TextCleaner._clean_hand_numbers(text)
        elif region_type == 'hero_cards':
            return TextCleaner._clean_card_text(text)
        elif region_type == 'hero_name' or '_name' in region_type:
            return TextCleaner._clean_player_name(text)
        elif region_type in ['tournament_header']:
            return TextCleaner._clean_tournament_header(text)
        elif region_type in ['blinds_info']:
            return TextCleaner._clean_blinds_info(text)
        elif region_type in ['position_stats']:
            return TextCleaner._clean_position_stats(text)
        else:
            return text.strip()
    
    @staticmethod
    def _clean_total_pot(text: str) -> str:
        text = re.sub(r'[^\d\.\sBB:Total]', '', text)
        text = re.sub(r'\s+', ' ', text)
        if 'Total' in text and not text.startswith('Total'):
            text = 'Total:' + text.replace('Total', '').strip()
        return text.strip()
    
    @staticmethod
    def _clean_current_pot(text: str) -> str:
        text = re.sub(r'[^\d\.\sBB:Pot]', '', text)
        text = re.sub(r'\s+', ' ', text)
        if 'Pot' in text and not text.startswith('Pot'):
            text = 'Pot ' + text.replace('Pot', '').strip()
        return text.strip()
    
    @staticmethod
    def _clean_stack_amount(text: str) -> str:
        text = re.sub(r'[^\d\.\sBB]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def _clean_hand_numbers(text: str) -> str:
        text = re.sub(r'[^\d:]', '', text)
        return text.strip()
    
    @staticmethod
    def _clean_card_text(text: str) -> str:
        text = re.sub(r'[^\dAKQJT♠♥♦♣\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def _clean_player_name(text: str) -> str:
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def _clean_tournament_header(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        common_fixes = {
            'S215': '$215',
            'S100': '$100',
            'S125': '$125',
            'Surday': 'Sunday',
            'S1OO': '$100',
            'S1O0': '$100',
            '5215': '$215'
        }
        for wrong, correct in common_fixes.items():
            text = text.replace(wrong, correct)
        return text.strip()
    
    @staticmethod
    def _clean_blinds_info(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        common_fixes = {
            'Arte': 'Ante',
            '9,OOC': '9,000',
            '9,O00': '9,000',
            'O': '0'
        }
        for wrong, correct in common_fixes.items():
            text = text.replace(wrong, correct)
        return text.strip()
    
    @staticmethod
    def _clean_position_stats(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        common_fixes = {
            'Paol': 'Pool',
            'DDpvgstack': 'Avg Stack',
            'S125': '$125',
            'S25': '$25'
        }
        for wrong, correct in common_fixes.items():
            text = text.replace(wrong, correct)
        return text.strip()

class TextValidator:
    
    @staticmethod
    def validate_extraction(text: str, region_type: str, confidence: float) -> Dict[str, Any]:
        validation_result = {
            'is_valid': True,
            'confidence_adjusted': confidence,
            'issues': [],
            'suggestions': []
        }
        
        if region_type in ['total_pot']:
            validation_result = TextValidator._validate_total_pot(text, confidence)
        elif region_type in ['current_pot']:
            validation_result = TextValidator._validate_current_pot(text, confidence)
        elif region_type in ['hero_stack'] or '_stack' in region_type:
            validation_result = TextValidator._validate_stack_amount(text, confidence)
        elif region_type == 'hand_history':
            validation_result = TextValidator._validate_hand_numbers(text, confidence)
        elif region_type == 'hero_name' or '_name' in region_type:
            validation_result = TextValidator._validate_player_name(text, confidence)
        
        return validation_result
    
    @staticmethod
    def _validate_total_pot(text: str, confidence: float) -> Dict[str, Any]:
        result = {'is_valid': True, 'confidence_adjusted': confidence, 'issues': [], 'suggestions': []}
        
        if 'Total' not in text:
            result['issues'].append("Missing 'Total' prefix")
            result['confidence_adjusted'] -= 20
        
        if 'BB' not in text:
            result['issues'].append("Missing 'BB' suffix")
            result['confidence_adjusted'] -= 15
        
        numeric_part = re.findall(r'\d+\.?\d*', text)
        if not numeric_part:
            result['issues'].append("No numeric value found")
            result['confidence_adjusted'] -= 30
            result['is_valid'] = False
        
        return result
    
    @staticmethod
    def _validate_current_pot(text: str, confidence: float) -> Dict[str, Any]:
        result = {'is_valid': True, 'confidence_adjusted': confidence, 'issues': [], 'suggestions': []}
        
        if 'Pot' not in text:
            result['issues'].append("Missing 'Pot' prefix")
            result['confidence_adjusted'] -= 20
        
        if 'BB' not in text:
            result['issues'].append("Missing 'BB' suffix")
            result['confidence_adjusted'] -= 15
        
        numeric_part = re.findall(r'\d+\.?\d*', text)
        if not numeric_part:
            result['issues'].append("No numeric value found")
            result['confidence_adjusted'] -= 30
            result['is_valid'] = False
        
        return result
    
    @staticmethod
    def _validate_stack_amount(text: str, confidence: float) -> Dict[str, Any]:
        result = {'is_valid': True, 'confidence_adjusted': confidence, 'issues': [], 'suggestions': []}
        
        if 'BB' not in text:
            result['issues'].append("Missing 'BB' suffix")
            result['confidence_adjusted'] -= 15
        
        numeric_part = re.findall(r'\d+\.?\d*', text)
        if not numeric_part:
            result['issues'].append("No numeric value found")
            result['confidence_adjusted'] -= 30
            result['is_valid'] = False
        elif len(numeric_part) == 1:
            value = float(numeric_part[0])
            if value < 0.1:
                result['issues'].append("Stack value too low")
                result['confidence_adjusted'] -= 10
            elif value > 1000:
                result['issues'].append("Stack value unusually high")
                result['confidence_adjusted'] -= 10
        
        return result
    
    @staticmethod
    def _validate_hand_numbers(text: str, confidence: float) -> Dict[str, Any]:
        result = {'is_valid': True, 'confidence_adjusted': confidence, 'issues': [], 'suggestions': []}
        
        if ':' not in text:
            result['issues'].append("Missing colon separator")
            result['confidence_adjusted'] -= 20
        
        numbers = re.findall(r'\d+', text)
        if len(numbers) < 2:
            result['issues'].append("Should contain at least 2 hand numbers")
            result['confidence_adjusted'] -= 25
            result['is_valid'] = False
        
        for num in numbers:
            if len(num) < 8:
                result['issues'].append(f"Hand number {num} seems too short")
                result['confidence_adjusted'] -= 10
        
        return result
    
    @staticmethod
    def _validate_player_name(text: str, confidence: float) -> Dict[str, Any]:
        result = {'is_valid': True, 'confidence_adjusted': confidence, 'issues': [], 'suggestions': []}
        
        if len(text) < 2:
            result['issues'].append("Player name too short")
            result['confidence_adjusted'] -= 20
            result['is_valid'] = False
        elif len(text) > 20:
            result['issues'].append("Player name unusually long")
            result['confidence_adjusted'] -= 10
        
        if not re.match(r'^[a-zA-Z0-9_]+$', text):
            result['issues'].append("Player name contains invalid characters")
            result['confidence_adjusted'] -= 15
        
        return result