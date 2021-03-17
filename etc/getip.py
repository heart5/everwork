#!PREFIX/bin/python
# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       jupytext_version: 1.10.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

"""
获取ip地址
"""
import socket

def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        sn = s.getsockname()
        # print(sn)
        ip = sn[0]
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    print(get_host_ip())
