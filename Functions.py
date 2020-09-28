import calendar
from datetime import datetime

WEEK_DAYS = {"Mon": "понедельник", "Tue": "вторник", "Wed": "среда", "Thu": "четверг",
             "Fri": "пятница", "Sat": "суббота", "Sun": "воскресенье"
             }
__all__ = ["get_day_name_by_date"]


def get_day_name_by_date(date: datetime) -> str:
    """По указанной дате возвращает название дня недели"""
    return WEEK_DAYS[calendar.day_abbr[date.weekday()]]
