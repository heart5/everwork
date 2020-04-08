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

# 显示所有变量值
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

# ### 火界麻将

# #### 库准备

# +
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

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
    from muse.majjianghuojie import fetchmjfang, zhanjidesc, updateurllst, updateallurlfromtxt
    from life.wccontact import getownername
# -


updateallurlfromtxt('白晔峰')
# %time

# #### 【漏掉的战绩链接数据直接入库】

# +
owner = getownername()
# owner = 'heart5'
fpath = getdirmain() / 'data' / 'webchat' / f'chatitems({owner}).txt'
fpath
ptn = re.compile('three')
with open(fpath) as f:
    threelst = [ x.strip().split('\t')[-1] for x in f.readlines() if re.findall(ptn, x)]

urllst = [x for x in threelst if x.startswith('http')]
for url in urllst:
    updateurllst(url)
# -

# ##### ~~从文本库文件中提取链接~~

specialurl = "updateurllst(url)"
updateurllst()

# #### 【战绩】

ownername = getownername()
# ownername = '白晔峰'

recetday = False
simpledesc = False
zhanji = zhanjidesc(ownername, recetday, simpledesc)

print(zhanji)

# #### 补充完善房间信息

# ##### 从存储文件中读取最新对局信息并另份存档备用

excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
recorddf = pd.read_excel(excelpath)
rstdf = recorddf.copy(deep=True)
rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
rstdf

# ##### 列出战友信息，并统计各人对战圈数

teams = list(set(rstdf['guest']))
print(teams)
playtimelst = []
for player in teams:
    playerindexlst = list(rstdf[rstdf.guest == player]['roomid'])
    print(player, len(playerindexlst))

# ##### 命名变量并提取开房信息

ownername = 'heart5'
ownername = '白晔峰'
fangdf = fetchmjfang(ownername)
# 显示各人最近一次开房信息
fangdf.groupby(['name']).first().sort_values('maxtime', ascending=False)

# #### 根据对局战绩修正房主信息

# ##### 按照基本逻辑修正

fangdf = fetchmjfang(ownername)
print(f"{fangdf.shape[0]}")
fangclosedf = rstdf.groupby('roomid')['time'].max()
print(fangclosedf.shape[0])
# 以房号为索引进行数据合并，默认join='outer'
fangfinaldf: pd.DataFrame = pd.concat([fangdf, fangclosedf], axis=1).sort_values(by=['mintime'], ascending=False)
print(fangfinaldf.shape[0])
fangfinaldf = fangfinaldf.rename(columns={'time': 'closetime'})
# print(fangfinaldf) fangfinaldf.loc[:, 'playmin'] = fangfinaldf.apply(lambda df: int((df['closetime'] - df[
# 'maxtime']).total_seconds() / 60) if df['closetime'] else pd.NaT, axis=1)
fangfinaldf.loc[:, 'playmin'] = fangfinaldf.apply(
    lambda df: (df['closetime'] - df['maxtime']).total_seconds() // 60 if df['closetime'] else pd.NaT, axis=1)
# print(fangfinaldf[fangfinaldf['mintime'].isnull()])
# 根据对局战绩修正房主信息
rstdfroomhost = rstdf[rstdf.host].groupby('roomid')['guest'].first()
print(rstdfroomhost.shape[0])
for ix in list(rstdfroomhost.index.values):
    hostname = rstdfroomhost[ix]
#     print(ix, hostname)
    fangfinaldf.loc[ix, 'name'] = hostname
fangdf1 = fangfinaldf.copy(deep=True)

# ##### 代开房间处理

# +
import random

dkds = rstdf.groupby(['roomid', 'host']).count()['guest']
type(dkds)
dkds[dkds % 4 == 0]
dkds[dkds % 4 == 0].index
dstuplelst = list(dkds[dkds % 4 == 0].index)
for r, h in dstuplelst:
    rstdf.groupby('roomid').nth(random.randint(0 ,3))['guest'].loc[r]
# -

daikaidf = rstdf.groupby(['roomid', 'host']).count()
daikaidf[daikaidf.score % 4 == 0]
daikaidf[daikaidf.score > 3]

rstdf[rstdf.roomid == 549300]

# ##### 中断牌局处理

rstdf[rstdf.roomid == 916781]

zdds = rstdf.groupby(['roomid']).count()['time']
zdds[zdds > 4]
list(zdds[zdds > 4].index)
for ix in list(zdds[zdds > 4].index):
    zdds[ix]
    time2drop = rstdf.groupby('roomid').min()['time'].loc[ix]
    rstdf = rstdf[rstdf.time != time2drop]

rstdf[rstdf.roomid == 916781]

# #### 验证房主信息修正

rstdfroomhost = rstdf[rstdf.host][['roomid', 'guest']].set_index('roomid')
print(rstdfroomhost)
fangcom = fangfinaldf.join(rstdfroomhost)
fangcomother = fangcom[fangcom['guest'].notnull()]
fangcomother[fangcomother.name != fangcomother.guest]

# #### 无开房信息填补

# ##### 找出无开房信息的记录，并计算出既有对局的平均用时

fangfdf = fangfinaldf
fangfdf[fangfdf['playmin'].notnull()]
# playmin的平均值
playminmean = int(fangfdf['playmin'].mean())
fangffix = fangfdf[fangfdf['playmin'].isnull() & fangfdf['count'].isnull()]
fangffix

# ##### 填充平均对局时长，开房时间，开房人等信息

print(len(fangffix.index))
for index in fangffix.index:
    fangffix.loc[index, ['maxtime']] = fangffix.loc[index, ['closetime']][0] - pd.to_timedelta(f'{playminmean}min')
    fangffix.loc[index, ['mintime']] = fangffix.loc[index, ['maxtime']][0]
    fangffix.loc[index, ['count']] = 1
    hostname = rstdf[rstdf.host].groupby('roomid')['guest'].first()[index]
#     print(hostname)
    fangffix.loc[index, ['name']] = hostname
    fangffix.loc[index, ['playmin']] = playminmean
    fangffix.loc[index, ['consumemin']] = 0
fangffix.sort_values('closetime', ascending=False)

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

# #### 【修正名号关联】

# ##### 从存储文件读出到DataFrame

excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
recorddf = pd.read_excel(excelpath)
rstdf = recorddf.copy(deep=True)
rstdf.sort_values(['time'], ascending=False)
# rstdf

# ##### 根据guestid和guest分组，找出对不上的信息

rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
gidds = rstdf.groupby(['guestid', 'guest']).count()
gidds

# ##### 手工修复guest和guestid对不上的信息记录

fixguestid = 1083558
fixguest = '普任鹏'
needdf = rstdf[rstdf.guestid == fixguestid]
print(needdf)
# print(needdf[needdf.guest != '徐晓锋'])
needindexlst = needdf.index[:2]
print(needindexlst)
rstdf.loc[list(needindexlst), 'guest'] = fixguest
pd.DataFrame(rstdf.groupby(['guestid', 'guest']).count().index)

# ##### 写回数据存储文件

excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
excelwriter = pd.ExcelWriter(excelpath)
rstdf.to_excel(excelwriter, index=False, encoding='utf-8')
excelwriter.close()

# ##### 调试名号错位问题

from func.evernttest import trycounttimes2, getinivaluefromnote
from muse.majjianghuojie import fetchmjurl, getsinglepage, updateurllst, fixnamebyguestid

ownername = "heart5"
zjurllst = fetchmjurl(ownername)
recentquandf = getsinglepage(zjurllst[0])
recentquandf

# 一次读取所有game下的items用于名称替换，避免一次次读取文件读取网络的效率损耗，也即为减少IO
from func.configpr import getcfp
cfpme, cfpmepath = getcfp('everinifromnote')
gamedict = dict(cfpme.items('game'))
gamedict
'1088457' in gamedict.keys()

guestidcl = 'guestid'
rstdf1: pd.DataFrame = recorddf.copy(deep=True)
# print(rstdf1)
guestidalllst = rstdf1.groupby(guestidcl).first().index.values
print(guestidalllst)
gidds = rstdf1.groupby(['guestid', 'guest']).count().groupby(level='guestid').count()['roomid']
print(gidds)
guestidlst = [str(guestid) for guestid in gidds.index]
print(guestidlst)
for nameid in guestidlst:
    if nameid in gamedict.keys():
        needdf = rstdf1[rstdf1.guestid == int(nameid)]
        print(nameid, gamedict[nameid], needdf.shape[0])
        rstdf1.loc[list(needdf.index), 'guest'] = gamedict[nameid]
rstdf1

guestidcl = 'guestid'
rstdf1: pd.DataFrame = recorddf.copy(deep=True)
# print(rstdf1)
guestidalllst = rstdf1.groupby(guestidcl).first().index.values
print(guestidalllst)
gidds = rstdf1.groupby(['guestid', 'guest']).count().groupby(level='guestid').count()['roomid']
print(gidds)
guestidlst = [str(guestid) for guestid in gidds.index]
print(guestidlst)
for nameid in guestidlst:
    if namez := getinivaluefromnote('game', nameid):
        needdf = rstdf1[rstdf1.guestid == int(nameid)]
        print(namez, needdf.shape[0])
        rstdf1.loc[list(needdf.index), 'guest'] = namez
rstdf1

rstdf1.groupby(['guestid', 'guest']).count()

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

# ### 战果曲线图

excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
recorddf = pd.read_excel(excelpath)
rstdf = recorddf.copy(deep=True).sort_values('time', ascending=False)
rstdf

zgridf = rstdf.groupby([pd.to_datetime(rstdf['time'].dt.strftime("%Y-%m-%d")), rstdf.guest]).sum().reset_index('guest', drop=False)[['guest', 'score']].sort_index()
zgridf

plt.figure(figsize=(30, 6))
for person in set(list(zgridf.guest.values)):
    pzgr = zgridf[zgridf.guest == person]['score'].cumsum()
#     print(person, pzgr)
    pzgr.name = person
    pzgr.plot(legend=True)

# ### 获取笔记本或笔记信息

# #### 获取笔记本

# +
import sqlite3 as lite
import pandas as pd

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.evernttest import getsampledffromdatahouse, findsomenotest2showornote, findnotebookfromevernote
# -
ntdf = findnotebookfromevernote()

ntdf[ntdf['笔记本组'] == 'softnet']

# #### 查找包含某关键词的某指定笔记本下的笔记列表

findsomenotest2showornote('4524187f-c131-4d7d-b6cc-a1af20474a7f', '标题')

# ### 从evernote获取火界麻将数据集

ntdf = getsampledffromdatahouse('火界')

ntdf.dtypes


ntdf[ntdf['closetime'].notnull()]

findsomenotest2showornote(ntdf.loc[ntdf.名称 == 'datahouse'].index.values[-1], '火界')

soup = getnotecontent('aa817eb9-4824-4599-ab9c-cdfeed8c549c')

soupstrlst = [item.text.split(',') for item in soup.find_all('div') if len(item.text) > 0]
pd.DataFrame(soupstrlst[1:], columns=soupstrlst[0])

int(1.0)


