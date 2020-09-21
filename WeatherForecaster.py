import io
import string
import json
from datetime import datetime, timedelta
from typing import Dict, List

import requests
from PIL import Image
from vk_api import VkUpload
from vk_api.utils import get_random_id
from vk_api.vk_api import VkApiMethod

from Keyboards import Keyboards
from WeatherInformation import WeatherInformation


class WeatherForecaster:
    def __init__(self, weather_api_key: string, vk: VkApiMethod, upload: VkUpload):
        self.__weather_api_key = weather_api_key
        self.__upload = upload
        self.__vk = vk

        with open("Configs/Weather/WindTypes.json", "r", encoding="utf-8") as file:
            self.WIND_TYPES = json.load(file)
        with open("Configs/Weather/WindDirections.json", "r", encoding="utf-8") as file:
            self.WIND_DIRECTIONS = json.load(file)
        with open("Configs/Weather/ImagesCodes.json", "r", encoding="utf-8") as file:
            self.IMAGES_CODES = json.load(file)
        with open("Configs/Weather/DayPeriods.json", "r", encoding="utf-8") as file:
            self.DAY_PERIODS = json.load(file)

    def send_weather_for_now(self, user_id: int) -> None:
        """Отправляет информацию о погоде на сейчас указанному пользователю, прикрепляет картинку"""
        weather_info = self.__get_weather_for_now()
        image_url = self.__upload_pictures([weather_info.image_code])
        message = self.__convert_weather_information_to_text(weather_info, is_weather_now=True)
        self.__send_message(user_id, message, image_url)

    def __get_weather_for_now(self) -> WeatherInformation:
        """Возвращает информацию о погоде на сейчас"""
        response = requests.get(
            "http://api.openweathermap.org/data/2.5/weather?q=moscow&appid=" + self.__weather_api_key +
            "&units=metric&lang=ru")
        return self.__parse_weather(response.json())

    def __get_weather_for_today(self):
        return self.__get_weather_for_day(datetime.today())

    def __get_weather_for_tomorrow(self):
        return self.__get_weather_for_day(datetime.today() + timedelta(1))

    def __get_weather_for_five_days(self):
        pass

    def __get_weather_for_day(self, date: datetime):
        response = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast?q=moscow&appid=" + self.__weather_api_key +
            "&units=metric&lang=ru")

        json_weather = response.json()["list"]

    def __parse_weather(self, json_day: Dict) -> WeatherInformation:
        icon_code = json_day["weather"][0]["icon"]
        wind_type = ""
        wind_direction = ""

        for i in self.WIND_TYPES:
            if self.WIND_TYPES[i][0] <= json_day["wind"]["speed"] <= self.WIND_TYPES[i][1]:
                wind_type = i
                break

        if "deg" in json_day["wind"]:
            for i in self.WIND_DIRECTIONS:
                if self.WIND_DIRECTIONS[i][0] <= json_day["wind"]["deg"] <= \
                        self.WIND_DIRECTIONS[i][1]:
                    wind_direction = i
                    break

        description = json_day["weather"][0]["description"].capitalize()
        pressure = str(round(float(json_day["main"]["pressure"]) * 100 / 133.3))
        average_temperature = json_day["main"]["temp"]
        min_temperature = json_day["main"]["temp_min"]
        max_temperature = json_day["main"]["temp_max"]
        humidity = json_day["main"]["humidity"]
        wind_speed = json_day["wind"]["speed"]
        return WeatherInformation(description, wind_type, wind_direction, wind_speed, icon_code, average_temperature,
                                  min_temperature, max_temperature, humidity, pressure)

    def __upload_pictures(self, images: List[str]) -> str:
        """Склеивает картинки из списка pictures в одну, загружает на сервер, возвращает attachment"""
        if 4 < len(images) <= 10:
            image = Image.open("Images/Background/background_1280x512.png")
            if "n" in images[0]:
                images.insert(0, "null")
            for i in range(5):
                day_image = Image.open("Images/Weather/" + self.IMAGES_CODES[images[i * 2]])
                night_image = Image.open("Images/Weather/" + self.IMAGES_CODES[images[i * 2 + 1]])

                image.paste(day_image.resize((256, 256)), (256 * i, 0))
                image.paste(night_image.resize((256, 256)), (256 * i, 256))
        else:
            image = Image.open("Images/Background/background_" + str(len(images) * 256) + "x256.png")
            for i in range(len(images)):
                new_image = Image.open("Images/Weather/" + self.IMAGES_CODES[images[i]])
                image.paste(new_image.resize((256, 256)), (256 * i, 0))
        arr = io.BytesIO()
        image.save(arr, format="PNG")
        arr.seek(0)
        photo = self.__upload.photo_messages(arr)
        image = "photo{}_{}".format(photo[0]["owner_id"], photo[0]["id"])
        return image

    def __send_message(self, user_id: int, message: string, image_url: str) -> None:
        """Отправляет указанное собщение выбранному пользоваелю. Можно добавить клавиатуру"""
        self.__vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            keyboard=Keyboards.get_weather_keyboard(),
            attachment=image_url
        )

    @staticmethod
    def __convert_weather_information_to_text(info: WeatherInformation, is_weather_now: bool) -> str:
        message = ""

        tab = "&#8194;" * 3

        if is_weather_now:
            tab = ""

        if is_weather_now:
            message += tab + "{}, температура: {}°C".format(info.description, info.average_temperature)
        else:
            message += tab + "{}, температура: {}..{}°C".format(info.description,
                                                                info.min_temperature, info.max_temperature)

        message += '\n' + tab + "Давление: {} мм рт. ст., влажность: {}%".format(info.pressure, info.humidity)
        message += '\n' + tab + "Ветер: {}, {} м/с".format(info.wind_type, info.wind_speed)
        message += ", направление: {}\n".format(info.wind_direction)
        return message
