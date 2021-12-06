"""Утилиты"""

import json
from socket import socket

from common.variables import MAX_PACKAGE_LENGTH, DEFAULT_ENCODING, ENCODING
from log.log import Log


# @Log()
def get_message(_socket):
    encoded_response = _socket.recv(MAX_PACKAGE_LENGTH)
    json_response = encoded_response.decode(DEFAULT_ENCODING)
    response = json.loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError
    # client.settimeout(5.0)
    # encoded_response = _socket.recv(MAX_PACKAGE_LENGTH)
    # if isinstance(encoded_response, bytes):
    #     json_response = encoded_response.decode(DEFAULT_ENCODING)
    #     response = json.loads(json_response)
    #     if isinstance(response, dict):
    #         return response
    #     raise ValueError
    # else:
    #     raise ValueError


# @Log()
def send_message(_socket, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode(DEFAULT_ENCODING)
    _socket.send(encoded_message)
    # if isinstance(_socket, socket):
    #     js_message = json.dumps(message)
    #     encoded_message = js_message.encode(DEFAULT_ENCODING)
    #     if isinstance(encoded_message, bytes):
    #         _socket.send(encoded_message)
    #     else:
    #         raise ValueError
    # else:
    #     raise ValueError
