"""Константы"""

# Порт поумолчанию для сетевого ваимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
DEFAULT_ENCODING = 'utf-8'

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
PASSWORD = 'password'
PORT = 'port'
TYPE = 'type'
STATUS = 'status'
TO = 'to'
FROM = 'from'
ENCODING = 'encoding'
MESSAGE = 'message'
ROOM = 'room'
ALERT = 'alert'
EXIT = 'exit'
SENDER = 'sender'
DESTINATION = 'destination'
MESSAGE_TEXT = 'mess_text'

##############################

# Прочие ключи, используемые в протоколе
RESPONSE = 'response'
ERROR = 'error'
RESPONDEFAULT_IP_ADDRESSSE = 'respondefault_ip_addressse'
########################################

# ACTIONS KEYS
PRESENCE = 'presence'
PROBE = 'probe'
MSG = 'msg'
QUIT = 'quit'
AUTHENTICATE = 'authenticate'
JOIN = 'join'
LEAVE = 'leave'
USERS_REQUEST = 'get_users'
LIST_INFO = 'data_list'
GET_CONTACTS = 'get_contacts'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
##############

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
            RESPONSE: 400,
            ERROR: None
        }
RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO:None
                }

SERVER_DATABASE = 'sqlite:///server.sqlite.db'