import pytesseract
import easyocr
import numpy as np
from PIL import Image
from typing import Dict, List, Any

from .config import OCRConfig
from .image_processor import ImageProcessor
from .text_cleaner import TextCleaner, TextValidator

class OCREngine:
    def __init__(self):
        self.easyocr_reader = easyocr.Reader(['en'])
        self.config = OCRConfig()

class TextExtractor:
    def __init__(self):
        self.ocr_engine = OCREngine()
        self.image_processor = ImageProcessor()
        self.text_cleaner = TextCleaner()
        self.text_validator = TextValidator()
        
    def extract_text_from_region(self, image: Image.Image, coordinates: Dict[str, int], region_type: str) -> Dict[str, Any]:
        x, y, width, height = coordinates['x'], coordinates['y'], coordinates['width'], coordinates['height']
        
        region = image.crop((x, y, x + width, y + height))
        region_np = np.array(region)
        
        processed_images = self.image_processor.preprocess_region(region_np, region_type)
        
        results = []
        
        for i, processed_img in enumerate(processed_images):
            pil_img = Image.fromarray(processed_img)
            
            tesseract_result = self._extract_with_tesseract(pil_img, region_type)
            if tesseract_result['confidence'] > 30:
                results.append({
                    'method': f'tesseract_v{i}',
                    'text': tesseract_result['text'],
                    'confidence': tesseract_result['confidence']
                })
            
            easyocr_result = self._extract_with_easyocr(processed_img, region_type)
            if easyocr_result['confidence'] > 0.3:
                results.append({
                    'method': f'easyocr_v{i}',
                    'text': easyocr_result['text'],
                    'confidence': easyocr_result['confidence'] * 100
                })
        
        best_result = self._select_best_result(results, region_type)
        
        return {
            'text': best_result['text'] if best_result else '',
            'confidence': best_result['confidence'] if best_result else 0,
            'method': best_result['method'] if best_result else 'none',
            'all_results': results,
            'region_type': region_type,
            'coordinates': coordinates
        }
    
    def _extract_with_tesseract(self, image: Image.Image, region_type: str) -> Dict[str, Any]:
        config = self.ocr_engine.config.get_config_for_region(region_type)
        
        try:
            text = pytesseract.image_to_string(image, config=config).strip()
            
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            cleaned_text = self.text_cleaner.clean_text(text, region_type)
            
            return {
                'text': cleaned_text,
                'confidence': avg_confidence
            }
        except Exception as e:
            return {'text': '', 'confidence': 0}
    
    def _extract_with_easyocr(self, image: np.ndarray, region_type: str) -> Dict[str, Any]:
        try:
            results = self.ocr_engine.easyocr_reader.readtext(image)
            
            if not results:
                return {'text': '', 'confidence': 0}
            
            combined_text = ' '.join([result[1] for result in results])
            avg_confidence = sum([result[2] for result in results]) / len(results)
            
            cleaned_text = self.text_cleaner.clean_text(combined_text, region_type)
            
            return {
                'text': cleaned_text,
                'confidence': avg_confidence
            }
        except Exception as e:
            return {'text': '', 'confidence': 0}
    
    def _select_best_result(self, results: List[Dict], region_type: str) -> Dict[str, Any]:
        if not results:
            return None
        
        valid_results = [r for r in results if r['text'] and len(r['text'].strip()) > 0]
        if not valid_results:
            return None
        
        scored_results = []
        for result in valid_results:
            score = self._calculate_result_score(result, region_type)
            scored_results.append((score, result))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return scored_results[0][1]
    
    def _calculate_result_score(self, result: Dict, region_type: str) -> float:
        base_score = result['confidence']
        text = result['text']
        
        validation = self.text_validator.validate_extraction(text, region_type, base_score)
        adjusted_confidence = validation['confidence_adjusted']
        
        if region_type in ['total_pot']:
            if 'Total' in text and 'BB' in text and any(char.isdigit() for char in text):
                adjusted_confidence += 40
        elif region_type in ['current_pot']:
            if 'Pot' in text and 'BB' in text and any(char.isdigit() for char in text):
                adjusted_confidence += 40
        elif region_type in ['hero_stack'] or '_stack' in region_type:
            if 'BB' in text and any(char.isdigit() for char in text) and '.' in text:
                adjusted_confidence += 30
        elif region_type == 'hand_history':
            if ':' in text and len([c for c in text if c.isdigit()]) >= 8:
                adjusted_confidence += 35
        elif region_type == 'hero_cards':
            if any(suit in text for suit in ['♠', '♥', '♦', '♣']):
                adjusted_confidence += 50
        elif region_type == 'tournament_header':
            if '$' in text and any(word in text.lower() for word in ['special', 'gtd', 'table']):
                adjusted_confidence += 25
        
        length_bonus = 0
        if region_type in ['total_pot', 'current_pot']:
            if 5 <= len(text) <= 15:
                length_bonus = 20
        elif region_type in ['hero_name'] or '_name' in region_type:
            if 3 <= len(text) <= 20:
                length_bonus = 15
        elif region_type in ['hero_stack'] or '_stack' in region_type:
            if 4 <= len(text) <= 12:
                length_bonus = 20
        
        adjusted_confidence += length_bonus
        
        if 'easyocr' in result['method']:
            adjusted_confidence += 5
        
        return adjusted_confidence