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

# ==========================================
# EMISSION CONTROL AND LEZ MODELS
# ==========================================

class EmissionStandards(db.Model):
    """Emission standards by vehicle type and manufacture year"""
    __tablename__ = 'emission_standards'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(50), nullable=False)  # motorcycle, car, truck, bus
    manufacture_year_start = db.Column(db.Integer, nullable=False)
    manufacture_year_end = db.Column(db.Integer, nullable=False)
    euro_standard = db.Column(db.String(10), nullable=False)  # Euro 3, Euro 4, Euro 5, etc.
    co_limit = db.Column(db.Float)  # CO emission limit (g/km)
    nox_limit = db.Column(db.Float)  # NOx emission limit (g/km)
    pm_limit = db.Column(db.Float)  # Particulate matter limit (g/km)
    hc_limit = db.Column(db.Float)  # Hydrocarbon limit (g/km)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmissionStandards {self.vehicle_type} {self.manufacture_year_start}-{self.manufacture_year_end} {self.euro_standard}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_type': self.vehicle_type,
            'manufacture_year_start': self.manufacture_year_start,
            'manufacture_year_end': self.manufacture_year_end,
            'euro_standard': self.euro_standard,
            'co_limit': self.co_limit,
            'nox_limit': self.nox_limit,
            'pm_limit': self.pm_limit,
            'hc_limit': self.hc_limit,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class LEZZones(db.Model):
    """Low Emission Zone definitions"""
    __tablename__ = 'lez_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_name = db.Column(db.String(100), nullable=False)
    zone_code = db.Column(db.String(20), unique=True, nullable=False)
    coordinates = db.Column(db.Text, nullable=False)  # JSON string of polygon coordinates
    restriction_hours = db.Column(db.String(50))  # e.g., "06:00-22:00", "24/7"
    allowed_euro_standards = db.Column(db.Text)  # JSON array of allowed standards
    vehicle_type_restrictions = db.Column(db.Text)  # JSON object of restrictions by type
    fine_amount = db.Column(db.Numeric(10, 2), default=0)  # Fine for violation in VND
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LEZZone {self.zone_name} ({self.zone_code})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'zone_name': self.zone_name,
            'zone_code': self.zone_code,
            'coordinates': self.coordinates,
            'restriction_hours': self.restriction_hours,
            'allowed_euro_standards': self.allowed_euro_standards,
            'vehicle_type_restrictions': self.vehicle_type_restrictions,
            'fine_amount': float(self.fine_amount) if self.fine_amount else 0,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EmissionViolations(db.Model):
    """Emission violation records"""
    __tablename__ = 'emission_violations'
    
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), nullable=False, index=True)
    violation_type = db.Column(db.String(50), nullable=False)  # lez_entry, smoke_detection, age_restriction
    lez_zone_id = db.Column(db.Integer, db.ForeignKey('lez_zones.id'))
    detected_vehicle_type = db.Column(db.String(50))
    estimated_year = db.Column(db.Integer)
    euro_standard = db.Column(db.String(10))
    smoke_level = db.Column(db.Float)  # 0-1 intensity of smoke detected
    vehicle_condition_score = db.Column(db.Float)  # 0-1 overall condition assessment
    confidence = db.Column(db.Float)  # AI detection confidence
    fine_amount = db.Column(db.Numeric(10, 2))
    fine_status = db.Column(db.String(20), default='pending')  # pending, issued, paid, cancelled
    evidence_image_path = db.Column(db.String(255))
    evidence_video_path = db.Column(db.String(255))
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    camera_id = db.Column(db.String(50))
    reported_to_authority = db.Column(db.Boolean, default=False)
    authority_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processed_at = db.Column(db.DateTime)
    
    # Relationship
    lez_zone = db.relationship('LEZZones', backref=db.backref('violations', lazy=True))
    
    def __repr__(self):
        return f'<EmissionViolation {self.license_plate} - {self.violation_type} at {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_plate': self.license_plate,
            'violation_type': self.violation_type,
            'lez_zone_id': self.lez_zone_id,
            'detected_vehicle_type': self.detected_vehicle_type,
            'estimated_year': self.estimated_year,
            'euro_standard': self.euro_standard,
            'smoke_level': self.smoke_level,
            'vehicle_condition_score': self.vehicle_condition_score,
            'confidence': self.confidence,
            'fine_amount': float(self.fine_amount) if self.fine_amount else 0,
            'fine_status': self.fine_status,
            'evidence_image_path': self.evidence_image_path,
            'evidence_video_path': self.evidence_video_path,
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'camera_id': self.camera_id,
            'reported_to_authority': self.reported_to_authority,
            'authority_response': self.authority_response,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'lez_zone': self.lez_zone.to_dict() if self.lez_zone else None
        }

class VehicleEmissionData(db.Model):
    """Extended emission data for registered vehicles"""
    __tablename__ = 'vehicle_emission_data'
    
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), nullable=False, index=True)
    manufacture_year = db.Column(db.Integer)
    engine_displacement = db.Column(db.Integer)  # cc
    fuel_type = db.Column(db.String(20))  # gasoline, diesel, electric, hybrid
    euro_standard = db.Column(db.String(10))
    last_emission_test_date = db.Column(db.Date)
    last_emission_test_result = db.Column(db.String(20))  # pass, fail, pending
    co_emission = db.Column(db.Float)  # g/km
    nox_emission = db.Column(db.Float)  # g/km
    pm_emission = db.Column(db.Float)  # g/km
    hc_emission = db.Column(db.Float)  # g/km
    environmental_impact_score = db.Column(db.Float)  # 0-100 score
    lez_access_permitted = db.Column(db.Boolean, default=False)
    restriction_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<VehicleEmissionData {self.license_plate} - {self.euro_standard}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_plate': self.license_plate,
            'manufacture_year': self.manufacture_year,
            'engine_displacement': self.engine_displacement,
            'fuel_type': self.fuel_type,
            'euro_standard': self.euro_standard,
            'last_emission_test_date': self.last_emission_test_date.isoformat() if self.last_emission_test_date else None,
            'last_emission_test_result': self.last_emission_test_result,
            'co_emission': self.co_emission,
            'nox_emission': self.nox_emission,
            'pm_emission': self.pm_emission,
            'hc_emission': self.hc_emission,
            'environmental_impact_score': self.environmental_impact_score,
            'lez_access_permitted': self.lez_access_permitted,
            'restriction_notes': self.restriction_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }