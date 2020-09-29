import json
import re
from datetime import datetime
from os import mkdir, path
import shutil

import requests
from bs4 import BeautifulSoup
from vk_api import VkUpload
from vk_api.utils import get_random_id
from vk_api.vk_api import VkApiMethod

from Keyboards import Keyboards


class ScheduleParser:
    def __init__(self, vk: VkApiMethod, upload: VkUpload):
        self.__upload = upload
        self.__vk = vk
        with open("./Configs/Schedule/LessonsTime.json", "r", encoding="utf-8") as file:
            self.LESSONS_TIME = json.load(file)
        with open("./Configs/Schedule/InstitutesDecryption.json", "r", encoding="utf-8") as file:
            self.INSTITUTES_DECRYPTION = json.load(file)
        if path.exists("./Schedule/ScheduleFiles"):
            shutil.rmtree("./Schedule/ScheduleFiles")
        self.__download_all_schedule_files()

    def send_lessons_time(self, user_id: int) -> None:
        """Отправляет указанному пользователю информацию о начале конце всех пар"""
        message = ""
        for key in self.LESSONS_TIME:
            message += key + ": " + self.LESSONS_TIME[key] + "\n"
        self.__send_message(user_id, message, "", True)

    def __download_all_schedule_files(self, should_print_all_files_names: bool = False) -> None:
        """Загружает или обновляет все файлы с расписанием для всех институтов, курсов и групп"""
        page = requests.get("https://www.mirea.ru/schedule/")
        soup = BeautifulSoup(page.text, "html.parser")

        links = soup.find("div", {"class": "rasspisanie"}).find_all("a", {"class": "uk-link-toggle"})
        files_links_array = [x["href"] for x in links if
                             "экз" not in x["href"] and "зач" not in x["href"] and "маг" not in x["href"]]

        if not path.exists("./Schedule/ScheduleFiles"):
            mkdir("./Schedule/ScheduleFiles")

        for url in files_links_array:
            folder_name = ""
            course = ""
            if re.match(".*/[А-Яа-я]{2,}_\\dк", url):
                folder_name = re.findall("[А-Яа-я]+", url.split("/")[-1])[0]
                course = re.findall("\\d", url.split("/")[-1])[0]
            elif re.match(".*/[а-яА-Я]{2,} \\d курс", url):
                folder_name = re.findall("[А-Яа-я]+", url.split("/")[-1])[0]
                course = re.findall("\\d", url.split("/")[-1])[0]
            elif re.match(".*/[А-Яа-я]{2,}_бак_\\dк", url):
                folder_name = re.findall("[А-Яа-я]+", url.split("/")[-1])[0]
                course = re.findall("\\d", url.split("/")[-1])[0]

            else:
                pass  # for testing

            if should_print_all_files_names:
                print(f"{folder_name} {course}")
            if folder_name and course and "маг" not in folder_name:
                if not path.exists("./Schedule/ScheduleFiles/" + folder_name):
                    mkdir("./Schedule/ScheduleFiles/" + folder_name)
                with open("./Schedule/ScheduleFiles/" + folder_name + "/" + course + ".xlsx", "bw") as file:
                    file.write(requests.get(url).content)

    def get_group_by_id(self, user_id: int) -> str:
        """Возвращает группу, сохраненную у пользователя c указанным id"""
        with open("./Configs/UsersBase.txt", "r", encoding="utf-8") as file:
            users = file.readlines()
        for line in users:
            if line[0:9] == str(user_id):
                return line[10:20]
        raise Exception("Пользователь не найден!")

    def get_course_by_group(self, group: str) -> int:
        """Возвращает курс для указанной группы"""
        current_month = datetime.today().month
        current_year = int(str(datetime.today().year)[2:])
        if 0 < current_month < 9:
            course = current_year - int(group[8:])
        else:
            course = current_year + 1 - int(group[8:])

        if 0 < course < 6:
            return course
        else:
            raise Exception("Невозможно получить для данной группы курс!")

    def get_full_institute_name_by_group(self, group: str) -> str:
        """Возвращает полное название института для указанной группы"""
        institute_info = self.INSTITUTES_DECRYPTION[group[0]]
        abbreviation = list(institute_info.keys())[0]
        return institute_info[abbreviation]

    def __send_message(self, user_id: int, message: str, image_url: str,
                       should_send_keyboard: bool = False) -> None:
        """Отправляет указанное собщение выбранному пользоваелю. Можно добавить клавиатуру"""
        keyboard = Keyboards.get_schedule_keyboard() if should_send_keyboard else ""
        self.__vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            keyboard=keyboard,
            attachment=image_url
        )
