from mission_manager import MissionManager
mission = MissionManager()

mission.set_mission(
    start=(1,2),
    goal=(8,9),
    weather="WIND",
    emergency=False
)

print(mission.get_mission())
