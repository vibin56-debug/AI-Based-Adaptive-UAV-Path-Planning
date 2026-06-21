import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class BatteryManager(Node):

    def __init__(self):

        super().__init__('battery_manager')

        self.publisher = self.create_publisher(
            Float32,
            '/battery_level',
            10
        )

        self.battery = 100.0

        self.timer = self.create_timer(
            1.0,
            self.publish_battery
        )

        self.get_logger().info(
            "Battery Manager Started"
        )

    def publish_battery(self):

        msg = Float32()
        msg.data = self.battery

        self.publisher.publish(msg)

        self.get_logger().info(
            f"Battery: {self.battery:.1f}%"
        )

        self.battery -= 1.0

        if self.battery < 0:
            self.battery = 0.0


def main(args=None):

    rclpy.init(args=args)

    node = BatteryManager()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
