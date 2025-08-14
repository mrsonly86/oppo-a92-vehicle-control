"""
Notification management for OPPO A92 Vehicle Control System
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from database.models import db, Alert

class NotificationManager:
    def __init__(self):
        """Initialize notification manager"""
        self.subscribers = []  # WebSocket subscribers
        self.alert_history = []
        self.max_history = 100
        
    def add_subscriber(self, subscriber):
        """Add WebSocket subscriber for real-time notifications"""
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)
    
    def remove_subscriber(self, subscriber):
        """Remove WebSocket subscriber"""
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)
    
    def send_alert(self, title, message, alert_type='warning', license_plate=None, detection_data=None):
        """
        Send alert notification
        
        Args:
            title: Alert title
            message: Alert message
            alert_type: Type of alert ('info', 'warning', 'error')
            license_plate: Related license plate
            detection_data: Additional detection data
        """
        try:
            # Create alert record in database
            alert = Alert(
                title=title,
                message=message,
                alert_type=alert_type,
                license_plate=license_plate,
                created_at=datetime.now()
            )
            
            db.session.add(alert)
            db.session.commit()
            
            # Create notification payload
            notification = {
                'id': alert.id,
                'title': title,
                'message': message,
                'type': alert_type,
                'license_plate': license_plate,
                'timestamp': datetime.now().isoformat(),
                'detection_data': detection_data
            }
            
            # Add to history
            self.alert_history.append(notification)
            if len(self.alert_history) > self.max_history:
                self.alert_history.pop(0)
            
            # Send to WebSocket subscribers
            self._broadcast_notification(notification)
            
            # Log alert
            self._log_alert(notification)
            
            return alert.id
            
        except Exception as e:
            print(f"❌ Error sending alert: {e}")
            return None
    
    def send_vehicle_detection_alert(self, vehicle_data):
        """
        Send alert for vehicle detection
        
        Args:
            vehicle_data: Vehicle detection information
        """
        license_plate = vehicle_data.get('license_plate', 'Unknown')
        vehicle_type = vehicle_data.get('class', 'vehicle')
        confidence = vehicle_data.get('confidence', 0)
        
        title = "Unauthorized Vehicle Detected"
        message = f"Unknown {vehicle_type} with plate {license_plate} detected (confidence: {confidence:.2f})"
        
        return self.send_alert(
            title=title,
            message=message,
            alert_type='warning',
            license_plate=license_plate,
            detection_data=vehicle_data
        )
    
    def send_system_alert(self, message, alert_type='info'):
        """
        Send system status alert
        
        Args:
            message: System message
            alert_type: Alert type
        """
        title = "System Notification"
        
        return self.send_alert(
            title=title,
            message=message,
            alert_type=alert_type
        )
    
    def send_camera_alert(self, status, camera_info=None):
        """
        Send camera status alert
        
        Args:
            status: Camera status ('connected', 'disconnected', 'error')
            camera_info: Camera information
        """
        status_messages = {
            'connected': 'OPPO A92 camera connected successfully',
            'disconnected': 'OPPO A92 camera disconnected',
            'error': 'OPPO A92 camera connection error',
            'reconnecting': 'Attempting to reconnect to OPPO A92 camera'
        }
        
        message = status_messages.get(status, f"Camera status: {status}")
        alert_type = 'info' if status == 'connected' else 'warning'
        
        return self.send_alert(
            title="Camera Status",
            message=message,
            alert_type=alert_type,
            detection_data=camera_info
        )
    
    def _broadcast_notification(self, notification):
        """Broadcast notification to WebSocket subscribers"""
        try:
            # This would integrate with Flask-SocketIO in the main app
            # For now, we'll store for later broadcast
            for subscriber in self.subscribers:
                try:
                    subscriber.emit('notification', notification)
                except Exception as e:
                    print(f"❌ Error broadcasting to subscriber: {e}")
                    # Remove failed subscriber
                    self.remove_subscriber(subscriber)
                    
        except Exception as e:
            print(f"❌ Error broadcasting notification: {e}")
    
    def _log_alert(self, notification):
        """Log alert to console and file"""
        timestamp = notification['timestamp']
        alert_type = notification['type'].upper()
        title = notification['title']
        message = notification['message']
        
        log_message = f"[{timestamp}] {alert_type}: {title} - {message}"
        print(f"🔔 {log_message}")
        
        # Here you could also write to a log file
        # self._write_to_log_file(log_message)
    
    def get_recent_alerts(self, limit=10):
        """
        Get recent alerts from database
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        try:
            alerts = Alert.query.order_by(Alert.created_at.desc()).limit(limit).all()
            return [alert.to_dict() for alert in alerts]
        except Exception as e:
            print(f"❌ Error getting recent alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id):
        """
        Acknowledge an alert
        
        Args:
            alert_id: ID of alert to acknowledge
            
        Returns:
            Success status
        """
        try:
            alert = Alert.query.get(alert_id)
            if alert:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"❌ Error acknowledging alert: {e}")
            return False
    
    def get_unacknowledged_alerts(self):
        """Get list of unacknowledged alerts"""
        try:
            alerts = Alert.query.filter_by(acknowledged=False).order_by(Alert.created_at.desc()).all()
            return [alert.to_dict() for alert in alerts]
        except Exception as e:
            print(f"❌ Error getting unacknowledged alerts: {e}")
            return []
    
    def clear_old_alerts(self, days_to_keep=30):
        """
        Clear alerts older than specified days
        
        Args:
            days_to_keep: Number of days to keep alerts
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            old_alerts = Alert.query.filter(Alert.created_at < cutoff_date).all()
            
            for alert in old_alerts:
                db.session.delete(alert)
            
            db.session.commit()
            print(f"🗑️  Cleared {len(old_alerts)} old alerts")
            
        except Exception as e:
            print(f"❌ Error clearing old alerts: {e}")
    
    def get_alert_statistics(self):
        """Get alert statistics"""
        try:
            total_alerts = Alert.query.count()
            unacknowledged = Alert.query.filter_by(acknowledged=False).count()
            
            # Count by type
            alert_types = db.session.query(Alert.alert_type, db.func.count(Alert.id)).group_by(Alert.alert_type).all()
            type_counts = {alert_type: count for alert_type, count in alert_types}
            
            return {
                'total_alerts': total_alerts,
                'unacknowledged': unacknowledged,
                'by_type': type_counts
            }
        except Exception as e:
            print(f"❌ Error getting alert statistics: {e}")
            return {
                'total_alerts': 0,
                'unacknowledged': 0,
                'by_type': {}
            }

class SMSNotification:
    """SMS notification integration (placeholder for future implementation)"""
    
    def __init__(self, api_key=None, sender_number=None):
        self.api_key = api_key
        self.sender_number = sender_number
        self.enabled = api_key is not None
    
    def send_sms(self, phone_number, message):
        """Send SMS notification"""
        if not self.enabled:
            print("📱 SMS notifications not configured")
            return False
        
        # Placeholder for SMS API integration
        print(f"📱 SMS to {phone_number}: {message}")
        return True

class EmailNotification:
    """Email notification integration (placeholder for future implementation)"""
    
    def __init__(self, smtp_server=None, username=None, password=None):
        self.smtp_server = smtp_server
        self.username = username
        self.password = password
        self.enabled = all([smtp_server, username, password])
    
    def send_email(self, to_email, subject, message):
        """Send email notification"""
        if not self.enabled:
            print("📧 Email notifications not configured")
            return False
        
        # Placeholder for email sending
        print(f"📧 Email to {to_email}: {subject}")
        return True