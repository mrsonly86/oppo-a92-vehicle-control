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
    
    # ==========================================
    # EMISSION CONTROL AND LEZ CONFIGURATION
    # ==========================================
    
    # Emission Detection Settings
    EMISSION_DETECTION_ENABLED = os.environ.get('EMISSION_DETECTION_ENABLED', 'True').lower() == 'true'
    SMOKE_DETECTION_THRESHOLD = float(os.environ.get('SMOKE_DETECTION_THRESHOLD', 0.6))
    VEHICLE_AGE_ESTIMATION_ENABLED = True
    EMISSION_REPORTING_INTERVAL_MINUTES = int(os.environ.get('EMISSION_REPORTING_INTERVAL', 30))
    
    # LEZ (Low Emission Zone) Settings
    LEZ_ENFORCEMENT_ENABLED = os.environ.get('LEZ_ENFORCEMENT_ENABLED', 'True').lower() == 'true'
    DEFAULT_LEZ_FINE_AMOUNT = int(os.environ.get('DEFAULT_LEZ_FINE_AMOUNT', 500000))  # VND
    LEZ_COMPLIANCE_GRACE_PERIOD_DAYS = int(os.environ.get('LEZ_GRACE_PERIOD', 30))
    
    # Government Integration Settings
    GOVERNMENT_API_ENABLED = os.environ.get('GOVERNMENT_API_ENABLED', 'False').lower() == 'true'
    VEHICLE_REGISTRY_URL = os.environ.get('VEHICLE_REGISTRY_URL', 'https://api.dkxe.gov.vn')
    TRAFFIC_POLICE_URL = os.environ.get('TRAFFIC_POLICE_URL', 'https://api.csgt.gov.vn')
    ENVIRONMENT_DEPT_URL = os.environ.get('ENVIRONMENT_DEPT_URL', 'https://api.monre.gov.vn')
    
    # API Keys (would be provided by government agencies)
    GOV_API_KEY = os.environ.get('GOV_API_KEY', 'demo_api_key')
    GOV_API_SECRET = os.environ.get('GOV_API_SECRET', 'demo_secret')
    ORGANIZATION_ID = os.environ.get('ORG_ID', 'oppo_a92_system')
    
    # Emission Standards (Vietnamese context)
    EURO_STANDARDS_HIERARCHY = ['Euro 6', 'Euro 5', 'Euro 4', 'Euro 3', 'Euro 2', 'Euro 1']
    MIN_EURO_STANDARD_LEZ = os.environ.get('MIN_EURO_STANDARD_LEZ', 'Euro 4')
    VEHICLE_AGE_LIMIT_YEARS = int(os.environ.get('VEHICLE_AGE_LIMIT_YEARS', 15))
    
    # Auto-reporting Settings
    AUTO_REPORT_VIOLATIONS = os.environ.get('AUTO_REPORT_VIOLATIONS', 'True').lower() == 'true'
    AUTO_REPORT_ENVIRONMENTAL_DATA = os.environ.get('AUTO_REPORT_ENV_DATA', 'True').lower() == 'true'
    BATCH_PROCESSING_SIZE = int(os.environ.get('BATCH_PROCESSING_SIZE', 10))
    
    # Mobile App Settings for Drivers
    MOBILE_API_ENABLED = os.environ.get('MOBILE_API_ENABLED', 'True').lower() == 'true'
    DRIVER_EDUCATION_ENABLED = True
    LEZ_NAVIGATION_ENABLED = True
    
    # Performance Settings for Emission AI (OPPO A92 Optimized)
    EMISSION_AI_CONFIDENCE_THRESHOLD = 0.6
    SMOKE_DETECTION_FPS = 2  # Process every 2nd frame for smoke detection
    AGE_ESTIMATION_INTERVAL_FRAMES = 10  # Estimate age every 10 frames
    EMISSION_MEMORY_LIMIT_MB = 200  # Additional memory limit for emission AI