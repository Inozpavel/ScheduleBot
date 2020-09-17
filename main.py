from Bot import Bot


def main():
    with open("vk_key.txt", "r") as file:
        vk_key = file.readline()

    with open("weather_key.txt", "r")as file:
        weather_key = file.readline()

    bot = Bot(vk_key, weather_key)
    bot.connect()
    bot.start_listening_for_messages()


if __name__ == '__main__':
    main()
