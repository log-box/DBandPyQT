import argparse
import select
import threading
from socket import AF_INET, SOCK_STREAM

from DataBaseServer import DataBaseServer
from descriptors import Port
from common.utils import *
from common.variables import *
from log.server_log_config import *
from log.server_log_config import SERVER_LOG
from metaclass import ServerMaker


# Парсер аргументов коммандной строки.
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        SERVER_LOG.critical(
            f'Попытка запуска сервера с указанием неподходящего порта {listen_port}. Допустимы адреса с 1024 до 65535.')
        exit(1)

    return listen_address, listen_port


class ChatServer(threading.Thread, metaclass=ServerMaker):
    listen_port = Port()

    def __init__(self, listen_address, listen_port, db):
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.clients = []
        self.messages_list = []
        self.db = db
        self.names = dict()
        super().__init__()

    def socket_init(self):
        transport = socket(AF_INET, SOCK_STREAM)
        transport.bind((self.listen_address, self.listen_port))
        transport.settimeout(0.5)
        self.socket = transport
        self.socket.listen(MAX_CONNECTIONS)

    def process_client_message(self, message, client):
        # print(message)
        if USER in message:
            SERVER_LOG.debug(f'Разбор сообщения от клиента : {message[USER][ACCOUNT_NAME]}')
        if SENDER in message:
            SERVER_LOG.debug(f'Разбор сообщения от клиента : {message[SENDER]}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован, регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                ip, client_port = client.getpeername()
                self.db.login(message[USER][ACCOUNT_NAME], ip)
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages_list.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.db.logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return

    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            SERVER_LOG.info(
                f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            SERVER_LOG.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    def run(self):
        self.socket_init()
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                SERVER_LOG.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)
            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass
            # принимаем сообщения и если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        SERVER_LOG.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)
            # Если есть сообщения, обрабатываем каждое.
            for i in self.messages_list:
                try:
                    self.process_message(i, send_data_lst)
                except:
                    SERVER_LOG.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    self.clients.remove(self.names[i[DESTINATION]])
                    del self.names[i[DESTINATION]]
            self.messages_list.clear()


def print_help():
    print('Поддерживаемые комманды:')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')

def starter():
    address, port = arg_parser()
    port = DEFAULT_PORT
    database = DataBaseServer()
    chat = ChatServer(address, port, database)
    chat.daemon = True
    chat.start()

    while True:
        command = input('Введите комманду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break

if __name__ == '__main__':
    starter()
    # connection = sqlite3.connect('server.db.sqlite')
    # cursor = connection.cursor()
    # cursor.execute("CREATE TABLE IF NOT EXISTS Clients (user_id int NOT NULL,account_name char(50), information char(150), PRIMARY KEY (user_id) )")
    # cursor.execute("CREATE TABLE IF NOT EXISTS ClientHistory (user_id int, login_time date, ip_address char(30), FOREIGN KEY (user_id) REFERENCES Clients(user_id))")
    # cursor.execute("CREATE TABLE IF NOT EXISTS Contacts (owner_id int, client_id int)")
    # connection.commit()
    # connection.close()
