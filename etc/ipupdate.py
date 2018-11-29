# -*- coding: utf-8 -*-
"""
获取服务器ip并定期更新至相关笔记
"""

import os
from threading import Timer
import pathmagic

with pathmagic.context():
    from func.first import getdirmain
    from func.nettools import get_host_ip
    from func.evernt import get_notestore, imglist2note
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone


if __name__ == '__main__':
    # global log
    print(f'运行文件\t{__file__}')
    print(get_host_ip())
    print('Done.')
