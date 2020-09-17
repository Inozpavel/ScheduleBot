import string
import json
from datetime import datetime, timedelta
import requests


class WeatherForecaster:
    def __init__(self, key: string):
        self.__api_key = key

        with open("Configs/Weather/WindTypes.json", "r", encoding="utf-8") as file:
            self.WIND_TYPES = json.load(file)
        with open("Configs/Weather/WindDirections.json", "r", encoding="utf-8") as file:
            self.WIND_DIRECTIONS = json.load(file)
        with open("Configs/Weather/ImagesCodes.json.json", "r", encoding="utf-8") as file:
            self.IMAGES_CODES = json.load(file)

    def get_weather_now(self):
        responce = requests.get(
            "http://api.openweathermap.org/data/2.5/weather?q=moscow&appid=" + self.__api_key + "&units=metric" +
            "&lang=ru")

    def get_weather_for_today(self):
        return self.get_weather_for_day(datetime.today())

    def get_weather_for_tomorrow(self):
        return self.get_weather_for_day(datetime.today() + timedelta(1))

    def get_weather_for_five_days(self):
        pass

    def get_weather_for_day(self, date: datetime) -> [str, [str]]:
        responce = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast?q=moscow&appid=" + self.__api_key + "&units=metric" +
            "&lang=ru")
