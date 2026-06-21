import rclpy
from rclpy.node import Node

from visualization_msgs.msg import Marker

from .mission_config import MISSION


class MissionStatusPublisher(Node):

    def __init__(self):

        super().__init__('mission_status_publisher')

        self.publisher = self.create_publisher(
            Marker,
            '/mission_status',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_status
        )

        self.get_logger().info(
            "Mission Status Publisher Started"
        )

    def publish_status(self):

        marker = Marker()

        marker.header.frame_id = "map"

        marker.ns = "mission_status"

        marker.id = 100

        marker.type = Marker.TEXT_VIEW_FACING

        marker.action = Marker.ADD

        marker.pose.position.x = 2.5
        marker.pose.position.y = -1.0
        marker.pose.position.z = 1.0

        marker.pose.orientation.w = 1.0

        marker.scale.z = 0.4

        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 1.0
        marker.color.b = 1.0

        marker.text = (
            f"MISSION APPROVED\n"
            f"WEATHER: {MISSION['weather']}\n"
            f"BATTERY: {MISSION['battery']}%"
        )

        self.publisher.publish(marker)


def main(args=None):

    rclpy.init(args=args)

    node = MissionStatusPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
