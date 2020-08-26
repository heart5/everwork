# encoding:utf-8
"""
操作系统相关的函数集
"""

import os
import traceback
import inspect
import sys
import platform
import signal
import time
import uuid
import re
from hashlib import sha256
# import wmi_client_wrapper as wmi

import pathmagic
with pathmagic.context():
    from func.logme import log

    
def convertframe2dic(frame):
    framestr = str(frame)
    filename = re.findall("filename=(.+)\s", framestr)[0].strip()
    lineno = re.findall("lineno=(.+)\s", framestr)[0].strip()
    code_context = [line.strip() for line in eval(re.findall("code_context=(.+)\s", framestr)[0].strip())]
    
    return filename, lineno, code_context


def set_timeout(num, callback):
    
    def wrap(func):
        def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                if (sysstr := platform.system()) == "Linux":
                    print(sysstr)
                    signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                    signal.alarm(num)  # 设置 num 秒的闹钟
                    print('start alarm signal.')
                    r = func(*args, **kwargs)
                    print('close alarm signal.')
                    signal.alarm(0)  # 关闭闹钟
                    return r
                else:
                    r = func(*args, **kwargs)
                    logstr = f"{sysstr}\t非linux系统，啥也没做。"
                    log.warning(logstr)
                    return r
                    
            except RuntimeError as e:
                callback()

        return to_do
 
    return wrap


def after_timeout():  
    """
    超时后的处理函数
    """
#     log.critical(sys._getframe().f_code.co_name)
#     log.critical(sys._getframe().f_back.f_lineno)
#     log.critical(sys._getframe().f_code.co_filename)
#     log.critical(traceback.extract_stack()[-2][2])
    log.critical(traceback.extract_stack())
#     log.critical(inspect.stack())
    log.critical("运行超出预设时间，退出!")
    
    
def uuid3hexstr(inputo: object):
    inputstr = str(inputo)

    return hex(hash(uuid.uuid3(uuid.NAMESPACE_URL, inputstr)))[2:].upper()


def sha2hexstr(inputo: object):
    if type(inputo) == bytes:
        targetb = inputo
    else:
        targetb = str(inputo).encode('utf-8')
    hhh = sha256(targetb)

    return hhh.hexdigest().upper()


def execcmd(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    outgetstr = execcmd("uname -a")
    print(outgetstr.strip("\n"))
    print(uuid3hexstr(outgetstr))
    print(sha2hexstr(outgetstr))
    log.info(f'文件\t{__file__}\t测试完毕。')
