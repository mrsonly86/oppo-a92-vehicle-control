"""
Emission calculation utilities for OPPO A92 Vehicle Control System
Handles emission impact calculations, LEZ compliance, and environmental reporting
"""
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class EmissionCalculator:
    """
    Calculate emissions and environmental impact for vehicles
    """
    
    def __init__(self):
        """Initialize emission calculator with Vietnamese standards"""
        
        # Vietnamese emission factors (approximate values)
        self.emission_factors = {
            'motorcycle': {
                'co_factor': 12.0,    # g/km for older motorcycles
                'nox_factor': 0.3,    # g/km
                'pm_factor': 0.05,    # g/km
                'hc_factor': 2.5      # g/km
            },
            'car': {
                'co_factor': 8.0,     # g/km for older cars
                'nox_factor': 1.2,    # g/km
                'pm_factor': 0.08,    # g/km  
                'hc_factor': 1.8      # g/km
            },
            'truck': {
                'co_factor': 15.0,    # g/km for trucks
                'nox_factor': 8.0,    # g/km
                'pm_factor': 0.5,     # g/km
                'hc_factor': 3.0      # g/km
            },
            'bus': {
                'co_factor': 12.0,    # g/km for buses
                'nox_factor': 10.0,   # g/km
                'pm_factor': 0.6,     # g/km
                'hc_factor': 2.5      # g/km
            }
        }
        
        # Euro standard improvement factors (reduction multiplier)
        self.euro_improvements = {
            'Euro 1': 1.0,      # Baseline
            'Euro 2': 0.8,      # 20% improvement
            'Euro 3': 0.6,      # 40% improvement
            'Euro 4': 0.4,      # 60% improvement
            'Euro 5': 0.25,     # 75% improvement
            'Euro 6': 0.15,     # 85% improvement
            'Unknown': 1.2      # Assume worse than baseline
        }
        
        # Health impact factors (relative harm per gram)
        self.health_impact_factors = {
            'co': 0.1,      # Low direct health impact
            'nox': 1.5,     # Moderate health impact
            'pm': 10.0,     # High health impact (particulates)
            'hc': 0.8       # Moderate health impact
        }
        
        # Economic cost factors (VND per gram)
        self.economic_cost_factors = {
            'co': 50,       # VND per gram
            'nox': 200,     # VND per gram
            'pm': 1000,     # VND per gram (very expensive)
            'hc': 100       # VND per gram
        }
    
    def calculate_emission_profile(self, vehicle_data: Dict, distance_km: float = 1.0) -> Dict:
        """
        Calculate emission profile for a vehicle
        
        Args:
            vehicle_data: Dict containing vehicle information
            distance_km: Distance to calculate emissions for (default 1km)
            
        Returns:
            Dict: Detailed emission profile
        """
        try:
            vehicle_type = vehicle_data.get('vehicle_type', 'car').lower()
            euro_standard = vehicle_data.get('euro_standard', 'Unknown')
            
            # Get base emission factors
            base_factors = self.emission_factors.get(vehicle_type, self.emission_factors['car'])
            
            # Apply Euro standard improvements
            improvement_factor = self.euro_improvements.get(euro_standard, 1.0)
            
            # Calculate emissions per km
            emissions_per_km = {
                'co': base_factors['co_factor'] * improvement_factor,
                'nox': base_factors['nox_factor'] * improvement_factor,
                'pm': base_factors['pm_factor'] * improvement_factor,
                'hc': base_factors['hc_factor'] * improvement_factor
            }
            
            # Calculate for specified distance
            total_emissions = {
                pollutant: value * distance_km 
                for pollutant, value in emissions_per_km.items()
            }
            
            # Calculate health impact score
            health_impact = sum(
                emissions * self.health_impact_factors[pollutant]
                for pollutant, emissions in total_emissions.items()
            )
            
            # Calculate economic cost
            economic_cost = sum(
                emissions * self.economic_cost_factors[pollutant]
                for pollutant, emissions in total_emissions.items()
            )
            
            return {
                'vehicle_type': vehicle_type,
                'euro_standard': euro_standard,
                'distance_km': distance_km,
                'emissions_per_km': emissions_per_km,
                'total_emissions': total_emissions,
                'total_health_impact': health_impact,
                'economic_cost_vnd': economic_cost,
                'emission_class': self._classify_emission_level(total_emissions),
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error calculating emission profile: {e}")
            return self._default_emission_profile()
    
    def check_lez_compliance(self, vehicle_data: Dict, lez_zone_data: Dict) -> Dict:
        """
        Check if vehicle complies with LEZ requirements
        
        Args:
            vehicle_data: Dict containing vehicle information
            lez_zone_data: Dict containing LEZ zone requirements
            
        Returns:
            Dict: Compliance check results
        """
        try:
            vehicle_type = vehicle_data.get('vehicle_type', 'car').lower()
            vehicle_euro = vehicle_data.get('euro_standard', 'Unknown')
            manufacture_year = vehicle_data.get('manufacture_year', 2000)
            
            # Parse LEZ requirements
            allowed_standards = json.loads(lez_zone_data.get('allowed_euro_standards', '[]'))
            vehicle_restrictions = json.loads(lez_zone_data.get('vehicle_type_restrictions', '{}'))
            
            # Check Euro standard compliance
            euro_compliant = vehicle_euro in allowed_standards
            
            # Check vehicle type restrictions
            type_restrictions = vehicle_restrictions.get(vehicle_type, {})
            min_year = type_restrictions.get('min_year', 2000)
            year_compliant = manufacture_year >= min_year
            
            # Check time restrictions
            current_time = datetime.now().time()
            restriction_hours = lez_zone_data.get('restriction_hours', '24/7')
            time_restricted = self._is_time_restricted(current_time, restriction_hours)
            
            # Overall compliance
            compliant = euro_compliant and year_compliant and not time_restricted
            
            # Calculate violation severity
            violation_severity = self._calculate_violation_severity(
                vehicle_data, lez_zone_data, euro_compliant, year_compliant
            )
            
            return {
                'compliant': compliant,
                'euro_compliant': euro_compliant,
                'year_compliant': year_compliant,
                'time_restricted': time_restricted,
                'violation_severity': violation_severity,
                'allowed_standards': allowed_standards,
                'vehicle_euro_standard': vehicle_euro,
                'required_min_year': min_year,
                'vehicle_year': manufacture_year,
                'zone_name': lez_zone_data.get('zone_name', 'Unknown'),
                'fine_amount': float(lez_zone_data.get('fine_amount', 0)),
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error checking LEZ compliance: {e}")
            return self._default_compliance_result()
    
    def calculate_fine_amount(self, violation_data: Dict, lez_zone_data: Dict) -> float:
        """
        Calculate appropriate fine amount for emission violation
        
        Args:
            violation_data: Dict containing violation information
            lez_zone_data: Dict containing LEZ zone information
            
        Returns:
            float: Fine amount in VND
        """
        try:
            base_fine = float(lez_zone_data.get('fine_amount', 500000))  # 500,000 VND default
            
            # Severity multiplier
            severity = violation_data.get('violation_severity', 'medium')
            severity_multipliers = {
                'low': 1.0,
                'medium': 1.5,
                'high': 2.0,
                'severe': 3.0
            }
            
            severity_multiplier = severity_multipliers.get(severity, 1.5)
            
            # Repeat offender multiplier
            is_repeat = violation_data.get('is_repeat_offender', False)
            repeat_multiplier = 2.0 if is_repeat else 1.0
            
            # Vehicle type multiplier (larger vehicles higher fines)
            vehicle_type = violation_data.get('vehicle_type', 'car')
            type_multipliers = {
                'motorcycle': 0.8,
                'car': 1.0,
                'truck': 1.5,
                'bus': 2.0
            }
            
            type_multiplier = type_multipliers.get(vehicle_type, 1.0)
            
            # Calculate final fine
            final_fine = base_fine * severity_multiplier * repeat_multiplier * type_multiplier
            
            # Round to nearest 10,000 VND
            return round(final_fine / 10000) * 10000
            
        except Exception as e:
            print(f"❌ Error calculating fine amount: {e}")
            return 500000.0  # Default fine
    
    def generate_environmental_report(self, vehicles_data: List[Dict], time_period: str = 'daily') -> Dict:
        """
        Generate environmental impact report for multiple vehicles
        
        Args:
            vehicles_data: List of vehicle detection data
            time_period: 'hourly', 'daily', 'weekly', 'monthly'
            
        Returns:
            Dict: Comprehensive environmental report
        """
        try:
            total_vehicles = len(vehicles_data)
            
            if total_vehicles == 0:
                return self._empty_report(time_period)
            
            # Categorize vehicles by type and emission level
            categorization = self._categorize_vehicles(vehicles_data)
            
            # Calculate total emissions
            total_emissions = self._calculate_total_emissions(vehicles_data)
            
            # Calculate health impact
            total_health_impact = sum(
                emissions * self.health_impact_factors[pollutant]
                for pollutant, emissions in total_emissions.items()
            )
            
            # Calculate economic cost
            total_economic_cost = sum(
                emissions * self.economic_cost_factors[pollutant]
                for pollutant, emissions in total_emissions.items()
            )
            
            # Identify top polluters
            top_polluters = self._identify_top_polluters(vehicles_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(categorization, total_emissions)
            
            return {
                'report_period': time_period,
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_vehicles_detected': total_vehicles,
                    'total_health_impact_score': total_health_impact,
                    'total_economic_cost_vnd': total_economic_cost,
                    'average_emission_per_vehicle': self._calculate_average_emissions(vehicles_data)
                },
                'categorization': categorization,
                'total_emissions': total_emissions,
                'top_polluters': top_polluters,
                'recommendations': recommendations,
                'compliance_rate': self._calculate_compliance_rate(vehicles_data),
                'pollution_trends': self._analyze_pollution_trends(vehicles_data)
            }
            
        except Exception as e:
            print(f"❌ Error generating environmental report: {e}")
            return self._empty_report(time_period)
    
    def _classify_emission_level(self, emissions: Dict) -> str:
        """Classify emission level as low, medium, high, or severe"""
        total_weighted = (
            emissions.get('co', 0) * 0.1 +
            emissions.get('nox', 0) * 1.5 +
            emissions.get('pm', 0) * 10.0 +
            emissions.get('hc', 0) * 0.8
        )
        
        if total_weighted < 5:
            return 'low'
        elif total_weighted < 15:
            return 'medium'
        elif total_weighted < 30:
            return 'high'
        else:
            return 'severe'
    
    def _is_time_restricted(self, current_time, restriction_hours: str) -> bool:
        """Check if current time falls within restriction hours"""
        try:
            if restriction_hours == '24/7':
                return True
            
            if '-' in restriction_hours:
                start_str, end_str = restriction_hours.split('-')
                start_time = datetime.strptime(start_str, '%H:%M').time()
                end_time = datetime.strptime(end_str, '%H:%M').time()
                
                if start_time <= end_time:
                    return start_time <= current_time <= end_time
                else:
                    # Overnight restriction
                    return current_time >= start_time or current_time <= end_time
            
            return False
            
        except Exception:
            return False
    
    def _calculate_violation_severity(self, vehicle_data: Dict, lez_data: Dict, 
                                   euro_compliant: bool, year_compliant: bool) -> str:
        """Calculate violation severity based on multiple factors"""
        try:
            severity_score = 0
            
            # Euro standard violation
            if not euro_compliant:
                vehicle_euro = vehicle_data.get('euro_standard', 'Unknown')
                if vehicle_euro in ['Euro 1', 'Euro 2', 'Unknown']:
                    severity_score += 3
                elif vehicle_euro == 'Euro 3':
                    severity_score += 2
                else:
                    severity_score += 1
            
            # Age violation
            if not year_compliant:
                age = datetime.now().year - vehicle_data.get('manufacture_year', 2000)
                if age > 20:
                    severity_score += 3
                elif age > 15:
                    severity_score += 2
                else:
                    severity_score += 1
            
            # Smoke detection
            if vehicle_data.get('smoke_detected', False):
                severity_score += 2
            
            # Vehicle condition
            condition_score = vehicle_data.get('condition_score', 0.5)
            if condition_score < 0.3:
                severity_score += 2
            elif condition_score < 0.5:
                severity_score += 1
            
            # Map score to severity level
            if severity_score >= 6:
                return 'severe'
            elif severity_score >= 4:
                return 'high'
            elif severity_score >= 2:
                return 'medium'
            else:
                return 'low'
                
        except Exception:
            return 'medium'
    
    def _categorize_vehicles(self, vehicles_data: List[Dict]) -> Dict:
        """Categorize vehicles by type and emission characteristics"""
        categories = {
            'by_type': {},
            'by_euro_standard': {},
            'by_emission_level': {},
            'by_age_group': {}
        }
        
        for vehicle in vehicles_data:
            # By type
            v_type = vehicle.get('vehicle_type', 'unknown')
            categories['by_type'][v_type] = categories['by_type'].get(v_type, 0) + 1
            
            # By Euro standard
            euro = vehicle.get('euro_standard', 'Unknown')
            categories['by_euro_standard'][euro] = categories['by_euro_standard'].get(euro, 0) + 1
            
            # By emission level
            emission_profile = self.calculate_emission_profile(vehicle)
            emission_class = emission_profile['emission_class']
            categories['by_emission_level'][emission_class] = categories['by_emission_level'].get(emission_class, 0) + 1
            
            # By age group
            year = vehicle.get('manufacture_year', 2000)
            age_group = self._get_age_group(year)
            categories['by_age_group'][age_group] = categories['by_age_group'].get(age_group, 0) + 1
        
        return categories
    
    def _calculate_total_emissions(self, vehicles_data: List[Dict]) -> Dict:
        """Calculate total emissions from all vehicles"""
        total = {'co': 0, 'nox': 0, 'pm': 0, 'hc': 0}
        
        for vehicle in vehicles_data:
            profile = self.calculate_emission_profile(vehicle)
            emissions = profile['total_emissions']
            
            for pollutant in total:
                total[pollutant] += emissions.get(pollutant, 0)
        
        return total
    
    def _get_age_group(self, manufacture_year: int) -> str:
        """Get age group for a vehicle"""
        age = datetime.now().year - manufacture_year
        
        if age <= 2:
            return 'new (0-2 years)'
        elif age <= 5:
            return 'recent (3-5 years)'
        elif age <= 10:
            return 'moderate (6-10 years)'
        elif age <= 15:
            return 'old (11-15 years)'
        else:
            return 'very_old (16+ years)'
    
    def _identify_top_polluters(self, vehicles_data: List[Dict], limit: int = 5) -> List[Dict]:
        """Identify vehicles with highest emissions"""
        polluter_scores = []
        
        for vehicle in vehicles_data:
            profile = self.calculate_emission_profile(vehicle)
            health_impact = profile['total_health_impact']
            
            polluter_scores.append({
                'license_plate': vehicle.get('license_plate', 'Unknown'),
                'vehicle_type': vehicle.get('vehicle_type', 'unknown'),
                'health_impact_score': health_impact,
                'emissions': profile['total_emissions'],
                'euro_standard': vehicle.get('euro_standard', 'Unknown')
            })
        
        # Sort by health impact and return top polluters
        polluter_scores.sort(key=lambda x: x['health_impact_score'], reverse=True)
        return polluter_scores[:limit]
    
    def _generate_recommendations(self, categorization: Dict, total_emissions: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check emission levels
        emission_levels = categorization['by_emission_level']
        high_polluters = emission_levels.get('high', 0) + emission_levels.get('severe', 0)
        total_vehicles = sum(emission_levels.values())
        
        if high_polluters / total_vehicles > 0.3:
            recommendations.append("High pollution detected. Consider stricter LEZ enforcement.")
        
        # Check Euro standards
        euro_standards = categorization['by_euro_standard']
        old_standards = euro_standards.get('Euro 1', 0) + euro_standards.get('Euro 2', 0) + euro_standards.get('Unknown', 0)
        
        if old_standards / total_vehicles > 0.2:
            recommendations.append("Many old vehicles detected. Promote vehicle renewal programs.")
        
        # Check vehicle types
        vehicle_types = categorization['by_type']
        if vehicle_types.get('truck', 0) + vehicle_types.get('bus', 0) > vehicle_types.get('car', 0):
            recommendations.append("High proportion of heavy vehicles. Consider separate restrictions.")
        
        return recommendations
    
    def _calculate_compliance_rate(self, vehicles_data: List[Dict]) -> float:
        """Calculate overall compliance rate"""
        if not vehicles_data:
            return 0.0
        
        compliant_count = sum(
            1 for vehicle in vehicles_data 
            if vehicle.get('lez_compliant', True)
        )
        
        return compliant_count / len(vehicles_data)
    
    def _analyze_pollution_trends(self, vehicles_data: List[Dict]) -> Dict:
        """Analyze pollution trends"""
        # Simplified trend analysis
        high_emission_count = sum(
            1 for vehicle in vehicles_data
            if self.calculate_emission_profile(vehicle)['emission_class'] in ['high', 'severe']
        )
        
        return {
            'high_emission_percentage': high_emission_count / len(vehicles_data) if vehicles_data else 0,
            'trend_direction': 'stable',  # Would need time series data for real analysis
            'improvement_needed': high_emission_count > len(vehicles_data) * 0.2
        }
    
    def _calculate_average_emissions(self, vehicles_data: List[Dict]) -> Dict:
        """Calculate average emissions per vehicle"""
        if not vehicles_data:
            return {'co': 0, 'nox': 0, 'pm': 0, 'hc': 0}
        
        total_emissions = self._calculate_total_emissions(vehicles_data)
        count = len(vehicles_data)
        
        return {
            pollutant: emissions / count
            for pollutant, emissions in total_emissions.items()
        }
    
    def _default_emission_profile(self) -> Dict:
        """Default emission profile when calculation fails"""
        return {
            'vehicle_type': 'unknown',
            'euro_standard': 'Unknown',
            'distance_km': 1.0,
            'emissions_per_km': {'co': 0, 'nox': 0, 'pm': 0, 'hc': 0},
            'total_emissions': {'co': 0, 'nox': 0, 'pm': 0, 'hc': 0},
            'total_health_impact': 0,
            'economic_cost_vnd': 0,
            'emission_class': 'unknown',
            'calculated_at': datetime.now().isoformat()
        }
    
    def _default_compliance_result(self) -> Dict:
        """Default compliance result when check fails"""
        return {
            'compliant': True,
            'euro_compliant': True,
            'year_compliant': True,
            'time_restricted': False,
            'violation_severity': 'low',
            'allowed_standards': [],
            'vehicle_euro_standard': 'Unknown',
            'required_min_year': 2000,
            'vehicle_year': 2000,
            'zone_name': 'Unknown',
            'fine_amount': 0.0,
            'checked_at': datetime.now().isoformat()
        }
    
    def _empty_report(self, time_period: str) -> Dict:
        """Empty report when no data available"""
        return {
            'report_period': time_period,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_vehicles_detected': 0,
                'total_health_impact_score': 0,
                'total_economic_cost_vnd': 0,
                'average_emission_per_vehicle': {'co': 0, 'nox': 0, 'pm': 0, 'hc': 0}
            },
            'categorization': {
                'by_type': {},
                'by_euro_standard': {},
                'by_emission_level': {},
                'by_age_group': {}
            },
            'total_emissions': {'co': 0, 'nox': 0, 'pm': 0, 'hc': 0},
            'top_polluters': [],
            'recommendations': ['No data available for analysis'],
            'compliance_rate': 1.0,
            'pollution_trends': {
                'high_emission_percentage': 0,
                'trend_direction': 'stable',
                'improvement_needed': False
            }
        }

# Helper functions for quick calculations
def quick_emission_check(vehicle_type: str, euro_standard: str, year: int) -> Dict:
    """Quick emission compliance check"""
    calculator = EmissionCalculator()
    
    vehicle_data = {
        'vehicle_type': vehicle_type,
        'euro_standard': euro_standard,
        'manufacture_year': year
    }
    
    return calculator.calculate_emission_profile(vehicle_data)

def quick_lez_check(vehicle_data: Dict, zone_requirements: Dict) -> bool:
    """Quick LEZ compliance check"""
    calculator = EmissionCalculator()
    
    result = calculator.check_lez_compliance(vehicle_data, zone_requirements)
    return result['compliant']