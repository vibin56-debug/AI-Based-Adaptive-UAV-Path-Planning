class MissionManager:

    def __init__(self):

        self.start = (0, 0)

        self.goal = (5, 5)

        self.weather = "WIND"

        self.emergency = False

    def set_mission(
        self,
        start,
        goal,
        weather="CLEAR",
        emergency=False
    ):

        self.start = start

        self.goal = goal

        self.weather = weather

        self.emergency = emergency

    def get_mission(self):

        return {
            "start": self.start,
            "goal": self.goal,
            "weather": self.weather,
            "emergency": self.emergency
        }
