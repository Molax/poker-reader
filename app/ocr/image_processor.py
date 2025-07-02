import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import List

class ImageProcessor:
    
    @staticmethod
    def preprocess_region(image: np.ndarray, region_type: str) -> List[np.ndarray]:
        processed_images = []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        processed_images.append(gray)
        
        if region_type in ['total_pot', 'current_pot', 'hero_stack'] or '_stack' in region_type:
            processed_images.extend(ImageProcessor._process_currency_regions(gray))
            
        elif region_type in ['hero_cards']:
            processed_images.extend(ImageProcessor._process_card_regions(gray))
            
        elif region_type in ['hero_name'] or '_name' in region_type:
            processed_images.extend(ImageProcessor._process_name_regions(gray))
            
        elif region_type in ['hand_history']:
            processed_images.extend(ImageProcessor._process_number_regions(gray))
            
        elif region_type in ['tournament_header', 'blinds_info']:
            processed_images.extend(ImageProcessor._process_tournament_regions(gray))
            
        else:
            processed_images.extend(ImageProcessor._process_default_regions(gray))
        
        return processed_images
    
    @staticmethod
    def _process_currency_regions(gray: np.ndarray) -> List[np.ndarray]:
        processed = []
        
        enhanced = cv2.convertScaleAbs(gray, alpha=2.5, beta=0)
        processed.append(enhanced)
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed.append(binary)
        
        inv_binary = cv2.bitwise_not(binary)
        processed.append(inv_binary)
        
        ultra_enhanced = cv2.convertScaleAbs(gray, alpha=3.0, beta=10)
        processed.append(ultra_enhanced)
        
        kernel = np.ones((2,2), np.uint8)
        morphed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        processed.append(morphed)
        
        return processed
    
    @staticmethod
    def _process_card_regions(gray: np.ndarray) -> List[np.ndarray]:
        processed = []
        
        enhanced = cv2.convertScaleAbs(gray, alpha=3.0, beta=0)
        processed.append(enhanced)
        
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        processed.append(sharpened)
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed.append(binary)
        
        return processed
    
    @staticmethod
    def _process_name_regions(gray: np.ndarray) -> List[np.ndarray]:
        processed = []
        
        enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
        processed.append(enhanced)
        
        denoised = cv2.medianBlur(enhanced, 3)
        processed.append(denoised)
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed.append(binary)
        
        return processed
    
    @staticmethod
    def _process_number_regions(gray: np.ndarray) -> List[np.ndarray]:
        processed = []
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed.append(binary)
        
        kernel = np.ones((2,2), np.uint8)
        morphed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        processed.append(morphed)
        
        enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
        processed.append(enhanced)
        
        return processed
    
    @staticmethod
    def _process_tournament_regions(gray: np.ndarray) -> List[np.ndarray]:
        processed = []
        
        enhanced = cv2.convertScaleAbs(gray, alpha=1.8, beta=15)
        processed.append(enhanced)
        
        denoised = cv2.medianBlur(gray, 3)
        processed.append(denoised)
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed.append(binary)
        
        return processed
    
    @staticmethod
    def _process_default_regions(gray: np.ndarray) -> List[np.ndarray]:
        processed = []
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed.append(binary)
        
        inv_binary = cv2.bitwise_not(binary)
        processed.append(inv_binary)
        
        contrast_enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
        processed.append(contrast_enhanced)
        
        return processed