"""Программа-клиент"""
import argparse
import json
import sys
import threading
from contextlib import contextmanager
from socket import *
import time
from common.utils import get_message, send_message
from common.variables import *
from log.client_log_config import *
from common.do_dict_utils import do_presence, do_message, do_wait_message, do_exit_message
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError


def message_from_server(sock, my_username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                CLIENT_LOG.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOG.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            CLIENT_LOG.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOG.critical(f'Потеряно соединение с сервером.')
            break


# Функция запрашивает кому отправить сообщение и само сообщение, и отправляет полученные данные на сервер.
def create_message(sock, account_name='Guest'):
    to = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOG.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        CLIENT_LOG.info(f'Отправлено сообщение для пользователя {to}')
    except:
        CLIENT_LOG.critical('Потеряно соединение с сервером.')
        exit(1)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOG.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)

    return server_address, server_port, client_name


@contextmanager
def socket_context(server_address, server_port, *args, **kw):
    s = socket(*args, **kw)
    s.connect((server_address, int(server_port)))
    try:
        yield s
    finally:
        s.close()


def user_interactive(sock, username):
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, do_exit_message(username))
            print('Завершение соединения.')
            CLIENT_LOG.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


def print_help():
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


def user_message(sock):
    msg = ''
    while msg.strip() == '':
        msg = input('Ваше сообщение: ')
    msg = do_message(msg, sock)
    send_message(sock, msg)
    answer = ''
    try:
        resp = get_message(sock)
        answer = read_server_response(resp)
    except Exception as err:  # (ValueError, json.JSONDecodeError)
        CLIENT_LOG.error('Не удалось декодировать сообщение сервера.')
        print(err)
    if answer != '':
        return answer
    else:
        return CLIENT_LOG.error('Не удалось декодировать сообщение сервера.')


def user_connect(sock, client_name):
    if client_name == '':
        user_name = input('Имя пользователя:\n')
    else:
        user_name = client_name
    message_to_server = do_presence(user_name.lower())
    send_message(sock, message_to_server)
    answer = ''
    try:
        answer = read_server_response(get_message(sock))
        CLIENT_LOG.info(answer)
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOG.error('Не удалось декодировать сообщение сервера.')
    if answer != '':
        return answer
    else:
        return CLIENT_LOG.error('Не удалось декодировать сообщение сервера.')


def user_wait_message(sock):
    message_to_server = do_wait_message()
    send_message(sock, message_to_server)
    try:
        data = sock.recv(1024).decode('utf-8')

        return data
    except Exception:
        return 'Server not answered'


# @Log()
def read_server_response(message):
    """
    Функция разбирает ответ сервера
    :param message:
    :return:
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200 and MESSAGE in message:
            return {200: message[MESSAGE]}
        if message[RESPONSE] == 200:
            return {RESPONSE: 200}
        elif message[RESPONSE] == 409:
            return {409: 'User already connected'}
        return {RESPONSE: 400, ERROR: 'Bad Request'}
    raise ReqFieldMissingError


def main():
    # Сообщаем о запуске
    print('Консольный месседжер. Клиентский модуль.')
    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = arg_parser()
    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    CLIENT_LOG.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')
    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, do_presence(client_name))
        answer = read_server_response(get_message(transport))
        CLIENT_LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOG.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as err:
        CLIENT_LOG.error(f'При установке соединения сервер вернул ошибку: {err.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOG.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOG.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:
        # Если соединение с сервером установлено корректно, запускаем клиенский процесс приёма сообщний
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()
        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOG.debug('Запущены процессы')
        # Watchdog основной цикл, если один из потоков завершён, то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках, достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
