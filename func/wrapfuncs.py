# encoding:utf-8
"""
功能描述
"""
import time
import platform
from functools import wraps
from inspect import signature
from py2ifttt import IFTTT

import pathmagic

with pathmagic.context():
    from func.logme import log


def ift2phone(msg=None):
    """
    目标函数运行时将信息通过ifttt发送至手机
    :param func:
    :return:
    """
    def decorate(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            pu = platform.uname()
            ifttt = IFTTT('0sa6Pl_UJ9a_w6UQlYuDJ', 'everwork')
            if msg is None:
                msginner = func.__doc__
            else:
                msginner = msg
            ifttt.notify(f'{pu.machine}_{pu.node}', f'{msginner}', f'{func.__name__}')
            return result

        return wrapper

    return decorate


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
@ift2phone()
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
    print(f"函数名\t{countdown.__name__}")
    print(f"函数文档\t{countdown.__doc__}")
    print(f"函数参数注释\t{countdown.__annotations__}")
    countdown(12234353)
    countdown(500)
    countdown.__wrapped__(500)
    print(f"函数参数签名\t{signature(countdown)}")
    print(f"函数类名\t{countdown.__class__}")
    print(f"函数模块\t{countdown.__module__}")
    print(f"函数包裹函数\t{countdown.__wrapped__}")
    print(f"函数语句\t{countdown.__closure__}")
    print(f"函数代码\t{countdown.__code__}")
    print(f"函数默认值\t{countdown.__defaults__}")
    print(f"函数字典\t{countdown.__dict__}")
    print(f"函数内涵全集\t{countdown.__dir__()}")
    print('Done.完毕。')
