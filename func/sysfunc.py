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
from IPython import get_ipython
from hashlib import sha256
# import wmi_client_wrapper as wmi

import pathmagic
with pathmagic.context():
    from func.logme import log


def extract_traceback4exception(tbtuple, func_name, alltraceback=False):
    """
    格式化指定异常的详细信息（tuple）并返回（字符串），默认只返回堆栈的首位各两个元素，除非显性指定显示全部
    """
    # 通sys函数获取eee的相关信息
    eee_type, eee_value, tblst, sleeptime = tbtuple
    if not alltraceback:
        brieftb = [x for x in tblst[:2]]
        brieftb.append('\t...\t')
        brieftb.extend([x for x in tblst[-2:]])
    else:
        brieftb = tblst
    rststr = f"&&&\t{sleeptime}\t&&& in (func_name),\t"
    rststr += "type is\t[ {eee_type}]\t, value is \t[{eee_value}],\t"
    rststr += "traceback is \t{brieftb}"

    return rststr


def not_IPython():
    """
    判断是否在IPython环境下运行
    """
    return get_ipython() is None


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
    log.critical(("运行超出预设时间，强制退出!", traceback.extract_stack()))


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
    if not_IPython():
        log.info(f'运行文件\t{__file__}……')
    outgetstr = execcmd("uname -a")
    print(outgetstr.strip("\n"))
    print(uuid3hexstr(outgetstr))
    print(sha2hexstr(outgetstr))
    if not_IPython():
        log.info(f'文件\t{__file__}\t测试完毕。')
