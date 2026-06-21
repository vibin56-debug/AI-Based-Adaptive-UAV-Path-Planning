import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker


class UAVMarkerPublisher(Node):

    def __init__(self):

        super().__init__('uav_marker_publisher')

        self.publisher = self.create_publisher(
            Marker,
            '/uav_marker',
            10
        )

        self.subscription = self.create_subscription(
            Point,
            '/uav_position',
            self.position_callback,
            10
        )

        self.x = 0.0
        self.y = 0.0

        self.get_logger().info(
            "UAV Marker Publisher Started"
        )

    def position_callback(self, msg):

        self.x = msg.x
        self.y = msg.y

        self.publish_marker()

    def publish_marker(self):

        marker = Marker()

        marker.header.frame_id = "map"

        marker.ns = "uav"

        marker.id = 0

        marker.type = Marker.SPHERE

        marker.action = Marker.ADD

        marker.pose.position.x = self.x
        marker.pose.position.y = self.y
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


def main(args=None):

    rclpy.init(args=args)

    node = UAVMarkerPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
