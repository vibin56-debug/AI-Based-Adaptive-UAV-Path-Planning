#!/bin/bash

# UAV Planner GUI Launcher
# This script launches the GUI for configuring and launching UAV missions

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if PyQt5 is installed
echo "Checking dependencies..."
python3 -c "import PyQt5" 2>/dev/null || {
    echo "PyQt5 not found. Installing..."
    pip3 install PyQt5
}

# Launch the GUI
echo "Launching UAV Planner GUI..."
python3 "$SCRIPT_DIR/uav_gui.py"
