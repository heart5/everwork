#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
获取服务器ip并定期更新至相关笔记
"""

import os
import sys
import datetime
import platform
# import urllib2
import evernote.edam.type.ttypes as ttypes
import pathmagic

with pathmagic.context():
    from func.first import dirmainpath
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.nettools import get_ip4alleth
    from func.datatools import readfromtxt, write2txt
    from func.evernttest import get_notestore, imglist2note, makenote
    from func.evernttest import evernoteapijiayi, readinifromnote
    from func.logme import log
    from func.termuxtools import termux_wifi_connectioninfo
    from etc.getid import getdeviceid


def iprecord():
    """
    获取本机ip
    """
    device_id = getdeviceid()
    ip = wifi = wifiid = tun = None
    ethlst = get_ip4alleth()
    print(ethlst)
    if platform.system() == 'Windows':
        ip = ethlst[0][1]
        cmd = 'netsh wlan show interfaces'
        rrr = os.popen(cmd)
        rrrinfo = rrr.readlines()
        print(rrrinfo)
        for line in rrrinfo:
            if line.find('BSSID') >= 0:
                wifi = line.split(':', 1)[1].strip()
                continue
            if line.find('SSID') >= 0:
                wifiid = line.split(':', 1)[1].strip()
                continue
        return ip, wifi, wifiid, tun, device_id
    for ethinfo in ethlst:
        name, ipinner = ethinfo
        if name.startswith('tun'):
            tun = ipinner
            continue
        if name.startswith('wlan'):
            wifiinfo = termux_wifi_connectioninfo()
            print(wifiinfo)
            wifi = wifiinfo['ssid']
            if wifi.find('unknown ssid') >= 0:
                logstr = f'WIFI处于假连状态：{wifi}\t{ipinner}'
                log.warning(logstr)
                wifi = None
                continue
            wifiid = wifiinfo['bssid']
        ip = ipinner

    return ip, wifi, wifiid, tun, device_id


def evalnone(input1):
    """
    转换从终端接收数据的数据类型
    """
    if input1 == 'None':
        return eval(input1)
    return input1


def showiprecords():
    """
    综合输出ip记录
    """
    namestr = 'everip'
    ip, wifi, wifiid, tun, device_id = iprecord()
    if ip is None:
        logstr = '无效ip，可能是没有处于联网状态'
        log.critical(logstr)
        sys.exit(1)
    print(f'{ip}\t{wifi}\t{wifiid}\t{tun}\t{device_id}')
    if not (guid := getcfpoptionvalue(namestr, device_id, 'guid')):
        token = getcfpoptionvalue('everwork', 'evernote', 'token')
        note_store = get_notestore()
        parentnotebook = note_store.getNotebook(
            '4524187f-c131-4d7d-b6cc-a1af20474a7f')
        evernoteapijiayi()
        note = ttypes.Note()
        note.title = f'服务器_{device_id}_ip更新记录'
        # note.title = "hengchu"
        print(note.title)
        note = makenote(token, note_store, note.title, notebody='',
                        parentnotebook=parentnotebook)
        guid = note.guid
        setcfpoptionvalue(namestr, device_id, 'guid', guid)
    if getcfpoptionvalue(namestr, device_id, 'ipr'):
        ipr = evalnone(getcfpoptionvalue(namestr, device_id, 'ipr'))
        wifir = evalnone(getcfpoptionvalue(namestr, device_id, 'wifir'))
        wifiidr = evalnone(getcfpoptionvalue(namestr, device_id, 'wifiidr'))
        tunr = evalnone(getcfpoptionvalue(namestr, device_id, 'tunr'))
        startr = getcfpoptionvalue(namestr, device_id, 'start')
    else:
        setcfpoptionvalue(namestr, device_id, 'ipr', ip)
        ipr = ip
        setcfpoptionvalue(namestr, device_id, 'wifir', str(wifi))
        wifir = wifi
        setcfpoptionvalue(namestr, device_id, 'wifiidr', str(wifiid))
        wifiidr = wifiid
        setcfpoptionvalue(namestr, device_id, 'tunr', str(tun))
        tunr = tun
        start = datetime.datetime.now().strftime('%F %T')
        startr = start
        setcfpoptionvalue(namestr, device_id, 'start', start)

    if (ip != ipr) or (wifiid != wifiidr) or (wifi != wifir) or (tun != tunr):
        txtfilename = str(dirmainpath / 'data' / 'ifttt' /
                          f'ip_{device_id}.txt')
        print(txtfilename)
        nowstr = datetime.datetime.now().strftime('%F %T')
        itemread = readfromtxt(txtfilename)
        itemclean = [x for x in itemread if 'unknown' not in x]
        itempolluted = [x for x in itemread if 'unknown' in x]
        logstr = f"不合法记录列表：\t{itempolluted}"
        log.info(logstr)
        itemnewr = [
            f'{ipr}\t{wifir}\t{wifiidr}\t{tunr}\t{startr}\t{nowstr}']
        itemnewr.extend(itemclean)
#         print(itemnewr)
        write2txt(txtfilename, itemnewr)
        itemnew = [
            f'{ip}\t{wifi}\t{wifiid}\t{tun}\t{nowstr}']
        itemnew.extend(itemnewr)
#         print(itemnew)
        readinifromnote()
        device_name = getcfpoptionvalue('everinifromnote', 'device', device_id)
        if not device_name:
            device_name = device_id
        setcfpoptionvalue(namestr, device_id, 'ipr', ip)
        setcfpoptionvalue(namestr, device_id, 'wifir', str(wifi))
        setcfpoptionvalue(namestr, device_id, 'wifiidr', str(wifiid))
        setcfpoptionvalue(namestr, device_id, 'tunr', str(tun))
        start = datetime.datetime.now().strftime('%F %T')
        setcfpoptionvalue(namestr, device_id, 'start', start)
        # 把笔记输出放到最后，避免更新不成功退出影响数据逻辑
        imglist2note(get_notestore(), [], guid,
                     f'服务器_{device_name}_ip更新记录', "<pre>"
                     + "\n".join(itemnew) + "</pre>")


if __name__ == '__main__':
    logstr2 = f'开始运行文件\t{__file__}\t{sys._getframe().f_code.co_name}\t{sys._getframe().f_code.co_filename}'
    log.info(logstr2)
    showiprecords()
    # print(f"{self.__class__.__name__}")
    logstr1 = f'文件\t{__file__}\t执行完毕'
    log.info(logstr1)
