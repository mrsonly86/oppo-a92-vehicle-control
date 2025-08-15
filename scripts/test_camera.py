#!/usr/bin/env python3
"""
Camera connection test script for OPPO A92
Tests camera connectivity and stream quality
"""

import cv2
import time
import requests
import socket
import argparse
from urllib.parse import urlparse

def test_network_connectivity(ip, port):
    """Test basic network connectivity"""
    print(f"🌐 Testing network connectivity to {ip}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            print("✅ Network connectivity: OK")
            return True
        else:
            print(f"❌ Network connectivity: FAILED (Error {result})")
            return False
            
    except Exception as e:
        print(f"❌ Network connectivity: ERROR ({e})")
        return False

def test_http_response(url):
    """Test HTTP response from camera"""
    print(f"🌍 Testing HTTP response from {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ HTTP response: {response.status_code}")
        
        if response.status_code == 200:
            return True
        else:
            print(f"⚠️  HTTP status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ HTTP response: Connection refused")
        return False
    except requests.exceptions.Timeout:
        print("❌ HTTP response: Timeout")
        return False
    except Exception as e:
        print(f"❌ HTTP response: ERROR ({e})")
        return False

def test_video_stream(stream_url):
    """Test video stream from OPPO A92"""
    print(f"📹 Testing video stream from {stream_url}...")
    
    try:
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            print("❌ Video stream: Cannot open stream")
            return False
        
        # Try to read a few frames
        frames_read = 0
        start_time = time.time()
        
        for i in range(10):  # Try to read 10 frames
            ret, frame = cap.read()
            if ret:
                frames_read += 1
                if i == 0:  # Check first frame
                    height, width = frame.shape[:2]
                    print(f"📏 Stream resolution: {width}x{height}")
            else:
                break
            
            time.sleep(0.1)  # Small delay between frames
        
        end_time = time.time()
        elapsed = end_time - start_time
        fps = frames_read / elapsed if elapsed > 0 else 0
        
        cap.release()
        
        if frames_read > 0:
            print(f"✅ Video stream: OK ({frames_read} frames, ~{fps:.1f} FPS)")
            return True
        else:
            print("❌ Video stream: No frames received")
            return False
            
    except Exception as e:
        print(f"❌ Video stream: ERROR ({e})")
        return False

def test_ip_webcam_features(ip, port):
    """Test IP Webcam app specific features"""
    print(f"📱 Testing IP Webcam app features...")
    
    # Test various IP Webcam endpoints
    endpoints = [
        ("/video", "Video stream"),
        ("/audio.wav", "Audio stream"),
        ("/sensors.json", "Sensor data"),
        ("/status.json", "Status info")
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        url = f"http://{ip}:{port}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: Available")
                results[endpoint] = True
            else:
                print(f"❌ {description}: Not available ({response.status_code})")
                results[endpoint] = False
        except:
            print(f"❌ {description}: Error")
            results[endpoint] = False
    
    return results

def analyze_stream_quality(stream_url, duration=10):
    """Analyze stream quality for OPPO A92 optimization"""
    print(f"📊 Analyzing stream quality for {duration} seconds...")
    
    try:
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            print("❌ Cannot analyze stream quality - stream not accessible")
            return None
        
        frames_analyzed = 0
        total_size = 0
        start_time = time.time()
        frame_times = []
        
        while time.time() - start_time < duration:
            frame_start = time.time()
            ret, frame = cap.read()
            
            if ret:
                frames_analyzed += 1
                
                # Calculate frame size
                frame_size = frame.nbytes
                total_size += frame_size
                
                # Record frame timing
                frame_times.append(time.time() - frame_start)
                
            else:
                break
        
        cap.release()
        
        if frames_analyzed > 0:
            elapsed = time.time() - start_time
            avg_fps = frames_analyzed / elapsed
            avg_frame_size = total_size / frames_analyzed / 1024  # KB
            avg_bitrate = (total_size * 8) / elapsed / 1024  # Kbps
            avg_frame_time = sum(frame_times) / len(frame_times) * 1000  # ms
            
            print(f"📈 Stream Quality Analysis:")
            print(f"   • Average FPS: {avg_fps:.2f}")
            print(f"   • Average frame size: {avg_frame_size:.1f} KB")
            print(f"   • Average bitrate: {avg_bitrate:.1f} Kbps")
            print(f"   • Average frame time: {avg_frame_time:.1f} ms")
            
            # OPPO A92 recommendations
            print(f"\n📱 OPPO A92 Optimization Recommendations:")
            
            if avg_fps > 15:
                print("   ⚠️  FPS is high - consider reducing to save battery")
            elif avg_fps < 8:
                print("   ⚠️  FPS is low - check network connection")
            else:
                print("   ✅ FPS is optimal for OPPO A92")
            
            if avg_frame_size > 100:
                print("   ⚠️  Frame size is large - consider reducing resolution")
            else:
                print("   ✅ Frame size is optimal for mobile processing")
            
            if avg_bitrate > 1000:
                print("   ⚠️  Bitrate is high - may impact battery life")
            else:
                print("   ✅ Bitrate is reasonable for mobile streaming")
            
            return {
                'fps': avg_fps,
                'frame_size_kb': avg_frame_size,
                'bitrate_kbps': avg_bitrate,
                'frame_time_ms': avg_frame_time
            }
        else:
            print("❌ No frames analyzed")
            return None
            
    except Exception as e:
        print(f"❌ Error analyzing stream quality: {e}")
        return None

def suggest_optimizations(quality_data):
    """Suggest optimizations based on test results"""
    print(f"\n🔧 OPPO A92 Optimization Suggestions:")
    
    if quality_data:
        fps = quality_data['fps']
        frame_size = quality_data['frame_size_kb']
        bitrate = quality_data['bitrate_kbps']
        
        print("\n📱 IP Webcam App Settings:")
        
        if fps > 12:
            print("   • Set FPS to 10-12 for optimal battery life")
        
        if frame_size > 80:
            print("   • Reduce resolution to 640x480 or lower")
            print("   • Consider using H.264 encoding if available")
        
        if bitrate > 800:
            print("   • Reduce video quality setting")
            print("   • Use lower bitrate for mobile optimization")
        
        print("\n⚙️  System Configuration:")
        print("   • Set MAX_FPS = 12 in config.py")
        print("   • Set PROCESSING_RESOLUTION = (640, 480)")
        print("   • Enable frame skipping for better performance")
        print("   • Use YOLO nano model for efficient detection")
    
    print("\n📋 General Recommendations:")
    print("   • Keep OPPO A92 connected to power during long sessions")
    print("   • Use 5GHz WiFi for better bandwidth if available")
    print("   • Close other apps to free up memory")
    print("   • Monitor device temperature regularly")

def main():
    parser = argparse.ArgumentParser(description="Test OPPO A92 camera connection")
    parser.add_argument("--ip", default="192.168.1.100", help="Camera IP address")
    parser.add_argument("--port", type=int, default=8080, help="Camera port")
    parser.add_argument("--duration", type=int, default=10, help="Analysis duration (seconds)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📱 OPPO A92 Camera Connection Test")
    print("=" * 60)
    print(f"🎯 Target: {args.ip}:{args.port}")
    print(f"⏱️  Analysis duration: {args.duration} seconds")
    print("-" * 60)
    
    # Test network connectivity
    if not test_network_connectivity(args.ip, args.port):
        print("\n❌ Basic connectivity failed. Check:")
        print("   • OPPO A92 is connected to the same network")
        print("   • IP Webcam app is running")
        print("   • Firewall is not blocking the connection")
        return False
    
    # Test HTTP response
    base_url = f"http://{args.ip}:{args.port}"
    if not test_http_response(base_url):
        print("\n❌ HTTP response failed. Check:")
        print("   • IP Webcam app is properly started")
        print("   • Port number is correct")
        return False
    
    # Test IP Webcam features
    features = test_ip_webcam_features(args.ip, args.port)
    
    # Test video stream
    stream_url = f"{base_url}/video"
    if not test_video_stream(stream_url):
        print("\n❌ Video stream test failed. Check:")
        print("   • Video option is enabled in IP Webcam")
        print("   • Camera permissions are granted")
        return False
    
    # Analyze stream quality
    quality_data = analyze_stream_quality(stream_url, args.duration)
    
    # Provide optimization suggestions
    suggest_optimizations(quality_data)
    
    print("\n" + "=" * 60)
    print("✅ OPPO A92 Camera Test Complete!")
    print("=" * 60)
    print(f"📱 Camera at {args.ip}:{args.port} is ready for use")
    print(f"🔗 Stream URL: {stream_url}")
    print("🚀 You can now start the Vehicle Control System")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)