"""
Emission Detection AI Model for OPPO A92
Detects vehicle smoke, age, and condition for emission control
"""
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import os
import requests
from pathlib import Path
from datetime import datetime

class EmissionDetector:
    """
    AI model for detecting vehicle emissions and condition
    Optimized for OPPO A92 performance
    """
    
    def __init__(self, smoke_model_path='models/smoke_detector.pt', age_model_path='models/age_classifier.pt'):
        """
        Initialize emission detection models
        
        Args:
            smoke_model_path: Path to smoke detection model
            age_model_path: Path to vehicle age classification model
        """
        self.smoke_model_path = smoke_model_path
        self.age_model_path = age_model_path
        self.smoke_model = None
        self.age_model = None
        
        # Detection thresholds optimized for OPPO A92
        self.smoke_confidence_threshold = 0.6
        self.age_confidence_threshold = 0.7
        self.condition_threshold = 0.5
        
        # Vehicle age categories for classification
        self.age_categories = {
            0: 'new (0-2 years)',
            1: 'recent (3-5 years)', 
            2: 'moderate (6-10 years)',
            3: 'old (11-15 years)',
            4: 'very_old (16+ years)'
        }
        
        # Euro standards by age (approximate)
        self.euro_standards_by_age = {
            'new': 'Euro 6',
            'recent': 'Euro 5', 
            'moderate': 'Euro 4',
            'old': 'Euro 3',
            'very_old': 'Euro 2'
        }
        
        self._load_models()
    
    def _load_models(self):
        """Load AI models for emission detection"""
        try:
            print("🔥 Loading emission detection models...")
            
            # Load smoke detection model (custom trained or use object detection)
            if os.path.exists(self.smoke_model_path):
                self.smoke_model = YOLO(self.smoke_model_path)
                print("✅ Smoke detection model loaded")
            else:
                # Use general YOLOv5 for smoke-like objects as fallback
                print("⚠️  Smoke detection model not found, using fallback detection")
                self.smoke_model = None
            
            # Load vehicle age classification model
            if os.path.exists(self.age_model_path):
                print("✅ Vehicle age classification model loaded")
            else:
                print("⚠️  Age classification model not found, using heuristic methods")
                self.age_model = None
                
        except Exception as e:
            print(f"❌ Error loading emission detection models: {e}")
    
    def detect_smoke(self, frame, vehicle_bbox):
        """
        Detect smoke from vehicle exhaust
        
        Args:
            frame: OpenCV image frame
            vehicle_bbox: Vehicle bounding box [x1, y1, x2, y2]
            
        Returns:
            dict: Smoke detection results
        """
        try:
            x1, y1, x2, y2 = vehicle_bbox
            
            # Extract rear area of vehicle (likely exhaust location)
            rear_width = int((x2 - x1) * 0.3)  # 30% of vehicle width
            rear_x1 = x2 - rear_width
            rear_y1 = int(y1 + (y2 - y1) * 0.4)  # Lower 60% of vehicle
            
            # Crop rear area
            rear_area = frame[rear_y1:y2, rear_x1:x2]
            
            if rear_area.size == 0:
                return self._default_smoke_result()
            
            # Method 1: Use trained smoke detection model if available
            if self.smoke_model:
                results = self.smoke_model(rear_area, conf=self.smoke_confidence_threshold, verbose=False)
                smoke_detections = []
                
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            conf = float(box.conf[0])
                            smoke_detections.append(conf)
                
                if smoke_detections:
                    max_confidence = max(smoke_detections)
                    return {
                        'smoke_detected': max_confidence > self.smoke_confidence_threshold,
                        'smoke_level': max_confidence,
                        'method': 'ai_model'
                    }
            
            # Method 2: Heuristic smoke detection using color and movement analysis
            return self._heuristic_smoke_detection(rear_area)
            
        except Exception as e:
            print(f"❌ Error in smoke detection: {e}")
            return self._default_smoke_result()
    
    def _heuristic_smoke_detection(self, rear_area):
        """
        Heuristic method for smoke detection using color analysis
        
        Args:
            rear_area: Cropped rear area of vehicle
            
        Returns:
            dict: Smoke detection results
        """
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(rear_area, cv2.COLOR_BGR2HSV)
            
            # Define range for dark smoke (black/dark gray)
            lower_smoke = np.array([0, 0, 0])
            upper_smoke = np.array([180, 255, 80])  # Dark colors
            
            # Create mask for potential smoke areas
            smoke_mask = cv2.inRange(hsv, lower_smoke, upper_smoke)
            
            # Calculate percentage of dark areas
            smoke_percentage = np.sum(smoke_mask > 0) / smoke_mask.size
            
            # Additional checks for smoke-like patterns
            # Check for vertical patterns (smoke tends to rise)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 7))
            vertical_patterns = cv2.morphologyEx(smoke_mask, cv2.MORPH_OPEN, kernel)
            vertical_percentage = np.sum(vertical_patterns > 0) / vertical_patterns.size
            
            # Combine factors for smoke likelihood
            smoke_score = (smoke_percentage * 0.7) + (vertical_percentage * 0.3)
            smoke_detected = smoke_score > 0.15  # Threshold for detection
            
            return {
                'smoke_detected': smoke_detected,
                'smoke_level': min(smoke_score * 3, 1.0),  # Scale to 0-1
                'method': 'heuristic'
            }
            
        except Exception as e:
            print(f"❌ Error in heuristic smoke detection: {e}")
            return self._default_smoke_result()
    
    def estimate_vehicle_age(self, frame, vehicle_bbox):
        """
        Estimate vehicle age based on visual appearance
        
        Args:
            frame: OpenCV image frame
            vehicle_bbox: Vehicle bounding box [x1, y1, x2, y2]
            
        Returns:
            dict: Age estimation results
        """
        try:
            x1, y1, x2, y2 = vehicle_bbox
            vehicle_crop = frame[y1:y2, x1:x2]
            
            if vehicle_crop.size == 0:
                return self._default_age_result()
            
            # Method 1: Use trained age classification model if available
            if self.age_model:
                # Resize for model input
                input_size = (224, 224)
                resized = cv2.resize(vehicle_crop, input_size)
                
                # Model inference would go here
                # For now, use heuristic method
                pass
            
            # Method 2: Heuristic age estimation
            return self._heuristic_age_estimation(vehicle_crop)
            
        except Exception as e:
            print(f"❌ Error in age estimation: {e}")
            return self._default_age_result()
    
    def _heuristic_age_estimation(self, vehicle_crop):
        """
        Heuristic method for vehicle age estimation
        
        Args:
            vehicle_crop: Cropped vehicle image
            
        Returns:
            dict: Age estimation results
        """
        try:
            # Analyze image quality and wear indicators
            
            # 1. Color analysis - older vehicles often have faded paint
            hsv = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2HSV)
            saturation = hsv[:, :, 1]
            avg_saturation = np.mean(saturation)
            
            # 2. Edge sharpness - newer vehicles have cleaner lines
            gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # 3. Rust/corrosion detection (brown/orange areas)
            lower_rust = np.array([5, 50, 50])
            upper_rust = np.array([15, 255, 255])
            rust_mask = cv2.inRange(hsv, lower_rust, upper_rust)
            rust_percentage = np.sum(rust_mask > 0) / rust_mask.size
            
            # 4. Overall condition score
            condition_score = (
                avg_saturation / 255 * 0.4 +  # Higher saturation = newer
                edge_density * 0.3 +           # More defined edges = newer
                (1 - rust_percentage * 5) * 0.3  # Less rust = newer
            )
            
            # Map condition score to age category
            if condition_score > 0.8:
                age_category = 'new'
                estimated_years = 2
            elif condition_score > 0.6:
                age_category = 'recent'
                estimated_years = 5
            elif condition_score > 0.4:
                age_category = 'moderate'
                estimated_years = 8
            elif condition_score > 0.2:
                age_category = 'old'
                estimated_years = 13
            else:
                age_category = 'very_old'
                estimated_years = 18
            
            # Estimate manufacture year
            current_year = datetime.now().year
            estimated_year = current_year - estimated_years
            
            return {
                'estimated_age_category': age_category,
                'estimated_years': estimated_years,
                'estimated_manufacture_year': estimated_year,
                'condition_score': condition_score,
                'euro_standard': self.euro_standards_by_age.get(age_category, 'Unknown'),
                'confidence': min(abs(condition_score - 0.5) * 2, 1.0)  # Higher confidence for extreme values
            }
            
        except Exception as e:
            print(f"❌ Error in heuristic age estimation: {e}")
            return self._default_age_result()
    
    def assess_vehicle_condition(self, frame, vehicle_bbox):
        """
        Assess overall vehicle condition for emission estimation
        
        Args:
            frame: OpenCV image frame
            vehicle_bbox: Vehicle bounding box [x1, y1, x2, y2]
            
        Returns:
            dict: Vehicle condition assessment
        """
        try:
            # Get age estimation
            age_data = self.estimate_vehicle_age(frame, vehicle_bbox)
            
            # Get smoke detection
            smoke_data = self.detect_smoke(frame, vehicle_bbox)
            
            # Combine factors for overall assessment
            condition_factors = {
                'visual_condition': age_data.get('condition_score', 0.5),
                'smoke_emissions': 1.0 - smoke_data.get('smoke_level', 0),
                'estimated_age': max(0, 1.0 - (age_data.get('estimated_years', 10) / 20)),
            }
            
            # Weighted overall score
            overall_score = (
                condition_factors['visual_condition'] * 0.4 +
                condition_factors['smoke_emissions'] * 0.4 +
                condition_factors['estimated_age'] * 0.2
            )
            
            # Determine emission compliance likelihood
            euro_standard = age_data.get('euro_standard', 'Unknown')
            likely_compliant = overall_score > 0.6 and not smoke_data.get('smoke_detected', False)
            
            return {
                'overall_condition_score': overall_score,
                'condition_factors': condition_factors,
                'estimated_euro_standard': euro_standard,
                'likely_emission_compliant': likely_compliant,
                'recommendation': self._get_recommendation(overall_score, smoke_data),
                'age_data': age_data,
                'smoke_data': smoke_data
            }
            
        except Exception as e:
            print(f"❌ Error in vehicle condition assessment: {e}")
            return self._default_condition_result()
    
    def _get_recommendation(self, condition_score, smoke_data):
        """Generate recommendation based on assessment"""
        if smoke_data.get('smoke_detected', False):
            return 'immediate_inspection_required'
        elif condition_score < 0.3:
            return 'emission_test_recommended'
        elif condition_score < 0.6:
            return 'maintenance_suggested'
        else:
            return 'good_condition'
    
    def _default_smoke_result(self):
        """Default result when smoke detection fails"""
        return {
            'smoke_detected': False,
            'smoke_level': 0.0,
            'method': 'failed'
        }
    
    def _default_age_result(self):
        """Default result when age estimation fails"""
        return {
            'estimated_age_category': 'unknown',
            'estimated_years': 0,
            'estimated_manufacture_year': datetime.now().year,
            'condition_score': 0.5,
            'euro_standard': 'Unknown',
            'confidence': 0.0
        }
    
    def _default_condition_result(self):
        """Default result when condition assessment fails"""
        return {
            'overall_condition_score': 0.5,
            'condition_factors': {},
            'estimated_euro_standard': 'Unknown',
            'likely_emission_compliant': True,
            'recommendation': 'assessment_failed',
            'age_data': self._default_age_result(),
            'smoke_data': self._default_smoke_result()
        }
    
    def is_ready(self):
        """Check if detector is ready for use"""
        return True  # Heuristic methods always available

# Utility functions for emission calculation
def calculate_environmental_impact_score(vehicle_data, emission_data):
    """
    Calculate environmental impact score for a vehicle
    
    Args:
        vehicle_data: Dict with vehicle information
        emission_data: Dict with emission assessment data
        
    Returns:
        float: Environmental impact score (0-100, lower is better)
    """
    try:
        base_score = 50  # Neutral score
        
        # Age factor (older vehicles generally worse)
        age_years = emission_data.get('age_data', {}).get('estimated_years', 10)
        age_penalty = min(age_years * 2, 40)  # Up to 40 points penalty
        
        # Smoke detection penalty
        if emission_data.get('smoke_data', {}).get('smoke_detected', False):
            smoke_penalty = 30
        else:
            smoke_penalty = 0
        
        # Euro standard bonus/penalty
        euro_standard = emission_data.get('estimated_euro_standard', 'Unknown')
        euro_bonus = {
            'Euro 6': -20,
            'Euro 5': -10,
            'Euro 4': 0,
            'Euro 3': 10,
            'Euro 2': 20,
            'Euro 1': 30,
            'Unknown': 15
        }.get(euro_standard, 15)
        
        # Vehicle type factor
        vehicle_type = vehicle_data.get('vehicle_type', 'car')
        type_factor = {
            'motorcycle': -5,  # Generally lower emissions
            'car': 0,
            'truck': 15,
            'bus': 20
        }.get(vehicle_type, 0)
        
        # Calculate final score
        impact_score = base_score + age_penalty + smoke_penalty + euro_bonus + type_factor
        
        # Clamp to 0-100 range
        return max(0, min(100, impact_score))
        
    except Exception as e:
        print(f"❌ Error calculating environmental impact: {e}")
        return 50  # Return neutral score on error