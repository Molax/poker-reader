import cv2
import numpy as np
from PIL import Image, ImageEnhance
import pytesseract
import easyocr
import re
from typing import Dict, List, Tuple, Any
import logging
import os
from datetime import datetime

class OCREngine:
    def __init__(self):
        self.easyocr_reader = easyocr.Reader(['en'])
        self.setup_tesseract_config()
        
    def setup_tesseract_config(self):
        self.tesseract_configs = {
            'default': '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,/:- ',
            'numbers_only': '--psm 8 -c tessedit_char_whitelist=0123456789',
            'currency': '--psm 8 -c tessedit_char_whitelist=0123456789$.,BB ',
            'currency_precise': '--psm 7 -c tessedit_char_whitelist=0123456789.BB ',
            'tournament': '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,/:- ',
            'player_name': '--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
            'cards': '--psm 8 -c tessedit_char_whitelist=0123456789AKQJT♠♥♦♣',
            'hand_numbers': '--psm 7 -c tessedit_char_whitelist=0123456789:',
            'pot_amount': '--psm 7 -c tessedit_char_whitelist=0123456789.BB ',
            'total_amount': '--psm 7 -c tessedit_char_whitelist=Total:0123456789.BB '
        }

class ImageProcessor:
    @staticmethod
    def preprocess_region(image: np.ndarray, region_type: str) -> List[np.ndarray]:
        processed_images = []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        processed_images.append(gray)
        
        # Enhanced preprocessing based on region type
        if region_type in ['total_pot', 'current_pot', 'hero_stack']:
            # High contrast for currency amounts
            enhanced = cv2.convertScaleAbs(gray, alpha=2.5, beta=0)
            processed_images.append(enhanced)
            
            # Binary threshold for clean text
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(binary)
            
            # Inverted binary for white text on dark background
            inv_binary = cv2.bitwise_not(binary)
            processed_images.append(inv_binary)
            
        elif region_type in ['hero_cards']:
            # Special processing for card symbols
            enhanced = cv2.convertScaleAbs(gray, alpha=3.0, beta=0)
            processed_images.append(enhanced)
            
            # Edge enhancement for card symbols
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            processed_images.append(sharpened)
            
        elif region_type in ['hero_name'] or region_type.endswith('_name'):
            # Player name optimization
            enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
            processed_images.append(enhanced)
            
            # Noise reduction
            denoised = cv2.medianBlur(enhanced, 3)
            processed_images.append(denoised)
            
        elif region_type in ['hand_history']:
            # Hand numbers - need very clean digits
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(binary)
            
            # Morphological operations to clean up
            kernel = np.ones((2,2), np.uint8)
            morphed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            processed_images.append(morphed)
            
        elif region_type in ['tournament_header', 'blinds_info']:
            # Tournament info enhancement
            enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=10)
            processed_images.append(enhanced)
            
            # Denoising
            denoised = cv2.medianBlur(gray, 3)
            processed_images.append(denoised)
            
        else:
            # Default processing
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(binary)
            
            inv_binary = cv2.bitwise_not(binary)
            processed_images.append(inv_binary)
            
            contrast_enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
            processed_images.append(contrast_enhanced)
        
        return processed_images

class TextExtractor:
    def __init__(self):
        self.ocr_engine = OCREngine()
        self.image_processor = ImageProcessor()
        
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
        config = self._get_tesseract_config(region_type)
        
        try:
            text = pytesseract.image_to_string(image, config=config).strip()
            
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            cleaned_text = self._clean_text(text, region_type)
            
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
            
            cleaned_text = self._clean_text(combined_text, region_type)
            
            return {
                'text': cleaned_text,
                'confidence': avg_confidence
            }
        except Exception as e:
            return {'text': '', 'confidence': 0}
    
    def _get_tesseract_config(self, region_type: str) -> str:
        config_map = {
            'tournament_header': 'tournament',
            'blinds_info': 'tournament',
            'position_stats': 'default',
            'hand_history': 'hand_numbers',
            'total_pot': 'total_amount',
            'current_pot': 'pot_amount',
            'hero_cards': 'cards',
            'hero_stack': 'currency_precise',
            'hero_name': 'player_name'
        }
        
        # Handle seat-specific regions
        if '_name' in region_type:
            return self.ocr_engine.tesseract_configs['player_name']
        elif '_stack' in region_type:
            return self.ocr_engine.tesseract_configs['currency_precise']
        elif '_bet' in region_type:
            return self.ocr_engine.tesseract_configs['currency_precise']
        elif region_type.startswith('seat_'):
            return self.ocr_engine.tesseract_configs['default']
            
        config_key = config_map.get(region_type, 'default')
        return self.ocr_engine.tesseract_configs[config_key]
    
    def _clean_text(self, text: str, region_type: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        
        if region_type in ['total_pot', 'current_pot']:
            # Clean pot amounts: keep only numbers, dots, BB, Total, Pot, colon
            text = re.sub(r'[^\d\.\sBB:TotalPot]', '', text)
            text = re.sub(r'\s+', ' ', text)
        elif region_type in ['hero_stack'] or '_stack' in region_type:
            # Clean stack amounts: keep only numbers, dots, BB, spaces
            text = re.sub(r'[^\d\.\sBB]', '', text)
        elif region_type == 'hand_history':
            # Clean hand numbers: keep only digits and colons
            text = re.sub(r'[^\d:]', '', text)
        elif region_type == 'hero_cards':
            # Clean card text: keep card symbols and values
            text = re.sub(r'[^\dAKQJT♠♥♦♣\s]', '', text)
        elif region_type == 'hero_name' or '_name' in region_type:
            # Clean player names: keep alphanumeric only
            text = re.sub(r'[^\w\s]', '', text)
        elif region_type in ['tournament_header', 'blinds_info']:
            # Minimal cleaning for tournament info
            text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
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
        
        # Length bonus (reasonable lengths get bonus)
        if region_type in ['total_pot', 'current_pot']:
            if 5 <= len(text) <= 15:  # "Total: 34.19 BB" or "Pot: 0.9 BB"
                base_score += 20
        elif region_type in ['hero_name'] or '_name' in region_type:
            if 3 <= len(text) <= 20:  # Reasonable player name length
                base_score += 15
        elif region_type in ['hero_stack'] or '_stack' in region_type:
            if 4 <= len(text) <= 12:  # "31.79 BB" format
                base_score += 20
        
        # Content validation bonuses
        if region_type in ['total_pot']:
            if 'Total' in text and 'BB' in text and any(char.isdigit() for char in text):
                base_score += 40
        elif region_type in ['current_pot']:
            if 'Pot' in text and 'BB' in text and any(char.isdigit() for char in text):
                base_score += 40
        elif region_type in ['hero_stack'] or '_stack' in region_type:
            if 'BB' in text and any(char.isdigit() for char in text) and '.' in text:
                base_score += 30
        elif region_type == 'hand_history':
            if ':' in text and len([c for c in text if c.isdigit()]) >= 8:
                base_score += 35
        elif region_type == 'hero_cards':
            if any(suit in text for suit in ['♠', '♥', '♦', '♣']):
                base_score += 50
        
        # Method preference (EasyOCR tends to be better for complex layouts)
        if 'easyocr' in result['method']:
            base_score += 5
        
        return base_score

class PokerAnalysisEngine:
    def __init__(self):
        self.text_extractor = TextExtractor()
        
    def analyze_poker_image(self, image_path: str, template: Dict[str, Any]) -> Dict[str, Any]:
        try:
            image = Image.open(image_path)
            regions = template.get('regions', {})
            
            analysis_results = {
                'site': template.get('site', 'unknown'),
                'timestamp': None,
                'image_file': os.path.basename(image_path),
                'image_size': {'width': image.width, 'height': image.height},
                'template_info': {
                    'total_regions': len(regions),
                    'player_count': template.get('player_count')
                },
                'extracted_data': {},
                'analysis_summary': {
                    'successful_extractions': 0,
                    'failed_extractions': 0,
                    'average_confidence': 0,
                    'high_confidence_count': 0
                }
            }
            
            confidences = []
            successful = 0
            failed = 0
            
            for region_key, region_data in regions.items():
                try:
                    coordinates = region_data['coordinates']
                    region_type = region_data['type']
                    
                    extraction_result = self.text_extractor.extract_text_from_region(
                        image, coordinates, region_type
                    )
                    
                    analysis_results['extracted_data'][region_key] = {
                        'display_name': region_data.get('display_name', region_key),
                        'type': region_type,
                        'coordinates': coordinates,
                        'text': extraction_result['text'],
                        'confidence': extraction_result['confidence'],
                        'method': extraction_result['method'],
                        'success': bool(extraction_result['text'] and extraction_result['confidence'] > 30)
                    }
                    
                    if extraction_result['text'] and extraction_result['confidence'] > 30:
                        successful += 1
                        confidences.append(extraction_result['confidence'])
                        if extraction_result['confidence'] > 70:
                            analysis_results['analysis_summary']['high_confidence_count'] += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    analysis_results['extracted_data'][region_key] = {
                        'display_name': region_data.get('display_name', region_key),
                        'type': region_data.get('type', 'unknown'),
                        'coordinates': region_data.get('coordinates', {}),
                        'text': '',
                        'confidence': 0,
                        'method': 'error',
                        'success': False,
                        'error': str(e)
                    }
                    failed += 1
            
            analysis_results['analysis_summary']['successful_extractions'] = successful
            analysis_results['analysis_summary']['failed_extractions'] = failed
            analysis_results['analysis_summary']['average_confidence'] = (
                sum(confidences) / len(confidences) if confidences else 0
            )
            
            return analysis_results
            
        except Exception as e:
            return {
                'error': f"Analysis failed: {str(e)}",
                'site': template.get('site', 'unknown'),
                'image_file': os.path.basename(image_path) if image_path else 'unknown'
            }