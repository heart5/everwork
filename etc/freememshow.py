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

# %% [markdown]
# # 显示可用内存

# %%
"""
显示可用内存
"""
# %% [markdown]
# ## 库引入

# %%
import os
import time
import math
import pandas as pd
from pathlib import Path
from pylab import plt
# %%
import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from etc.getid import getdeviceid
    from func.evernttest import get_notestore, imglist2note, \
        getinivaluefromnote
# %% [markdown]
# ## 函数集合

# %% [markdown]
# ### def getdatapath()

# %%
def getdatapath(indatapath = None):
    """
    获取数据所在路径
    """
    if indatapath is None:
        indatapath = getdirmain()
    else:
        indatapath = os.path.expanduser('~') / Path(indatapath)
    cpath = indatapath / 'data' / 'freeinfo.txt'

    return cpath


# %% [markdown]
# ### def gettotalmen(cpath)

# %%
def gettotalmem(cpath):
    print(os.path.abspath(cpath))
    firstline = ""
    with open(cpath, 'r') as f:
        firstline = f.readline().strip()
    print(firstline)
    totalmem = int(firstline.split('=')[1])
    totalmeminG = math.ceil(totalmem / (1024 * 1024))

    return totalmeminG


# %%
# datarelatepath = "sbase/zshscripts"
# gettotalmem(getdatapath(datarelatepath))

# %% [markdown]
# ### def getdatadf

# %%
def getdatadf(cpath):
    indf = pd.read_csv(cpath, sep='\t', skiprows=1, header=None)
    indf['timel'] = indf[0].apply(lambda x: time.strftime("%F %T", time.localtime(x)))
    indf['time'] = pd.to_datetime(indf['timel'])
    fdf = indf.loc[:, ['time', 1, 2, 3]]
    fdf = fdf.set_index('time', drop=False)
    fdf.columns = ['time', 'freeper', 'swap', 'swapfree']

    return fdf


# %% [markdown]
# ### def getdelta()

# %%
def getdelta():
    if (delta := getinivaluefromnote('freemem', getdeviceid())) is not None:
        print(delta)
        delta = [int(x) for x in delta.split(',')]
        deltatime = pd.Timedelta(minutes=delta[0], seconds=delta[1])
    elif (delta := getinivaluefromnote('freemem', 'common')) is not None:
        print(delta)
        delta = [int(x) for x in delta.split(',')]
        deltatime = pd.Timedelta(minutes=delta[0], seconds=delta[1])
    else:
        deltatime = pd.Timedelta(minutes=8, seconds=0)

    return deltatime


# %% [markdown]
# ### def getcunpoint(inputdatapath)

# %%
def getcutpoint(inputdatapath):
    totalmen = gettotalmem(getdatapath(inputdatapath))
    inputdf = getdatadf(getdatapath(inputdatapath))
    ds = inputdf['time'] - inputdf['time'].shift()
    deltads = ds[ds > getdelta()]

    outlst = list()
    for ix in deltads.index:
        ipos = list(inputdf.index).index(ix)
        if inputdf.iloc[ipos - 1]['freeper'] == 0:
            continue
        print()
        print(ipos, ix, deltads[ix])
        outlst.append(ipos)
#         bfdf = inputdf[inputdf.index >= (ix - deltads[ix] + pd.Timedelta(minutes=-5))]
#         tmpdf = bfdf[bfdf.index < (ix + pd.Timedelta(minutes=5))]
#         print(tmpdf)

    outlst.insert(0, 0)
    outlst.append(inputdf.shape[0])

    plt.figure(figsize=(20, 40))
#     fig, ax1 = plt.subplots()
    if len(outlst) > 2:
        plt.subplot(211)
    plt.ylabel(f'空闲内存百分比({totalmen}G)')
    cutdf = inputdf.iloc[outlst[-2]:outlst[-1]]
    plt.plot(cutdf.index, cutdf['freeper'])
    plt.annotate(cutdf.index[0].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[0], cutdf.iloc[0, 1]])
    plt.annotate(cutdf.index[-1].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[-1], cutdf.iloc[-1, 1]])

    if len(outlst) == 2:
        imgpath = getdirmain() / 'img' / 'freemen.png'
        plt.savefig(imgpath)
        return imgpath
    plt.subplot(212)
    plt.ylabel(f'空闲内存百分比({totalmen}G)')
    for i in range(len(outlst) - 1):
        cutdf = inputdf.iloc[outlst[i]:outlst[i + 1]]
        plt.plot(cutdf.index, cutdf['freeper'])
        plt.annotate(cutdf.index[0].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[0], cutdf.iloc[0, 1]])
        plt.annotate(cutdf.index[-1].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[-1], cutdf.iloc[-1, 1]])

    imgpath = getdirmain() / 'img' / 'freemen.png'
    touchfilepath2depth(imgpath)
    plt.savefig(imgpath)
    return str(imgpath)


# %%
def show2evernote(imglst):
    deviceid = getdeviceid()
    guid = getinivaluefromnote('freemem', f'free_{deviceid}')
    print(guid)
    if (device_name := getinivaluefromnote('device', deviceid)) is None:
        device_name = deviceid

    imglist2note(get_notestore(), imglst, guid,
                 f'手机_{device_name}_空闲内存动态', "")


# %% [markdown]
# ## 主函数

# %%
if __name__ == '__main__':
    datarelatepath = "sbase/zshscripts"
    img = getcutpoint(datarelatepath)
    show2evernote([img])

# %%
