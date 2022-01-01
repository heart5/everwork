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


# %%
def items2df(fl):
    print(fl)
    content = open(fl, 'r').read()
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
    dfdict = dict()
    fllst = [f for f in os.listdir(wcdatapath) if f.startswith("chatitems")]
    for fl in fllst[::-1]:
        rs1 = re.search("\((\w+)\)", fl)
        account = rs1.groups()[0]
        dfinner = items2df(wcdatapath / fl)
        if account in dfdict.keys():
            dfall = dfdict[account].append(dfinner)
            dfall = dfall.drop_duplicates().sort_values(['time'], ascending=False)
            dfdict.update({account:dfall})
        else:
            dfdict[account] = dfinner.drop_duplicates().sort_values(['time'], ascending=False)

    return dfdict


# %%
wcdatapath = Path("../data/webchat")
dfdict = txtfiles2dfdict(wcdatapath)

# %%
dfdict

# %%
for k in dfdict:
    print(f"{k}\t{dfdict[k].shape[0]}")

# %%
for k in dfdict:
    print(f"{k}\t{dfdict[k].shape[0]}")

# %%
name_byf = "白晔峰"
name_heart5 = "heart5"
dfbyf = dfdict[name_byf]
dfheart5 = dfdict[name_heart5]
filepath_byf = wcdatapath / f"{name_byf}.xlsx"
filepath_heart5 = wcdatapath / f"{name_heart5}.xlsx"

# %%
dfbyf.to_excel(filepath_byf, engine='xlsxwriter', index=False)


# %%
def getdaterange(start, end):
    if start.strftime("%Y-%m") == end.strftime('%Y-%m'):
        drlst = [start, end]
    else:
        dr = pd.date_range(pd.to_datetime(start.strftime("%F 23:59:59")), end, freq='M')
        drlst = list(dr)
#         drlst.pop()
        drlst.insert(0, start)
        drlst.append(end)
    
    print(drlst)
    return drlst


# %%
dftimestart = dfbyf['time'].min()
dftimeend = dfbyf['time'].max()
dr = getdaterange(dftimestart, dftimeend)

# %%
for i in range(len(dr) - 1):
    dftmp = dfbyf[(dfbyf.time >= dr[i]) & (dfbyf.time <= dr[i + 1])]
    print(i, dr[i], dr[i + 1], dftmp.shape[0])

# %%
dftmp

# %%
dfbyf

# %%
dfheart5['time'].duplicated()

# %%
dfbyf[dfbyf['time'].duplicated()]

# %%
lstunique = dfbyf['sender'].unique()
print(type(lstunique))
lstunique = sorted(lstunique)
for tp in  lstunique[:20]:
    print(tp)

# %%
dfbyf[dfbyf.content.str.contains("加入了群聊")].iloc[:10]

# %%
dfbyf[dfbyf.sender.str.contains('微信运动')]

# %%
dfbyf.describe()

# %%
dfbyf.iloc[32767]

# %%
dfdict['heart5'].to_excel(wcdatapath / 'heart5.xlsx', index=False)

# %%
dftmp[dftmp.sender == '徐晓锋']

# %%
dftmp[~dftmp.sender.str.contains("群")]

# %%
