# encoding:utf-8
"""
操作系统相关的函数集
"""

import os
import sys
import platform
import uuid
# import wmi_client_wrapper as wmi

import pathmagic
with pathmagic.context():
    from func.logme import log


def uuid3hexstr(inputo: object):
    inputstr = str(inputo)

    return hex(hash(uuid.uuid3(uuid.NAMESPACE_URL, inputstr)))[2:].upper()


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
    log.info(f'文件\t{__file__}\t测试完毕。')
