"""
Продолжая задачу логирования, реализовать декоратор @log, фиксирующий обращение к декорируемой функции.
Он сохраняет ее имя и аргументы.
В декораторе @log реализовать фиксацию функции, из которой была вызвана декорированная. Если имеется такой код:
    @log
    def func_z():
        pass

    def main():
        func_z()
 ...в логе должна быть отражена информация:
 "<дата-время> Функция func_z() вызвана из функции main"
"""
import functools
import inspect
import os
import sys
from datetime import date
import logging.handlers


class Log:
    sys.path.append(os.path.join(os.getcwd(), '..'))
    sys.path.append('../')
    TODAY = str(date.today())
    PATH = os.path.dirname(os.path.abspath(__file__))
    PATH = os.path.join(PATH, f'{TODAY}-decor.log')
    DECOR_LOG = logging.getLogger('decor')
    FORMATTER = logging.Formatter("%(asctime)-25s  %(message)s")
    FILE_HANDLER = logging.handlers.RotatingFileHandler(PATH, encoding='utf8')
    FILE_HANDLER.setLevel(logging.DEBUG)
    FILE_HANDLER.setFormatter(FORMATTER)
    DECOR_LOG.addHandler(FILE_HANDLER)
    DECOR_LOG.setLevel(logging.DEBUG)
    STREAM_HANDLER = logging.StreamHandler()
    STREAM_HANDLER.setFormatter(FORMATTER)
    DECOR_LOG.addHandler(STREAM_HANDLER)

    def __init__(self):
        pass

    def __call__(self, func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            self.DECOR_LOG.info(
                f'Декоратором @Log была обернута функция "{func.__name__}" с параметрами {args} {kwargs}')
            func_execute = func(*args, **kwargs)
            self.DECOR_LOG.info(
                f'Функция "{func.__name__}" была вызвана из модуля {inspect.getfile(func).split("/")[-1]} '
                f'Её вызвала функция {inspect.stack()[1][3]}')
            return func_execute

        return decorator


if __name__ == '__main__':
    @Log()
    def fun(arg):
        return arg


    def logbox():
        fun('logbox')


    logbox()
    print(fun.__name__)
