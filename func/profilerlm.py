# encoding:utf-8
"""
装饰器函数集，ift2phone、timethis, logit
"""
import time
import platform
import wrapt
from functools import wraps
from inspect import signature
from py2ifttt import IFTTT
from line_profiler import LineProfiler as lpt
# from memory_profiler import LineProfiler as lpm, show_results as lpm_show

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.wrapfuncs import countdown
    from func.nettools import trycounttimes2, ifttt_notify
    from func.evernttest import getinivaluefromnote


lptt = lpt()


def lpt_wrapper():
    """
    显示函数调用时间（逐行）
    """
    @wrapt.decorator
    def wrapper(func, instance, args, kwargs):
        global lptt
        print(instance)
        lp_wrapper = lptt(func)
        res = lp_wrapper(*args, **kwargs)
        lptt.print_stats()
        return res

    return wrapper


# lpmm = lpm()


# def lpm_wrapper():
    # """
    # 显示函数内存消耗（逐行）
    # """
    # @wrapt.decorator
    # def wrapper(func, instance, args, kwargs):
        # global lpmm
        # print(instance)
        # lp_wrapper = lpmm(func)
        # res = lp_wrapper(*args, **kwargs)
        # lpm_show(lpmm)
        # return res

    # return wrapper


@lpt_wrapper()
def countdwontest():
    countdown(10901)


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    countdwontest()
    log.info(f"文件\t{__file__}\t结束运行")
