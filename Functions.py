import calendar
from datetime import datetime

WEEK_DAYS = {"Mon": "понедельник", "Tue": "вторник", "Wed": "среда", "Thu": "четверг",
             "Fri": "пятница", "Sat": "суббота", "Sun": "воскресенье"
             }

MONTHS = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня", 7: "июля", 8: "августа",
          9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}
__all__ = ["get_day_name_by_date"]


def get_day_name_by_date(date: datetime) -> str:
    """По указанной дате возвращает название дня недели"""
    return WEEK_DAYS[calendar.day_abbr[date.weekday()]]


def get_month_name_by_date(date: datetime) -> str:
    """По указанной дате возвращает название месяца в родительном падеже"""
    return MONTHS[date.month]
