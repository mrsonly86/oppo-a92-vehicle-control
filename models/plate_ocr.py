"""
EasyOCR License Plate Recognition for Vietnamese plates
Optimized for OPPO A92 performance
"""
import cv2
import numpy as np
import easyocr
import re
from typing import List, Tuple, Optional

class PlateOCR:
    def __init__(self, languages=['vi', 'en'], confidence_threshold=0.6):
        """
        Initialize EasyOCR for Vietnamese license plate recognition
        
        Args:
            languages: List of languages to recognize (Vietnamese + English)
            confidence_threshold: OCR confidence threshold
        """
        self.languages = languages
        self.confidence_threshold = confidence_threshold
        self.reader = None
        
        # Vietnamese license plate patterns
        self.plate_patterns = [
            r'^[0-9]{2}[A-Z]{1,2}-[0-9]{3,5}$',  # 29A-12345, 51H-1234
            r'^[0-9]{2}[A-Z]{1}-[0-9]{3,4}\.[0-9]{2}$',  # 30G-123.45
            r'^[A-Z]{2}-[0-9]{4}$',  # LD-1234 (diplomatic)
        ]
        
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Initialize EasyOCR reader"""
        try:
            print("🔧 Initializing EasyOCR for Vietnamese plates on OPPO A92...")
            
            # Initialize with Vietnamese and English support
            self.reader = easyocr.Reader(
                self.languages,
                gpu=False,  # Use CPU for mobile compatibility
                verbose=False
            )
            
            print("✅ EasyOCR license plate reader ready!")
            
        except Exception as e:
            print(f"❌ Error initializing EasyOCR: {e}")
            self.reader = None
    
    def extract_text(self, frame, bbox, vehicle_detection=None):
        """
        Extract license plate text from vehicle bounding box
        
        Args:
            frame: OpenCV image frame
            bbox: Vehicle bounding box [x1, y1, x2, y2]
            vehicle_detection: Additional vehicle detection info
            
        Returns:
            Detected license plate text or empty string
        """
        if self.reader is None:
            return ""
        
        try:
            x1, y1, x2, y2 = bbox
            
            # Extract vehicle region
            vehicle_region = frame[y1:y2, x1:x2]
            
            if vehicle_region.size == 0:
                return ""
            
            # Preprocess for better OCR results
            processed_region = self._preprocess_for_ocr(vehicle_region)
            
            # Find potential license plate regions
            plate_regions = self._find_plate_regions(processed_region)
            
            best_plate_text = ""
            best_confidence = 0
            
            # Try OCR on each potential plate region
            for plate_region in plate_regions:
                plate_text, confidence = self._perform_ocr(plate_region)
                
                if confidence > best_confidence and self._is_valid_plate(plate_text):
                    best_plate_text = plate_text
                    best_confidence = confidence
            
            # If no plate regions found, try on whole vehicle region
            if not best_plate_text:
                plate_text, confidence = self._perform_ocr(processed_region)
                if confidence > self.confidence_threshold and self._is_valid_plate(plate_text):
                    best_plate_text = plate_text
            
            return self._clean_plate_text(best_plate_text)
            
        except Exception as e:
            print(f"❌ Error in license plate OCR: {e}")
            return ""
    
    def _preprocess_for_ocr(self, image):
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image region
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Resize for better OCR (if too small)
        height, width = gray.shape
        if height < 50 or width < 100:
            scale_factor = max(50/height, 100/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        return gray
    
    def _find_plate_regions(self, image):
        """
        Find potential license plate regions in vehicle image
        
        Args:
            image: Preprocessed vehicle image
            
        Returns:
            List of potential plate regions
        """
        regions = []
        
        try:
            # Apply edge detection
            edges = cv2.Canny(image, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            height, width = image.shape
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter based on license plate dimensions
                aspect_ratio = w / h if h > 0 else 0
                area = w * h
                
                # Vietnamese license plates typically have aspect ratio 2-5
                if (2 < aspect_ratio < 5 and 
                    area > 500 and  # Minimum area
                    w > 50 and h > 15 and  # Minimum dimensions
                    area < (width * height * 0.3)):  # Maximum area (30% of image)
                    
                    # Extract region with some padding
                    x_pad = max(0, x - 5)
                    y_pad = max(0, y - 5)
                    x_end = min(width, x + w + 5)
                    y_end = min(height, y + h + 5)
                    
                    region = image[y_pad:y_end, x_pad:x_end]
                    if region.size > 0:
                        regions.append(region)
            
            # Sort by area (largest first)
            regions.sort(key=lambda r: r.shape[0] * r.shape[1], reverse=True)
            
            # Return top 3 candidates
            return regions[:3]
            
        except Exception as e:
            print(f"❌ Error finding plate regions: {e}")
            return [image]  # Return original image as fallback
    
    def _perform_ocr(self, image):
        """
        Perform OCR on image region
        
        Args:
            image: Image to perform OCR on
            
        Returns:
            Tuple of (text, confidence)
        """
        try:
            results = self.reader.readtext(image, detail=1)
            
            if not results:
                return "", 0
            
            # Combine all detected text and calculate average confidence
            full_text = ""
            total_confidence = 0
            
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Minimum confidence per character
                    full_text += text
                    total_confidence += confidence
            
            avg_confidence = total_confidence / len(results) if results else 0
            
            return full_text.strip(), avg_confidence
            
        except Exception as e:
            print(f"❌ Error in OCR: {e}")
            return "", 0
    
    def _is_valid_plate(self, text):
        """
        Check if text matches Vietnamese license plate patterns
        
        Args:
            text: Text to validate
            
        Returns:
            Boolean indicating if text is a valid plate
        """
        if len(text) < 5:
            return False
        
        # Clean and normalize text
        text = re.sub(r'[^A-Z0-9\-\.]', '', text.upper())
        
        # Check against known patterns
        for pattern in self.plate_patterns:
            if re.match(pattern, text):
                return True
        
        # Additional heuristic checks
        # Must contain numbers and letters
        has_numbers = bool(re.search(r'[0-9]', text))
        has_letters = bool(re.search(r'[A-Z]', text))
        
        return has_numbers and has_letters and 5 <= len(text) <= 12
    
    def _clean_plate_text(self, text):
        """
        Clean and format license plate text
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned license plate text
        """
        if not text:
            return ""
        
        # Remove unwanted characters
        text = re.sub(r'[^A-Z0-9\-\.]', '', text.upper())
        
        # Common OCR corrections for Vietnamese plates
        corrections = {
            'O': '0',  # O to 0
            'I': '1',  # I to 1
            'S': '5',  # S to 5
            'B': '8',  # B to 8
        }
        
        # Apply corrections to number parts
        parts = text.split('-')
        if len(parts) == 2:
            # First part: numbers and letters
            # Second part: mostly numbers
            second_part = parts[1]
            for old, new in corrections.items():
                if old in second_part:
                    second_part = second_part.replace(old, new)
            text = f"{parts[0]}-{second_part}"
        
        return text
    
    def is_ready(self):
        """Check if OCR reader is ready"""
        return self.reader is not None