# encoding:utf-8
"""
功能描述
"""
import time
from functools import wraps
from func.logme import log


def timethis(func):
    '''
    装饰执行时间（tida）
    :param func:
    :return:
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper


@timethis
def countdown(n):
    while n > 0:
        n -= 1


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    countdown(10008888)
    countdown(1122343535)
    print('Done.完毕。')
