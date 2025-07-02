import os
from datetime import datetime
from PIL import Image
from typing import Dict, Any

from .text_extractor import TextExtractor

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
                    'high_confidence_count': 0,
                    'validation_issues': []
                },
                'performance_metrics': {
                    'processing_time': 0,
                    'regions_per_second': 0
                }
            }
            
            start_time = datetime.now()
            confidences = []
            successful = 0
            failed = 0
            all_validation_issues = []
            
            for region_key, region_data in regions.items():
                try:
                    coordinates = region_data['coordinates']
                    region_type = region_data['type']
                    
                    extraction_result = self.text_extractor.extract_text_from_region(
                        image, coordinates, region_type
                    )
                    
                    is_successful = bool(extraction_result['text'] and extraction_result['confidence'] > 30)
                    
                    region_result = {
                        'display_name': region_data.get('display_name', region_key),
                        'type': region_type,
                        'coordinates': coordinates,
                        'text': extraction_result['text'],
                        'confidence': extraction_result['confidence'],
                        'method': extraction_result['method'],
                        'success': is_successful
                    }
                    
                    if is_successful:
                        successful += 1
                        confidences.append(extraction_result['confidence'])
                        if extraction_result['confidence'] > 70:
                            analysis_results['analysis_summary']['high_confidence_count'] += 1
                    else:
                        failed += 1
                    
                    analysis_results['extracted_data'][region_key] = region_result
                        
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
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            analysis_results['analysis_summary']['successful_extractions'] = successful
            analysis_results['analysis_summary']['failed_extractions'] = failed
            analysis_results['analysis_summary']['average_confidence'] = (
                sum(confidences) / len(confidences) if confidences else 0
            )
            analysis_results['analysis_summary']['validation_issues'] = all_validation_issues
            
            analysis_results['performance_metrics']['processing_time'] = processing_time
            analysis_results['performance_metrics']['regions_per_second'] = (
                len(regions) / processing_time if processing_time > 0 else 0
            )
            
            analysis_results = self._add_poker_insights(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            return {
                'error': f"Analysis failed: {str(e)}",
                'site': template.get('site', 'unknown'),
                'image_file': os.path.basename(image_path) if image_path else 'unknown'
            }
    
    def _add_poker_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        extracted_data = analysis_results.get('extracted_data', {})
        
        insights = {
            'game_state': {},
            'player_info': {},
            'pot_analysis': {},
            'tournament_info': {}
        }
        
        try:
            if 'total_pot' in extracted_data and extracted_data['total_pot']['success']:
                total_pot_text = extracted_data['total_pot']['text']
                pot_value = self._extract_numeric_value(total_pot_text)
                if pot_value:
                    insights['pot_analysis']['total_pot_bb'] = pot_value
            
            if 'current_pot' in extracted_data and extracted_data['current_pot']['success']:
                current_pot_text = extracted_data['current_pot']['text']
                pot_value = self._extract_numeric_value(current_pot_text)
                if pot_value:
                    insights['pot_analysis']['current_pot_bb'] = pot_value
            
            if 'hero_stack' in extracted_data and extracted_data['hero_stack']['success']:
                hero_stack_text = extracted_data['hero_stack']['text']
                stack_value = self._extract_numeric_value(hero_stack_text)
                if stack_value:
                    insights['player_info']['hero_stack_bb'] = stack_value
            
            if 'hero_name' in extracted_data and extracted_data['hero_name']['success']:
                insights['player_info']['hero_name'] = extracted_data['hero_name']['text']
            
            if 'hero_cards' in extracted_data and extracted_data['hero_cards']['success']:
                insights['player_info']['hero_cards'] = extracted_data['hero_cards']['text']
            
            active_players = []
            for key, data in extracted_data.items():
                if key.startswith('seat_') and not key.endswith('_stack') and not key.endswith('_bet'):
                    if data['success']:
                        player_name = data['text']
                        stack_key = f"{key}_stack"
                        stack_value = None
                        if stack_key in extracted_data and extracted_data[stack_key]['success']:
                            stack_value = self._extract_numeric_value(extracted_data[stack_key]['text'])
                        
                        active_players.append({
                            'seat': key,
                            'name': player_name,
                            'stack_bb': stack_value
                        })
            
            insights['player_info']['active_players'] = active_players
            insights['player_info']['player_count'] = len(active_players)
            
            if 'position_stats' in extracted_data and extracted_data['position_stats']['success']:
                position_text = extracted_data['position_stats']['text']
                insights['tournament_info']['position_text'] = position_text
            
        except Exception as e:
            insights['extraction_error'] = str(e)
        
        analysis_results['poker_insights'] = insights
        return analysis_results
    
    def _extract_numeric_value(self, text: str) -> float:
        import re
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        return None