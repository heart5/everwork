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

# %%
import os
import re
import xlsxwriter
import pandas as pd
from pathlib import Path
from datetime import datetime

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.logme import log
    from etc.getid import getdeviceid
    from func.sysfunc import not_IPython
    from func.evernttest import getinivaluefromnote, getnoteresource, \
        gettoken, get_notestore, getnotecontent, updatereslst2note
    from filedatafunc import getfilemtime


# %%
def items2df(fl):
    try:
        content = open(fl, 'r').read()
    except Exception as e:
        log.critical(f"文件{fl}读取时出现错误，返回空的pd.DataFrame")
        return pd.DataFrame()
#     ptn = re.compile("(^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\t(True|False)\t(\S+)\t(\S+)\t", re.M)
    ptn = re.compile("(^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\t(True|False)\t([^\t]+)\t(\w+)\t", re.M)
    itemlst = re.split(ptn, content)
    itemlst = [im.strip() for im in itemlst if len(im) > 0]
    step = 5
    itemlst4pd1 = [itemlst[i : i + step] for i in range(0, len(itemlst), step)]
    df2 = pd.DataFrame(itemlst4pd1, columns=['time', 'send', 'sender', 'type', 'content'])
    df2['time'] = pd.to_datetime(df2['time'])
    df2['send'] = df2['send'].apply(lambda x : True if x == 'True' else False)
    df2['content'] = df2['content'].apply(lambda x: re.sub("(\[\w+前\])?", "", x))
    dfout = df2.drop_duplicates().sort_values('time', ascending=False)
    
    return dfout


# %%
def txtfiles2dfdict(wcdatapath):
    fllst = [f for f in os.listdir(wcdatapath) if f.startswith("chatitems")]
    
    def getownerfromfilename(fn):
        """
        从文件名中获取账号
        """
        ptn = re.compile("\((\w*)\)")
        ac = ac if (ac := re.search(ptn, fn).groups()[0]) not in ['', 'None'] else '白晔峰'
        return ac

    names = list(set([getownerfromfilename(nm) for nm in fllst]))
    print(names)
    # 如果设置为new，则找到每个账号的最新记录文件处理，否则是全部记录文件
    if (datafilesnew := getinivaluefromnote('wcitems', 'datafiles')) == 'new':
        nametimedict = dict()
        for nm in names:
            nametimedict[f"{nm}_newtime"] = datetime.fromtimestamp(0)
        for fl in fllst:
            flmtime = getfilemtime(wcdatapath / fl)
            accounttmp = getownerfromfilename(fl)
            if flmtime > nametimedict[f"{accounttmp}_newtime"]:
                nametimedict[f"{accounttmp}_newtime"] = flmtime
                nametimedict[f"{accounttmp}_filename"] = fl
        fllst = [nametimedict[f"{nm}_filename"] for nm in names]
        fllst = [v for (k, v) in nametimedict.items() if k.endswith('filename')]

    dfdict = dict()
    for fl in fllst[::-1]:
        rs1 = re.search("\((\w*)\)", fl)
        if rs1 is None:
            log.critical(f"记录文件《{fl}》的文件名不符合规范，跳过")
            continue
        account = getownerfromfilename(fl)
        dfinner = items2df(wcdatapath / fl)
        print(f"{fl}\t{getfilemtime(wcdatapath / fl).strftime('%F %T')}\t{account}\t{dfinner.shape[0]}", end="\t")
        if account in dfdict.keys():
            dfall = dfdict[account].append(dfinner)
            dfall = dfall.drop_duplicates().sort_values(['time'], ascending=False)
            print(f"{dfall.shape[0]}")
            dfdict.update({account:dfall})
        else:
            dfall = dfinner.drop_duplicates().sort_values(['time'], ascending=False)
            print(f"{dfall.shape[0]}")
            dfdict[account] = dfall

    return dfdict


# %%
def getdaterange(start, end):
    start = start + pd.Timedelta(-1, 'sec')
    if start.strftime("%Y-%m") == end.strftime('%Y-%m'):
        drlst = [start, end]
    else:
        dr = pd.date_range(pd.to_datetime(start.strftime("%F 23:59:59")), end, freq='M')
        drlst = list(dr)
#         drlst.pop()
        drlst.insert(0, start)
        drlst.append(end)
    
    log.info(f"时间范围横跨{len(drlst) - 1}个月")
    return drlst


# %%
def splitdf(name, df, wcdatapath):
    dftimestart = df['time'].min()
    dftimeend = df['time'].max()
    dr = getdaterange(dftimestart, dftimeend)

    for i in range(len(dr) - 1):
        dftmp = df[(df.time > dr[i]) & (df.time <= dr[i + 1])]
        if dftmp.shape[0] != 0:
            nianyue = dftmp['time'].iloc[0].strftime("%y%m")
            dftmp.to_excel(wcdatapath / f"wcitems_{name}_{nianyue}.xlsx", engine='xlsxwriter', index=False)
            print(i, nianyue, dr[i], dr[i + 1], dftmp.shape[0])



# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')

    wcdatapath = getdirmain() / 'data' / 'webchat'
    dfdict = txtfiles2dfdict(wcdatapath)

    for k in dfdict:
        dfinner = dfdict[k]
        print(f"{k}\t{dfinner.shape[0]}", end='\n\n')
        splitdf(k, dfinner, wcdatapath)
        print("\n")

    if not_IPython():
        log.info(f"文件\t{__file__}\t运行结束。")

# %%
