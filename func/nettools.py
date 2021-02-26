# encoding:utf-8
"""
网络相关函数集
"""
import sys
import ssl
import socket
import time
import random
import platform
import os
import re
import traceback
import itchat
# from requests.packages.urllib3 import HTTPConnectionPool
from evernote.edam.error.ttypes import EDAMSystemException
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import *
import requests
from bs4 import BeautifulSoup
import struct
from functools import wraps
from py2ifttt import IFTTT

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.termuxtools import termux_sms_send
    from func.sysfunc import not_IPython


def isitchat(pklabpath):
    """
    判断itchat是否已经运行，没有则热启动之。
    如果成功则返回True，否则直接退出运行。
    """

    inputpklpath = os.path.abspath(pklabpath)
#     print(inputpklpath)

    if itchat.originInstance.alive:
        # 转换成绝对路径方便对比

        loginpklpath = os.path.abspath(itchat.originInstance.hotReloadDir)
        if inputpklpath == loginpklpath:
            log.info(f"微信处于正常登录状态，pkl路径为：\t{loginpklpath}……")
        else:
            logstr = f"当前登录的pkl路径为{loginpklpath}，不同于传入的参数路径：\t{inputpklpath}"
            log.critical(logstr)
            sys.exit(1)
    else:
        itchat.auto_login(hotReload=True, statusStorageDir=pklabpath)   #热启动你的微信
        if not itchat.originInstance.alive:
            log.critical("微信未能热启动，仍处于未登陆状态，退出！")
            sys.exit(1)
        else:
            loginpklpath = os.path.abspath(itchat.originInstance.hotReloadDir)
            logstr = f"微信热启动成功\t{loginpklpath}"
            log.info(logstr)

    return True


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
        if ipfind is not None:
            if re.search(r'0\.0\.0\.0', ipfind.group()) is None:
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
    print(args)
    resultiplst = []
    if platform.system() == 'Windows':
        ip = get_host_ip()
        return [['wlan', ip]]
    else:

        # ethinfo = os.popen("ifconfig -a | grep -A 0 'Link encap'").read()
        ethinfo = os.popen("ifconfig -a | grep -A 0 'flags'").read()
        ptn = re.compile(r"^(?P<name>\w+)\W+", re.M)
        ethlst = re.findall(ptn, ethinfo)
        print(ethlst)
        ethlst2test = [x for x in ethlst if x != "lo"]
        for ethitem in ethlst2test:
            my_addr = os.popen(
                "ifconfig | grep -A 1 %s|tail -1| awk '{print $2}'" % ethitem).read()
            print(my_addr)
            ipfind = re.search(r'(?<![\.\d])(?:25[0-5]\.|2[0-4]\d\.|[01]?\d\d?\.)'
                               r'{3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?![\.\d])', my_addr)
            #  print(ipfind)
            ip = None
            if ipfind is not None:
                if re.match(r'0\.0\.0\.0', ipfind.group()) is None:
                    ip = ipfind.group()
                    resultiplst.append([ethitem, ip])
            #  print(ip)
    #  print(resultiplst)
    return resultiplst


def trycounttimes2(servname='服务器', maxtimes=100, maxsecs=50):
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
                except (requests.exceptions.ConnectionError,
                        ConnectionRefusedError, ConnectionResetError,
                        ConnectionAbortedError, NewConnectionError,
                        ConnectionError, MaxRetryError,
                        struct.error, socket.gaierror,
                        ssl.SSLError, EDAMSystemException,
                        OSError, IndexError, Exception, ValueError
                ) as eee:

                    # 通过sys函数获取eee的相关信息
                    eee_type, eee_value, eee_traceback = sys.exec_info()
                    # 5的倍数次尝试输出log，避免网络不佳时的log冗余
                    if i % showfreq == 0:
                        # 如果eee包含错误代码，尽量显示详细信息方便深入了解、统计、分析、诊断
                        if hasattr(eee, 'errno'):
                            eeestr = f"{eee}\t{traceback.extract_stack()}"
                            if eee.errno == 11001:
                                log.critical(f'寻址失败，貌似网络不通。{eeestr}')
                            elif eee.errno == 10061:
                                log.critical(f'被主动拒绝，好没面啊！{eeestr}')
                            elif eee.errno == 10060:
                                log.critical(f'够不着啊，是不是在墙外？！{eeestr}')
                            elif eee.errno == 10048:
                                log.critical(f'多次强行连接，被拒了！{eeestr}')
                            elif eee.errno == 10054:
                                log.critical(f'主机发脾气，强行断线了。{eeestr}')
                            elif eee.errno == 8:
                                log.critical(f'和{servname}握手失败。{eeestr}')
                            elif eee.errno == 7:
                                log.critical(f'和{servname}连接失败。域名无法解析，断网了  。{eeestr}')
                                # 断网特殊，二十倍延时等网回来～_～
                                sleeptime *= 20
                            elif eee.errno == 4:
                                log.critical(f'和{servname}连接异常，被中断。{eeestr}')
                            elif eee.errno == 13:
                                log.critical(f'连接{servname}的权限不够哦。{eeestr}')
                            else:
                                log.critical(f'连接失败。{eee.errno}\t{eeestr}')
                        else:
                            log.critical(f'连接失败。{eee}\t{args}\t{kwargs}')
                        log.critical(
                            f"第{i}次（最多尝试{trytimes}次）连接“{servname}”时失败，将于{sleeptime}秒后重试。")
                    # 跑够次数，日志记录，通知，抛出给上级处理
                    if i == (trytimes - 1):
                        badnews = f'{__file__}\"{servname}\"连接尝试了{trytimes}次后仍然失败，只好无功而返。\t{" ".join(sys.argv)}\t{eee}'
                        # badnews = f'{sys._getframe().f_code.co_name}\t{sys._getframe().f_code.co__filename}\t\"{
                        # servname}\"连接尝试了{trytimes}次后仍然失败，只好无功而返。\t{" ".join(sys.argv)}'
                        log.critical(badnews)
                        termux_sms_send(badnews)
                        # exit(1)
                        raise eee
                    # 暂歇开始前终端输出，看看而已
                    print(f"&&&\t{sleeptime}\t&&& in (tct2), type is {eee_type}")
                    time.sleep(sleeptime)

        return wrapper

    return decorate


@trycounttimes2("ifttt服务器")
def ifttt_notify(content="content", funcname="funcname"):
    ifttt = IFTTT('0sa6Pl_UJ9a_w6UQlYuDJ', 'everwork')
    pu = platform.uname()
    ifttt.notify(f'{pu.machine}_{pu.node}', content, funcname)
    log.critical(f'{pu.machine}_{pu.node}\t{content}\t{funcname}')


def tst4trycounttimes2():
    if not_IPython():
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
    if not_IPython():
        log.info(f'测试文件\t{__file__}……')

    # print(get_ip4alleth('wlan0'))
#     pklpath = getdirmain() / 'itchat.pkl'
#     print(pklpath)
#     isitchat(pklpath)
    print(get_ip4alleth())
#     print(get_host_ip())
#     tst4trycounttimes2()
    if not_IPython():
        log.info(f'文件\t{__file__}\t测试完毕。')
