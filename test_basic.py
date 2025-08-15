#!/usr/bin/env python3
"""
Basic functionality test for OPPO A92 Vehicle Control System
Tests core components without AI dependencies
"""

import os
import sys

def test_imports():
    """Test basic imports"""
    print("🧪 Testing basic imports...")
    
    try:
        import flask
        print("✅ Flask - OK")
    except ImportError as e:
        print(f"❌ Flask - FAILED: {e}")
        return False
    
    try:
        import flask_socketio
        print("✅ Flask-SocketIO - OK")
    except ImportError as e:
        print(f"❌ Flask-SocketIO - FAILED: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy - OK")
    except ImportError as e:
        print(f"❌ Flask-SQLAlchemy - FAILED: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV - OK")
    except ImportError as e:
        print(f"❌ OpenCV - FAILED: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy - OK")
    except ImportError as e:
        print(f"❌ NumPy - FAILED: {e}")
        return False
    
    return True

def test_database():
    """Test database functionality"""
    print("\n🗄️  Testing database...")
    
    try:
        from database.models import db, Vehicle, AccessLog, SystemSettings
        print("✅ Database models imported successfully")
        
        # Test if database file exists
        if os.path.exists('instance/vehicle_control.db'):
            print("✅ Database file exists")
            return True
        else:
            print("❌ Database file not found")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from config import Config
        print("✅ Configuration imported successfully")
        
        # Test key configuration values
        print(f"📱 Camera IP: {Config.CAMERA_IP}")
        print(f"🎯 Target FPS: {Config.MAX_FPS}")
        print(f"📏 Processing Resolution: {Config.PROCESSING_RESOLUTION}")
        print(f"🧠 Max Memory: {Config.MAX_MEMORY_USAGE}GB")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_templates():
    """Test template files"""
    print("\n📄 Testing templates...")
    
    templates = ['base.html', 'dashboard.html', 'camera.html', 'vehicles.html', 'logs.html']
    
    for template in templates:
        template_path = f"templates/{template}"
        if os.path.exists(template_path):
            print(f"✅ {template} - OK")
        else:
            print(f"❌ {template} - MISSING")
            return False
    
    return True

def test_static_files():
    """Test static files"""
    print("\n💅 Testing static files...")
    
    static_files = [
        'static/css/style.css',
        'static/js/main.js',
        'static/js/camera.js'
    ]
    
    for static_file in static_files:
        if os.path.exists(static_file):
            print(f"✅ {static_file} - OK")
        else:
            print(f"❌ {static_file} - MISSING")
            return False
    
    return True

def test_utilities():
    """Test utility modules"""
    print("\n🔧 Testing utilities...")
    
    try:
        from utils.camera_utils import CameraHandler, IPWebcamHelper
        print("✅ Camera utilities - OK")
    except Exception as e:
        print(f"❌ Camera utilities - FAILED: {e}")
        return False
    
    try:
        from utils.image_processing import resize_for_mobile
        print("✅ Image processing utilities - OK")
    except Exception as e:
        print(f"❌ Image processing utilities - FAILED: {e}")
        return False
    
    try:
        from utils.notification import NotificationManager
        print("✅ Notification utilities - OK")
    except Exception as e:
        print(f"❌ Notification utilities - FAILED: {e}")
        return False
    
    return True

def test_project_structure():
    """Test project structure"""
    print("\n📁 Testing project structure...")
    
    required_dirs = [
        'database',
        'models', 
        'static',
        'static/css',
        'static/js',
        'static/images',
        'templates',
        'utils',
        'scripts',
        'docs'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ - OK")
        else:
            print(f"❌ {directory}/ - MISSING")
            return False
    
    required_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - OK")
        else:
            print(f"❌ {file} - MISSING")
            return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 OPPO A92 Vehicle Control System - Basic Tests")
    print("=" * 60)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Templates", test_templates),
        ("Static Files", test_static_files),
        ("Utilities", test_utilities)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The basic system structure is ready.")
        print("💡 To complete setup:")
        print("   1. Install AI dependencies: pip install -r requirements.txt")
        print("   2. Run: python scripts/setup_oppo_a92.py")
        print("   3. Start system: python app.py")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed. Please fix the issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)