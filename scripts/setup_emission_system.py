#!/usr/bin/env python3
"""
Setup script for OPPO A92 Vehicle Control - Emission System Extension
Initializes database with emission standards, sample LEZ zones, and test data
"""

import os
import sys
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database.models import (
    db, Vehicle, AccessLog, 
    EmissionStandards, LEZZones, EmissionViolations, VehicleEmissionData
)

def create_emission_standards():
    """Create emission standards for Vietnamese vehicles"""
    print("📋 Creating emission standards...")
    
    standards = [
        # Motorcycles
        {
            'vehicle_type': 'motorcycle',
            'manufacture_year_start': 2020,
            'manufacture_year_end': 2030,
            'euro_standard': 'Euro 5',
            'co_limit': 2.0,
            'nox_limit': 0.15,
            'pm_limit': 0.01,
            'hc_limit': 0.8
        },
        {
            'vehicle_type': 'motorcycle',
            'manufacture_year_start': 2015,
            'manufacture_year_end': 2019,
            'euro_standard': 'Euro 4',
            'co_limit': 3.5,
            'nox_limit': 0.25,
            'pm_limit': 0.02,
            'hc_limit': 1.2
        },
        {
            'vehicle_type': 'motorcycle',
            'manufacture_year_start': 2010,
            'manufacture_year_end': 2014,
            'euro_standard': 'Euro 3',
            'co_limit': 5.0,
            'nox_limit': 0.4,
            'pm_limit': 0.03,
            'hc_limit': 1.8
        },
        
        # Cars
        {
            'vehicle_type': 'car',
            'manufacture_year_start': 2020,
            'manufacture_year_end': 2030,
            'euro_standard': 'Euro 6',
            'co_limit': 1.0,
            'nox_limit': 0.08,
            'pm_limit': 0.005,
            'hc_limit': 0.1
        },
        {
            'vehicle_type': 'car',
            'manufacture_year_start': 2015,
            'manufacture_year_end': 2019,
            'euro_standard': 'Euro 5',
            'co_limit': 1.8,
            'nox_limit': 0.18,
            'pm_limit': 0.01,
            'hc_limit': 0.15
        },
        {
            'vehicle_type': 'car',
            'manufacture_year_start': 2010,
            'manufacture_year_end': 2014,
            'euro_standard': 'Euro 4',
            'co_limit': 2.5,
            'nox_limit': 0.3,
            'pm_limit': 0.02,
            'hc_limit': 0.25
        },
        
        # Trucks
        {
            'vehicle_type': 'truck',
            'manufacture_year_start': 2018,
            'manufacture_year_end': 2030,
            'euro_standard': 'Euro 6',
            'co_limit': 4.0,
            'nox_limit': 0.4,
            'pm_limit': 0.01,
            'hc_limit': 0.13
        },
        {
            'vehicle_type': 'truck',
            'manufacture_year_start': 2012,
            'manufacture_year_end': 2017,
            'euro_standard': 'Euro 5',
            'co_limit': 5.0,
            'nox_limit': 2.0,
            'pm_limit': 0.02,
            'hc_limit': 0.46
        },
        
        # Buses
        {
            'vehicle_type': 'bus',
            'manufacture_year_start': 2018,
            'manufacture_year_end': 2030,
            'euro_standard': 'Euro 6',
            'co_limit': 4.0,
            'nox_limit': 0.4,
            'pm_limit': 0.01,
            'hc_limit': 0.13
        },
        {
            'vehicle_type': 'bus',
            'manufacture_year_start': 2012,
            'manufacture_year_end': 2017,
            'euro_standard': 'Euro 5',
            'co_limit': 5.0,
            'nox_limit': 2.0,
            'pm_limit': 0.02,
            'hc_limit': 0.46
        }
    ]
    
    for standard_data in standards:
        existing = EmissionStandards.query.filter_by(
            vehicle_type=standard_data['vehicle_type'],
            euro_standard=standard_data['euro_standard']
        ).first()
        
        if not existing:
            standard = EmissionStandards(**standard_data)
            db.session.add(standard)
            print(f"  ✅ Added {standard_data['vehicle_type']} {standard_data['euro_standard']} standard")
    
    db.session.commit()
    print(f"📋 Created {len(standards)} emission standards")

def create_sample_lez_zones():
    """Create sample LEZ zones for Ho Chi Minh City"""
    print("🌍 Creating sample LEZ zones...")
    
    zones = [
        {
            'zone_name': 'District 1 Center',
            'zone_code': 'LEZ-D1-CENTER',
            'coordinates': json.dumps([
                [10.7769, 106.7009],  # City center coordinates
                [10.7800, 106.7000],
                [10.7850, 106.7050],
                [10.7820, 106.7080],
                [10.7769, 106.7009]
            ]),
            'restriction_hours': '06:00-22:00',
            'allowed_euro_standards': json.dumps(['Euro 5', 'Euro 6']),
            'vehicle_type_restrictions': json.dumps({
                'motorcycle': {'min_year': 2015},
                'car': {'min_year': 2012},
                'truck': {'min_year': 2015},
                'bus': {'min_year': 2015}
            }),
            'fine_amount': Decimal('1000000'),  # 1,000,000 VND
            'is_active': True
        },
        {
            'zone_name': 'District 3 Commercial',
            'zone_code': 'LEZ-D3-COMM',
            'coordinates': json.dumps([
                [10.7850, 106.6950],
                [10.7900, 106.6950],
                [10.7900, 106.7000],
                [10.7850, 106.7000],
                [10.7850, 106.6950]
            ]),
            'restriction_hours': '07:00-19:00',
            'allowed_euro_standards': json.dumps(['Euro 4', 'Euro 5', 'Euro 6']),
            'vehicle_type_restrictions': json.dumps({
                'motorcycle': {'min_year': 2012},
                'car': {'min_year': 2010},
                'truck': {'min_year': 2012, 'max_weight': 5000},
                'bus': {'min_year': 2012}
            }),
            'fine_amount': Decimal('500000'),  # 500,000 VND
            'is_active': True
        },
        {
            'zone_name': 'Airport Road Corridor',
            'zone_code': 'LEZ-AIRPORT',
            'coordinates': json.dumps([
                [10.8100, 106.6600],
                [10.8200, 106.6600],
                [10.8200, 106.6700],
                [10.8100, 106.6700],
                [10.8100, 106.6600]
            ]),
            'restriction_hours': '24/7',
            'allowed_euro_standards': json.dumps(['Euro 5', 'Euro 6']),
            'vehicle_type_restrictions': json.dumps({
                'motorcycle': {'min_year': 2018},
                'car': {'min_year': 2015},
                'truck': {'min_year': 2018},
                'bus': {'min_year': 2018}
            }),
            'fine_amount': Decimal('2000000'),  # 2,000,000 VND
            'is_active': True
        },
        {
            'zone_name': 'School Zone - District 10',
            'zone_code': 'LEZ-SCHOOL-D10',
            'coordinates': json.dumps([
                [10.7700, 106.6800],
                [10.7750, 106.6800],
                [10.7750, 106.6850],
                [10.7700, 106.6850],
                [10.7700, 106.6800]
            ]),
            'restriction_hours': '06:30-17:30',
            'allowed_euro_standards': json.dumps(['Euro 4', 'Euro 5', 'Euro 6']),
            'vehicle_type_restrictions': json.dumps({
                'motorcycle': {'min_year': 2015},
                'car': {'min_year': 2012},
                'truck': {'prohibited': True},
                'bus': {'electric_only': True}
            }),
            'fine_amount': Decimal('750000'),  # 750,000 VND
            'is_active': False  # Not active yet
        }
    ]
    
    for zone_data in zones:
        existing = LEZZones.query.filter_by(zone_code=zone_data['zone_code']).first()
        
        if not existing:
            zone = LEZZones(**zone_data)
            db.session.add(zone)
            print(f"  ✅ Added LEZ zone: {zone_data['zone_name']}")
    
    db.session.commit()
    print(f"🌍 Created {len(zones)} LEZ zones")

def create_sample_vehicle_emission_data():
    """Create sample vehicle emission data"""
    print("🚗 Creating sample vehicle emission data...")
    
    # Get existing vehicles
    vehicles = Vehicle.query.all()
    
    if not vehicles:
        print("  ⚠️  No vehicles found. Creating sample vehicles first...")
        create_sample_vehicles()
        vehicles = Vehicle.query.all()
    
    emission_data_list = []
    
    for i, vehicle in enumerate(vehicles[:10]):  # Limit to first 10 vehicles
        # Determine emission data based on vehicle type and simulated age
        base_year = 2015 + (i % 8)  # Years 2015-2022
        
        if vehicle.vehicle_type == 'motorcycle':
            euro_standard = 'Euro 4' if base_year >= 2015 else 'Euro 3'
            engine_cc = 110 + (i % 3) * 50  # 110, 160, 210cc
            fuel_type = 'gasoline'
        elif vehicle.vehicle_type == 'car':
            euro_standard = 'Euro 5' if base_year >= 2018 else 'Euro 4'
            engine_cc = 1500 + (i % 4) * 500  # 1500-3000cc
            fuel_type = 'gasoline' if i % 4 != 0 else 'diesel'
        else:  # truck/bus
            euro_standard = 'Euro 5' if base_year >= 2016 else 'Euro 4'
            engine_cc = 3000 + (i % 3) * 1000  # 3000-5000cc
            fuel_type = 'diesel'
        
        # Calculate environmental score based on vehicle characteristics
        age = datetime.now().year - base_year
        base_score = 50
        age_penalty = age * 3
        euro_bonus = {'Euro 6': -15, 'Euro 5': -10, 'Euro 4': 0, 'Euro 3': 10}.get(euro_standard, 15)
        env_score = max(0, min(100, base_score + age_penalty + euro_bonus))
        
        emission_data = {
            'license_plate': vehicle.license_plate,
            'manufacture_year': base_year,
            'engine_displacement': engine_cc,
            'fuel_type': fuel_type,
            'euro_standard': euro_standard,
            'last_emission_test_date': datetime.now().date() - timedelta(days=30 + i*10),
            'last_emission_test_result': 'pass' if env_score < 70 else 'fail',
            'co_emission': 2.5 - (0.3 * (ord(euro_standard[-1]) - ord('3'))),  # Better euro = lower emissions
            'nox_emission': 0.4 - (0.05 * (ord(euro_standard[-1]) - ord('3'))),
            'pm_emission': 0.03 - (0.005 * (ord(euro_standard[-1]) - ord('3'))),
            'hc_emission': 1.2 - (0.15 * (ord(euro_standard[-1]) - ord('3'))),
            'environmental_impact_score': env_score,
            'lez_access_permitted': env_score < 60,
            'restriction_notes': 'High emissions detected' if env_score >= 70 else None
        }
        
        emission_data_list.append(emission_data)
    
    for data in emission_data_list:
        existing = VehicleEmissionData.query.filter_by(
            license_plate=data['license_plate']
        ).first()
        
        if not existing:
            emission_record = VehicleEmissionData(**data)
            db.session.add(emission_record)
            print(f"  ✅ Added emission data for {data['license_plate']}")
    
    db.session.commit()
    print(f"🚗 Created emission data for {len(emission_data_list)} vehicles")

def create_sample_violations():
    """Create sample emission violations"""
    print("⚠️  Creating sample emission violations...")
    
    # Get LEZ zones and vehicles
    lez_zones = LEZZones.query.all()
    vehicles = Vehicle.query.all()
    
    if not lez_zones or not vehicles:
        print("  ⚠️  No LEZ zones or vehicles found. Skipping violation creation.")
        return
    
    violations = []
    
    for i in range(15):  # Create 15 sample violations
        zone = lez_zones[i % len(lez_zones)]
        vehicle = vehicles[i % len(vehicles)]
        
        # Randomize violation types and times
        violation_types = ['lez_entry', 'smoke_detection', 'age_restriction']
        violation_type = violation_types[i % len(violation_types)]
        
        # Create violation timestamp (last 7 days)
        violation_time = datetime.now() - timedelta(
            days=i % 7,
            hours=i % 24,
            minutes=i % 60
        )
        
        violation_data = {
            'license_plate': vehicle.license_plate,
            'violation_type': violation_type,
            'lez_zone_id': zone.id,
            'detected_vehicle_type': vehicle.vehicle_type,
            'estimated_year': 2010 + (i % 12),
            'euro_standard': ['Euro 3', 'Euro 4', 'Euro 5'][i % 3],
            'smoke_level': 0.1 + (i % 5) * 0.2,  # 0.1 to 0.9
            'vehicle_condition_score': 0.3 + (i % 7) * 0.1,  # 0.3 to 0.9
            'confidence': 0.6 + (i % 4) * 0.1,  # 0.6 to 0.9
            'fine_amount': zone.fine_amount,
            'fine_status': ['pending', 'issued', 'paid'][i % 3],
            'evidence_image_path': f'/evidence/violation_{i+1}.jpg',
            'location_lat': 10.7769 + (i % 10) * 0.001,
            'location_lng': 106.7009 + (i % 10) * 0.001,
            'camera_id': f'CAM_{(i % 5) + 1:02d}',
            'reported_to_authority': i % 3 == 0,  # 1/3 reported
            'timestamp': violation_time
        }
        
        violations.append(violation_data)
    
    for data in violations:
        violation = EmissionViolations(**data)
        db.session.add(violation)
        print(f"  ✅ Added violation: {data['license_plate']} - {data['violation_type']}")
    
    db.session.commit()
    print(f"⚠️  Created {len(violations)} sample violations")

def create_sample_vehicles():
    """Create sample vehicles if none exist"""
    print("🚗 Creating sample vehicles...")
    
    sample_vehicles = [
        {'license_plate': '29A-12345', 'owner_name': 'Nguyen Van A', 'vehicle_type': 'car'},
        {'license_plate': '51H-67890', 'owner_name': 'Tran Thi B', 'vehicle_type': 'motorcycle'},
        {'license_plate': '30G-11111', 'owner_name': 'Le Van C', 'vehicle_type': 'car'},
        {'license_plate': '59A-22222', 'owner_name': 'Pham Thi D', 'vehicle_type': 'motorcycle'},
        {'license_plate': '43B-33333', 'owner_name': 'Hoang Van E', 'vehicle_type': 'truck'},
        {'license_plate': '50F-44444', 'owner_name': 'Vo Thi F', 'vehicle_type': 'bus'},
        {'license_plate': '77S-55555', 'owner_name': 'Dao Van G', 'vehicle_type': 'car'},
        {'license_plate': '61C-66666', 'owner_name': 'Bui Thi H', 'vehicle_type': 'motorcycle'},
    ]
    
    for vehicle_data in sample_vehicles:
        existing = Vehicle.query.filter_by(license_plate=vehicle_data['license_plate']).first()
        if not existing:
            vehicle = Vehicle(**vehicle_data)
            db.session.add(vehicle)
            print(f"  ✅ Added vehicle: {vehicle_data['license_plate']}")
    
    db.session.commit()

def initialize_emission_system():
    """Initialize the complete emission control system"""
    print("=" * 60)
    print("🚀 OPPO A92 Vehicle Control - Emission System Setup")
    print("=" * 60)
    
    try:
        with app.app_context():
            # Create all database tables
            print("🗄️  Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create emission standards
            create_emission_standards()
            
            # Create sample LEZ zones
            create_sample_lez_zones()
            
            # Create sample vehicle emission data
            create_sample_vehicle_emission_data()
            
            # Create sample violations
            create_sample_violations()
            
            print("\n" + "=" * 60)
            print("✅ EMISSION SYSTEM SETUP COMPLETED!")
            print("=" * 60)
            print("\n📊 System Summary:")
            print(f"  • Emission Standards: {EmissionStandards.query.count()}")
            print(f"  • LEZ Zones: {LEZZones.query.count()}")
            print(f"  • Vehicles with Emission Data: {VehicleEmissionData.query.count()}")
            print(f"  • Sample Violations: {EmissionViolations.query.count()}")
            print(f"  • Total Vehicles: {Vehicle.query.count()}")
            
            print("\n🌐 Next Steps:")
            print("  1. Start the application: python app.py")
            print("  2. Visit LEZ Dashboard: http://localhost:5000/lez")
            print("  3. Check emission statistics and violations")
            print("  4. Configure real camera for live detection")
            
            print("\n🔧 Configuration:")
            print("  • Emission detection: Enabled")
            print("  • LEZ enforcement: Enabled")
            print("  • Government API: Demo mode")
            print("  • Auto-reporting: Enabled")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = initialize_emission_system()
    sys.exit(0 if success else 1)