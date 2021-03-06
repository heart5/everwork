#! /data/data/com.termux/files/usr/bin/python
# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.10.3
# ---

# %%
"""
获取服务器ip并定期更新至相关笔记
"""

# %%
import os
import sys
import datetime
import platform
import re
import pathmagic

# %%
with pathmagic.context():
    from func.first import getdirmain, dirmainpath
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.nettools import get_host_ip, get_ip, get_ip4alleth
    from func.datatools import readfromtxt, write2txt
    from func.evernttest import get_notestore, gettoken, imglist2note, timestamp2str, makenote2, evernoteapijiayi, readinifromnote
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.termuxtools import termux_wifi_connectioninfo, battery_status
    from etc.getid import getdeviceid
    from func.sysfunc import set_timeout, after_timeout, not_IPython


# %%
@set_timeout(240, after_timeout)
@timethis
def iprecord():
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
                log.warning(f'WIFI处于假连状态：{wifi}\t{ipinner}')
                wifi = None
                continue
            wifiid = wifiinfo['bssid']
        ip = ipinner

    return ip, wifi, wifiid, tun, device_id


# %%
def evalnone(input):
    if input == 'None':
        return eval(input)
    else:
        return input


# %%
def showiprecords():
    namestr = 'everip'
    ip, wifi, wifiid, tun, device_id = iprecord()
    if ip is None:
        log.critical('无效ip，可能是没有处于联网状态')
        exit(1)
    print(f'{ip}\t{wifi}\t{wifiid}\t{tun}\t{device_id}')
    if not (guid := getcfpoptionvalue(namestr, device_id, 'guid')):
        parentnotebookguid = '4524187f-c131-4d7d-b6cc-a1af20474a7f'
        note_title = f'服务器_{device_id}_ip更新记录'
        # note.title = "hengchu"
        print(note_title)
        note = makenote2(note_title, notebody='',
                        parentnotebook=parentnotebookguid)
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
        log.info(f"不合法记录列表：\t{itempolluted}")
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
                     f'服务器_{device_name}_ip更新记录', "<pre>" + "\n".join(itemnew) + "</pre>")


# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(
            f'开始运行文件\t{__file__}\t……\t{sys._getframe().f_code.co_name}\t{sys._getframe().f_code.co_filename}')
    if (bsdict := battery_status())['percentage'] >= 20:
        showiprecords()
    else:
        log.warning("手机电量低于20%，跳过ip轮询")
    # print(f"{self.__class__.__name__}")
    if not_IPython():
        log.info(f'文件\t{__file__}\t执行完毕')
