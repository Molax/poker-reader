# app/ocr/__init__.py
from .analysis_engine import PokerAnalysisEngine

__all__ = ['PokerAnalysisEngine']

# app/ocr/analysis_engine.py
import cv2
import numpy as np
from PIL import Image
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
            'numbers': '--psm 8 -c tessedit_char_whitelist=0123456789.,',
            'text': '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ',
            'currency': '--psm 8 -c tessedit_char_whitelist=0123456789$.,',
            'tournament': '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,/:- '
        }

class ImageProcessor:
    @staticmethod
    def preprocess_region(image: np.ndarray, region_type: str) -> List[np.ndarray]:
        processed_images = []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        processed_images.append(gray)
        
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        processed_images.append(binary)
        
        inv_binary = cv2.bitwise_not(binary)
        processed_images.append(inv_binary)
        
        if region_type in ['tournament_header', 'position_stats']:
            denoised = cv2.medianBlur(gray, 3)
            processed_images.append(denoised)
            
        if region_type in ['pot_info', 'hero_info']:
            kernel = np.ones((2,2), np.uint8)
            morphed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            processed_images.append(morphed)
            
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
            'position_stats': 'default',
            'hand_history': 'numbers',
            'pot_info': 'currency',
            'hero_info': 'default'
        }
        
        if region_type.startswith('seat_'):
            return self.ocr_engine.tesseract_configs['default']
            
        config_key = config_map.get(region_type, 'default')
        return self.ocr_engine.tesseract_configs[config_key]
    
    def _clean_text(self, text: str, region_type: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        
        if region_type == 'pot_info':
            text = re.sub(r'[^\d\.\$\s,BB]', '', text)
        elif region_type == 'hand_history':
            text = re.sub(r'[^\d,:]', '', text)
        elif region_type in ['hero_info'] and any(suit in text for suit in ['♠', '♥', '♦', '♣']):
            text = re.sub(r'[^\d\w\s♠♥♦♣\.,BB]', '', text)
        
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
        
        length_bonus = min(len(text) * 2, 20)
        base_score += length_bonus
        
        if region_type == 'tournament_header':
            if '$' in text and 'GTD' in text:
                base_score += 30
            if any(word in text.lower() for word in ['table', 'limit', 'ante']):
                base_score += 20
        elif region_type == 'pot_info':
            if 'BB' in text and any(char.isdigit() for char in text):
                base_score += 25
        elif region_type == 'position_stats':
            if 'position' in text.lower() or 'stack' in text.lower():
                base_score += 20
        elif region_type.startswith('seat_'):
            if 'BB' in text and any(char.isdigit() for char in text):
                base_score += 15
        
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