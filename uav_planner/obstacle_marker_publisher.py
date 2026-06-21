import rclpy
from rclpy.node import Node

from visualization_msgs.msg import Marker


class ObstacleMarkerPublisher(Node):

    def __init__(self):

        super().__init__('obstacle_marker_publisher')

        self.publisher = self.create_publisher(
            Marker,
            '/obstacle_marker',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_obstacle
        )

        self.obstacle = (0, 4)

        self.get_logger().info(
            "Obstacle Marker Publisher Started"
        )

    def publish_obstacle(self):

        marker = Marker()

        marker.header.frame_id = "map"

        marker.ns = "obstacle"

        marker.id = 1

        marker.type = Marker.CUBE

        marker.action = Marker.ADD

        marker.pose.position.x = float(
            self.obstacle[1]
        )

        marker.pose.position.y = float(
            self.obstacle[0]
        )

        marker.pose.position.z = 0.0

        marker.pose.orientation.w = 1.0

        marker.scale.x = 0.5
        marker.scale.y = 0.5
        marker.scale.z = 0.5

        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0

        self.publisher.publish(marker)


def main(args=None):

    rclpy.init(args=args)

    node = ObstacleMarkerPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
