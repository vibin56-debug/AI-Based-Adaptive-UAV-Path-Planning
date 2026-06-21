from obstacle_manager import ObstacleManager

manager = ObstacleManager()

manager.add_obstacle((2, 3))
manager.add_obstacle((4, 4))

print("Obstacles:", manager.get_obstacles())

print(
    "Is (2,3) obstacle?",
    manager.is_obstacle((2, 3))
)

manager.remove_obstacle((2, 3))

print(
    "After Removal:",
    manager.get_obstacles()
)
