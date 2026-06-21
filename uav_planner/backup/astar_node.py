import rclpy
from rclpy.node import Node

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32

import numpy as np

from .astar import astar
from .mission_config import MISSION
from .weather_manager import WeatherManager
from .emergency_manager import EmergencyManager


class AStarNode(Node):

    def __init__(self):

        super().__init__('astar_node')

        self.path_publisher = self.create_publisher(
            Path,
            '/uav_path',
            10
        )

        self.subscription = self.create_subscription(
            Float32,
            '/battery_level',
            self.battery_callback,
            10
        )

        self.grid = np.array([
            [0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0]
        ])

        self.start = MISSION["start"]
        self.goal = MISSION["goal"]
        self.weather = MISSION["weather"]
        self.battery = MISSION["battery"]
        self.emergency_goal = MISSION["emergency_goal"]

        self.weather_manager = WeatherManager()
        self.emergency_manager = EmergencyManager()

        self.path = astar(
            self.grid,
            self.start,
            self.goal
        )

        self.current_index = 0
        self.current_position = self.start

        self.mission_completed = False
        self.emergency_triggered = False
        self.mission_checked = False

        self.timer = self.create_timer(
            1.0,
            self.update_uav
        )

        self.get_logger().info(
            "AI-Based Adaptive UAV Planner Started"
        )

    def battery_callback(self, msg):

        self.battery = msg.data

    def check_mission(self):

        if self.mission_checked:
            return True

        path_length = len(self.path)

        weather_penalty = (
            self.weather_manager.get_weather_penalty(
                self.weather
            )
        )

        required_battery = (
            path_length * 2
            + weather_penalty
            + 20
        )

        self.get_logger().info(
            f"Mission Start: {self.start}"
        )

        self.get_logger().info(
            f"Mission Goal: {self.goal}"
        )

        self.get_logger().info(
            f"Weather: {self.weather}"
        )
        self.get_logger().info(
            self.weather_manager.get_weather_message(
                self.weather
            )
        )

        if not self.weather_manager.is_weather_safe(
            self.weather
        ):

            self.get_logger().error(
                 "UNSAFE WEATHER CONDITIONS"
            )

            self.get_logger().error(
                 "MISSION REJECTED"
            )

            self.timer.cancel()

            return False
        self.get_logger().info(
            f"Required Battery: {required_battery:.1f}%"
        )

        self.get_logger().info(
            f"Available Battery: {self.battery:.1f}%"
        )

        if self.battery >= required_battery:

            self.get_logger().info(
                "MISSION APPROVED"
            )

            self.mission_checked = True
            return True

        self.get_logger().error(
            "MISSION REJECTED"
        )

        self.timer.cancel()

        return False

    def trigger_emergency(self):

        self.get_logger().warn(
            "EMERGENCY DETECTED"
        )

        self.emergency_manager.trigger_emergency(
            self.emergency_goal
        )

        self.goal = self.emergency_goal

        self.get_logger().warn(
            f"Emergency Goal: {self.goal}"
        )

        self.path = astar(
            self.grid,
            self.current_position,
            self.goal
        )

        self.current_index = 0

        self.emergency_triggered = True

        self.get_logger().warn(
            "PATH REPLANNED"
        )

    def publish_path(self):

        path_msg = Path()

        path_msg.header.frame_id = "map"

        for point in self.path:

            pose = PoseStamped()

            pose.header.frame_id = "map"

            pose.pose.position.x = float(point[1])
            pose.pose.position.y = float(point[0])
            pose.pose.position.z = 0.0

            pose.pose.orientation.w = 1.0

            path_msg.poses.append(pose)

        self.path_publisher.publish(path_msg)

    def update_uav(self):

        if self.mission_completed:
            return

        if not self.mission_checked:

            if not self.check_mission():
                return

        if self.current_index >= len(self.path):

            if self.emergency_triggered:

                self.get_logger().info(
                    "EMERGENCY MISSION COMPLETED"
                )

            else:

                self.get_logger().info(
                    "MISSION COMPLETED"
                )

            self.get_logger().info(
                f"Destination Reached: {self.goal}"
            )

            self.mission_completed = True

            self.timer.cancel()

            return

        self.current_position = self.path[
            self.current_index
        ]

        self.get_logger().info(
            f"Current Position: {self.current_position}"
        )

        if (
            not self.emergency_triggered
            and self.current_index >= len(self.path) // 2
        ):

            self.trigger_emergency()

            self.publish_path()

            return

        self.publish_path()

        self.current_index += 1


def main(args=None):

    rclpy.init(args=args)

    node = AStarNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
