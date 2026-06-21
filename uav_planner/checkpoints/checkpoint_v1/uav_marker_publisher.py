import rclpy
from rclpy.node import Node

from visualization_msgs.msg import Marker


class UAVMarkerPublisher(Node):

    def __init__(self):

        super().__init__('uav_marker_publisher')

        self.publisher = self.create_publisher(
            Marker,
            '/uav_marker',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_marker
        )

        self.x = 0.0

        self.get_logger().info(
            "UAV Marker Publisher Started"
        )

    def publish_marker(self):

        marker = Marker()

        marker.header.frame_id = "map"

        marker.ns = "uav"

        marker.id = 0

        marker.type = Marker.SPHERE

        marker.action = Marker.ADD

        marker.pose.position.x = self.x
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0

        marker.pose.orientation.w = 1.0

        marker.scale.x = 0.3
        marker.scale.y = 0.3
        marker.scale.z = 0.3

        marker.color.a = 1.0
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0

        self.publisher.publish(marker)

        self.x += 0.2

        if self.x > 5:
            self.x = 0.0


def main(args=None):

    rclpy.init(args=args)

    node = UAVMarkerPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
