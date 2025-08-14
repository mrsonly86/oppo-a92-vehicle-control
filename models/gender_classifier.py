"""
MediaPipe Gender Classification for OPPO A92
Lightweight gender detection for vehicle drivers
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple

class GenderClassifier:
    def __init__(self, confidence_threshold=0.7):
        """
        Initialize MediaPipe for gender classification
        
        Args:
            confidence_threshold: Classification confidence threshold
        """
        self.confidence_threshold = confidence_threshold
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize face detection and mesh
        self.face_detection = None
        self.face_mesh = None
        
        self._initialize_mediapipe()
    
    def _initialize_mediapipe(self):
        """Initialize MediaPipe components"""
        try:
            print("🔧 Initializing MediaPipe for gender classification on OPPO A92...")
            
            # Initialize face detection (lightweight)
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=0,  # 0 for short-range detection (mobile optimized)
                min_detection_confidence=0.5
            )
            
            # Initialize face mesh for detailed analysis
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=2,  # Maximum 2 faces (driver + passenger)
                refine_landmarks=False,  # Disable for performance
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            print("✅ MediaPipe gender classifier ready!")
            
        except Exception as e:
            print(f"❌ Error initializing MediaPipe: {e}")
            self.face_detection = None
            self.face_mesh = None
    
    def classify(self, frame, bbox, vehicle_detection=None):
        """
        Classify gender of person in vehicle
        
        Args:
            frame: OpenCV image frame
            bbox: Vehicle bounding box [x1, y1, x2, y2]
            vehicle_detection: Additional vehicle detection info
            
        Returns:
            Gender classification ('male', 'female', 'unknown')
        """
        if self.face_detection is None or self.face_mesh is None:
            return 'unknown'
        
        try:
            x1, y1, x2, y2 = bbox
            
            # Extract vehicle region
            vehicle_region = frame[y1:y2, x1:x2]
            
            if vehicle_region.size == 0:
                return 'unknown'
            
            # Convert to RGB for MediaPipe
            rgb_region = cv2.cvtColor(vehicle_region, cv2.COLOR_BGR2RGB)
            
            # Detect faces in vehicle region
            faces = self._detect_faces(rgb_region)
            
            if not faces:
                return 'unknown'
            
            # Classify gender for each detected face
            gender_predictions = []
            
            for face_bbox in faces:
                gender, confidence = self._classify_face_gender(rgb_region, face_bbox)
                if confidence > self.confidence_threshold:
                    gender_predictions.append(gender)
            
            # Return most confident prediction or first if multiple
            if gender_predictions:
                return gender_predictions[0]  # Return first (usually driver)
            
            return 'unknown'
            
        except Exception as e:
            print(f"❌ Error in gender classification: {e}")
            return 'unknown'
    
    def _detect_faces(self, image):
        """
        Detect faces in image using MediaPipe
        
        Args:
            image: RGB image
            
        Returns:
            List of face bounding boxes
        """
        faces = []
        
        try:
            results = self.face_detection.process(image)
            
            if results.detections:
                height, width = image.shape[:2]
                
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    
                    # Convert relative coordinates to absolute
                    x = int(bbox.xmin * width)
                    y = int(bbox.ymin * height)
                    w = int(bbox.width * width)
                    h = int(bbox.height * height)
                    
                    # Ensure coordinates are valid
                    x = max(0, x)
                    y = max(0, y)
                    w = min(w, width - x)
                    h = min(h, height - y)
                    
                    if w > 20 and h > 20:  # Minimum face size
                        faces.append([x, y, x + w, y + h])
            
            return faces
            
        except Exception as e:
            print(f"❌ Error detecting faces: {e}")
            return []
    
    def _classify_face_gender(self, image, face_bbox):
        """
        Classify gender based on facial features
        
        Args:
            image: RGB image
            face_bbox: Face bounding box [x1, y1, x2, y2]
            
        Returns:
            Tuple of (gender, confidence)
        """
        try:
            x1, y1, x2, y2 = face_bbox
            
            # Extract face region
            face_region = image[y1:y2, x1:x2]
            
            if face_region.size == 0:
                return 'unknown', 0
            
            # Resize face for consistent analysis
            face_resized = cv2.resize(face_region, (128, 128))
            
            # Get facial landmarks
            results = self.face_mesh.process(face_resized)
            
            if not results.multi_face_landmarks:
                # Fallback to simple color-based heuristics
                return self._simple_gender_heuristics(face_resized)
            
            # Extract features from landmarks
            landmarks = results.multi_face_landmarks[0]
            features = self._extract_gender_features(landmarks, face_resized)
            
            # Simple rule-based classification
            gender, confidence = self._rule_based_classification(features)
            
            return gender, confidence
            
        except Exception as e:
            print(f"❌ Error in face gender classification: {e}")
            return 'unknown', 0
    
    def _extract_gender_features(self, landmarks, face_image):
        """
        Extract gender-related features from facial landmarks
        
        Args:
            landmarks: MediaPipe face landmarks
            face_image: Face image
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            height, width = face_image.shape[:2]
            
            # Convert landmarks to pixel coordinates
            points = []
            for landmark in landmarks.landmark:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                points.append([x, y])
            
            points = np.array(points)
            
            # Face width to height ratio
            face_width = np.max(points[:, 0]) - np.min(points[:, 0])
            face_height = np.max(points[:, 1]) - np.min(points[:, 1])
            features['face_ratio'] = face_width / face_height if face_height > 0 else 1
            
            # Jaw strength (distance between jaw points)
            # Using approximate jaw landmarks
            if len(points) > 10:
                jaw_width = abs(points[172][0] - points[397][0]) if len(points) > 397 else face_width * 0.8
                features['jaw_strength'] = jaw_width / face_width if face_width > 0 else 0.8
            
            # Eye area (simple approximation)
            features['eye_area_ratio'] = 0.15  # Default ratio
            
            # Lip thickness (approximation)
            features['lip_thickness'] = 0.1  # Default value
            
            return features
            
        except Exception as e:
            print(f"❌ Error extracting gender features: {e}")
            return {'face_ratio': 1, 'jaw_strength': 0.8, 'eye_area_ratio': 0.15, 'lip_thickness': 0.1}
    
    def _rule_based_classification(self, features):
        """
        Simple rule-based gender classification
        
        Args:
            features: Extracted facial features
            
        Returns:
            Tuple of (gender, confidence)
        """
        try:
            male_score = 0
            female_score = 0
            
            # Face ratio analysis (males typically have wider faces)
            face_ratio = features.get('face_ratio', 1)
            if face_ratio > 1.1:
                male_score += 0.3
            else:
                female_score += 0.3
            
            # Jaw strength (males typically have stronger jaws)
            jaw_strength = features.get('jaw_strength', 0.8)
            if jaw_strength > 0.85:
                male_score += 0.4
            else:
                female_score += 0.4
            
            # Additional heuristics
            male_score += 0.3  # Base assumption for unclear cases
            female_score += 0.3
            
            # Determine classification
            if male_score > female_score:
                confidence = male_score / (male_score + female_score)
                return 'male', confidence
            else:
                confidence = female_score / (male_score + female_score)
                return 'female', confidence
                
        except Exception as e:
            print(f"❌ Error in rule-based classification: {e}")
            return 'unknown', 0
    
    def _simple_gender_heuristics(self, face_image):
        """
        Fallback gender classification using simple image analysis
        
        Args:
            face_image: Face image region
            
        Returns:
            Tuple of (gender, confidence)
        """
        try:
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(face_image, cv2.COLOR_RGB2HSV)
            
            # Simple heuristics based on color distribution
            # This is a very basic approach and not very reliable
            
            # Calculate average brightness
            brightness = np.mean(hsv[:, :, 2])
            
            # Calculate color variation
            color_var = np.std(hsv[:, :, 1])
            
            # Very simple rules (not reliable, just for demo)
            if brightness > 120 and color_var < 30:
                return 'female', 0.6  # Smoother skin assumption
            else:
                return 'male', 0.6
                
        except Exception as e:
            print(f"❌ Error in simple heuristics: {e}")
            return 'unknown', 0
    
    def draw_face_detections(self, frame, bbox, gender, confidence):
        """
        Draw face detection results on frame
        
        Args:
            frame: OpenCV image frame
            bbox: Vehicle bounding box
            gender: Detected gender
            confidence: Classification confidence
            
        Returns:
            Frame with drawn detections
        """
        if gender == 'unknown':
            return frame
        
        frame_copy = frame.copy()
        x1, y1, x2, y2 = bbox
        
        # Color coding for gender
        color = (255, 0, 255) if gender == 'female' else (0, 255, 255)  # Pink for female, yellow for male
        
        # Draw gender label on vehicle
        label = f"Driver: {gender.title()} ({confidence:.2f})"
        label_pos = (x1, y1 - 10)
        
        cv2.putText(frame_copy, label, label_pos, 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame_copy
    
    def is_ready(self):
        """Check if gender classifier is ready"""
        return self.face_detection is not None and self.face_mesh is not None