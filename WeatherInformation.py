import string


class WeatherInformation:
    def __init__(self, description: string, wind_type: string, wind_direction: string, wind_speed: string,
                 image_code: string, average_temperature: float, min_temperature: float, max_temperature: float,
                 humidity: float, pressure: float, day_period=""):
        self.description = description
        self.wind_type = wind_type
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.image_code = image_code
        self.average_temperature = average_temperature
        self.min_temperature = min_temperature
        self.max_temperature = max_temperature
        self.humidity = humidity
        self.pressure = pressure
        self.day_period = day_period
