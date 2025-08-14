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
from models.vehicle_detector import VehicleDetector
from models.plate_ocr import PlateOCR
from models.gender_classifier import GenderClassifier
from utils.camera_utils import CameraHandler
from utils.notification import NotificationManager

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

# Global variables
processing_active = False
current_frame = None

def initialize_ai_models():
    """Initialize AI models for OPPO A92 optimization"""
    global vehicle_detector, plate_ocr, gender_classifier, notification_manager
    
    try:
        print("Initializing AI models for OPPO A92...")
        vehicle_detector = VehicleDetector()
        plate_ocr = PlateOCR()
        gender_classifier = GenderClassifier()
        notification_manager = NotificationManager()
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