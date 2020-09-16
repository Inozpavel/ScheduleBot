from Bot import Bot


def main():
    Bot(open("vk_key.txt").readline(), open("weather_key.txt", "r").readline())


if __name__ == '__main__':
    main()
