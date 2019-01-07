# -*- coding: utf-8 -*-
"""
获取服务器ip并定期更新至相关笔记
"""

import os
import datetime
import subprocess
import socket
import requests
# import urllib2
import re
from threading import Timer
import pathmagic
import evernote.edam.type.ttypes as ttypes

with pathmagic.context():
    from func.first import getdirmain, dirmainpath
    from func.configpr import getcfp
    from func.nettools import get_host_ip, get_ip
    from func.datatools import readfromtxt, write2txt
    from func.evernt import get_notestore, imglist2note, timestamp2str, makenote, token, evernoteapijiayi
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.termuxtools import termux_telephony_deviceinfo, termux_telephony_cellinfo, termux_wifi_connectioninfo, termux_wifi_scaninfo


def iprecord():
    outputdict = termux_telephony_deviceinfo()
    # print(outputdict)
    device_id = outputdict["device_id"].strip()
    # wifilist = termux_wifi_scaninfo()
    # for wifi in wifilist:
    # print(
    # f"WIFI名称：{wifi['ssid']}\ttimestamp:{wifi['timestamp']}\t连接时间：{timestamp2str(wifi['timestamp']/10)}")
    wifiinfo = termux_wifi_connectioninfo()
    if wifiinfo['bssid'] != None:
        ip = wifiinfo['ip']
        wifi = wifiinfo['ssid']
        wifiid = wifiinfo['bssid']
    else:
        ip = get_ip('rmnet_data0')
        if ip is None:
            ip = get_ip('rmnet_data1')
        if ip is None:
            ip = get_ip('rmnet0')
        if ip is None:
            ip = "None"

        wifi = "None"
        wifiid = "None"
    tun = get_ip('tun0')
    if tun is None:
        tun = 'None'
    return ip, wifi, wifiid, tun, device_id


def showiprecords():
    namestr = 'everip'
    cfp, cfppath = getcfp(namestr)
    ip, wifi, wifiid, tun, device_id = iprecord()
    print(f'{ip}\t{wifi}\t{wifiid}\t{tun}\t{device_id}')
    if not cfp.has_section(device_id):
        cfp.add_section(device_id)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))
    if cfp.has_option(device_id, 'guid'):
        guid = cfp.get(device_id, 'guid')
    else:
        global token
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
        cfp.set(device_id, 'guid', guid)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))
    if cfp.has_option(device_id, 'ipr'):
        ipr = cfp.get(device_id, 'ipr')
        wifir = cfp.get(device_id, 'wifir')
        wifiidr = cfp.get(device_id, 'wifiidr')
        tunr = cfp.get(device_id, 'tunr')
        startr = cfp.get(device_id, 'start')
    else:
        cfp.set(device_id, 'ipr', ip)
        ipr = ip
        cfp.set(device_id, 'wifir', wifi)
        wifir = wifi
        cfp.set(device_id, 'wifiidr', wifiid)
        wifiir = wifiid
        cfp.set(device_id, 'tunr', tun)
        tunr = tun
        start = datetime.datetime.now().strftime('%F %T')
        startr = start
        cfp.set(device_id, 'start', start)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))

    if ip != ipr:
        txtfilename = str(dirmainpath / 'data' / 'ifttt' /
                          f'ip_{device_id}.txt')
        print(txtfilename)
        nowstr = datetime.datetime.now().strftime('%F %T')
        itemread = readfromtxt(txtfilename)
        print(itemread)
        itemnewr = [
            f'{ipr}\t{wifir}\t{wifiidr}\t{tunr}\t{startr}\t{nowstr}']
        itemnewr.extend(itemread)
        print(itemnewr)
        write2txt(txtfilename, itemnewr)
        itemnew = [
            f'{ip}\t{wifi}\t{wifiid}\t{tun}\t{nowstr}']
        itemnew.extend(itemnewr)
        print(itemnew)
        imglist2note(get_notestore(), [], guid,
                     f'服务器_{device_id}_ip更新记录', "<br></br>".join(itemnew))
        cfp.set(device_id, 'ipr', ip)
        cfp.set(device_id, 'wifir', wifi)
        cfp.set(device_id, 'wifiidr', wifiid)
        cfp.set(device_id, 'tunr', tun)
        start = datetime.datetime.now().strftime('%F %T')
        cfp.set(device_id, 'start', start)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))


if __name__ == '__main__':
    # global log
    print(f'运行文件\t{__file__}')
    showiprecords()
    print('Done.')
