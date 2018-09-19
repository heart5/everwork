# encoding:utf-8
"""
功能描述
"""
import time
from functools import wraps
from inspect import signature

import pathmagic

with pathmagic.context():
    from func.logme import log


def timethis(func):
    """
    装饰执行时间（tida）
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper


@timethis
def countdown(n: int):
    """
    倒计时
    :param n:
    :return: NULL
    """
    print(n)
    while n > 0:
        n -= 1


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    countdown(100088)
    print(countdown.__name__)
    print(countdown.__doc__)
    print(countdown.__annotations__)
    countdown(12234353)
    countdown(500)
    countdown.__wrapped__(500)
    print(signature(countdown))
    print(countdown.__class__)
    print(countdown.__closure__)
    print(countdown.__code__)
    print(countdown.__defaults__)
    print(countdown.__dict__)
    print(countdown.__dir__())
    print('Done.完毕。')
