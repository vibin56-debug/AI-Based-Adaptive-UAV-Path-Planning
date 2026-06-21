from weather_manager import WeatherManager

weather = WeatherManager()

print(
    weather.get_weather_penalty(
        "CLEAR"
    )
)

print(
    weather.get_weather_penalty(
        "WIND"
    )
)

print(
    weather.get_weather_penalty(
        "RAIN"
    )
)

print(
    weather.get_weather_penalty(
        "STORM"
    )
)
