import string
from datetime import datetime
import vk_api
from vk_api.upload import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


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

                if event.text.lower() in self.HELLO_WORDS:
                    user_name = self.vk.users.get(user_id=event.user_id)[0]['first_name']
                    user_surname = self.vk.users.get(user_id=event.user_id)[0]['last_name']
                    self.send_message(f"Рад тебя приветствовать,{user_surname} {user_name}, снова. Я помню " +
                                      "твою группу.\nЧтобы общаться со мной, используй меню или пиши надписи "
                                      "на кнопочках ручками.\n\nМожешь написать \"бот команды\" и узнаешь, "
                                      "что я еще умею", user_id)

                else:
                    self.send_message("Я пока не знаю такой команды... Но, возможно, скоро узнаю. " +
                                      "Проверь правильность еще раз или выбери из списка.", user_id)

    def send_message(self, user_id: int, message="", keyboard=None) -> None:
        self.vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            keyboard=keyboard,
        )
