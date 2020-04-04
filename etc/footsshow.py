"""
记录足迹
"""

import os
# import urllib2
import re
import socket
import subprocess
import datetime
from threading import Timer
from math import radians, cos, sin, asin, sqrt
import pandas as pd
import numpy as np
from pylab import *

import pathmagic
with pathmagic.context():
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.first import getdirmain, dirmainpath, touchfilepath2depth
    from func.datatools import readfromtxt, write2txt
    from func.evernttest import token, get_notestore, imglist2note, \
        evernoteapijiayi, makenote, readinifromnote, getinivaluefromnote
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.termuxtools import termux_telephony_deviceinfo, \
        termux_telephony_cellinfo, termux_location
    from etc.getid import getdeviceid


def geodistance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2) ** 2
    dis = 4 * asin(sqrt(a)) * 6371 * 1000
    return dis


@timethis
def foot2show():
    namestr = 'everloc'
    if (device_id := getcfpoptionvalue(namestr, namestr, 'device_id')):
        device_id = str(device_id)
    else:
        device_id = getdeviceid()
        setcfpoptionvalue(namestr, namestr, 'device_id', device_id)
        
    if (guid := getcfpoptionvalue(namestr, device_id, 'guid')):
        pass
    else:
        global token
        note_store = get_notestore()
        parentnotebook = note_store.getNotebook(
            '4524187f-c131-4d7d-b6cc-a1af20474a7f')
        evernoteapijiayi()
        # note = ttypes.Note()
        title = f'手机_{device_id}_location更新记录'
        # note.title = "hengchu"
        print(title)
        note = makenote(token, note_store, title, notebody='',
                        parentnotebook=parentnotebook)
        guid = note.guid
        setcfpoptionvalue(namestr, device_id, 'guid', guid)

    txtfilename = str(dirmainpath / 'data' / 'ifttt' /
                      f'location_{device_id}.txt')
    print(txtfilename)
    itemread = readfromtxt(txtfilename)
    numlimit = 9    # 显示项目数
    print(itemread[:numlimit])
    itemsrc = [x.split('\t') for x in itemread if not 'False' in x]
    itemnotfine = [x for x in itemsrc if len(x) < 3]
    print(f"有问题的数据共有{len(itemnotfine)}行：{itemnotfine}")
    itemfine = [x for x in itemsrc if len(x) >= 3]
    # print(itemfine)
    if len(itemfine) < 2:
        print('gps数据量不足，暂时无法输出移动距离信息')
        return
    timesr = list()
    dissr = list()
    # speedsr = list()
    highspeed = getinivaluefromnote('life', 'highspeed')
    print(f"{highspeed}\t{type(highspeed)}")
    for i in range(len(itemfine) - 1):
#        if len(itemfine[i+1]) < 3:
#            print(f"{itemfine[i]}")
#            print(f"{itemfine[i+1]}")
        time1, lng1, lat1, *others = itemfine[i]
        time2, lng2, lat2, *others = itemfine[i + 1]
        # print(f'{lng1}\t{lat1}\t\t{lng2}\t{lat2}')
        dis = round(geodistance(eval(lng1), eval(lat1), eval(lng2), eval(lat2)) / 1000, 3)
        try:
            itemtime = pd.to_datetime(time1)
            itemtimeend = pd.to_datetime(time2)
            timedelta = itemtime - itemtimeend
        except:
            log.critical(f"{time1}\t{time2}，此时间点处数据存在问题")
            raise
        while timedelta.seconds == 0:
            log.info(f"位置记录时间戳相同：{itemtime}\t{itemtimeend}")
            i = i + 1
            time2, lng2, lat2, *others = itemfine[i + 1]
            dis = geodistance(eval(lng1), eval(lat1), eval(lng2), eval(lat2))
            itemtime = pd.to_datetime(time1)
            itemtimeend = pd.to_datetime(time2)
            timedelta = itemtime - itemtimeend
        timedeltahour = timedelta.seconds / 60 / 60
        itemspeed = round(dis / timedeltahour, 2)
        if itemspeed >= highspeed:
            log.info(f"时间起点：{itemtimeend}，时间截止点：{itemtime}，时长：{round(timedeltahour, 3)}小时，距离：{dis}公里，速度：{itemspeed}码")
            i += 1
            continue
        timesr.append(itemtime)
        dissr.append(round(dis, 1))
    imglst = []
    ds = pd.Series(dissr, index=timesr)
    today = datetime.datetime.now().strftime('%F')
    dstoday = ds[today].sort_index().cumsum()
    print(dstoday)
    if dstoday.shape[0] > 1:
        dstoday.plot()
        imgpathtoday = dirmainpath / 'img' / 'gpstoday.png'
        touchfilepath2depth(imgpathtoday)
        plt.savefig(str(imgpathtoday))
        plt.close()
        imglst.append(str(imgpathtoday))
    dsdays = ds.resample('D').sum()
    print(dsdays)
    dsdays.plot()
    imgpathdays = dirmainpath / 'img' / 'gpsdays.png'
    touchfilepath2depth(imgpathdays)
    plt.savefig(str(imgpathdays))
    plt.close()
    imglst.append(str(imgpathdays))
    print(imglst)
        
    if (device_name := getinivaluefromnote('device', device_id)):
        pass
    else:
        device_name = device_id
        
    tlst = ['datetime', 'latitude', 'longitude', 'altitude', 'accuracy',
            'bearing', 'speed', 'elapsedMs', 'provider']
    tlstitem = ["\t".join(tlst)]
    tlstitem.extend(itemread)
    imglist2note(get_notestore(), imglst, guid,
                 f'手机_{device_name}_location更新记录',
                 "<br></br>".join(tlstitem[:50]))


if __name__ == '__main__':
    # global log
    print(f'运行文件\t{__file__}')
    foot2show()
    # showdis()
    print('Done.')
