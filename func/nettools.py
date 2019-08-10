# encoding:utf-8
"""
功能描述
"""
import sys
import ssl
import socket
import time
import random
import platform
import os
import re
# from requests.packages.urllib3 import HTTPConnectionPool
from evernote.edam.error.ttypes import EDAMSystemException
from requests.packages.urllib3.exceptions import NewConnectionError
import requests
from bs4 import BeautifulSoup
import struct
from functools import wraps
from py2ifttt import IFTTT

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.termuxtools import termux_sms_send
    # from func.evernttest import getinivaluefromnote


def get_ip(*args):
    if platform.system() == 'Windows':
        my_name = socket.getfqdn(socket.gethostbyname('localhost'))
        print(my_name)
        my_addr = socket.gethostbyname(my_name)
        print(my_addr)
        ip = my_addr.split('\n')[0]
        return ip
    else:

        my_addr = os.popen(
            "ifconfig | grep -A 1 %s|tail -1| awk '{print $2}'" % args[0]).read()
        print(my_addr)
        ipfind = re.search(r'(?<![\.\d])(?:25[0-5]\.|2[0-4]\d\.|[01]?\d\d?\.)'
                           r'{3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?![\.\d])', my_addr)
        print(ipfind)
        ip = None
        if (ipfind != None):
            if re.search(r'0\.0\.0\.0', ipfind.group()) == None:
                ip = ipfind.group()
        print(ip)
        return ip


def get_host_ip():
    """
    在windows下查询本机ip地址,对多个网卡可以得到wlan0那个,亲测有效
    :return: ip
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        sn = s.getsockname()
        # print(sn)
        ip = sn[0]
    finally:
        s.close()
    return ip


def get_ip4alleth(*args):
    resultiplst = []
    if platform.system() == 'Windows':
        ip = get_host_ip()
        return [['wlan', ip]]
    else:

        # ethinfo = os.popen("ifconfig -a | grep -A 0 'Link encap'").read()
        ethinfo = os.popen("ifconfig -a | grep -A 0 'flags'").read()
        ptn = re.compile(r"^(?P<name>\w+)\W+", re.M)
        ethlst = re.findall(ptn, ethinfo)
        # print(ethlst)
        ethlst2test = [x for x in ethlst if x != "lo"]
        for ethitem in ethlst2test:
            my_addr = os.popen(
                "ifconfig | grep -A 1 %s|tail -1| awk '{print $2}'" % ethitem).read()
            # print(my_addr)
            ipfind = re.search(r'(?<![\.\d])(?:25[0-5]\.|2[0-4]\d\.|[01]?\d\d?\.)'
                               r'{3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?![\.\d])', my_addr)
            #  print(ipfind)
            ip = None
            if ipfind is not None:
                if re.match(r'0\.0\.0\.0', ipfind.group()) == None:
                    ip = ipfind.group()
                    resultiplst.append([ethitem, ip])
            #  print(ip)
    #  print(resultiplst)
    return resultiplst


def trycounttimes(jutifunc, inputparam='', returnresult=False, servname='服务器'):
    trytimes = 3
    sleeptime = 15
    for i in range(trytimes):
        try:
            if returnresult:
                if len(inputparam) == 0:
                    result = jutifunc()
                else:
                    result = jutifunc(inputparam)
                return result
            else:
                if len(inputparam) == 0:
                    jutifunc()
                else:
                    jutifunc(inputparam)
            break
        except (OSError, ConnectionRefusedError, ConnectionResetError, ConnectionError, struct.error) as eee:
            if hasattr(eee, 'errno'):
                if eee.errno == 11001:
                    log.critical(f'寻址失败，貌似网络不通。{eee}')
                elif eee.errno == 10061:
                    log.critical(f'被主动拒绝，好没面啊！{eee}')
                elif eee.errno == 10060:
                    log.critical(f'够不着啊，是不是在墙外？！{eee}')
                elif eee.errno == 10048:
                    log.critical(f'多次强行连接，被拒了！{eee}')
                elif eee.errno == 10054:
                    log.critical(f'主机发脾气，强行断线了。{eee}')
                elif eee.errno == 8:
                    log.critical(f'和evernote服务器握手失败。{eee}')
                else:
                    log.critical(f'连接失败。{eee.errno}\t{eee}')
            else:
                log.critical(f'连接失败。{eee}')
            log.critical(
                f"第{i+1}次（最多尝试{trytimes}次）连接“{servname}”时失败，将于{sleeptime}秒后重试。")
            # log.critical(f'{eee.args}\t{eee.errno}\t{eee.filename}\t{eee.filename2}\t{eee.strerror}\t{eee.winerror}')
            if i == (trytimes - 1):
                log.critical(f'“{servname}”连接失败，只好无功而返。')
                # raise eee
            time.sleep(sleeptime)


def trycounttimes2(servname='服务器', maxtimes=20, maxsecs=30):
    def decorate(jutifunc):

        @wraps(jutifunc)
        def wrapper(*args, **kwargs):
            trytimes = maxtimes
            # showfreq = getinivaluefromnote('everlog', 'showfreq')
            showfreq = 5
            for i in range(1, trytimes + 1):
                sleeptime = random.randint(2, maxsecs)
                try:
                    result = jutifunc(*args, **kwargs)
                    return result
                except (
                        ConnectionRefusedError, ConnectionResetError,
                        ConnectionAbortedError, NewConnectionError,
                        ConnectionError,
                        struct.error,socket.gaierror,
                        ssl.SSLError, EDAMSystemException,
                        OSError, IndexError, Exception
                ) as eee:

                    # 5的倍数次尝试输出log，避免网络不佳时的log冗余
                    if i % showfreq == 0:
                        if hasattr(eee, 'errno'):
                            if eee.errno == 11001:
                                log.critical(f'寻址失败，貌似网络不通。{eee}')
                            elif eee.errno == 10061:
                                log.warning(f'被主动拒绝，好没面啊！{eee}')
                            elif eee.errno == 10060:
                                log.warning(f'够不着啊，是不是在墙外？！{eee}')
                            elif eee.errno == 10048:
                                log.warning(f'多次强行连接，被拒了！{eee}')
                            elif eee.errno == 10054:
                                log.warning(f'主机发脾气，强行断线了。{eee}')
                            elif eee.errno == 8:
                                log.warning(f'和{servname}握手失败。{eee}')
                            elif eee.errno == 4:
                                log.warning(f'和{servname}连接异常，被中断。{eee}')
                            else:
                                log.warning(f'连接失败。{eee.errno}\t{eee}')
                        else:
                            log.critical(f'连接失败。{eee}')
                        log.critical(
                            f"第{i}次（最多尝试{trytimes}次）连接“{servname}”时失败，将于{sleeptime}秒后重试。")
                    # log.critical(f"第{i+1}次（最多尝试{trytimes}次）连接服务器时失败，将于{sleeptime}秒后重试。")
                    # log.critical(f'{eee.args}\t{eee.errno}\t{eee.filename}\t{eee.filename2}\t{eee.strerror}\t{eee.winerror}')
                    if i == (trytimes - 1):
                        badnews = f'{__file__}\"{servname}\"连接尝试了{trytimes}次后仍然失败，只好无功而返。\t{" ".join(sys.argv)}\t{eee}'
                        # badnews = f'{sys._getframe().f_code.co_name}\t{sys._getframe().f_code.co__filename}\t\"{servname}\"连接尝试了{trytimes}次后仍然失败，只好无功而返。\t{" ".join(sys.argv)}'
                        log.critical(badnews)
                        termux_sms_send(badnews)
                        # exit(1)
                        raise eee
                    time.sleep(sleeptime)

        return wrapper

    return decorate


@trycounttimes2("ifttt服务器")
def ifttt_notify(content="content", funcname="funcname"):
    ifttt = IFTTT('0sa6Pl_UJ9a_w6UQlYuDJ', 'everwork')
    pu = platform.uname()
    ifttt.notify(f'{pu.machine}_{pu.node}', content, funcname)
    log.info(f'{pu.machine}_{pu.node}\t{content}\t{funcname}')


def tst4trycounttimes2():
    ifttt_notify("test for ifttt notify", f"{__file__}")

    @trycounttimes2('xmu.edu.cn网站服务器')
    def fetchfromnet(addressin: object):
        """
        从网址获取内容
        :param addressin: 网址
        :return: 页面内容html
        """
        r = requests.get(addressin)
        html = r.content
        return html

    # html2 = trycounttimes2(fetchfromnet, '', True, 'xmu.edu.cn网站服务器')
    address = 'http://www.wise.xmu1.edu.cn/people/faculty'
    print(fetchfromnet.__doc__)
    html2 = fetchfromnet(address)
    if html2 is None:
        exit(5)
    soup = BeautifulSoup(html2, 'html.parser')  # html.parser是解析器
    div_people_list = soup.find('div', attrs={'class': 'people_list'})
    a_s = div_people_list.find_all('a', attrs={'target': '_blank'})
    for a in a_s:
        url = a['href']
        name = a.get_text()
        print(f'{name},{url}')


if __name__ == '__main__':
    log.info(f'测试文件\t{__file__}')

    # print(get_ip4alleth('wlan0'))
    print(get_ip4alleth())
    # print(get_host_ip())
    # tst4trycounttimes2()

    print('Done.测试完毕。')
