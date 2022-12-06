
from aiogram.dispatcher.filters.state import State, StatesGroup

import database

from datetime import datetime

class head(StatesGroup):
    GroupName = State()
    CourseNum = State()
    StudentBirthday = State()
    QuestionAnswer = State()
    Message = State()

class userState(StatesGroup):
    Emoji = State()
    Birthday = State()
    Wish = State()
    Ask = State()
    Donate = State()

class admin_state(StatesGroup):
    Message = State()


def getUserBirthday(id, dt):
    today = datetime(dt.year, dt.month, dt.day)
    user = database.getUser(id)
    if user[5] is None:
        return None, None
    try:
        newDate = datetime(today.year, user[5].month, user[5].day)
    except:
        newDate = datetime(today.year, user[5].month, user[5].day - 1)
    return (newDate - today).days , today.year - user[5].year