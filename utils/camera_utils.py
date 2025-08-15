"""
Camera handling utilities for OPPO A92 integration
Support for IP Webcam app and HTTP streaming
"""
import cv2
import numpy as np
import requests
import threading
import time
from urllib.parse import urlparse
import socket

class CameraHandler:
    def __init__(self, stream_url, processing_resolution=(640, 480)):
        """
        Initialize camera handler for OPPO A92
        
        Args:
            stream_url: Camera stream URL (HTTP/RTSP)
            processing_resolution: Target resolution for processing
        """
        self.stream_url = stream_url
        self.processing_resolution = processing_resolution
        self.cap = None
        self.connected = False
        self.last_frame = None
        self.frame_lock = threading.Lock()
        
        # Connection settings for mobile optimization
        self.connection_timeout = 10  # seconds
        self.read_timeout = 5  # seconds
        self.retry_interval = 2  # seconds
        self.max_retries = 5
        
        # Performance settings
        self.target_fps = 12
        self.frame_skip = 1  # Skip frames for performance
        self.frame_count = 0
        
    def connect(self):
        """Connect to OPPO A92 camera stream"""
        try:
            print(f"📱 Connecting to OPPO A92 camera: {self.stream_url}")
            
            # Test network connectivity first
            if not self._test_connectivity():
                print("❌ Network connectivity test failed")
                return False
            
            # Initialize video capture
            self.cap = cv2.VideoCapture(self.stream_url)
            
            if not self.cap.isOpened():
                print("❌ Failed to open camera stream")
                return False
            
            # Configure capture settings for OPPO A92 optimization
            self._configure_capture()
            
            # Test frame capture
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("❌ Failed to capture test frame")
                self.disconnect()
                return False
            
            self.connected = True
            print("✅ OPPO A92 camera connected successfully!")
            print(f"📺 Stream resolution: {frame.shape[1]}x{frame.shape[0]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to camera: {e}")
            self.disconnect()
            return False
    
    def _test_connectivity(self):
        """Test network connectivity to camera"""
        try:
            parsed_url = urlparse(self.stream_url)
            host = parsed_url.hostname
            port = parsed_url.port or (80 if parsed_url.scheme == 'http' else 443)
            
            # Test socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.connection_timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
            
        except Exception as e:
            print(f"❌ Connectivity test error: {e}")
            return False
    
    def _configure_capture(self):
        """Configure video capture for OPPO A92 optimization"""
        try:
            # Set buffer size to reduce latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Set FPS (may not work with all streams)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            
            # Set resolution if supported
            width, height = self.processing_resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            print(f"🔧 Camera configured for {width}x{height} @ {self.target_fps}FPS")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not configure all camera settings: {e}")
    
    def get_frame(self):
        """
        Get current frame from camera stream
        
        Returns:
            OpenCV frame or None if not available
        """
        if not self.connected or not self.cap:
            return None
        
        try:
            # Skip frames for performance optimization
            self.frame_count += 1
            if self.frame_count % (self.frame_skip + 1) != 0:
                return self.last_frame
            
            # Capture frame
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                print("⚠️  Frame capture failed, attempting reconnection...")
                self._attempt_reconnection()
                return self.last_frame
            
            # Resize for processing efficiency
            if frame.shape[1] > self.processing_resolution[0]:
                frame = cv2.resize(frame, self.processing_resolution)
            
            # Store frame with thread safety
            with self.frame_lock:
                self.last_frame = frame.copy()
            
            return frame
            
        except Exception as e:
            print(f"❌ Error capturing frame: {e}")
            self._attempt_reconnection()
            return self.last_frame
    
    def _attempt_reconnection(self):
        """Attempt to reconnect to camera"""
        if not self.connected:
            return
        
        print("🔄 Attempting camera reconnection...")
        
        # Disconnect first
        self.disconnect()
        
        # Wait before retry
        time.sleep(self.retry_interval)
        
        # Attempt reconnection
        for attempt in range(self.max_retries):
            if self.connect():
                print(f"✅ Reconnected after {attempt + 1} attempts")
                return
            
            print(f"❌ Reconnection attempt {attempt + 1}/{self.max_retries} failed")
            time.sleep(self.retry_interval)
        
        print("❌ All reconnection attempts failed")
    
    def disconnect(self):
        """Disconnect from camera stream"""
        self.connected = False
        
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
        
        print("📱 Camera disconnected")
    
    def is_connected(self):
        """Check if camera is connected"""
        return self.connected and self.cap is not None
    
    def get_stream_info(self):
        """Get camera stream information"""
        if not self.cap:
            return {}
        
        try:
            info = {
                'fps': self.cap.get(cv2.CAP_PROP_FPS),
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'codec': int(self.cap.get(cv2.CAP_PROP_FOURCC)),
                'buffer_size': int(self.cap.get(cv2.CAP_PROP_BUFFERSIZE)),
            }
            return info
        except:
            return {}
    
    def save_frame(self, frame, filename):
        """Save frame to file"""
        try:
            cv2.imwrite(filename, frame)
            return True
        except Exception as e:
            print(f"❌ Error saving frame: {e}")
            return False

class IPWebcamHelper:
    """Helper class for IP Webcam app integration"""
    
    @staticmethod
    def generate_stream_url(ip, port=8080, quality='640x480', format='mjpeg'):
        """
        Generate IP Webcam stream URL
        
        Args:
            ip: Camera IP address
            port: Camera port (default 8080)
            quality: Video quality (640x480, 1280x720, etc.)
            format: Stream format (mjpeg, h264)
            
        Returns:
            Stream URL
        """
        if format == 'mjpeg':
            return f"http://{ip}:{port}/video"
        elif format == 'h264':
            return f"http://{ip}:{port}/videofeed"
        else:
            return f"http://{ip}:{port}/video"
    
    @staticmethod
    def get_camera_info(ip, port=8080):
        """
        Get camera information from IP Webcam app
        
        Args:
            ip: Camera IP address
            port: Camera port
            
        Returns:
            Dictionary with camera info
        """
        try:
            info_url = f"http://{ip}:{port}/sensors.json"
            response = requests.get(info_url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Error getting camera info: {e}")
            return {}
    
    @staticmethod
    def test_connection(ip, port=8080):
        """
        Test connection to IP Webcam app
        
        Args:
            ip: Camera IP address
            port: Camera port
            
        Returns:
            Boolean indicating connection success
        """
        try:
            test_url = f"http://{ip}:{port}/enabletorch"
            response = requests.get(test_url, timeout=5)
            return response.status_code in [200, 404]  # 404 is also OK (feature not available)
            
        except:
            return False

def auto_discover_cameras(network_range="192.168.1.", port_range=[8080, 4747, 8081]):
    """
    Auto-discover IP cameras on network
    
    Args:
        network_range: Network range to scan (e.g., "192.168.1.")
        port_range: List of ports to check
        
    Returns:
        List of discovered camera URLs
    """
    discovered_cameras = []
    
    print("🔍 Scanning for IP cameras on network...")
    
    # Scan IP range
    for i in range(100, 255):  # Common device range
        ip = f"{network_range}{i}"
        
        for port in port_range:
            try:
                # Quick connection test
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    # Test if it's actually a camera
                    camera_url = f"http://{ip}:{port}/video"
                    if IPWebcamHelper.test_connection(ip, port):
                        discovered_cameras.append({
                            'ip': ip,
                            'port': port,
                            'url': camera_url
                        })
                        print(f"📱 Found camera: {camera_url}")
                
            except:
                continue
    
    print(f"✅ Discovery complete. Found {len(discovered_cameras)} cameras.")
    return discovered_cameras