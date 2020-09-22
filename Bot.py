import json
import string
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from os import path

from Keyboards import Keyboards
from Weather.WeatherForecaster import WeatherForecaster


class Bot:
    TAB = "&#8194;" * 4

    def __init__(self, vk_key: string, weather_key: string):
        with open("Configs/BotPhrases/HelloWords.json", "r", encoding="utf-8") as file:
            self.HELLO_WORDS = json.load(file)
        self.__vk_key = vk_key
        self.__weather_key = weather_key
        print("Бот создан")

    def connect(self) -> None:
        self.vk_session = VkApi(token=self.__vk_key)
        self.vk = self.vk_session.get_api()
        self.upload = VkUpload(self.vk_session)
        self.long_poll = VkLongPoll(self.vk_session)
        self.weather_forecaster = WeatherForecaster(self.__weather_key, self.vk, self.upload)

        print("Бот успешно подключен к чату")

    def start_listening_for_messages(self) -> None:
        print("Бот начал слушать сообщения")

        for event in self.long_poll.listen():

            if event.type == VkEventType.MESSAGE_NEW and event.to_me:

                print("From {} message = {}".format(event.user_id, event.text))
                user_id = event.user_id
                message = event.text.lower()

                if message in self.HELLO_WORDS:
                    user_name = self.vk.users.get(user_id=event.user_id)[0]['first_name']
                    user_surname = self.vk.users.get(user_id=event.user_id)[0]['last_name']

                    if self.__check_id_in_data_base(user_id):
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

                    self.__send_message(user_id, text, Keyboards.get_main_keyboard())

                elif message == "погода сейчас":
                    self.weather_forecaster.send_weather_for_now(user_id)

                elif message == "погода сегодня":
                    self.weather_forecaster.send_weather_for_today(user_id)

                elif message == "погода завтра":
                    self.weather_forecaster.send_weather_for_tomorrow(user_id)

                elif message == "погода на 5 дней":
                    self.weather_forecaster.send_weather_for_five_days(user_id)

                elif message == "расписание":
                    if self.__check_id_in_data_base(user_id):
                        self.__send_message(user_id, "Выбери, пожалуйста, из списка:",
                                            Keyboards.get_schedule_keyboard())
                    else:
                        self.__send_message(user_id, "Ты пока не сохранил свою группу. Функция не доступна.",
                                            Keyboards.get_main_keyboard())
                elif message == "погода":
                    self.__send_message(user_id, "Выбери, пожалуйста, из списка:", Keyboards.get_weather_keyboard())
                elif message == "назад":
                    self.__send_message(user_id, "Возвращаю тебя в меню...", Keyboards.get_main_keyboard())
                elif message == "настройки":
                    self.__send_message(user_id, "Выбери, пожалуйста, из списка:", Keyboards.get_settings_keyboard())
                else:
                    self.__send_message(user_id, "Я пока не знаю такой команды... Но, возможно, скоро узнаю. " +
                                        "Проверь правильность еще раз или выбери из списка.",
                                        Keyboards.get_main_keyboard())

    def __send_message(self, user_id: int, message: string = "", keyboard: VkKeyboard = None) -> None:
        """Отправляет указанное собщение выбранному пользоваелю. Можно добавить клавиатуру"""
        self.vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            keyboard=keyboard,
        )

    def __check_id_in_data_base(self, user_id: int) -> bool:
        """Возвращает True, если в базе уже есть этот пользователь, иначе False"""
        if not path.exists("Users_Base.txt"):
            return False

        for i in open("Users_Base.txt", "r", encoding="utf-8"):
            if i[0:9] == str(user_id):
                return True
        else:
            return False
