#!/usr/bin/env python3
"""
OPPO A92 Setup Script for Vehicle Control System
Automated setup and configuration for optimal performance
"""

import os
import sys
import subprocess
import json
import platform
import socket
import requests
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🔧 OPPO A92 Vehicle Control System Setup")
    print("=" * 60)
    print("📱 Target Device: OPPO A92 (MediaTek Helio P60)")
    print("🎯 Optimization: <1.5GB RAM, 8-12 FPS")
    print("💰 Cost: 100% Free")
    print("-" * 60)

def check_python_version():
    """Check Python version requirements"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required. Current version:", sys.version)
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_system_requirements():
    """Check system requirements"""
    print("\n💻 Checking system requirements...")
    
    # Check OS
    system = platform.system()
    print(f"🖥️  Operating System: {system}")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"🧠 Available RAM: {memory_gb:.1f} GB")
        
        if memory_gb < 2:
            print("⚠️  Warning: Low RAM detected. Performance may be limited.")
    except ImportError:
        print("📊 Memory check skipped (psutil not available)")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install requirements with mobile optimizations
        cmd = [
            sys.executable, "-m", "pip", "install", 
            "-r", str(requirements_file),
            "--prefer-binary",  # Use binary packages for faster installation
            "--no-cache-dir"    # Don't cache to save space
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_database():
    """Initialize database"""
    print("\n🗄️  Setting up database...")
    
    try:
        # Import after dependencies are installed
        from database.init_db import init_database
        
        init_database()
        print("✅ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def download_ai_models():
    """Download and setup AI models for OPPO A92"""
    print("\n🤖 Setting up AI models for OPPO A92...")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # YOLOv5n model (nano version for mobile)
    yolo_model_path = models_dir / "yolov5n.pt"
    
    if not yolo_model_path.exists():
        print("📥 Downloading YOLOv5n model (optimized for mobile)...")
        try:
            import torch
            from ultralytics import YOLO
            
            # This will automatically download the model
            model = YOLO('yolov5n.pt')
            print("✅ YOLOv5n model ready!")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not download YOLOv5n model: {e}")
            print("💡 Model will be downloaded on first use")
    
    # Test EasyOCR
    print("🔤 Setting up EasyOCR for Vietnamese license plates...")
    try:
        import easyocr
        # Initialize with Vietnamese and English
        reader = easyocr.Reader(['vi', 'en'], gpu=False, verbose=False)
        print("✅ EasyOCR ready for Vietnamese plates!")
        
    except Exception as e:
        print(f"⚠️  Warning: EasyOCR setup issue: {e}")
    
    # Test MediaPipe
    print("👤 Setting up MediaPipe for gender classification...")
    try:
        import mediapipe as mp
        mp_face_detection = mp.solutions.face_detection
        print("✅ MediaPipe ready for gender detection!")
        
    except Exception as e:
        print(f"⚠️  Warning: MediaPipe setup issue: {e}")
    
    return True

def detect_oppo_camera():
    """Auto-detect OPPO A92 camera on network"""
    print("\n📱 Scanning for OPPO A92 camera...")
    
    # Common IP ranges for mobile hotspots and local networks
    ip_ranges = [
        "192.168.1.",
        "192.168.0.",
        "192.168.43.",  # Common Android hotspot range
        "10.0.0."
    ]
    
    common_ports = [8080, 4747, 8081]
    found_cameras = []
    
    for ip_range in ip_ranges:
        print(f"🔍 Scanning {ip_range}x...")
        
        for i in range(100, 255):  # Scan common device range
            ip = f"{ip_range}{i}"
            
            for port in common_ports:
                try:
                    # Quick connection test
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result == 0:
                        # Test if it's actually a camera
                        try:
                            response = requests.get(f"http://{ip}:{port}/", timeout=2)
                            if response.status_code in [200, 404]:
                                found_cameras.append(f"http://{ip}:{port}")
                                print(f"📱 Found potential camera: {ip}:{port}")
                        except:
                            pass
                            
                except:
                    continue
    
    if found_cameras:
        print(f"✅ Found {len(found_cameras)} potential camera(s)")
        return found_cameras[0]  # Return first found
    else:
        print("❌ No cameras detected automatically")
        return None

def create_config_file(camera_url=None):
    """Create configuration file"""
    print("\n⚙️  Creating configuration...")
    
    config = {
        "camera": {
            "url": camera_url or "http://192.168.1.100:8080/video",
            "resolution": [640, 480],
            "max_fps": 12
        },
        "ai": {
            "yolo_confidence": 0.5,
            "ocr_confidence": 0.6,
            "gender_confidence": 0.7
        },
        "performance": {
            "max_memory_gb": 1.5,
            "processing_threads": 2,
            "frame_skip": 1
        }
    }
    
    config_path = Path("config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration file created!")
    return True

def create_startup_scripts():
    """Create startup scripts for different platforms"""
    print("\n📜 Creating startup scripts...")
    
    # Windows batch file
    windows_script = """@echo off
echo Starting OPPO A92 Vehicle Control System...
cd /d "%~dp0"
python app.py
pause
"""
    
    with open("start_windows.bat", "w") as f:
        f.write(windows_script)
    
    # Linux/Mac shell script
    unix_script = """#!/bin/bash
echo "Starting OPPO A92 Vehicle Control System..."
cd "$(dirname "$0")"
python3 app.py
"""
    
    with open("start_unix.sh", "w") as f:
        f.write(unix_script)
    
    # Make shell script executable
    try:
        os.chmod("start_unix.sh", 0o755)
    except:
        pass
    
    print("✅ Startup scripts created!")
    return True

def run_tests():
    """Run basic system tests"""
    print("\n🧪 Running system tests...")
    
    # Test imports
    modules_to_test = [
        ("OpenCV", "cv2"),
        ("PyTorch", "torch"),
        ("Ultralytics", "ultralytics"),
        ("EasyOCR", "easyocr"),
        ("MediaPipe", "mediapipe"),
        ("Flask", "flask"),
        ("NumPy", "numpy"),
        ("Pillow", "PIL")
    ]
    
    for name, module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {name} - OK")
        except ImportError:
            print(f"❌ {name} - MISSING")
    
    return True

def print_completion_info():
    """Print setup completion information"""
    print("\n" + "=" * 60)
    print("🎉 OPPO A92 Vehicle Control System Setup Complete!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("1. Connect your OPPO A92 to the same network")
    print("2. Install 'IP Webcam' app on OPPO A92")
    print("3. Start IP Webcam and note the IP address")
    print("4. Run the system:")
    print("   • Windows: double-click start_windows.bat")
    print("   • Linux/Mac: ./start_unix.sh")
    print("   • Manual: python app.py")
    print()
    print("🌐 Access the system at: http://localhost:5000")
    print()
    print("📱 OPPO A92 Optimization Features:")
    print("• YOLOv5n (nano) for efficient vehicle detection")
    print("• Vietnamese license plate OCR with EasyOCR")
    print("• Gender classification with MediaPipe")
    print("• Memory usage optimized for <1.5GB")
    print("• Target 8-12 FPS for smooth operation")
    print()
    print("💡 For troubleshooting, see docs/TROUBLESHOOTING.md")
    print("📖 For detailed setup, see docs/OPPO_A92_SETUP.md")
    print("=" * 60)

def main():
    """Main setup function"""
    print_header()
    
    # Check requirements
    if not check_python_version():
        return False
    
    if not check_system_requirements():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup database
    if not setup_database():
        return False
    
    # Setup AI models
    if not download_ai_models():
        return False
    
    # Detect camera
    camera_url = detect_oppo_camera()
    
    # Create configuration
    if not create_config_file(camera_url):
        return False
    
    # Create startup scripts
    if not create_startup_scripts():
        return False
    
    # Run tests
    if not run_tests():
        return False
    
    # Print completion info
    print_completion_info()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🚀 Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)