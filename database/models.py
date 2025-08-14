from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Vehicle(db.Model):
    """Vehicle registration model"""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), unique=True, nullable=False, index=True)
    owner_name = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)  # motorcycle, car, truck
    status = db.Column(db.String(20), default='active')  # active, inactive, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with access logs (optional, via license plate)
    # Note: This is a loose relationship since access logs can have unlisted plates
    
    def __repr__(self):
        return f'<Vehicle {self.license_plate}: {self.owner_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_plate': self.license_plate,
            'owner_name': self.owner_name,
            'vehicle_type': self.vehicle_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AccessLog(db.Model):
    """Access log model for tracking vehicle entries/exits"""
    __tablename__ = 'access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), nullable=False, index=True)
    vehicle_type = db.Column(db.String(50))  # detected vehicle type
    driver_gender = db.Column(db.String(10))  # male, female, unknown
    confidence = db.Column(db.Float)  # AI detection confidence
    action = db.Column(db.String(20), nullable=False)  # entry, exit
    authorized = db.Column(db.Boolean, default=False)  # whether vehicle is registered
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    image_path = db.Column(db.String(255))  # path to captured image
    notes = db.Column(db.Text)  # additional notes
    
    def __repr__(self):
        return f'<AccessLog {self.license_plate} - {self.action} at {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_plate': self.license_plate,
            'vehicle_type': self.vehicle_type,
            'driver_gender': self.driver_gender,
            'confidence': self.confidence,
            'action': self.action,
            'authorized': self.authorized,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'image_path': self.image_path,
            'notes': self.notes
        }

class SystemSettings(db.Model):
    """System settings model"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.key}: {self.value}>'
    
    @staticmethod
    def get_setting(key, default=None):
        """Get a system setting value"""
        setting = SystemSettings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """Set a system setting value"""
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(key=key, value=value, description=description)
            db.session.add(setting)
        
        db.session.commit()
        return setting

class Alert(db.Model):
    """Alert model for notifications"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.String(50), default='warning')  # info, warning, error
    license_plate = db.Column(db.String(20))  # related license plate
    acknowledged = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Alert {self.title} - {self.created_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'alert_type': self.alert_type,
            'license_plate': self.license_plate,
            'acknowledged': self.acknowledged,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }