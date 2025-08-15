from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import cv2
import threading
import time
import json
from datetime import datetime
import os

from config import Config
from database.models import db, Vehicle, AccessLog
from database.models import EmissionStandards, LEZZones, EmissionViolations, VehicleEmissionData
from models.vehicle_detector import VehicleDetector
from models.plate_ocr import PlateOCR
from models.gender_classifier import GenderClassifier
from utils.camera_utils import CameraHandler
from utils.notification import NotificationManager
from utils.emission_calculator import EmissionCalculator
from models.emission_detector import EmissionDetector
from api.government_integration import GovernmentAPI, AutoReportingService

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize AI components
vehicle_detector = None
plate_ocr = None
gender_classifier = None
camera_handler = None
notification_manager = None

# Initialize emission control components
emission_detector = None
emission_calculator = None
government_api = None
auto_reporting_service = None

# Global variables
processing_active = False
current_frame = None

def initialize_ai_models():
    """Initialize AI models for OPPO A92 optimization"""
    global vehicle_detector, plate_ocr, gender_classifier, notification_manager
    global emission_detector, emission_calculator, government_api, auto_reporting_service
    
    try:
        print("Initializing AI models for OPPO A92...")
        vehicle_detector = VehicleDetector()
        plate_ocr = PlateOCR()
        gender_classifier = GenderClassifier()
        notification_manager = NotificationManager()
        
        # Initialize emission control components
        print("Initializing emission control components...")
        emission_detector = EmissionDetector()
        emission_calculator = EmissionCalculator()
        government_api = GovernmentAPI()
        auto_reporting_service = AutoReportingService()
        
        # Start auto-reporting service
        auto_reporting_service.start_auto_reporting()
        
        print("AI models initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing AI models: {e}")
        return False

def initialize_camera():
    """Initialize camera connection for OPPO A92"""
    global camera_handler
    
    try:
        print("Connecting to OPPO A92 camera...")
        camera_handler = CameraHandler(
            app.config['CAMERA_STREAM_URL'],
            app.config['PROCESSING_RESOLUTION']
        )
        return camera_handler.connect()
    except Exception as e:
        print(f"Error connecting to camera: {e}")
        return False

def process_video_stream():
    """Main video processing loop optimized for OPPO A92"""
    global processing_active, current_frame
    
    while processing_active:
        try:
            if not camera_handler or not camera_handler.is_connected():
                time.sleep(1)
                continue
                
            frame = camera_handler.get_frame()
            if frame is None:
                time.sleep(0.1)
                continue
                
            current_frame = frame.copy()
            
            # AI Processing Pipeline
            detections = {}
            
            # 1. Vehicle Detection
            if vehicle_detector:
                vehicles = vehicle_detector.detect(frame)
                detections['vehicles'] = vehicles
                
            # 2. License Plate OCR
            if plate_ocr and detections.get('vehicles'):
                for vehicle in detections['vehicles']:
                    plate_text = plate_ocr.extract_text(frame, vehicle['bbox'])
                    vehicle['license_plate'] = plate_text
                    
            # 3. Gender Classification
            if gender_classifier and detections.get('vehicles'):
                for vehicle in detections['vehicles']:
                    gender = gender_classifier.classify(frame, vehicle['bbox'])
                    vehicle['driver_gender'] = gender
            
            # 4. Emission Detection (New)
            if emission_detector and detections.get('vehicles'):
                for vehicle in detections['vehicles']:
                    emission_data = emission_detector.assess_vehicle_condition(frame, vehicle['bbox'])
                    vehicle['emission_data'] = emission_data
                    
                    # Check LEZ compliance
                    if emission_calculator:
                        vehicle_info = {
                            'vehicle_type': vehicle.get('class', 'unknown'),
                            'euro_standard': emission_data.get('estimated_euro_standard', 'Unknown'),
                            'manufacture_year': emission_data.get('age_data', {}).get('estimated_manufacture_year', 2020)
                        }
                        # This would check against active LEZ zones
                        # For now, we'll add basic compliance check
                        vehicle['emission_compliance'] = emission_data.get('likely_emission_compliant', True)
            
            # Process detections and update database
            if detections.get('vehicles'):
                process_detections(detections['vehicles'])
            
            # Emit real-time updates via WebSocket
            socketio.emit('detection_update', {
                'timestamp': datetime.now().isoformat(),
                'detections': detections
            })
            
            # Control frame rate for OPPO A92 performance
            time.sleep(1.0 / app.config['MAX_FPS'])
            
        except Exception as e:
            print(f"Error in video processing: {e}")
            time.sleep(1)

def process_detections(vehicles):
    """Process vehicle detections and update database"""
    try:
        for vehicle in vehicles:
            license_plate = vehicle.get('license_plate', '')
            if not license_plate:
                continue
                
            # Check if vehicle is registered
            registered_vehicle = Vehicle.query.filter_by(license_plate=license_plate).first()
            
            # Log access attempt
            access_log = AccessLog(
                license_plate=license_plate,
                vehicle_type=vehicle.get('class', 'unknown'),
                driver_gender=vehicle.get('driver_gender', 'unknown'),
                confidence=vehicle.get('confidence', 0),
                action='entry',
                authorized=registered_vehicle is not None,
                timestamp=datetime.now()
            )
            
            db.session.add(access_log)
            db.session.commit()
            
            # Send notification for unauthorized vehicles
            if not registered_vehicle and app.config['ALERT_UNKNOWN_VEHICLES']:
                notification_manager.send_alert(
                    f"Unauthorized vehicle detected: {license_plate}",
                    vehicle
                )
                
    except Exception as e:
        print(f"Error processing detections: {e}")

@app.route('/')
def dashboard():
    """Main dashboard"""
    recent_logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(10).all()
    total_vehicles = Vehicle.query.count()
    return render_template('dashboard.html', 
                         recent_logs=recent_logs,
                         total_vehicles=total_vehicles)

@app.route('/camera')
def camera_view():
    """Live camera view with AI detection overlay"""
    return render_template('camera.html')

@app.route('/vehicles')
def vehicles():
    """Vehicle management page"""
    all_vehicles = Vehicle.query.all()
    return render_template('vehicles.html', vehicles=all_vehicles)

@app.route('/logs')
def access_logs():
    """Access logs page"""
    page = request.args.get('page', 1, type=int)
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('logs.html', logs=logs)

# ==========================================
# LEZ AND EMISSION CONTROL ROUTES
# ==========================================

@app.route('/lez')
def lez_dashboard():
    """LEZ Management Dashboard"""
    try:
        # Get LEZ zones
        lez_zones = LEZZones.query.all()
        active_zones_count = LEZZones.query.filter_by(is_active=True).count()
        
        # Get recent violations
        recent_violations = EmissionViolations.query.order_by(
            EmissionViolations.timestamp.desc()
        ).limit(10).all()
        
        # Calculate statistics
        today = datetime.now().date()
        today_violations = EmissionViolations.query.filter(
            EmissionViolations.timestamp >= today
        ).count()
        
        total_fines = db.session.query(db.func.sum(EmissionViolations.fine_amount)).scalar() or 0
        
        # Calculate compliance rate (simplified)
        total_detections = AccessLog.query.filter(AccessLog.timestamp >= today).count()
        compliant_detections = total_detections - today_violations
        compliance_rate = compliant_detections / total_detections if total_detections > 0 else 1.0
        
        # Count clean vs polluting vehicles (simplified)
        clean_vehicles = total_detections - today_violations
        polluting_vehicles = today_violations
        
        return render_template('lez_dashboard.html',
                             lez_zones=lez_zones,
                             active_zones_count=active_zones_count,
                             recent_violations=recent_violations,
                             today_violations=today_violations,
                             total_fines=total_fines,
                             compliance_rate=compliance_rate,
                             clean_vehicles=clean_vehicles,
                             polluting_vehicles=polluting_vehicles)
    
    except Exception as e:
        print(f"❌ Error loading LEZ dashboard: {e}")
        return render_template('lez_dashboard.html',
                             lez_zones=[], active_zones_count=0,
                             recent_violations=[], today_violations=0,
                             total_fines=0, compliance_rate=1.0,
                             clean_vehicles=0, polluting_vehicles=0)

@app.route('/api/vehicles', methods=['GET', 'POST'])
def api_vehicles():
    """Vehicle management API"""
    if request.method == 'POST':
        data = request.get_json()
        vehicle = Vehicle(
            license_plate=data['license_plate'],
            owner_name=data['owner_name'],
            vehicle_type=data['vehicle_type'],
            status=data.get('status', 'active')
        )
        db.session.add(vehicle)
        db.session.commit()
        return jsonify({'status': 'success', 'id': vehicle.id})
    
    vehicles = Vehicle.query.all()
    return jsonify([{
        'id': v.id,
        'license_plate': v.license_plate,
        'owner_name': v.owner_name,
        'vehicle_type': v.vehicle_type,
        'status': v.status
    } for v in vehicles])

@app.route('/api/camera/status')
def camera_status():
    """Check camera connection status"""
    status = {
        'connected': camera_handler.is_connected() if camera_handler else False,
        'processing': processing_active,
        'camera_url': app.config['CAMERA_STREAM_URL']
    }
    return jsonify(status)

@app.route('/api/camera/start')
def start_processing():
    """Start video processing"""
    global processing_active
    
    if not processing_active:
        processing_active = True
        thread = threading.Thread(target=process_video_stream)
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'started'})
    
    return jsonify({'status': 'already_running'})

@app.route('/api/camera/stop')
def stop_processing():
    """Stop video processing"""
    global processing_active
    processing_active = False
    return jsonify({'status': 'stopped'})

# ==========================================
# LEZ AND EMISSION CONTROL API ROUTES
# ==========================================

@app.route('/api/lez/zones', methods=['GET', 'POST'])
def api_lez_zones():
    """LEZ zones management API"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Create new LEZ zone
            zone = LEZZones(
                zone_name=data['zone_name'],
                zone_code=data['zone_code'],
                coordinates=data.get('coordinates', '[]'),
                restriction_hours=data.get('restriction_hours'),
                allowed_euro_standards=data.get('allowed_euro_standards', '[]'),
                fine_amount=data.get('fine_amount', 500000),
                is_active=True
            )
            
            db.session.add(zone)
            db.session.commit()
            
            return jsonify({'status': 'success', 'id': zone.id})
        
        except Exception as e:
            print(f"❌ Error creating LEZ zone: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    # GET request - return all zones
    zones = LEZZones.query.all()
    return jsonify([zone.to_dict() for zone in zones])

@app.route('/api/lez/zones/<int:zone_id>', methods=['PUT', 'DELETE'])
def api_lez_zone_details(zone_id):
    """Manage specific LEZ zone"""
    zone = LEZZones.query.get_or_404(zone_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            
            zone.zone_name = data.get('zone_name', zone.zone_name)
            zone.restriction_hours = data.get('restriction_hours', zone.restriction_hours)
            zone.allowed_euro_standards = data.get('allowed_euro_standards', zone.allowed_euro_standards)
            zone.fine_amount = data.get('fine_amount', zone.fine_amount)
            zone.is_active = data.get('is_active', zone.is_active)
            
            db.session.commit()
            return jsonify({'status': 'success'})
        
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(zone)
            db.session.commit()
            return jsonify({'status': 'success'})
        
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/lez/zones/<int:zone_id>/toggle', methods=['POST'])
def api_toggle_lez_zone(zone_id):
    """Toggle LEZ zone active status"""
    try:
        zone = LEZZones.query.get_or_404(zone_id)
        zone.is_active = not zone.is_active
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'is_active': zone.is_active
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/lez/statistics')
def api_lez_statistics():
    """Get LEZ statistics"""
    try:
        today = datetime.now().date()
        
        stats = {
            'active_zones': LEZZones.query.filter_by(is_active=True).count(),
            'total_zones': LEZZones.query.count(),
            'today_violations': EmissionViolations.query.filter(
                EmissionViolations.timestamp >= today
            ).count(),
            'total_violations': EmissionViolations.query.count(),
            'total_fines': float(db.session.query(
                db.func.sum(EmissionViolations.fine_amount)
            ).scalar() or 0),
            'compliance_rate': 0.85,  # Simplified calculation
            'violation_types': {
                'lez_entry': EmissionViolations.query.filter_by(violation_type='lez_entry').count(),
                'smoke_detection': EmissionViolations.query.filter_by(violation_type='smoke_detection').count(),
                'age_restriction': EmissionViolations.query.filter_by(violation_type='age_restriction').count()
            }
        }
        
        return jsonify(stats)
    
    except Exception as e:
        print(f"❌ Error getting LEZ statistics: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@app.route('/api/emission/detect', methods=['POST'])
def api_emission_detect():
    """Emission detection API endpoint"""
    try:
        if not emission_detector:
            return jsonify({'error': 'Emission detector not available'}), 503
        
        # This would typically receive image data
        # For now, return mock detection results
        detection_result = {
            'smoke_detected': False,
            'smoke_level': 0.1,
            'estimated_age_category': 'moderate',
            'estimated_euro_standard': 'Euro 4',
            'condition_score': 0.7,
            'emission_compliance': True,
            'recommendations': ['regular_maintenance']
        }
        
        return jsonify(detection_result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicle/lookup/<license_plate>')
def api_vehicle_lookup(license_plate):
    """Look up vehicle information from government database"""
    try:
        if not government_api:
            return jsonify({'error': 'Government API not available'}), 503
        
        result = government_api.lookup_vehicle(license_plate)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/emission/report', methods=['POST'])
def api_emission_report():
    """Generate emission report"""
    try:
        if not emission_calculator:
            return jsonify({'error': 'Emission calculator not available'}), 503
        
        data = request.get_json()
        time_period = data.get('time_period', 'daily')
        
        # Get recent vehicle data (simplified)
        recent_logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(100).all()
        
        # Convert to format expected by emission calculator
        vehicles_data = []
        for log in recent_logs:
            vehicles_data.append({
                'license_plate': log.license_plate,
                'vehicle_type': log.vehicle_type,
                'euro_standard': 'Euro 4',  # Default, would be looked up
                'manufacture_year': 2018    # Default, would be looked up
            })
        
        report = emission_calculator.generate_environmental_report(vehicles_data, time_period)
        return jsonify(report)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lez/report/download')
def api_download_lez_report():
    """Download LEZ compliance report"""
    try:
        # Generate report data
        zones = LEZZones.query.all()
        violations = EmissionViolations.query.order_by(EmissionViolations.timestamp.desc()).limit(1000).all()
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'zones': [zone.to_dict() for zone in zones],
            'violations': [violation.to_dict() for violation in violations],
            'summary': {
                'total_zones': len(zones),
                'active_zones': sum(1 for zone in zones if zone.is_active),
                'total_violations': len(violations),
                'total_fines': sum(float(v.fine_amount or 0) for v in violations)
            }
        }
        
        # Return as downloadable JSON file
        response = app.response_class(
            response=json.dumps(report_data, indent=2, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
        response.headers['Content-Disposition'] = f'attachment; filename=lez_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def video_stream():
    """Generate video stream for web interface"""
    while True:
        if current_frame is not None:
            # Encode frame as JPEG
            ret, jpeg = cv2.imencode('.jpg', current_frame)
            if ret:
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(1.0 / app.config['MAX_FPS'])

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(video_stream(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'status': 'Connected to OPPO A92 Vehicle Control'})

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Initialize AI models
    ai_ready = initialize_ai_models()
    
    # Initialize camera
    camera_ready = initialize_camera()
    
    if ai_ready and camera_ready:
        print("✅ OPPO A92 Vehicle Control System ready!")
    else:
        print("⚠️  System starting with limited functionality")
    
    # Start the application
    socketio.run(app, 
                host=app.config['HOST'], 
                port=app.config['PORT'], 
                debug=app.config['DEBUG'])