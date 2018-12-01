# -*- coding: utf-8 -*-
import requests
"""
获取服务器ip并定期更新至相关笔记
"""

import os
import subprocess
import socket
# import urllib2
import re
from threading import Timer
import pathmagic

with pathmagic.context():
    from func.first import getdirmain
    from func.nettools import get_host_ip
    from func.evernt import get_notestore, imglist2note
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone


# 查看当前主机名
# print('当前主机名称为 : ' + socket.gethostname())

# 根据主机名称获取当前IP
# print('当前主机的IP为: ' + socket.gethostbyname(socket.gethostname()))


# Mac下上述方法均返回127.0.0.1
# 通过使用socket中的getaddrinfo中的函数获取真真的IP

# 下方代码为获取当前主机IPV4 和IPV6的所有IP地址(所有系统均通用)
# addrs = socket.getaddrinfo(socket.gethostname(), None)

# for item in addrs:
# print(item)

# 仅获取当前IPV4地址
# print('当前主机IPV4地址为:' + [item[4][0]
# for item in addrs if ':' not in item[4][0]][0])

# 同上仅获取当前IPV4地址
# for item in addrs:
# if ':' not in item[4][0]:
# print('当前主机IPV4地址为:' + item[4][0])
# # break

output = subprocess.check_output('termux-telephony-deviceinfo',
                                 shell=True).decode('utf-8').replace('false',
                                                                     'False')
# print(type(output))
# print(output)
outputdict = eval(output)
print(outputdict)
device_id = outputdict["device_id"]
print(device_id)


if __name__ == '__main__':
    # global log
    print(f'运行文件\t{__file__}')
    print(get_host_ip())
    print('Done.')
