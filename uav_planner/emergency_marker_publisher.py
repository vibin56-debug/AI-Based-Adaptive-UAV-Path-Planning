import rclpy
from rclpy.node import Node

from visualization_msgs.msg import Marker

from .mission_config import MISSION


class EmergencyMarkerPublisher(Node):

    def __init__(self):

        super().__init__('emergency_marker_publisher')

        self.publisher = self.create_publisher(
            Marker,
            '/emergency_marker',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_marker
        )

        self.goal = MISSION["emergency_goal"]

        self.get_logger().info(
            "Emergency Marker Publisher Started"
        )

    def publish_marker(self):

        marker = Marker()

        marker.header.frame_id = "map"

        marker.ns = "emergency_goal"

        marker.id = 2

        marker.type = Marker.CYLINDER

        marker.action = Marker.ADD

        marker.pose.position.x = float(
            self.goal[1]
        )

        marker.pose.position.y = float(
            self.goal[0]
        )

        marker.pose.position.z = 0.0

        marker.pose.orientation.w = 1.0

        marker.scale.x = 0.6
        marker.scale.y = 0.6
        marker.scale.z = 0.2

        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 1.0
        marker.color.b = 0.0

        self.publisher.publish(marker)


def main(args=None):

    rclpy.init(args=args)

    node = EmergencyMarkerPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
