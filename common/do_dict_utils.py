import time

from common.variables import *


def do_authenticate(account_name, password):
    """
    Функция генерирует запрос об авторизации клиента (авторизация)
    :param account_name:
    :param password:
    :return:
    """
    out = {
        ACTION: AUTHENTICATE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
            PASSWORD: password
        }
    }
    return out


def do_exit_message(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


# @Log()
def do_quit(account_name):
    """
    Функция отправляет запрос о выходе клиента (отключение)
    :param account_name:
    :return:
    """
    out = {
        ACTION: QUIT,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return out


# @Log()
def do_presence(account_name='Guest', status='I`m online'):
    """
    Функция генерирует запрос о присутствии клиента (подключение)
    :param status:
    :param account_name:
    :return:
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
        }
    }
    return out



def do_wait_message():
    out = {
        ACTION: MSG,
        MESSAGE: '...',
    }
    return out


# @Log()
def do_message(message, client):
    """
    Функция генерирует сообщение пользователю или чату (Пользователь-Пользователь, Пользователь-Чат)
    :param client:
    :param message:
    :return:
    """

    out = {
        ACTION: MSG,
        TIME: time.time(),
        FROM: str(client),  # Доделать через сохранение имени пользователя в файл(пока просто 'account_name')
        ENCODING: DEFAULT_ENCODING,
        MESSAGE: message,
    }
    return out


def do_message_to_user(to_user, message):
    """
    Функция генерирует сообщение пользователю или чату (Пользователь-Пользователь, Пользователь-Чат)
    :param message:
    :param to_user:
    :return:
    """
    out = {
        ACTION: MSG,
        TIME: time.time(),
        TO: to_user,
        FROM: ACCOUNT_NAME,  # Доделать через сохранение имени пользователя в файл(пока просто 'account_name')
        ENCODING: DEFAULT_ENCODING,
        MESSAGE: message
    }
    return out


# @Log()
def do_join_chat(room_name):
    """
    Функция Присоединяет пользователя к чату (Присоединиться к чату)
    :param room_name:
    :return:
    """
    out = {
        ACTION: JOIN,
        TIME: time.time(),
        ROOM: room_name
    }
    return out


# @Log()
def do_leave_chat(room_name):
    """
    Функция отсоединяет пользователя от чата (Покинуть чат)
    :param room_name:
    :return:
    """
    out = {
        ACTION: LEAVE,
        TIME: time.time(),
        ROOM: room_name
    }
    return out
