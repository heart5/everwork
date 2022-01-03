# encoding:utf-8
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
# # 火界游戏数据集动态存储至evernote（不同主机针对同一类笔记）

# %% [markdown]
# # 引入库

# %%
import os
import re
import pandas as pd

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.logme import log
    from etc.getid import getdeviceid
    from func.sysfunc import not_IPython
    from func.evernttest import getinivaluefromnote, getnoteresource, gettoken, get_notestore, getnotecontent, updatereslst2note
# print(f"{__file__} is loading now...")

# %% [markdown]
# # 功能函数集

# %%
def huojieds2note():
    huojieguid = getinivaluefromnote('game', 'guid')
    notecontent = getnotecontent(huojieguid)

    try:
        neirong = notecontent.find('pre').text
        print(neirong)
        nrlst = neirong.split('\n')
        print(nrlst)
        jushufromnote = int(nrlst[0].split("：")[1])
    except Exception as e:
        print(e)
        jushufromnote = 0
    print(jushufromnote)
    musedatapath = getdirmain() / 'data' / 'muse'
    tlst = [musedatapath / pt for pt in os.listdir(musedatapath) if (pt.endswith('xlsx') or pt.endswith('xls'))]
    print(tlst)
    df = pd.DataFrame()
    for datafile in tlst:
        countbefore = df.shape[0]
        df = df.append(pd.read_excel(datafile))
        log.info(f"{os.path.basename(datafile)}\t{df.shape[0] - countbefore}")

    df = df.drop_duplicates().sort_values('time', ascending=False)
    jushufromhost = df.shape[0] // 4
    log.info(f"主机本地数据文件有效局数为：\t{jushufromhost}")

    if jushufromnote != jushufromhost:
        datamainpath = musedatapath / 'huojiemain.xlsx'
        touchfilepath2depth(datamainpath)

        reslst = getnoteresource(huojieguid)
        targetbinlst = [x[1] for x in reslst if x[0] == os.path.basename(datamainpath)]
        if len(targetbinlst) != 0:
            huojiefromnotepath = musedatapath / 'huojiemainfromnote.xlsx'
            f = open(huojiefromnotepath, 'wb')
            f.write(targetbinlst[0])
            f.close()
            log.info(f"本地数据局数为：{jushufromhost}")
            df = df.append(pd.read_excel(huojiefromnotepath))
            df = df.drop_duplicates().sort_values('time', ascending=False)
            jushufromhost = df.shape[0] // 4
            log.info(f"添加网络数据后的总局数为：{jushufromhost}")
        df.to_excel(datamainpath, index=False)

        timemin = df['time'].min()
        timemax = df['time'].max()
        deviceid = getdeviceid()
        if (device_name := getinivaluefromnote('device', deviceid)) is None:
            device_name = deviceid
        updatereslst2note([datamainpath], huojieguid, 
                          neirong=f'局数：{jushufromhost}\n时间跨度：{timemin}至{timemax}\n主机名称：{device_name}', filenameonly=True)

    return jushufromnote, jushufromhost


# %% [markdown]
# # 运行主函数main

# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')

    huojieds2note()

    if not_IPython():
        log.info(f"文件\t{__file__}\t运行结束。")

# %%
