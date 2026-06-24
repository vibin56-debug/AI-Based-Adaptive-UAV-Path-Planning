class EmergencyStationManager:

    def __init__(self):

        self.stations = [
            (2, 2),
            (5, 0),
            (0, 5)
        ]

    def get_nearest_station(
        self,
        current_position
    ):

        best_station = None

        best_distance = float("inf")

        for station in self.stations:

            distance = (
                abs(current_position[0] - station[0])
                +
                abs(current_position[1] - station[1])
            )

            if distance < best_distance:

                best_distance = distance

                best_station = station

        return best_station
