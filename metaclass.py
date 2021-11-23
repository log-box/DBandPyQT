import dis


class ClientMaker(type):
    def __init__(self, classname, bases, classdict):
        bad_methods = []
        attrs = []
        for param in classdict:
            try:
                # print(classdict)
                ret = dis.get_instructions(classdict[param])
            except Exception:
                pass
            else:
                for item in ret:
                    if item.opname == 'LOAD_GLOBAL':
                        if item.argval not in bad_methods:
                            bad_methods.append(item.argval)
                    elif item.opname == 'LOAD_ATTR':
                        if item.argval not in attrs:
                            attrs.append(item.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in bad_methods:
                raise TypeError(f'Запрещенный метод {command}')
        # if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
        #     raise TypeError('не тот сокет')
        super().__init__(classname, bases, classdict)
        print('======Meta is god======')

class ServerMaker(type):
    def __init__(self, classname, bases, classdict):
        methods = []
        attrs = []
        for param in classdict:
            try:
                ret = dis.get_instructions(classdict[param])
            except Exception:
                pass
            else:
                for item in ret:
                    if item.opname == 'LOAD_GLOBAL':
                        if item.argval not in methods:
                            methods.append(item.argval)
                    elif item.opname == 'LOAD_ATTR':
                        if item.argval not in attrs:
                            attrs.append(item.argval)
        if 'connect' in methods:
            raise TypeError(f'Запрещенный метод "connect"')
        # if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
        #     raise TypeError('Не тот сокет')
        super().__init__(classname, bases, classdict)
        print('===Meta is god===')
