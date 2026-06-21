class EmergencyManager:

    def __init__(self):

        self.emergency = False

        self.emergency_goal = None

    def trigger_emergency(self, goal):

        self.emergency = True

        self.emergency_goal = goal

    def clear_emergency(self):

        self.emergency = False

        self.emergency_goal = None

    def is_emergency(self):

        return self.emergency

    def get_emergency_goal(self):

        return self.emergency_goal
