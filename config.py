import os

class Config:
    """Configuration class for OPPO A92 Vehicle Control System"""
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'oppo-a92-vehicle-control-secret-key'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///vehicle_control.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Camera Configuration for OPPO A92
    CAMERA_IP = os.environ.get('CAMERA_IP') or '192.168.1.100'
    CAMERA_PORT = int(os.environ.get('CAMERA_PORT', 8080))
    CAMERA_USERNAME = os.environ.get('CAMERA_USERNAME') or ''
    CAMERA_PASSWORD = os.environ.get('CAMERA_PASSWORD') or ''
    CAMERA_STREAM_URL = f'http://{CAMERA_IP}:{CAMERA_PORT}/video'
    
    # AI Model Configuration - Optimized for OPPO A92
    YOLO_MODEL_PATH = 'models/yolov5n.pt'  # Nano version for mobile
    YOLO_CONFIDENCE_THRESHOLD = 0.5
    YOLO_IOU_THRESHOLD = 0.45
    
    # EasyOCR Configuration for Vietnamese
    OCR_LANGUAGES = ['vi', 'en']  # Vietnamese and English
    OCR_CONFIDENCE_THRESHOLD = 0.6
    
    # MediaPipe Configuration
    MEDIAPIPE_CONFIDENCE_THRESHOLD = 0.7
    
    # Performance Settings for OPPO A92
    MAX_FPS = 12  # Target FPS for smooth operation
    PROCESSING_RESOLUTION = (640, 480)  # Optimized resolution
    MAX_MEMORY_USAGE = 1.5  # GB - Stay under OPPO A92 limits
    
    # Access Control Settings
    ALERT_UNKNOWN_VEHICLES = True
    LOG_ALL_DETECTIONS = True
    AUTO_SAVE_IMAGES = True
    
    # Web Interface
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))