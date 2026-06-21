class WeatherManager:

    def __init__(self):

        self.weather_costs = {
            "CLEAR": 0,
            "WIND": 10,
            "RAIN": 20,
            "STORM": 35
        }

    def get_weather_penalty(self, weather):

        return self.weather_costs.get(
            weather.upper(),
            0
        )

    def is_weather_safe(self, weather):

        weather = weather.upper()

        if weather == "STORM":
            return False

        return True

    def get_weather_message(self, weather):

        weather = weather.upper()

        if weather == "CLEAR":
            return "Weather Clear - Mission Safe"

        if weather == "WIND":
            return "Wind Detected - Increased Battery Usage"

        if weather == "RAIN":
            return "Rain Detected - High Battery Consumption"

        if weather == "STORM":
            return "Storm Detected - Mission Unsafe"

        return "Unknown Weather"
