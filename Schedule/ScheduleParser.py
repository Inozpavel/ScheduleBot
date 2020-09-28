import json

from vk_api.utils import get_random_id

from Keyboards import Keyboards


class ScheduleParser:
    def __init__(self, vk, upload):
        self.__upload = upload
        self.__vk = vk
        with open("./Configs/Schedule/LessonsTime.json", "r", encoding="utf-8") as file:
            self.LESSONS_TIME = json.load(file)

    def send_lessons_time(self, user_id):
        message = ""
        for key in self.LESSONS_TIME:
            message += key + ": " + self.LESSONS_TIME[key] + "\n"
        self.__send_message(user_id, message, "", "")

    def __send_message(self, user_id: int, message: str, image_url: str,
                       should_send_keyboard: bool = False) -> None:
        """Отправляет указанное собщение выбранному пользоваелю. Можно добавить клавиатуру"""
        keyboard = Keyboards.get_weather_keyboard() if should_send_keyboard else ""
        self.__vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            keyboard=keyboard,
            attachment=image_url
        )
