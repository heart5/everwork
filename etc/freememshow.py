#!PREFIX/bin/python
# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       jupytext_version: 1.13.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
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
    from func.logme import log
    from func.first import getdirmain, touchfilepath2depth
    from etc.getid import getdeviceid
    from func.evernttest import get_notestore, imglist2note, \
        getinivaluefromnote
    from func.sysfunc import not_IPython


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
        # os.path.expanduser() 解决用户home目录的绝对路径问题
        indatapath = os.path.expanduser('~') / Path(indatapath)
    cpath = indatapath / 'data' / 'freeinfo.txt'

    return cpath


# %% [markdown]
# ### def gettotalmen(cpath)

# %%
def gettotalmem(cpath):
    """
    从数据文件首行获取内存总量信息，单位G
    """
    print(os.path.abspath(cpath))
    firstline = ""
    with open(cpath, 'r') as f:
        firstline = f.readline().strip()
    print(firstline)
    totalmem = int(firstline.split('=')[1])
    totalmeminG = math.ceil(totalmem / (1024 * 1024))

    return totalmeminG


# %% [markdown]
# datarelatepath = "sbase/zshscripts"
# gettotalmem(getdatapath(datarelatepath))

# %% [markdown]
# ### def getdatadf

# %%
def getdatadf(cpath):
    """
    从数据文件读取内存信息并转换为DataFrame形式输出
    """
    indf = pd.read_csv(cpath, sep='\t', skiprows=1, header=None)
    indf['timel'] = indf[0].apply(lambda x: time.strftime("%F %T", time.localtime(x)))
    indf['time'] = pd.to_datetime(indf['timel'])
    fdf = indf.loc[:, ['time', 1, 2, 3]]
    fdf = fdf.set_index('time', drop=False)
    fdf.columns = ['time', 'freeper', 'swap', 'swapfree']
    fdf['freeper'] = fdf['freeper'].apply(lambda x: 100 - int(x))

    return fdf


# %% [markdown]
# ### def getdelta()

# %%
def getdelta():
    """
    从网络配置笔记中获取时间间隔（用于判断宕机时间，逻辑上不完全准确，取经验值）
    """
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
    """
    根据时间间隔找到分割点，生成最近一次的图像和全部综合图像并返回
    """
    totalmen = gettotalmem(getdatapath(inputdatapath))
    inputdf = getdatadf(getdatapath(inputdatapath))
    ds = inputdf['time'] - inputdf['time'].shift()
    deltads = ds[ds > getdelta()]

    outlst = list()
    for ix in deltads.index:
        ipos = list(inputdf.index).index(ix)
        # 处理内存占满（但未重启）的特殊情况
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

    plt.rcParams['font.sans-serif'] = 'SimHei'
    olen = len(outlst)
    if olen == 2:
        picheight = 1
    elif olen == 3:
        picheight = 2
    else:
        picheight = 3
    plt.figure(figsize=(10, 10 * picheight))
    imgpath = getdirmain() / 'img' / 'freemen.png'
    touchfilepath2depth(imgpath)
    #     fig, ax1 = plt.subplots()
    # 针对数据集周期次数进行处理，主要是处理小于三次的情况
    if len(outlst) > 3:
        plt.subplot(311)
    elif len(outlst) == 3:
        plt.subplot(211)

    # 最近数据集图形化输出
    plt.ylabel(f'空闲内存百分比({totalmen}G)')
    cutdf = inputdf.iloc[outlst[-2]:outlst[-1]]
    plt.plot(cutdf.index, cutdf['freeper'])
    plt.ylim(0, 100)
    plt.title('最近一次运行')
    plt.annotate(cutdf.index[0].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[0], cutdf.iloc[0, 1]])
    plt.annotate(cutdf.index[-1].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[-1], cutdf.iloc[-1, 1]])

    # 针对单次（一般也是首次运行）数据集进行处理
    if len(outlst) == 2:
        plt.savefig(imgpath)
        return str(imgpath)

    # 针对数据集周期次数进行处理，主要是处理小于三次的情况
    if len(outlst) == 3:
        plt.subplot(212)
    elif len(outlst) > 3:
        plt.subplot(312)
    plt.ylabel(f'空闲内存百分比({totalmen}G)')
    plt.ylim(0, 100)
    plt.title('最近两次运行')
    twolst = outlst[-3:]
    for i in range(len(twolst) - 1):
        cutdf = inputdf.iloc[twolst[i]:twolst[i + 1]]
        plt.plot(cutdf.index, cutdf['freeper'])
        plt.annotate(cutdf.index[0].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[0], cutdf.iloc[0, 1]])
        plt.annotate(cutdf.index[-1].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[-1], cutdf.iloc[-1, 1]])

    # 综合（全部）数据集图形输出
    # 针对仅有两次数据集进行处理
    if len(outlst) == 3:
        plt.savefig(imgpath)
        return str(imgpath)
    else:
        plt.subplot(313)
    plt.ylabel(f'空闲内存百分比({totalmen}G)')
    plt.ylim(0, 100)
    plt.title('历次运行')
    for i in range(len(outlst) - 1):
        cutdf = inputdf.iloc[outlst[i]:outlst[i + 1]]
        plt.plot(cutdf.index, cutdf['freeper'])
        plt.annotate(cutdf.index[0].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[0], cutdf.iloc[0, 1]])
        plt.annotate(cutdf.index[-1].strftime("%y-%m-%d %H:%M"), xy=[cutdf.index[-1], cutdf.iloc[-1, 1]])

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
    if not_IPython():
        logstrouter = "运行文件\t%s……" % __file__
        log.info(logstrouter)
    datarelatepath = "sbase/zshscripts"
    img = getcutpoint(datarelatepath)
    show2evernote([img])
    if not_IPython():
        logstrouter = "文件%s运行结束" % (__file__)
        log.info(logstrouter)
