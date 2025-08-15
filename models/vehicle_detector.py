"""
YOLOv5 Vehicle Detection optimized for OPPO A92
Lightweight nano model for mobile performance
"""
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import os
import requests
from pathlib import Path

class VehicleDetector:
    def __init__(self, model_path='models/yolov5n.pt', confidence_threshold=0.5):
        """
        Initialize YOLOv5 Nano for vehicle detection on OPPO A92
        
        Args:
            model_path: Path to YOLOv5 nano model
            confidence_threshold: Detection confidence threshold
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = 0.45
        self.model = None
        
        # Vehicle classes we're interested in (COCO dataset)
        self.vehicle_classes = {
            2: 'car',
            3: 'motorcycle', 
            5: 'bus',
            7: 'truck'
        }
        
        self._load_model()
    
    def _load_model(self):
        """Load YOLOv5 nano model, download if necessary"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs('models', exist_ok=True)
            
            # Download YOLOv5n if not present
            if not os.path.exists(self.model_path):
                print("📥 Downloading YOLOv5n model for OPPO A92...")
                self._download_model()
            
            # Load model with CPU/GPU detection
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"🔧 Loading YOLOv5n on {device} for OPPO A92 optimization...")
            
            self.model = YOLO(self.model_path)
            self.model.to(device)
            
            print("✅ YOLOv5n vehicle detector ready!")
            
        except Exception as e:
            print(f"❌ Error loading YOLOv5 model: {e}")
            self.model = None
    
    def _download_model(self):
        """Download YOLOv5n model"""
        try:
            # YOLOv5n is the smallest and fastest model
            model_url = "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt"
            
            print("Downloading YOLOv5n model...")
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            with open(self.model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("✅ YOLOv5n model downloaded successfully!")
            
        except Exception as e:
            print(f"❌ Error downloading model: {e}")
            # Fallback to automatic download by ultralytics
            self.model_path = 'yolov5n.pt'
    
    def detect(self, frame):
        """
        Detect vehicles in frame
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            List of detected vehicles with bounding boxes and confidence
        """
        if self.model is None:
            return []
        
        try:
            # Resize frame for processing efficiency on OPPO A92
            height, width = frame.shape[:2]
            if width > 640:  # Optimize for mobile processing
                scale = 640 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame_resized = cv2.resize(frame, (new_width, new_height))
            else:
                frame_resized = frame
                scale = 1.0
            
            # Run inference
            results = self.model(frame_resized, 
                               conf=self.confidence_threshold,
                               iou=self.iou_threshold,
                               verbose=False)
            
            detections = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get class ID and confidence
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        
                        # Filter for vehicle classes only
                        if class_id in self.vehicle_classes:
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            
                            # Scale coordinates back to original frame size
                            x1 = int(x1 / scale)
                            y1 = int(y1 / scale)
                            x2 = int(x2 / scale)
                            y2 = int(y2 / scale)
                            
                            detection = {
                                'class': self.vehicle_classes[class_id],
                                'confidence': confidence,
                                'bbox': [x1, y1, x2, y2],
                                'center': [(x1 + x2) // 2, (y1 + y2) // 2],
                                'area': (x2 - x1) * (y2 - y1)
                            }
                            
                            detections.append(detection)
            
            # Sort by confidence (highest first)
            detections.sort(key=lambda x: x['confidence'], reverse=True)
            
            return detections
            
        except Exception as e:
            print(f"❌ Error in vehicle detection: {e}")
            return []
    
    def draw_detections(self, frame, detections):
        """
        Draw detection results on frame
        
        Args:
            frame: OpenCV image frame
            detections: List of vehicle detections
            
        Returns:
            Frame with drawn detections
        """
        frame_copy = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            vehicle_class = detection['class']
            
            # Color coding for different vehicle types
            colors = {
                'car': (0, 255, 0),      # Green
                'motorcycle': (255, 0, 0), # Blue  
                'bus': (0, 255, 255),    # Yellow
                'truck': (255, 0, 255)   # Magenta
            }
            color = colors.get(vehicle_class, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{vehicle_class}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame_copy, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame_copy, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame_copy
    
    def is_ready(self):
        """Check if detector is ready"""
        return self.model is not None