"""
Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только последний
октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.
"""


from ipaddress import ip_address
from task1 import host_ping


def host_range_ping():
    while True:
        # запрос первоначального адреса
        start_ip = input('Введите первоначальный адрес: ')
        try:
            # смотрим чему равен последний октет
            las_oct = int(start_ip.split('.')[3])
            break
        except Exception as e:
            print(e)
    while True:
        # запрос на количество проверяемых адресов
        end_ip = input('Сколько адресов проверить?: ')
        if not end_ip.isnumeric():
            print('Необходимо ввести число: ')
        else:
            # по условию меняется только последний октет
            if (las_oct+int(end_ip)) > 254:
                print(f"Можем менять только последний октет, т.е. "
                      f"максимальное число хостов для проверки: {254-las_oct}")
            else:
                break

    host_list = []
    # формируем список ip адресов
    [host_list.append(str(ip_address(start_ip)+x)) for x in range(int(end_ip))]
    # передаем список в функцию из задания 1 для проверки доступности
    return host_ping(host_list)


if __name__== "__main__":
    host_range_ping()