#!/usr/bin/env python3

"""
Advanced GUI Configuration Handler
Provides advanced features like ROS2 parameter integration, config validation, and mission planning.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys


class ConfigValidator:
    """Validates mission configurations"""
    
    @staticmethod
    def validate_position(pos: Tuple[float, float], grid_size: int) -> bool:
        """Validate if position is within grid bounds"""
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            return False
        x, y = pos
        return 0 <= x < grid_size and 0 <= y < grid_size
    
    @staticmethod
    def validate_config(config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate entire configuration
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        grid_size = config.get("grid_size", 6)
        
        # Validate start point
        if not ConfigValidator.validate_position(config.get("start", (0, 0)), grid_size):
            errors.append("Start point is outside grid bounds")
        
        # Validate goal point
        if not ConfigValidator.validate_position(config.get("goal", (0, 0)), grid_size):
            errors.append("Goal point is outside grid bounds")
        
        # Validate emergency goal
        if not ConfigValidator.validate_position(config.get("emergency_goal", (0, 0)), grid_size):
            errors.append("Emergency goal is outside grid bounds")
        
        # Validate dynamic obstacle
        if not ConfigValidator.validate_position(config.get("dynamic_obstacle", (0, 0)), grid_size):
            errors.append("Dynamic obstacle is outside grid bounds")
        
        # Check start != goal
        if config.get("start") == config.get("goal"):
            errors.append("Start and goal cannot be the same position")
        
        # Validate weather
        valid_weather = ["CLEAR", "WIND", "RAIN", "STORM"]
        if config.get("weather") not in valid_weather:
            errors.append(f"Invalid weather. Must be one of: {valid_weather}")
        
        # Validate battery
        battery = config.get("battery", 80.0)
        if not (0 <= battery <= 100):
            errors.append(f"Battery must be between 0-100%, got {battery}%")
        
        # Validate grid size
        if not (4 <= grid_size <= 20):
            errors.append(f"Grid size must be between 4-20, got {grid_size}")
        
        # Validate obstacles within bounds
        for idx, obs in enumerate(config.get("obstacles", [])):
            if not ConfigValidator.validate_position(obs, grid_size):
                errors.append(f"Obstacle {idx} is outside grid bounds")
        
        return len(errors) == 0, errors


class MissionPlanner:
    """Analyzes mission feasibility"""
    
    @staticmethod
    def calculate_distance(start: Tuple[float, float], end: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return ((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5
    
    @staticmethod
    def estimate_battery_cost(
        start: Tuple[float, float],
        goal: Tuple[float, float],
        weather: str,
        obstacles_count: int = 0
    ) -> float:
        """
        Estimate battery cost for mission
        Returns battery percentage consumed
        """
        # Base cost: 1% per unit distance
        distance_cost = MissionPlanner.calculate_distance(start, goal)
        
        # Weather multiplier
        weather_multipliers = {
            "CLEAR": 1.0,
            "WIND": 1.1,
            "RAIN": 1.2,
            "STORM": 1.5
        }
        weather_multiplier = weather_multipliers.get(weather, 1.0)
        
        # Obstacle avoidance cost
        obstacle_cost = obstacles_count * 2.0
        
        total_cost = (distance_cost * weather_multiplier) + obstacle_cost
        return round(total_cost, 2)
    
    @staticmethod
    def analyze_mission(config: Dict) -> Dict:
        """Analyze mission and return analysis"""
        start = config.get("start", (0, 0))
        goal = config.get("goal", (0, 0))
        emergency = config.get("emergency_goal", (0, 0))
        weather = config.get("weather", "CLEAR")
        battery = config.get("battery", 80.0)
        obstacles = config.get("obstacles", [])
        
        # Calculate distances
        main_distance = MissionPlanner.calculate_distance(start, goal)
        emergency_distance = MissionPlanner.calculate_distance(goal, emergency)
        total_distance = main_distance + emergency_distance
        
        # Estimate costs
        main_cost = MissionPlanner.estimate_battery_cost(start, goal, weather, len(obstacles))
        emergency_cost = MissionPlanner.estimate_battery_cost(goal, emergency, weather, 0)
        total_cost = main_cost + emergency_cost
        
        # Feasibility analysis
        is_feasible = battery >= total_cost
        safety_margin = battery - total_cost
        
        # Risk assessment
        risk_level = "SAFE"
        if battery == 100:
            risk_level = "OPTIMAL"
        elif safety_margin < 0:
            risk_level = "CRITICAL"
        elif safety_margin < 20:
            risk_level = "HIGH"
        elif safety_margin < 40:
            risk_level = "MEDIUM"
        elif safety_margin < 60:
            risk_level = "LOW"
        
        return {
            "main_distance": round(main_distance, 2),
            "emergency_distance": round(emergency_distance, 2),
            "total_distance": round(total_distance, 2),
            "main_battery_cost": main_cost,
            "emergency_battery_cost": emergency_cost,
            "total_battery_cost": total_cost,
            "available_battery": battery,
            "safety_margin": round(safety_margin, 2),
            "is_feasible": is_feasible,
            "risk_level": risk_level,
            "weather_impact": MissionPlanner.get_weather_description(weather),
            "obstacle_count": len(obstacles),
            "recommendations": MissionPlanner.get_recommendations(
                config, main_cost, battery, risk_level
            )
        }
    
    @staticmethod
    def get_weather_description(weather: str) -> str:
        """Get weather impact description"""
        descriptions = {
            "CLEAR": "Optimal conditions - no restrictions",
            "WIND": "Increased battery consumption - monitor closely",
            "RAIN": "High battery consumption - reduced range",
            "STORM": "Mission not recommended - safety concern"
        }
        return descriptions.get(weather, "Unknown")
    
    @staticmethod
    def get_recommendations(config: Dict, main_cost: float, battery: float, risk_level: str) -> List[str]:
        """Get recommendations for mission"""
        recommendations = []
        
        if risk_level == "CRITICAL":
            recommendations.append("⚠️ Battery insufficient for mission! Increase battery or reduce distance.")
            recommendations.append("💡 Consider using the emergency goal as intermediate waypoint.")
        elif risk_level == "HIGH":
            recommendations.append("⚠️ Low battery margin - mission risky.")
            recommendations.append("💡 Reduce complexity or improve routing.")
        elif risk_level == "MEDIUM":
            recommendations.append("ℹ️ Moderate risk level - proceed with caution.")
            recommendations.append("💡 Monitor battery levels during flight.")
        elif risk_level == "LOW":
            recommendations.append("✓ Low risk - mission looks feasible.")
        else:  # OPTIMAL
            recommendations.append("✓ Optimal conditions - excellent mission setup.")
        
        if config.get("weather") in ["RAIN", "STORM"]:
            recommendations.append("🌧️ Weather conditions will increase battery consumption.")
        
        if len(config.get("obstacles", [])) > 5:
            recommendations.append("🏔️ Many obstacles - path planning may be complex.")
        
        return recommendations


class ConfigurationManager:
    """Manages mission configurations"""
    
    def __init__(self, config_file: Path = None):
        if config_file is None:
            config_file = Path.home() / ".uav_mission_config.json"
        self.config_file = config_file
        self.config = self.load()
    
    def load(self) -> Dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.get_default_config()
        return self.get_default_config()
    
    def save(self, config: Dict = None) -> bool:
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    @staticmethod
    def get_default_config() -> Dict:
        """Get default configuration"""
        return {
            "start": [0, 0],
            "goal": [4, 5],
            "weather": "RAIN",
            "battery": 80.0,
            "emergency_goal": [2, 2],
            "dynamic_obstacle": [0, 4],
            "grid_size": 6,
            "obstacles": []
        }
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate current configuration"""
        return ConfigValidator.validate_config(self.config)
    
    def analyze(self) -> Dict:
        """Analyze current configuration"""
        return MissionPlanner.analyze_mission(self.config)
    
    def get_report(self) -> str:
        """Get full configuration report"""
        is_valid, errors = self.validate()
        analysis = self.analyze()
        
        report = "\n" + "="*70 + "\n"
        report += "MISSION CONFIGURATION REPORT\n"
        report += "="*70 + "\n\n"
        
        # Configuration
        report += "MISSION PARAMETERS:\n"
        report += f"  Start Point: {self.config['start']}\n"
        report += f"  Goal Point: {self.config['goal']}\n"
        report += f"  Emergency Goal: {self.config['emergency_goal']}\n"
        report += f"  Weather: {self.config['weather']}\n"
        report += f"  Battery: {self.config['battery']}%\n"
        report += f"  Grid Size: {self.config.get('grid_size', 6)}\n"
        report += f"  Static Obstacles: {len(self.config.get('obstacles', []))}\n\n"
        
        # Validation
        report += "VALIDATION:\n"
        if is_valid:
            report += "  ✓ Configuration is valid\n\n"
        else:
            report += "  ✗ Configuration has errors:\n"
            for error in errors:
                report += f"    - {error}\n"
            report += "\n"
        
        # Analysis
        report += "MISSION ANALYSIS:\n"
        report += f"  Main Distance: {analysis['main_distance']} units\n"
        report += f"  Emergency Distance: {analysis['emergency_distance']} units\n"
        report += f"  Total Distance: {analysis['total_distance']} units\n"
        report += f"  Battery Cost (Main): {analysis['main_battery_cost']}%\n"
        report += f"  Battery Cost (Emergency): {analysis['emergency_battery_cost']}%\n"
        report += f"  Total Battery Cost: {analysis['total_battery_cost']}%\n"
        report += f"  Safety Margin: {analysis['safety_margin']}%\n"
        report += f"  Feasibility: {'✓ FEASIBLE' if analysis['is_feasible'] else '✗ NOT FEASIBLE'}\n"
        report += f"  Risk Level: {analysis['risk_level']}\n\n"
        
        # Recommendations
        report += "RECOMMENDATIONS:\n"
        for rec in analysis['recommendations']:
            report += f"  {rec}\n"
        
        report += "\n" + "="*70 + "\n"
        
        return report


def main():
    """CLI interface for configuration management"""
    if len(sys.argv) < 2:
        print("Usage: python3 mission_config_advanced.py [validate|analyze|report|apply]")
        sys.exit(1)
    
    manager = ConfigurationManager()
    command = sys.argv[1].lower()
    
    if command == "validate":
        is_valid, errors = manager.validate()
        if is_valid:
            print("✓ Configuration is valid")
        else:
            print("✗ Configuration has errors:")
            for error in errors:
                print(f"  - {error}")
    
    elif command == "analyze":
        analysis = manager.analyze()
        print(json.dumps(analysis, indent=2))
    
    elif command == "report":
        print(manager.get_report())
    
    elif command == "apply":
        # Apply configuration to mission_config.py
        try:
            gui_dir = Path.home() / "uav_ws" / "src" / "uav_planner" / "uav_planner"
            mission_config_path = gui_dir / "mission_config.py"
            
            config = manager.config
            content = f'''# Auto-generated from GUI configuration
MISSION = {{
    "start": {tuple(config["start"])},
    "goal": {tuple(config["goal"])},
    "weather": "{config["weather"]}",
    "battery": {config["battery"]},
    "emergency_goal": {tuple(config["emergency_goal"])},
    "dynamic_obstacle": {tuple(config["dynamic_obstacle"])},
    "grid_size": {config.get("grid_size", 6)},
    "obstacles": {config.get("obstacles", [])}
}}
'''
            with open(mission_config_path, 'w') as f:
                f.write(content)
            print(f"✓ Configuration applied to {mission_config_path}")
        except Exception as e:
            print(f"✗ Error applying configuration: {e}")
    
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
