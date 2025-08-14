"""
Database initialization script for OPPO A92 Vehicle Control System
"""
from flask import Flask
from models import db, Vehicle, AccessLog, SystemSettings, Alert
import os

def init_database():
    """Initialize database with default data"""
    
    # Create Flask app for database context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicle_control.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add default system settings
        default_settings = [
            ('camera_ip', '192.168.1.100', 'OPPO A92 IP address'),
            ('camera_port', '8080', 'Camera streaming port'),
            ('detection_threshold', '0.5', 'AI detection confidence threshold'),
            ('max_fps', '12', 'Maximum processing FPS for OPPO A92'),
            ('processing_resolution_width', '640', 'Processing frame width'),
            ('processing_resolution_height', '480', 'Processing frame height'),
            ('alert_unknown_vehicles', 'true', 'Send alerts for unknown vehicles'),
            ('log_all_detections', 'true', 'Log all vehicle detections'),
            ('auto_save_images', 'true', 'Automatically save detection images'),
        ]
        
        for key, value, description in default_settings:
            if not SystemSettings.query.filter_by(key=key).first():
                setting = SystemSettings(key=key, value=value, description=description)
                db.session.add(setting)
        
        # Add sample vehicles for testing
        sample_vehicles = [
            ('29A-12345', 'Nguyễn Văn A', 'motorcycle'),
            ('30G-67890', 'Trần Thị B', 'car'),
            ('51H-11111', 'Lê Văn C', 'motorcycle'),
        ]
        
        for license_plate, owner_name, vehicle_type in sample_vehicles:
            if not Vehicle.query.filter_by(license_plate=license_plate).first():
                vehicle = Vehicle(
                    license_plate=license_plate,
                    owner_name=owner_name,
                    vehicle_type=vehicle_type,
                    status='active'
                )
                db.session.add(vehicle)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print(f"📊 Total registered vehicles: {Vehicle.query.count()}")
        print(f"⚙️  System settings configured: {SystemSettings.query.count()}")

if __name__ == '__main__':
    init_database()