# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %% [markdown]
# # 足迹展示

# %%
"""
展示足迹
"""

# %% [markdown]
# ## 库引入

# %%
import os
# import urllib2
import re
import datetime
from math import radians, cos, sin, asin, sqrt
import pandas as pd
import numpy as np
from pylab import plt

# %%
import pathmagic
with pathmagic.context():
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.first import getdirmain, dirmainpath, touchfilepath2depth
    from func.datatools import readfromtxt, write2txt
    from func.evernttest import get_notestore, imglist2note, \
        evernoteapijiayi, makenote, readinifromnote, getinivaluefromnote, \
        tablehtml2evernote
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.termuxtools import termux_telephony_deviceinfo, \
        termux_telephony_cellinfo, termux_location
    from etc.getid import getdeviceid
    from func.sysfunc import not_IPython, set_timeout, after_timeout


# %% [markdown]
# ## 功能函数

# %% [markdown]
# ### geodistance(lng1, lat1, lng2, lat2)

# %%
def geodistance(lng1, lat1, lng2, lat2):
    """
    计算两点之间的距离并返回（公里，千米）
    """
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 4 * asin(sqrt(a)) * 6371 * 1000
    return dis


# %% [markdown]
# ### chuli_datasource()

# %%
@timethis
def chuli_datasource():
    """
    展示足迹
    """
    namestr = 'everloc'
    if (device_id := str(getcfpoptionvalue(namestr, namestr, 'device_id'))) is None:
        device_id = getdeviceid()
        setcfpoptionvalue(namestr, namestr, 'device_id', device_id)

    txtfilename = str(dirmainpath / 'data' / 'ifttt' /
                      f'location_{device_id}.txt')
    print(txtfilename)
    itemread = readfromtxt(txtfilename)
    numlimit = 9    # 显示项目数
    print(itemread[:numlimit])
    itemsrc = [x.split('\t') for x in itemread if not 'False' in x]
    itemnotfine = [x for x in itemsrc if len(x) < 3]
    print(f"有问题的数据共有{len(itemnotfine)}行：{itemnotfine}")
#     itemfine = [x for x in itemsrc if len(x) >= 3][:10000]
    itemfine = [x for x in itemsrc if len(x) >= 3]
    # print(itemfine)
    if len(itemfine) < 2:
        print('gps数据量不足，暂时无法输出移动距离信息')
        return
    timesr = list()
    dissr = list()
    outlst = list()
    # speedsr = list()
    highspeed = getinivaluefromnote('life', 'highspeed')
    print(f"{highspeed}\t{type(highspeed)}")
    for i in range(len(itemfine) - 1):
        if (len(itemfine[i]) <5 ) | (len(itemfine[i + 1]) <5):
            print(itemfine[i], itemfine[i + 1])
        time1, lat1, lng1, alt1, *others, pro1 = itemfine[i]
        time2, lat2, lng2, alt2, *others, pro2 = itemfine[i + 1]
        # print(f'{lng1}\t{lat1}\t\t{lng2}\t{lat2}')
        dis = round(geodistance(eval(lng1), eval(lat1), eval(lng2), eval(lat2)) / 1000, 3)
#         dis = round(geodistance(eval(lng1), eval(lat1), eval(lng2), eval(lat2)), 3)
        try:
            itemtime = pd.to_datetime(time1)
            itemtimeend = pd.to_datetime(time2)
            timedelta = itemtime - itemtimeend
        except Exception as eep:
            log.critical(f"{time1}\t{time2}，处理此时间点处数据出现问题。跳过此组（两个）数据条目！！！{eep}")
            continue
        while timedelta.seconds == 0:
            log.info(f"位置记录时间戳相同：{itemtime}\t{itemtimeend}")
            i = i + 1
            time2, lng2, lat2, *others = itemfine[i + 1]
            dis = round(geodistance(eval(lng1), eval(lat1), eval(lng2), eval(lat2)) / 1000, 3)
#             dis = round(geodistance(eval(lng1), eval(lat1), eval(lng2), eval(lat2)), 3)
            itemtime = pd.to_datetime(time1)
            itemtimeend = pd.to_datetime(time2)
            timedelta = itemtime - itemtimeend
        timedeltahour = timedelta.seconds / 60 / 60
        itemspeed = round(dis / timedeltahour, 2)
        if itemspeed >= highspeed * 1000:
            log.info(f"时间起点：{itemtimeend}，时间截止点：{itemtime}，时长：{round(timedeltahour, 3)}小时，距离：{dis}公里，速度：{itemspeed}码")
            i += 1
            continue
        timesr.append(itemtime)
        dissr.append(round(dis, 3))
        outlst.append([pd.to_datetime(time1), float(lng1), float(lat1), float(alt1), pro1])

    df = pd.DataFrame(outlst, columns=['time', 'longi', 'lati', 'alti', 'provider']).sort_values(['time'])
    df['jiange'] = df['time'].diff()
    df['longi1'] = df['longi'].shift()
    df['lati1'] = df['lati'].shift()
    df['distance'] = df.apply(lambda x: round(geodistance(x.longi1, x.lati1, x.longi, x.lati) / 1000, 3), axis=1)
#     df['distance'] = df.apply(lambda x: round(geodistance(x.longi1, x.lati1, x.longi, x.lati), 3), axis=1)

    return df.set_index(['time'])[['longi', 'lati', 'alti', 'provider', 'jiange', 'distance']]


# %% [markdown]
# ### foot2show(df4dis)

# %%
@set_timeout(360, after_timeout)
@timethis
def foot2show(df4dis):
    """
    展示足迹
    """
    namestr = 'everloc'
    if (device_id := getcfpoptionvalue(namestr, namestr, 'device_id')) is None:
        device_id = getdeviceid()
        setcfpoptionvalue(namestr, namestr, 'device_id', device_id)
    device_id = str(device_id)

    if (guid := getcfpoptionvalue(namestr, device_id, 'guid')) is None:
        token = getcfpoptionvalue('everwork', 'evernote', 'token')
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

    imglst = []
    ds = df4dis['distance']
    today = datetime.datetime.now().strftime('%F')
    dstoday = ds[today].sort_index().cumsum()
    print(dstoday)
    if dstoday.shape[0] > 1:
        dstoday.plot()
        imgpathtoday = dirmainpath / 'img' / 'gpstoday.png'
        touchfilepath2depth(imgpathtoday)
        plt.tight_layout() # 紧缩排版，缩小默认的边距
        plt.savefig(str(imgpathtoday))
        plt.close()
        imglst.append(str(imgpathtoday))
    dsdays = ds.resample('D').sum()
    print(dsdays)
    dsdays.plot()
    imgpathdays = dirmainpath / 'img' / 'gpsdays.png'
    touchfilepath2depth(imgpathdays)
    plt.tight_layout() # 紧缩排版，缩小默认的边距
    plt.savefig(str(imgpathdays))
    plt.close()
    imglst.append(str(imgpathdays))
    print(imglst)

    if (device_name := getinivaluefromnote('device', device_id)) is None:
        device_name = device_id
    imglist2note(get_notestore(), imglst, guid,
                 f'手机_{device_name}_location更新记录',
                 tablehtml2evernote(df4dis.sort_index(ascending=False).iloc[:100, ], "坐标流水记录单"))


# %% [markdown]
# ## 主函数main

# %%
if __name__ == '__main__':

    if not_IPython():
        log.info(f'运行文件\t{__file__}……')
    dout = chuli_datasource()
    foot2show(dout)
    # showdis()
    if not_IPython():
        log.info(f"完成文件{__file__}\t的运行")


# %%
def sampledef(dout):
    df = dout.copy(deep=True)

    df.sort_index(ascending=False).iloc[:100,]

    def is_normal(timed):
        return timed.total_seconds() > 12 * 3600

    df[df['jiange'].map(is_normal) == True]

    jglst = list(df[df['jiange'].map(is_normal) == True].index)
    jglst

    jglst.insert(0, 0)

    df.loc[jglst[-1]:,]


