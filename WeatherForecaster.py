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
        self.__send_message(user_id, message, image_url, should_send_keyboard=True)

    def send_weather_for_today(self, user_id: int) -> None:
        """Отправляет информацию о погоде на сегодня указанному пользователю, прикрепляет картинку.
            Картинка - несколько склеенных картинок с прогнозом погоды для каждого периода дня
        """
        self.__send_weather_for_one_day(user_id, datetime.today().date())

    def send_weather_for_tomorrow(self, user_id: int) -> None:
        """Отправляет информацию о погоде на завтра указанному пользователю, прикрепляет картинку.
            Картинка - несколько склеенных картинок с прогнозом погоды для каждого периода дня
        """
        self.__send_weather_for_one_day(user_id, datetime.today().date() + timedelta(1))

    def __send_weather_for_one_day(self, user_id: int, day_date: datetime) -> None:
        """Отправляет информацию о погоде на указанный день указанному пользователю, прикрепляет картинку.
            Картинка - несколько склеенных картинок с прогнозом погоды для каждого периода дня
        """
        images = []
        for weather_info in self.__get_weather_for_day(day_date):
            images.append(weather_info.image_code)
            message = weather_info.day_period.capitalize() + ":\n" + self.__convert_weather_information_to_text(
                weather_info, is_weather_now=False)
            self.__send_message(user_id, message, "", should_send_keyboard=False)
        image_url = self.__upload_pictures(images)
        self.__send_message(user_id, "", image_url, should_send_keyboard=True)

    def __get_weather_for_now(self) -> WeatherInformation:
        """Возвращает информацию о погоде на сейчас"""
        response = requests.get(
            "http://api.openweathermap.org/data/2.5/weather?q=moscow&appid=" + self.__weather_api_key +
            "&units=metric&lang=ru")
        return self.__parse_weather(response.json())

    def __get_weather_for_five_days(self):
        """Возвращает информацию о погоде на 5 дней"""
        pass

    def __get_weather_for_day(self, day_date: datetime):
        """Возвращает информацию о погоде на указанный день"""
        response = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast?q=moscow&appid=" + self.__weather_api_key +
            "&units=metric&lang=ru")

        day_weather_periods = {
            "утром": [],
            "днем": [],
            "вечером": [],
            "ночью": [],
        }

        for period in response.json()["list"]:
            period_date = datetime.strptime(period["dt_txt"], "%Y-%m-%d %H:%M:%S").date()
            hour = datetime.strptime(period["dt_txt"], "%Y-%m-%d %H:%M:%S").hour
            is_today = day_date == period_date and not hour == 0
            is_in_early_morning = 0 <= hour <= 3 and day_date + timedelta(1) == period_date
            if is_today or is_in_early_morning:
                for period_name in self.DAY_PERIODS:
                    if hour == 3 and period_name == "ночью" and day_date == period_date:
                        continue
                    if hour in self.DAY_PERIODS[period_name]:
                        day_weather_periods[period_name].append(period)

        for period in day_weather_periods:
            if len(day_weather_periods[period]) == 0:
                continue
            max_temp = max([x["main"]["temp_max"] for x in day_weather_periods[period]])
            min_temp = min([x["main"]["temp_min"] for x in day_weather_periods[period]])
            weather_info = self.__parse_weather(day_weather_periods[period][0])
            weather_info.min_temperature = min_temp
            weather_info.max_temperature = max_temp
            weather_info.day_period = period
            yield weather_info

    def __parse_weather(self, json_day: Dict) -> WeatherInformation:
        """Конвертирует объект класса WeatherInformation в строковое представление погоды"""
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
        """Склеивает картинки из списка images в одну, загружает на сервер, возвращает ссылку"""
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

    def __send_message(self, user_id: int, message: string, image_url: str, should_send_keyboard: bool = False) -> None:
        """Отправляет указанное собщение выбранному пользоваелю. Можно добавить клавиатуру"""
        keyboard = Keyboards.get_weather_keyboard() if should_send_keyboard else ""
        self.__vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            keyboard=keyboard,
            attachment=image_url
        )

    @staticmethod
    def __convert_weather_information_to_text(info: WeatherInformation, is_weather_now: bool) -> str:
        tab = "" if is_weather_now else "&#8194;" * 3
        message = tab + "{}, температура: ".format(info.description)

        message += "{}°C".format(info.average_temperature) if is_weather_now else "{}..{}°C".format(
            info.min_temperature, info.max_temperature)

        message += '\n' + tab + "Давление: {} мм рт. ст., влажность: {}%".format(info.pressure, info.humidity)
        message += '\n' + tab + "Ветер: {}, {} м/с".format(info.wind_type, info.wind_speed)
        message += ", направление: {}\n".format(info.wind_direction)
        return message
