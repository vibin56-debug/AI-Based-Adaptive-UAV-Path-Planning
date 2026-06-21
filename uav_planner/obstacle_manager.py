class ObstacleManager:

    def __init__(self):

        self.dynamic_obstacles = []

    def add_obstacle(self, position):

        if position not in self.dynamic_obstacles:

            self.dynamic_obstacles.append(position)

    def remove_obstacle(self, position):

        if position in self.dynamic_obstacles:

            self.dynamic_obstacles.remove(position)

    def get_obstacles(self):

        return self.dynamic_obstacles

    def is_obstacle(self, position):

        return position in self.dynamic_obstacles
