"""
Government Integration API for OPPO A92 Vehicle Control System
Handles integration with Vietnamese vehicle registry and authority systems
"""
import requests
import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

class GovernmentAPI:
    """
    Integration with Vietnamese government vehicle databases and authorities
    """
    
    def __init__(self):
        """Initialize government API integration"""
        
        # API Configuration (These would be real endpoints in production)
        self.vehicle_registry_url = os.environ.get('VEHICLE_REGISTRY_URL', 'https://api.dkxe.gov.vn')
        self.traffic_police_url = os.environ.get('TRAFFIC_POLICE_URL', 'https://api.csgt.gov.vn')
        self.environment_dept_url = os.environ.get('ENVIRONMENT_DEPT_URL', 'https://api.monre.gov.vn')
        
        # API Credentials (would be provided by government)
        self.api_key = os.environ.get('GOV_API_KEY', 'demo_api_key')
        self.api_secret = os.environ.get('GOV_API_SECRET', 'demo_secret')
        self.organization_id = os.environ.get('ORG_ID', 'oppo_a92_system')
        
        # Request timeout and retry settings
        self.request_timeout = 30
        self.max_retries = 3
        
        # Mock data for demonstration (in production, remove this)
        self.mock_vehicle_data = {
            '29A-12345': {
                'license_plate': '29A-12345',
                'owner_name': 'Nguyen Van A',
                'owner_id': '123456789',
                'vehicle_type': 'car',
                'manufacturer': 'Toyota',
                'model': 'Camry',
                'manufacture_year': 2018,
                'engine_displacement': 2400,
                'fuel_type': 'gasoline',
                'euro_standard': 'Euro 4',
                'registration_date': '2018-03-15',
                'last_inspection': '2023-03-15',
                'inspection_result': 'pass',
                'emission_certificate': 'valid',
                'status': 'active'
            },
            '51H-6789': {
                'license_plate': '51H-6789',
                'owner_name': 'Tran Thi B',
                'owner_id': '987654321',
                'vehicle_type': 'motorcycle',
                'manufacturer': 'Honda',
                'model': 'Wave',
                'manufacture_year': 2015,
                'engine_displacement': 110,
                'fuel_type': 'gasoline',
                'euro_standard': 'Euro 3',
                'registration_date': '2015-08-20',
                'last_inspection': '2023-08-20',
                'inspection_result': 'pass',
                'emission_certificate': 'valid',
                'status': 'active'
            }
        }
    
    def lookup_vehicle(self, license_plate: str) -> Dict:
        """
        Look up vehicle information from government registry
        
        Args:
            license_plate: Vietnamese license plate number
            
        Returns:
            Dict: Vehicle information from government database
        """
        try:
            # Validate license plate format
            if not self._validate_vietnamese_plate(license_plate):
                return {'error': 'Invalid Vietnamese license plate format'}
            
            # In production, this would make a real API call
            if os.environ.get('USE_MOCK_DATA', 'true').lower() == 'true':
                return self._mock_vehicle_lookup(license_plate)
            
            # Real API call (commented out for demo)
            """
            headers = self._get_auth_headers()
            response = requests.get(
                f"{self.vehicle_registry_url}/api/v1/vehicles/{license_plate}",
                headers=headers,
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {'error': 'Vehicle not found in registry'}
            else:
                return {'error': f'API error: {response.status_code}'}
            """
            
            return self._mock_vehicle_lookup(license_plate)
            
        except requests.RequestException as e:
            print(f"❌ Error looking up vehicle {license_plate}: {e}")
            return {'error': 'Network error accessing vehicle registry'}
        except Exception as e:
            print(f"❌ Unexpected error in vehicle lookup: {e}")
            return {'error': 'Internal error'}
    
    def report_violation(self, violation_data: Dict) -> Dict:
        """
        Report emission violation to traffic police system
        
        Args:
            violation_data: Dict containing violation details
            
        Returns:
            Dict: Response from traffic police system
        """
        try:
            # Prepare violation report
            report = {
                'report_id': f"EMV_{datetime.now().strftime('%Y%m%d%H%M%S')}_{violation_data.get('license_plate', 'UNKNOWN')}",
                'license_plate': violation_data.get('license_plate'),
                'violation_type': violation_data.get('violation_type'),
                'violation_time': violation_data.get('timestamp', datetime.now().isoformat()),
                'location': {
                    'lat': violation_data.get('location_lat'),
                    'lng': violation_data.get('location_lng'),
                    'address': violation_data.get('location_address', 'Unknown')
                },
                'lez_zone': violation_data.get('lez_zone_name'),
                'evidence': {
                    'image_path': violation_data.get('evidence_image_path'),
                    'video_path': violation_data.get('evidence_video_path'),
                    'ai_confidence': violation_data.get('confidence')
                },
                'emission_data': {
                    'smoke_level': violation_data.get('smoke_level'),
                    'vehicle_condition_score': violation_data.get('vehicle_condition_score'),
                    'estimated_euro_standard': violation_data.get('euro_standard')
                },
                'fine_amount': violation_data.get('fine_amount'),
                'reporting_system': 'OPPO A92 Vehicle Control',
                'camera_id': violation_data.get('camera_id')
            }
            
            # In production, send to traffic police system
            if os.environ.get('USE_MOCK_DATA', 'true').lower() == 'true':
                return self._mock_violation_report(report)
            
            # Real API call (commented out for demo)
            """
            headers = self._get_auth_headers()
            response = requests.post(
                f"{self.traffic_police_url}/api/v1/violations",
                headers=headers,
                json=report,
                timeout=self.request_timeout
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                return {'error': f'Failed to report violation: {response.status_code}'}
            """
            
            return self._mock_violation_report(report)
            
        except Exception as e:
            print(f"❌ Error reporting violation: {e}")
            return {'error': 'Failed to report violation to authorities'}
    
    def submit_environmental_data(self, environmental_report: Dict) -> Dict:
        """
        Submit environmental impact data to Department of Natural Resources and Environment
        
        Args:
            environmental_report: Environmental impact report data
            
        Returns:
            Dict: Response from environmental department
        """
        try:
            # Prepare environmental submission
            submission = {
                'submission_id': f"ENV_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'organization_id': self.organization_id,
                'report_period': environmental_report.get('report_period'),
                'generated_at': environmental_report.get('generated_at'),
                'location': 'Ho Chi Minh City',  # System location
                'data': {
                    'total_vehicles_monitored': environmental_report.get('summary', {}).get('total_vehicles_detected', 0),
                    'total_emissions': environmental_report.get('total_emissions', {}),
                    'health_impact_score': environmental_report.get('summary', {}).get('total_health_impact_score', 0),
                    'economic_cost_vnd': environmental_report.get('summary', {}).get('total_economic_cost_vnd', 0),
                    'compliance_rate': environmental_report.get('compliance_rate', 0),
                    'top_polluters': environmental_report.get('top_polluters', []),
                    'recommendations': environmental_report.get('recommendations', [])
                },
                'monitoring_system': {
                    'name': 'OPPO A92 Vehicle Control System',
                    'version': '1.0.0',
                    'ai_accuracy': 0.85,
                    'coverage_area': 'Urban LEZ zones'
                }
            }
            
            # In production, send to environmental department
            if os.environ.get('USE_MOCK_DATA', 'true').lower() == 'true':
                return self._mock_environmental_submission(submission)
            
            # Real API call (commented out for demo)
            """
            headers = self._get_auth_headers()
            response = requests.post(
                f"{self.environment_dept_url}/api/v1/emissions/reports",
                headers=headers,
                json=submission,
                timeout=self.request_timeout
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                return {'error': f'Failed to submit environmental data: {response.status_code}'}
            """
            
            return self._mock_environmental_submission(submission)
            
        except Exception as e:
            print(f"❌ Error submitting environmental data: {e}")
            return {'error': 'Failed to submit environmental data'}
    
    def generate_fine_notice(self, violation_data: Dict) -> Dict:
        """
        Generate official fine notice through government system
        
        Args:
            violation_data: Violation information
            
        Returns:
            Dict: Fine notice details
        """
        try:
            # Look up vehicle owner information
            vehicle_info = self.lookup_vehicle(violation_data.get('license_plate'))
            
            if 'error' in vehicle_info:
                return {'error': 'Cannot generate fine: Vehicle not found'}
            
            # Generate fine notice
            fine_notice = {
                'fine_notice_id': f"FN_{datetime.now().strftime('%Y%m%d%H%M%S')}_{violation_data.get('license_plate')}",
                'violation_report_id': violation_data.get('violation_id'),
                'license_plate': violation_data.get('license_plate'),
                'owner_info': {
                    'name': vehicle_info.get('owner_name'),
                    'id_number': vehicle_info.get('owner_id'),
                    'address': vehicle_info.get('owner_address', 'On file')
                },
                'vehicle_info': {
                    'type': vehicle_info.get('vehicle_type'),
                    'manufacturer': vehicle_info.get('manufacturer'),
                    'model': vehicle_info.get('model'),
                    'year': vehicle_info.get('manufacture_year')
                },
                'violation_details': {
                    'type': violation_data.get('violation_type'),
                    'location': violation_data.get('location_address'),
                    'time': violation_data.get('timestamp'),
                    'lez_zone': violation_data.get('lez_zone_name'),
                    'evidence_photos': [violation_data.get('evidence_image_path')] if violation_data.get('evidence_image_path') else []
                },
                'fine_details': {
                    'amount_vnd': violation_data.get('fine_amount'),
                    'due_date': (datetime.now() + timedelta(days=30)).isoformat(),
                    'payment_methods': ['Bank transfer', 'Online payment', 'Traffic police station'],
                    'appeal_deadline': (datetime.now() + timedelta(days=15)).isoformat()
                },
                'legal_basis': 'Decree 100/2019/ND-CP on Road Traffic Violations',
                'issuing_authority': 'Ho Chi Minh City Traffic Police',
                'status': 'issued',
                'issued_at': datetime.now().isoformat()
            }
            
            print(f"✅ Fine notice generated: {fine_notice['fine_notice_id']}")
            return fine_notice
            
        except Exception as e:
            print(f"❌ Error generating fine notice: {e}")
            return {'error': 'Failed to generate fine notice'}
    
    def check_vehicle_restrictions(self, license_plate: str, lez_zone_id: str) -> Dict:
        """
        Check if vehicle has any existing restrictions or violations
        
        Args:
            license_plate: Vehicle license plate
            lez_zone_id: LEZ zone identifier
            
        Returns:
            Dict: Restriction check results
        """
        try:
            # Look up vehicle history
            vehicle_info = self.lookup_vehicle(license_plate)
            
            if 'error' in vehicle_info:
                return {'error': 'Vehicle not found'}
            
            # Check for existing violations (mock data)
            restrictions = {
                'license_plate': license_plate,
                'has_restrictions': False,
                'restriction_type': None,
                'restriction_expiry': None,
                'violation_history': {
                    'total_violations': 0,
                    'recent_violations': 0,
                    'unpaid_fines': 0,
                    'total_unpaid_amount': 0
                },
                'vehicle_status': vehicle_info.get('status', 'active'),
                'emission_certificate_status': vehicle_info.get('emission_certificate', 'unknown'),
                'last_inspection': vehicle_info.get('last_inspection'),
                'inspection_result': vehicle_info.get('inspection_result'),
                'lez_access_permitted': True,
                'checked_at': datetime.now().isoformat()
            }
            
            # Determine LEZ access based on vehicle data
            euro_standard = vehicle_info.get('euro_standard', 'Unknown')
            manufacture_year = vehicle_info.get('manufacture_year', 2000)
            
            # Simple rules for demonstration
            if euro_standard in ['Euro 1', 'Euro 2', 'Unknown']:
                restrictions['lez_access_permitted'] = False
                restrictions['has_restrictions'] = True
                restrictions['restriction_type'] = 'emission_standard'
            elif manufacture_year < 2010:
                restrictions['lez_access_permitted'] = False
                restrictions['has_restrictions'] = True
                restrictions['restriction_type'] = 'vehicle_age'
            
            return restrictions
            
        except Exception as e:
            print(f"❌ Error checking vehicle restrictions: {e}")
            return {'error': 'Failed to check vehicle restrictions'}
    
    def _validate_vietnamese_plate(self, license_plate: str) -> bool:
        """Validate Vietnamese license plate format"""
        import re
        
        # Vietnamese license plate patterns
        patterns = [
            r'^\d{2}[A-Z]-\d{4,5}$',      # Old format: 29A-1234
            r'^\d{2}[A-Z]{1,2}-\d{4,5}$', # New format: 29AB-1234
            r'^\d{2}[A-Z]-\d{3}\.\d{2}$'   # Special format: 29A-123.45
        ]
        
        return any(re.match(pattern, license_plate.upper()) for pattern in patterns)
    
    def _get_auth_headers(self) -> Dict:
        """Generate authentication headers for government API"""
        timestamp = str(int(datetime.now().timestamp()))
        
        # Create signature (HMAC-SHA256)
        message = f"{self.api_key}{timestamp}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'Authorization': f'Bearer {self.api_key}',
            'X-Timestamp': timestamp,
            'X-Signature': signature,
            'Content-Type': 'application/json',
            'User-Agent': 'OPPO-A92-Vehicle-Control/1.0'
        }
    
    def _mock_vehicle_lookup(self, license_plate: str) -> Dict:
        """Mock vehicle lookup for demonstration"""
        plate = license_plate.upper()
        
        if plate in self.mock_vehicle_data:
            return {
                'status': 'found',
                'data': self.mock_vehicle_data[plate],
                'source': 'mock_registry',
                'retrieved_at': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'not_found',
                'error': 'Vehicle not found in registry',
                'license_plate': plate,
                'checked_at': datetime.now().isoformat()
            }
    
    def _mock_violation_report(self, report: Dict) -> Dict:
        """Mock violation report for demonstration"""
        return {
            'status': 'success',
            'report_id': report['report_id'],
            'case_number': f"CASE_{datetime.now().strftime('%Y%m%d')}_{report['license_plate']}",
            'fine_notice_id': f"FN_{report['report_id']}",
            'processing_status': 'accepted',
            'estimated_processing_time': '2-3 business days',
            'next_steps': [
                'Violation review by traffic police',
                'Fine notice generation',
                'Notification to vehicle owner'
            ],
            'submitted_at': datetime.now().isoformat()
        }
    
    def _mock_environmental_submission(self, submission: Dict) -> Dict:
        """Mock environmental data submission for demonstration"""
        return {
            'status': 'success',
            'submission_id': submission['submission_id'],
            'reference_number': f"ENV_{datetime.now().strftime('%Y%m%d')}_{submission['organization_id']}",
            'processing_status': 'received',
            'acknowledgment': 'Environmental data successfully received and will be processed within 5 business days',
            'contact_info': {
                'department': 'Department of Natural Resources and Environment',
                'email': 'emissions@monre.gov.vn',
                'phone': '+84-28-1234-5678'
            },
            'submitted_at': datetime.now().isoformat()
        }

# Helper functions for quick access
def quick_vehicle_lookup(license_plate: str) -> Dict:
    """Quick vehicle lookup function"""
    api = GovernmentAPI()
    return api.lookup_vehicle(license_plate)

def quick_violation_report(violation_data: Dict) -> Dict:
    """Quick violation reporting function"""
    api = GovernmentAPI()
    return api.report_violation(violation_data)

def quick_restriction_check(license_plate: str, lez_zone_id: str = 'default') -> Dict:
    """Quick restriction check function"""
    api = GovernmentAPI()
    return api.check_vehicle_restrictions(license_plate, lez_zone_id)

# Auto-reporting system
class AutoReportingService:
    """
    Automated reporting service for violations
    """
    
    def __init__(self, reporting_interval_minutes: int = 30):
        """Initialize auto-reporting service"""
        self.api = GovernmentAPI()
        self.reporting_interval = reporting_interval_minutes
        self.is_running = False
        
    def start_auto_reporting(self):
        """Start automated reporting to government systems"""
        import threading
        import time
        
        def reporting_loop():
            while self.is_running:
                try:
                    self._process_pending_reports()
                    time.sleep(self.reporting_interval * 60)  # Convert to seconds
                except Exception as e:
                    print(f"❌ Error in auto-reporting: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        self.is_running = True
        reporting_thread = threading.Thread(target=reporting_loop, daemon=True)
        reporting_thread.start()
        print(f"✅ Auto-reporting service started (interval: {self.reporting_interval} minutes)")
    
    def stop_auto_reporting(self):
        """Stop automated reporting"""
        self.is_running = False
        print("⏹️  Auto-reporting service stopped")
    
    def _process_pending_reports(self):
        """Process pending violation reports"""
        from database.models import EmissionViolations
        
        try:
            # Get unreported violations
            pending_violations = EmissionViolations.query.filter_by(
                reported_to_authority=False
            ).limit(10).all()  # Process in batches
            
            for violation in pending_violations:
                try:
                    # Prepare violation data
                    violation_data = {
                        'violation_id': violation.id,
                        'license_plate': violation.license_plate,
                        'violation_type': violation.violation_type,
                        'timestamp': violation.timestamp.isoformat() if violation.timestamp else None,
                        'location_lat': violation.location_lat,
                        'location_lng': violation.location_lng,
                        'lez_zone_name': violation.lez_zone.zone_name if violation.lez_zone else 'Unknown',
                        'evidence_image_path': violation.evidence_image_path,
                        'fine_amount': float(violation.fine_amount) if violation.fine_amount else 0,
                        'confidence': violation.confidence,
                        'smoke_level': violation.smoke_level,
                        'vehicle_condition_score': violation.vehicle_condition_score,
                        'camera_id': violation.camera_id
                    }
                    
                    # Report to government system
                    result = self.api.report_violation(violation_data)
                    
                    if result.get('status') == 'success':
                        # Update violation record
                        violation.reported_to_authority = True
                        violation.authority_response = json.dumps(result)
                        violation.processed_at = datetime.now()
                        
                        # Generate fine notice
                        fine_notice = self.api.generate_fine_notice(violation_data)
                        if fine_notice and 'error' not in fine_notice:
                            violation.fine_status = 'issued'
                        
                        print(f"✅ Reported violation: {violation.license_plate} - {violation.violation_type}")
                    else:
                        print(f"❌ Failed to report violation {violation.id}: {result.get('error')}")
                
                except Exception as e:
                    print(f"❌ Error processing violation {violation.id}: {e}")
            
            # Commit changes
            from database.models import db
            db.session.commit()
            
            if pending_violations:
                print(f"📊 Processed {len(pending_violations)} violation reports")
                
        except Exception as e:
            print(f"❌ Error in pending reports processing: {e}")