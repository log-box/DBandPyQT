"""
Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов. Аргументом
функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""
import socket
from ipaddress import ip_address
from subprocess import Popen, PIPE, call, DEVNULL
from sys import platform

def host_ping(list_ip_addresses, timeout=500, requests=1):
    results = {'Доступные узлы': "", 'Недоступные узлы': ""}  # словарь с результатами
    for address in list_ip_addresses:
        host_ip = ''
        try:
            address = ip_address(address)
        except ValueError:
            try:
                host_ip = socket.gethostbyname(address)
            except Exception:
                host_ip = 'Wrong  Hostname'
        if platform == 'win32':
            proc = Popen(f"ping {address} -w {timeout} -n {requests}", shell=False, stdout=PIPE)
        if platform == 'linux':
            proc = Popen(f"ping {address} -W {int(timeout/300)} -c {requests}", shell=True, stdout=DEVNULL, stderr=DEVNULL)
        proc.wait()
        # проверяем код завершения подпроцесса
        if proc.returncode == 0:
            results['Доступные узлы'] += f"{str(address)}\n"
            # num_str = f'{num:.2f}' if ppl else f'{num}'
            res_string = f'{host_ip} ({address}) - Узел доступен' if host_ip else f'{address} - Узел доступен'
        else:
            results['Недоступные узлы'] += f"{str(address)}\n"
            res_string = f'{host_ip} ({address}) - Узел недоступен' if host_ip else f'{address} - Узел недоступен'
        print(res_string)
    return results


if __name__ == '__main__':
    ip_addresses = ['yandex.ru', '2.2.2.2', '192.168.0.100', '192.168.0.101', 'test.ru', 'bkdfjdhfsdk']
    host_ping(ip_addresses)