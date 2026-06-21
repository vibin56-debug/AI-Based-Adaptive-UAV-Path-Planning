from setuptools import setup, find_packages
from glob import glob
import os

package_name = 'uav_planner'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vibin',
    maintainer_email='vibin@example.com',
    description='AI Based Adaptive UAV Path Planning',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'astar_node = uav_planner.astar_node:main',
            'battery_manager = uav_planner.battery_manager:main',
            'uav_marker_publisher = uav_planner.uav_marker_publisher:main',
            'position_publisher = uav_planner.position_publisher:main',
            'obstacle_marker_publisher = uav_planner.obstacle_marker_publisher:main',
            'emergency_marker_publisher = uav_planner.emergency_marker_publisher:main',
            'mission_status_publisher = uav_planner.mission_status_publisher:main',
        ],
    },
)
