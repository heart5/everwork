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
    

# execute command, and return the output  
def execcmd(cmd):  
    r = os.popen(cmd)  
    text = r.read()  
    r.close()  
    return text  


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    outgetstr = execcmd("uname -a")
    print(outgetstr.strip("\n"))
    log.info(f'文件\t{__file__}\t测试完毕。')