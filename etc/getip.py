#!PREFIX//bin/python

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
