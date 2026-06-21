import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Point


class PositionPublisher(Node):

    def __init__(self):

        super().__init__('position_publisher')

        self.publisher = self.create_publisher(
            Point,
            '/uav_position',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_position
        )

        self.x = 0.0
        self.y = 0.0

        self.get_logger().info(
            "Position Publisher Started"
        )

    def publish_position(self):

        msg = Point()

        msg.x = self.x
        msg.y = self.y
        msg.z = 0.0

        self.publisher.publish(msg)

        self.get_logger().info(
            f"Position: ({self.x}, {self.y})"
        )

        self.x += 0.2

        if self.x > 5:
            self.x = 0.0


def main(args=None):

    rclpy.init(args=args)

    node = PositionPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
