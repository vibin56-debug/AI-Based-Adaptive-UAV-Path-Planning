from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='uav_planner',
            executable='battery_manager',
            output='screen'
        ),

        Node(
            package='uav_planner',
            executable='astar_node',
            output='screen'
        ),

        Node(
            package='uav_planner',
            executable='uav_marker_publisher',
            output='screen'
        ),

        Node(
            package='uav_planner',
            executable='obstacle_marker_publisher',
            output='screen'
        ),

        Node(
            package='uav_planner',
            executable='emergency_marker_publisher',
            output='screen'
        ),

        Node(
            package='uav_planner',
            executable='mission_status_publisher',
            output='screen'
        )

    ])
