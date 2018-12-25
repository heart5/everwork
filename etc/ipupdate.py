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
    from func.nettools import get_host_ip, get_ip
    from func.evernt import get_notestore, imglist2note
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone


output = subprocess.check_output('termux-telephony-deviceinfo',
                                 shell=True).decode('utf-8').replace('false',
                                                                     'False').replace('true',
                                                                                      'True')
print(type(output))
print(output)
outputdict = eval(output)
print(outputdict)
device_id = outputdict["device_id"]
print(device_id)


if __name__ == '__main__':
    # global log
    print(f'运行文件\t{__file__}')
    print(get_ip('wlan0'))
    print('Done.')
