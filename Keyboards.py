from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Keyboards:
    @staticmethod
    def get_main_keyboard() -> VkKeyboard:
        keyboard = VkKeyboard(one_time=True)

        keyboard.add_button("Расписание", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button("Погода", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button("Настройки", color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("Коронавирус", color=VkKeyboardColor.POSITIVE)

        return keyboard.get_keyboard()

    @staticmethod
    def get_settings_keyboard() -> VkKeyboard:
        keyboard = VkKeyboard(one_time=True)

        keyboard.add_button("Узнать свой институт, курс и группу", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("Сохранить группу", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

    @staticmethod
    def get_schedule_keyboard() -> VkKeyboard:
        keyboard = VkKeyboard(one_time=True)

        keyboard.add_button("На сегодня", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button("На завтра", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("На эту неделю", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button("На следующую неделю", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("На конкретный день недели", color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("Номер учебной недели", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Расписание занятий", color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

    @staticmethod
    def get_weather_keyboard() -> VkKeyboard:
        keyboard = VkKeyboard(one_time=True)

        keyboard.add_button("Погода сейчас", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Погода сегодня", color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("Погода завтра", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("Погода на 5 дней", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()
