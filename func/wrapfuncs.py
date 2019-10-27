# encoding:utf-8
"""
装饰器函数集，ift2phone、timethis, logit
"""


import time
from functools import wraps
from inspect import signature

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.nettools import ifttt_notify
    from func.evernttest import getinivaluefromnote


def logit(func):
    """
    函数具体调用信息写入日志或print至控制台
    :param func
    :return
    """
    @wraps(func)
    def with_logging(*args, **kwargs):
        if getinivaluefromnote('everwork', 'logdetails'):
            log.info(f'{func.__name__}函数被调用，参数列表：{args}')
        else:
            print(f'{func.__name__}函数被调用，参数列表：{args}')

        return func(*args, **kwargs)
    return with_logging


def ift2phone(msg=None):
    """
    目标函数运行时将信息通过ifttt发送至手机
    :param msg:
    :return:
    """
    def decorate(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if msg is None:
                msginner = func.__doc__
            else:
                msginner = msg
            ifttt_notify(f'{msginner}_{args}', f'{func.__name__}')
            return result

        return wrapper

    return decorate


def timethis(func):
    """
    装饰执行时间（tida）
    :param func:
    :return:
    """

    @logit
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        timelen = end - start
        if timelen >= (60 * 60):
            timelenstr = f'{int(timelen / (60 * 60))}小时{int((timelen % (60*60)) / 60)}分钟{timelen % (60*60) % 60:.2f}秒'
        elif timelen >= 60:
            timelenstr = f'{int(timelen / 60)}分钟{timelen % 60:.2f}秒'
        else:
            timelenstr = f'{timelen % 60:.2f}秒'
        if getinivaluefromnote('everwork', 'logdetails'):
            log.info(f"{func.__name__}\t{timelenstr}")
        else:
            print(f"{func.__name__}\t{timelenstr}")

        return result

    return wrapper


@timethis
# @ift2phone("倒数计时器")
@ift2phone()
# @lpt_wrapper()
def countdown(n: int):
    """
    倒计时
    :param n:
    :return: NULL
    """
    print(n)
    while n > 0:
        n -= 1
        if (n % 5000) == 0:
            print(n)


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    countdown(10088)
    print(f"函数名\t{countdown.__name__}")
    print(f"函数文档\t{countdown.__doc__}")
    print(f"函数参数注释\t{countdown.__annotations__}")
    # countdown(12234353)
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
    log.info(f"文件\t{__file__}\t结束运行")
