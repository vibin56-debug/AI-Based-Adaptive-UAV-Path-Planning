#!/usr/bin/env python3

import sys
import json
from pathlib import Path

def update_mission_config(config_file):
    """Update mission_config.py with values from GUI"""
    if not Path(config_file).exists():
        print(f"Config file not found: {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        # Generate the new mission config
        mission_config_content = f'''# Auto-generated from GUI configuration
MISSION = {{
    "start": {tuple(config_data["start"])},
    "goal": {tuple(config_data["goal"])},
    "weather": "{config_data["weather"]}",
    "battery": {config_data["battery"]},
    "emergency_goal": {tuple(config_data["emergency_goal"])},
    "dynamic_obstacle": {tuple(config_data["dynamic_obstacle"])},
    "grid_size": {config_data["grid_size"]},
    "obstacles": {config_data["obstacles"]}
}}
'''
        
        # Write to mission_config.py
        mission_config_path = Path(__file__).parent / "mission_config.py"
        with open(mission_config_path, 'w') as f:
            f.write(mission_config_content)
        
        print(f"✓ Mission configuration updated successfully")
        return True
    except Exception as e:
        print(f"✗ Error updating mission config: {str(e)}")
        return False


if __name__ == '__main__':
    config_file = Path.home() / ".uav_mission_config.json"
    
    if len(sys.argv) > 1:
        config_file = Path(sys.argv[1])
    
    update_mission_config(str(config_file))
