import string
from datetime import datetime

import vk_api
from vk_api.upload import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from os import path

from Keyboards import Keyboards


class Bot:
    HELLO_WORDS = ["бот", "начать", "привет",
                   "добрый день", "здравствуй", "здравствуйте",
                   "добрый вечер", "доброе утро", "доброй ночи"]
    TAB = "&#8194;" * 4

    def __init__(self, vk_key: string, weather_key: string):

        self.__vk_key = vk_key
        self.__weather_key = weather_key

        self.vk_session = vk_api.VkApi(token=self.__vk_key)

        self.vk = self.vk_session.get_api()
        self.upload = VkUpload(self.vk_session)
        self.long_poll = VkLongPoll(self.vk_session)
        self.listen_for_messages()

    def listen_for_messages(self) -> None:
        print("Бот успешно запущен")

        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                print("From {} message = {}".format(event.user_id, event.text))
                user_id = event.user_id
                message = event.text.lower()

                if message in self.HELLO_WORDS:
                    user_name = self.vk.users.get(user_id=event.user_id)[0]['first_name']
                    user_surname = self.vk.users.get(user_id=event.user_id)[0]['last_name']

                    if self.check_id_in_data_base(user_id):
                        text = (f"Рад тебя приветствовать, {user_name} {user_surname}, снова. Я - бот:" +
                                f"\n{self.TAB}*Я помогу тебе с расписанием, подскажу погоду.*" +
                                f"\n{self.TAB}*Ты уже сохранил свою группу.*" +
                                f"\n{self.TAB}*Тебе доступно расписание.*" +
                                f"\n{self.TAB}*Тебе доступна погода.*" +
                                "\nЧтобы общаться со мной, можешь использовать:" +
                                f"\n{self.TAB}1) Кнопочки в меню" +
                                f"\n{self.TAB}2) Писать команды ручками"
                                "\n\nНапиши \"бот команды\", узнаешь дополнительные команды.")
                    else:
                        text = (f"Привет, {user_name} {user_surname}, я - бот: " +
                                f"\n{self.TAB}*Я помогу тебе с расписанием, подскажу погоду.*" +
                                f"\n{self.TAB}*Тебе пока не доступно расписание.*" +
                                f"\n{self.TAB}*Сохрани, пожалуйста, свою группу в настройках.*" +
                                f"\n{self.TAB}*Тебе доступна погода.*" +
                                "\nЧтобы общаться со мной, можешь использовать:" +
                                f"\n{self.TAB}1) Кнопочки в меню" +
                                f"\n{self.TAB}2) Писать команды ручками"
                                "\n\nНапиши \"бот команды\", узнаешь дополнительные команды.")
                    self.send_message(user_id, text, Keyboards.get_main_keyboard())

                elif message == "расписание":
                    if self.check_id_in_data_base(user_id):
                        self.send_message(user_id, "Выбери, пожалуйста, из списка:", Keyboards.get_schedule_keyboard())
                    else:
                        self.send_message(user_id, "Ты пока не сохранил свою группу. Функция не доступна.",
                                          Keyboards.get_main_keyboard())
                elif message == "погода":
                    self.send_message(user_id, "Выбери, пожалуйста, из списка:", Keyboards.get_weather_keyboard())
                elif message == "назад":
                    self.send_message(user_id, "Возвращаю тебя в меню...", Keyboards.get_main_keyboard())
                elif message == "настройки":
                    self.send_message(user_id, "Выбери, пожалуйста, из списка:", Keyboards.get_settings_keyboard())
                else:
                    self.send_message(user_id, "Я пока не знаю такой команды... Но, возможно, скоро узнаю. " +
                                      "Проверь правильность еще раз или выбери из списка.",
                                      Keyboards.get_main_keyboard())

    def send_message(self, user_id: int, message="", keyboard=None) -> None:
        """Отправляет указанное собщение выбранному пользоваелю. Можно добавить клавиатуру"""
        self.vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            keyboard=keyboard,
        )

    def check_id_in_data_base(self, user_id: int) -> bool:
        """Возвращает True, если в базе уже есть этот пользователь, иначе False"""
        if not path.exists("Users_Base.txt"):
            return False

        for i in open("Users_Base.txt", "r", encoding="utf-8"):
            if i[0:9] == str(user_id):
                return True
        else:
            return False
