# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ### 调试麻将战绩统计输出函数

# #### 补充没有开局链接的房间信息

# +
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.evernttest import trycounttimes2, getinivaluefromnote
    from func.first import getdirmain, touchfilepath2depth
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from muse.majjianghuojie import fetchmjfang
# -

excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
recorddf = pd.read_excel(excelpath)
rstdf = recorddf.copy(deep=True)
rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
rstdf

ownername = '白晔峰'
recetday = True
simpledesc = True

fangdf = fetchmjfang(ownername)
fangdf.groupby(['name']).first()

fangdf = fetchmjfang(ownername)
# print(fangdf)
fangclosedf = rstdf.groupby('roomid')['time'].max()
# print(fangclosedf)
# 以房号为索引进行数据合并，默认join='outer'
fangfinaldf: pd.DataFrame = pd.concat([fangdf, fangclosedf], axis=1).sort_values(by=['mintime'], ascending=False)
fangfinaldf = fangfinaldf.rename(columns={'time': 'closetime'})
# print(fangfinaldf) fangfinaldf.loc[:, 'playmin'] = fangfinaldf.apply(lambda df: int((df['closetime'] - df[
# 'maxtime']).total_seconds() / 60) if df['closetime'] else pd.NaT, axis=1)
fangfinaldf.loc[:, 'playmin'] = fangfinaldf.apply(
    lambda df: (df['closetime'] - df['maxtime']).total_seconds() // 60 if df['closetime'] else pd.NaT, axis=1)
# print(fangfinaldf[fangfinaldf['mintime'].isnull()])
fangfdf = fangfinaldf.copy(deep=True)
fangfdf

fangfdf[fangfdf['playmin'].notnull()]
# playmin的平均值
playminmean = int(fangfdf['playmin'].mean())
fangffix = fangfdf[fangfdf['playmin'].isnull() & fangfdf['count'].isnull()]
fangffix

print(fangffix.index)
for index in fangffix.index:
    print(fangffix.loc[index, ['closetime']].values - pd.to_timedelta(f'{playminmean}min'))
    fangffix.loc[index, ['maxtime']] = fangffix.loc[index, ['closetime']][0] - pd.to_timedelta(f'{playminmean}min')
    fangffix.loc[index, ['mintime']] = fangffix.loc[index, ['maxtime']][0]
    fangffix.loc[index, ['count']] = 1
    fangffix.loc[index, ['name']] = rstdf[rstdf.host].set_index('roomid').loc[index, ['guest']][0]
    fangffix.loc[index, ['playmin']] = playminmean
    fangffix.loc[index, ['consumemin']] = 0

print(type(fangffix.loc[index, ['closetime']]))
print(type(fangffix.loc[index, ['closetime']].values))
print(type(fangffix.loc[index, ['closetime']].values[0]))
print(type(fangffix.loc[index, ['closetime']][0]))

fangffix

# #### 输出最高赢注的局圈信息

rstdf

highbool = False
highscore = (rstdf['score'].min(), rstdf['score'].max())[highbool]
outlst = list()
title = ('赛事暗黑', '赛事高亮')[highbool]
outlst.append(title)
for id in rstdf[rstdf['score'] == highscore]['roomid'].values:
    iddf = rstdf[rstdf.roomid == id]
    outstr = '赛事时间：'
    outstr += iddf['time'].max().strftime('%m-%d %H:%M')
    dayingjialst = iddf[iddf.score == highscore]['guest'].values
    dayingjiastr = ('大输家', '大赢家')[highbool]
    outstr += f'，{dayingjiastr}：{dayingjialst}'
    highstr = ('输的最惨', '赢得高分')[highbool]
    outstr += f'，{highstr}：{highscore}'
    tongjuguest = iddf[~iddf['guest'].isin(dayingjialst)]['guest'].values
    tongjustr = ('同局共坑', '同局共奉')[highbool]
    outstr += f'，{tongjustr}兄：{tongjuguest}'
    outlst.append(outstr)
'\n'.join(outlst)

# #### 关联名称，完善统计信息

rstdf = fangdf.copy(deep=True)
rstdf.groupby('name').first().index.values

clname = 'name'
for name in rstdf.groupby(clname).first().index.values:
    if namez := getinivaluefromnote('game', name):
        print(name, namez)
        namedf = rstdf[rstdf[clname] == name]
        print(name, namedf.shape[0])
        for ix in namedf.index:
            rstdf.loc[ix, [clname]] = namez
#         print(namedf)
#     else:
#         print(name)


rstdf

rstdf = backdf.copy(deep=True)
rstdf.groupby(['guest']).sum()

# ### 获取笔记本信息

# +
import sqlite3 as lite
import pandas as pd

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.evernttest import getsampledffromdatahouse
# -
# ### 从evernote获取火界麻将数据集

ntdf = getsampledffromdatahouse('火界')

ntdf.dtypes


ntdf[ntdf['closetime'].notnull()]

findsomenotest2showornote(ntdf.loc[ntdf.名称 == 'datahouse'].index.values[-1], '火界')

soup = getnotecontent('aa817eb9-4824-4599-ab9c-cdfeed8c549c')

soupstrlst = [item.text.split(',') for item in soup.find_all('div') if len(item.text) > 0]
pd.DataFrame(soupstrlst[1:], columns=soupstrlst[0])

int(1.0)


