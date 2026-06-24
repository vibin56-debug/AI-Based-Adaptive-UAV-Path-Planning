#!/usr/bin/env python3

import sys
import json
from pathlib import Path
import PyQt5
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton,
    QGroupBox, QGridLayout, QMessageBox, QTabWidget, QSlider,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QColor, QPixmap, QPainter, QFont, QPen, QBrush
from PyQt5.QtWidgets import QFrame
import numpy as np


class MissionConfig:
    """Handles mission configuration"""
    
    def __init__(self):
        self.start = (0, 0)
        self.goal = (4, 5)
        self.weather = "RAIN"
        self.battery = 80.0
        self.emergency_goal = (2, 2)
        self.dynamic_obstacle = (0, 4)
        self.grid_size = 6
        self.obstacles = []
        
    def to_dict(self):
        return {
            "start": self.start,
            "goal": self.goal,
            "weather": self.weather,
            "battery": self.battery,
            "emergency_goal": self.emergency_goal,
            "dynamic_obstacle": self.dynamic_obstacle,
            "grid_size": self.grid_size,
            "obstacles": self.obstacles
        }
    
    def from_dict(self, data):
        self.start = tuple(data.get("start", (0, 0)))
        self.goal = tuple(data.get("goal", (4, 5)))
        self.weather = data.get("weather", "RAIN")
        self.battery = float(data.get("battery", 80.0))
        self.emergency_goal = tuple(data.get("emergency_goal", (2, 2)))
        self.dynamic_obstacle = tuple(data.get("dynamic_obstacle", (0, 4)))
        self.grid_size = int(data.get("grid_size", 6))
        self.obstacles = data.get("obstacles", [])


class GridVisualizer(QFrame):
    """Visualizes the grid with start, goal, obstacles, etc."""
    
    def __init__(self):
        super().__init__()
        self.config = MissionConfig()
        self.setMinimumSize(400, 400)
        self.setStyleSheet("border: 1px solid black;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw white background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # Calculate cell size
        width = self.width()
        height = self.height()
        cell_width = width / self.config.grid_size
        cell_height = height / self.config.grid_size
        
        # Draw grid
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        for i in range(self.config.grid_size + 1):
            x = i * cell_width
            y = i * cell_height
            painter.drawLine(int(x), 0, int(x), height)
            painter.drawLine(0, int(y), width, int(y))
        
        # Draw static obstacles
        painter.fillRect(0, 0, 0, 0, QBrush(QColor(100, 100, 100)))
        for obs in self.config.obstacles:
            x, y = obs[0], obs[1]
            rect_x = int(x * cell_width)
            rect_y = int(y * cell_height)
            painter.fillRect(rect_x, rect_y, int(cell_width), int(cell_height), QBrush(QColor(100, 100, 100)))
        
        # Draw dynamic obstacle
        if self.config.dynamic_obstacle:
            x, y = self.config.dynamic_obstacle
            rect_x = int(x * cell_width)
            rect_y = int(y * cell_height)
            painter.fillRect(rect_x, rect_y, int(cell_width), int(cell_height), QBrush(QColor(255, 165, 0)))
        
        # Draw emergency goal
        if self.config.emergency_goal:
            x, y = self.config.emergency_goal
            rect_x = int(x * cell_width + cell_width / 4)
            rect_y = int(y * cell_height + cell_height / 4)
            painter.fillRect(rect_x, rect_y, int(cell_width / 2), int(cell_height / 2), QBrush(QColor(255, 0, 0)))
        
        # Draw goal
        if self.config.goal:
            x, y = self.config.goal
            rect_x = int(x * cell_width + cell_width / 4)
            rect_y = int(y * cell_height + cell_height / 4)
            painter.fillRect(rect_x, rect_y, int(cell_width / 2), int(cell_height / 2), QBrush(QColor(0, 255, 0)))
        
        # Draw start
        if self.config.start:
            x, y = self.config.start
            rect_x = int(x * cell_width + cell_width / 4)
            rect_y = int(y * cell_height + cell_height / 4)
            painter.fillRect(rect_x, rect_y, int(cell_width / 2), int(cell_height / 2), QBrush(QColor(0, 0, 255)))
        
        # Draw legend
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setFont(QFont("Arial", 8))
        painter.fillRect(5, 5, 15, 15, QBrush(QColor(0, 0, 255)))
        painter.drawText(25, 15, "Start")
        painter.fillRect(5, 25, 15, 15, QBrush(QColor(0, 255, 0)))
        painter.drawText(25, 35, "Goal")
        painter.fillRect(5, 45, 15, 15, QBrush(QColor(255, 0, 0)))
        painter.drawText(25, 55, "Emergency")
        painter.fillRect(5, 65, 15, 15, QBrush(QColor(100, 100, 100)))
        painter.drawText(25, 75, "Obstacle")
    
    def update_config(self, config):
        self.config = config
        self.update()


class UAVGUI(QMainWindow):
    """Main GUI Application for UAV Planner Configuration"""
    
    def __init__(self):
        super().__init__()
        self.config = MissionConfig()
        self.config_file = Path.home() / ".uav_mission_config.json"
        
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("UAV Planner Configuration GUI")
        self.setGeometry(100, 100, 1200, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        
        # Left side - Controls
        left_layout = QVBoxLayout()
        
        # Tabs for different sections
        tabs = QTabWidget()
        
        # Mission Tab
        mission_widget = self.create_mission_tab()
        tabs.addTab(mission_widget, "Mission")
        
        # Weather Tab
        weather_widget = self.create_weather_tab()
        tabs.addTab(weather_widget, "Weather")
        
        # Obstacles Tab
        obstacles_widget = self.create_obstacles_tab()
        tabs.addTab(obstacles_widget, "Obstacles")
        
        # Battery Tab
        battery_widget = self.create_battery_tab()
        tabs.addTab(battery_widget, "Battery")
        
        left_layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Config")
        self.save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton("Load Config")
        self.load_btn.clicked.connect(self.load_config_dialog)
        button_layout.addWidget(self.load_btn)
        
        self.launch_btn = QPushButton("Launch Mission")
        self.launch_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.launch_btn.clicked.connect(self.launch_mission)
        button_layout.addWidget(self.launch_btn)
        
        left_layout.addLayout(button_layout)
        
        # Right side - Visualization
        right_layout = QVBoxLayout()
        right_label = QLabel("Grid Visualization")
        right_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(right_label)
        
        self.grid_visualizer = GridVisualizer()
        self.grid_visualizer.update_config(self.config)
        right_layout.addWidget(self.grid_visualizer)
        
        # Add layouts to main
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)
        
        main_widget.setLayout(main_layout)
    
    def create_mission_tab(self):
        """Create mission configuration tab"""
        widget = QWidget()
        layout = QGridLayout()
        
        # Start Point
        layout.addWidget(QLabel("Start Point:"), 0, 0)
        self.start_x = QSpinBox()
        self.start_x.setMaximum(99)
        self.start_x.setValue(int(self.config.start[0]))
        self.start_x.valueChanged.connect(self.update_visualization)
        layout.addWidget(QLabel("X:"), 0, 1)
        layout.addWidget(self.start_x, 0, 2)
        
        self.start_y = QSpinBox()
        self.start_y.setMaximum(99)
        self.start_y.setValue(int(self.config.start[1]))
        self.start_y.valueChanged.connect(self.update_visualization)
        layout.addWidget(QLabel("Y:"), 0, 3)
        layout.addWidget(self.start_y, 0, 4)
        
        # Goal Point
        layout.addWidget(QLabel("Goal Point:"), 1, 0)
        self.goal_x = QSpinBox()
        self.goal_x.setMaximum(99)
        self.goal_x.setValue(int(self.config.goal[0]))
        self.goal_x.valueChanged.connect(self.update_visualization)
        layout.addWidget(QLabel("X:"), 1, 1)
        layout.addWidget(self.goal_x, 1, 2)
        
        self.goal_y = QSpinBox()
        self.goal_y.setMaximum(99)
        self.goal_y.setValue(int(self.config.goal[1]))
        self.goal_y.valueChanged.connect(self.update_visualization)
        layout.addWidget(QLabel("Y:"), 1, 3)
        layout.addWidget(self.goal_y, 1, 4)
        
        # Emergency Goal
        layout.addWidget(QLabel("Emergency Goal:"), 2, 0)
        self.emergency_x = QSpinBox()
        self.emergency_x.setMaximum(99)
        self.emergency_x.setValue(int(self.config.emergency_goal[0]))
        self.emergency_x.valueChanged.connect(self.update_visualization)
        layout.addWidget(QLabel("X:"), 2, 1)
        layout.addWidget(self.emergency_x, 2, 2)
        
        self.emergency_y = QSpinBox()
        self.emergency_y.setMaximum(99)
        self.emergency_y.setValue(int(self.config.emergency_goal[1]))
        self.emergency_y.valueChanged.connect(self.update_visualization)
        layout.addWidget(QLabel("Y:"), 2, 3)
        layout.addWidget(self.emergency_y, 2, 4)
        
        # Grid Size
        layout.addWidget(QLabel("Grid Size:"), 3, 0)
        self.grid_size = QSpinBox()
        self.grid_size.setMinimum(4)
        self.grid_size.setMaximum(20)
        self.grid_size.setValue(self.config.grid_size)
        self.grid_size.valueChanged.connect(self.update_visualization)
        layout.addWidget(self.grid_size, 3, 1)
        
        layout.addItem(PyQt5.QtWidgets.QSpacerItem(0, 200, PyQt5.QtWidgets.QSizePolicy.Minimum, PyQt5.QtWidgets.QSizePolicy.Expanding))
        
        widget.setLayout(layout)
        return widget
    
    def create_weather_tab(self):
        """Create weather configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Weather Selection
        weather_group = QGroupBox("Weather Conditions")
        weather_layout = QGridLayout()
        
        weather_layout.addWidget(QLabel("Weather Type:"), 0, 0)
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(["CLEAR", "WIND", "RAIN", "STORM"])
        self.weather_combo.setCurrentText(self.config.weather)
        self.weather_combo.currentTextChanged.connect(self.update_visualization)
        weather_layout.addWidget(self.weather_combo, 0, 1)
        
        # Weather Info
        self.weather_info = QLabel(self.get_weather_info(self.config.weather))
        self.weather_info.setWordWrap(True)
        weather_layout.addWidget(self.weather_info, 1, 0, 1, 2)
        
        weather_group.setLayout(weather_layout)
        layout.addWidget(weather_group)
        
        # Weather Effects
        effects_group = QGroupBox("Weather Effects")
        effects_layout = QGridLayout()
        
        effects_info = {
            "CLEAR": ("Base cost: 0", "Safe flying conditions"),
            "WIND": ("Base cost: 10", "Increased battery consumption"),
            "RAIN": ("Base cost: 20", "High battery consumption, reduced visibility"),
            "STORM": ("Base cost: 35", "Mission unsafe - recommended to abort")
        }
        
        row = 0
        for weather, (cost, effect) in effects_info.items():
            effects_layout.addWidget(QLabel(f"{weather}:"), row, 0)
            effects_layout.addWidget(QLabel(cost), row, 1)
            effects_layout.addWidget(QLabel(effect), row, 2)
            row += 1
        
        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)
        
        layout.addItem(PyQt5.QtWidgets.QSpacerItem(0, 200, PyQt5.QtWidgets.QSizePolicy.Minimum, PyQt5.QtWidgets.QSizePolicy.Expanding))
        
        widget.setLayout(layout)
        return widget
    
    def create_obstacles_tab(self):
        """Create obstacles configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Dynamic Obstacle
        dynamic_group = QGroupBox("Dynamic Obstacle")
        dynamic_layout = QGridLayout()
        
        dynamic_layout.addWidget(QLabel("Position:"), 0, 0)
        self.dynamic_x = QSpinBox()
        self.dynamic_x.setMaximum(99)
        self.dynamic_x.setValue(int(self.config.dynamic_obstacle[0]))
        self.dynamic_x.valueChanged.connect(self.update_visualization)
        dynamic_layout.addWidget(QLabel("X:"), 0, 1)
        dynamic_layout.addWidget(self.dynamic_x, 0, 2)
        
        self.dynamic_y = QSpinBox()
        self.dynamic_y.setMaximum(99)
        self.dynamic_y.setValue(int(self.config.dynamic_obstacle[1]))
        self.dynamic_y.valueChanged.connect(self.update_visualization)
        dynamic_layout.addWidget(QLabel("Y:"), 0, 3)
        dynamic_layout.addWidget(self.dynamic_y, 0, 4)
        
        dynamic_group.setLayout(dynamic_layout)
        layout.addWidget(dynamic_group)
        
        # Static Obstacles
        static_group = QGroupBox("Static Obstacles")
        static_layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        add_obs_btn = QPushButton("Add Obstacle")
        add_obs_btn.clicked.connect(self.add_obstacle)
        button_layout.addWidget(add_obs_btn)
        
        remove_obs_btn = QPushButton("Remove Selected")
        remove_obs_btn.clicked.connect(self.remove_obstacle)
        button_layout.addWidget(remove_obs_btn)
        
        static_layout.addLayout(button_layout)
        
        self.obstacles_table = QTableWidget()
        self.obstacles_table.setColumnCount(3)
        self.obstacles_table.setHorizontalHeaderLabels(["X", "Y", "Delete"])
        self.obstacles_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.obstacles_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.obstacles_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.populate_obstacles_table()
        static_layout.addWidget(self.obstacles_table)
        
        static_group.setLayout(static_layout)
        layout.addWidget(static_group)
        
        layout.addItem(PyQt5.QtWidgets.QSpacerItem(0, 100, PyQt5.QtWidgets.QSizePolicy.Minimum, PyQt5.QtWidgets.QSizePolicy.Expanding))
        
        widget.setLayout(layout)
        return widget
    
    def create_battery_tab(self):
        """Create battery configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Battery Level
        battery_group = QGroupBox("Battery Configuration")
        battery_layout = QGridLayout()
        
        battery_layout.addWidget(QLabel("Battery Level (%):"), 0, 0)
        self.battery_slider = QSlider(Qt.Horizontal)
        self.battery_slider.setMinimum(0)
        self.battery_slider.setMaximum(100)
        self.battery_slider.setValue(int(self.config.battery))
        self.battery_slider.setTickPosition(QSlider.TicksBelow)
        self.battery_slider.setTickInterval(10)
        self.battery_slider.valueChanged.connect(self.update_battery_label)
        battery_layout.addWidget(self.battery_slider, 0, 1)
        
        self.battery_label = QLabel(f"{int(self.config.battery)}%")
        battery_layout.addWidget(self.battery_label, 0, 2)
        
        battery_layout.addWidget(QLabel(""), 1, 0)  # Spacer
        
        self.battery_spinbox = QDoubleSpinBox()
        self.battery_spinbox.setMinimum(0)
        self.battery_spinbox.setMaximum(100)
        self.battery_spinbox.setValue(self.config.battery)
        self.battery_spinbox.setSingleStep(1)
        battery_layout.addWidget(QLabel("Precise Value:"), 2, 0)
        battery_layout.addWidget(self.battery_spinbox, 2, 1)
        
        self.battery_slider.valueChanged.connect(lambda: self.battery_spinbox.setValue(self.battery_slider.value()))
        self.battery_spinbox.valueChanged.connect(lambda: self.battery_slider.setValue(int(self.battery_spinbox.value())))
        
        battery_group.setLayout(battery_layout)
        layout.addWidget(battery_group)
        
        # Battery Info
        info_group = QGroupBox("Battery Information")
        info_layout = QVBoxLayout()
        
        info_text = """
Battery Management Guidelines:
• 0-20%: Critical - Mission recommended to be aborted
• 20-40%: Low - Limited range, consider emergency goal
• 40-60%: Medium - Plan route carefully
• 60-80%: Good - Optimal for missions
• 80-100%: Excellent - Full mission capability

Weather Impact on Battery:
• CLEAR: No additional consumption
• WIND: +10% additional consumption
• RAIN: +20% additional consumption
• STORM: Mission not recommended
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addItem(PyQt5.QtWidgets.QSpacerItem(0, 100, PyQt5.QtWidgets.QSizePolicy.Minimum, PyQt5.QtWidgets.QSizePolicy.Expanding))
        
        widget.setLayout(layout)
        return widget
    
    def update_visualization(self):
        """Update the visualization and config"""
        self.config.start = (self.start_x.value(), self.start_y.value())
        self.config.goal = (self.goal_x.value(), self.goal_y.value())
        self.config.emergency_goal = (self.emergency_x.value(), self.emergency_y.value())
        self.config.weather = self.weather_combo.currentText()
        self.config.dynamic_obstacle = (self.dynamic_x.value(), self.dynamic_y.value())
        self.config.grid_size = self.grid_size.value()
        self.config.battery = self.battery_spinbox.value()
        
        self.grid_visualizer.update_config(self.config)
        self.weather_info.setText(self.get_weather_info(self.config.weather))
    
    def update_battery_label(self):
        """Update battery percentage label"""
        self.battery_label.setText(f"{self.battery_slider.value()}%")
    
    def get_weather_info(self, weather):
        """Get weather information"""
        info = {
            "CLEAR": "✓ Clear Weather - Optimal flying conditions, no restrictions",
            "WIND": "⚠ Wind Conditions - Increased battery consumption by 10%",
            "RAIN": "⚠ Rain Conditions - High battery consumption by 20%, reduced visibility",
            "STORM": "✗ Storm Warning - Mission unsafe, recommended to cancel"
        }
        return info.get(weather, "Unknown weather condition")
    
    def add_obstacle(self):
        """Add a new obstacle"""
        self.config.obstacles.append([0, 0])
        self.populate_obstacles_table()
        self.update_visualization()
    
    def remove_obstacle(self):
        """Remove selected obstacle"""
        current_row = self.obstacles_table.currentRow()
        if current_row >= 0:
            self.config.obstacles.pop(current_row)
            self.populate_obstacles_table()
            self.update_visualization()
    
    def populate_obstacles_table(self):
        """Populate the obstacles table"""
        self.obstacles_table.setRowCount(len(self.config.obstacles))
        
        for row, obstacle in enumerate(self.config.obstacles):
            x_spinbox = QSpinBox()
            x_spinbox.setMaximum(99)
            x_spinbox.setValue(obstacle[0])
            x_spinbox.valueChanged.connect(lambda value, r=row: self.update_obstacle(r, 0, value))
            
            y_spinbox = QSpinBox()
            y_spinbox.setMaximum(99)
            y_spinbox.setValue(obstacle[1])
            y_spinbox.valueChanged.connect(lambda value, r=row: self.update_obstacle(r, 1, value))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_obstacle_row(r))
            
            self.obstacles_table.setCellWidget(row, 0, x_spinbox)
            self.obstacles_table.setCellWidget(row, 1, y_spinbox)
            self.obstacles_table.setCellWidget(row, 2, delete_btn)
    
    def update_obstacle(self, row, col, value):
        """Update obstacle coordinate"""
        if row < len(self.config.obstacles):
            self.config.obstacles[row][col] = value
            self.update_visualization()
    
    def delete_obstacle_row(self, row):
        """Delete obstacle by row"""
        if row < len(self.config.obstacles):
            self.config.obstacles.pop(row)
            self.populate_obstacles_table()
            self.update_visualization()
    
    def save_config(self):
        """Save configuration to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Mission Configuration",
            str(self.config_file),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                config_data = self.config.to_dict()
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                QMessageBox.information(self, "Success", f"Configuration saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        """Load default configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.config.from_dict(data)
                    self.refresh_ui()
            except Exception as e:
                print(f"Failed to load default config: {str(e)}")
    
    def load_config_dialog(self):
        """Load configuration from file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Mission Configuration",
            str(self.config_file.parent),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.config.from_dict(data)
                    self.refresh_ui()
                QMessageBox.information(self, "Success", "Configuration loaded successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load configuration: {str(e)}")
    
    def refresh_ui(self):
        """Refresh all UI elements with current config"""
        self.start_x.setValue(int(self.config.start[0]))
        self.start_y.setValue(int(self.config.start[1]))
        self.goal_x.setValue(int(self.config.goal[0]))
        self.goal_y.setValue(int(self.config.goal[1]))
        self.emergency_x.setValue(int(self.config.emergency_goal[0]))
        self.emergency_y.setValue(int(self.config.emergency_goal[1]))
        self.dynamic_x.setValue(int(self.config.dynamic_obstacle[0]))
        self.dynamic_y.setValue(int(self.config.dynamic_obstacle[1]))
        self.weather_combo.setCurrentText(self.config.weather)
        self.battery_slider.setValue(int(self.config.battery))
        self.battery_spinbox.setValue(self.config.battery)
        self.grid_size.setValue(self.config.grid_size)
        self.populate_obstacles_table()
        self.update_visualization()
    
    def launch_mission(self):
        """Launch the mission with current configuration"""
        self.update_visualization()
        
        config_msg = f"""
Mission Configuration Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Start Point: {self.config.start}
Goal Point: {self.config.goal}
Emergency Goal: {self.config.emergency_goal}
Weather: {self.config.weather}
Battery: {self.config.battery}%
Dynamic Obstacle: {self.config.dynamic_obstacle}
Grid Size: {self.config.grid_size}
Static Obstacles: {len(self.config.obstacles)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to launch mission?
        """
        
        reply = QMessageBox.question(
            self,
            "Launch Mission",
            config_msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Save current config as default
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(self.config.to_dict(), f, indent=2)
            except:
                pass
            
            QMessageBox.information(
                self,
                "Mission Launched",
                "Configuration saved. Launch command would be executed here.\n\n"
                "Configuration file saved to: " + str(self.config_file)
            )


def main():
    app = QApplication(sys.argv)
    window = UAVGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
