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

# ### 微信延时

# +
import time
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

import pathmagic
with pathmagic.context():
    from func.first import touchfilepath2depth, getdirmain
    from life.wcdelay import getdelaydb, showdelayimg


# -
showdelayimg()

# +
jujinm, timedf = getdelaydb()
register_matplotlib_converters()

plt.figure(figsize=(36, 6), dpi=300)
plt.style.use('ggplot')   ##使得作图自带色彩，这样不用费脑筋去考虑配色什么的；
tmin = timedf.index.min()
tmax = timedf.index.max()
shicha = tmax - tmin
bianjie = int(shicha.total_seconds() / 40)
print(f"左边界：{bianjie}秒，也就是大约{int(bianjie / 60)}分钟")
# plt.xlim(xmin=tmin-pd.Timedelta(f'{bianjie}s'))
plt.xlim(xmin=tmin)
plt.xlim(xmax=tmax + pd.Timedelta(f'{bianjie}s'))
# plt.vlines(tmin, 0, int(timedf.max() / 2))
plt.vlines(tmax, 0, int(timedf.max() / 2))
plt.scatter(timedf.index, timedf, s=timedf)
plt.scatter(timedf[timedf == 0].index, timedf[timedf == 0], s=0.5)
plt.title('信息频率和延时')
plt.savefig(touchfilepath2depth(getdirmain() / 'img' / 'webchat' / 'wcdelay.png'))
plt.show()


# -
plt.figure(figsize=(12, 6))
weiyi = 20
plt.ylim(ymin=(-1) * weiyi)
plt.ylim(ymax=timedf.max().values[0] + weiyi)
# plt.plot(timedf[::200])
plt.plot(timedf)

print(timedf.shape[0])
itemds = pd.Series([timedf.iloc[-1].values[0]], index=[pd.to_datetime(time.ctime())], name='delay')
print(itemds.dtypes)
print(itemds)
pd.concat([timedf, itemds])

print(time.time())
print(int(time.time() * 1000))

# +
import pandas as pd
import time

endds = pd.Series()
print(timedf.shape[0])
timedf.append(pd.DataFrame([timedf.iloc[-1]], index=[pd.to_datetime(time.ctime())]))
print(timedf.shape[0])
# -

plt.scatter(timedf.index, timedf)


# +
def delitemfromdb(key):
    conn = lite.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(f"delete from {tablename} where time= {key}")
    conn.commit()
    log.info(f"删除\ttime为\t{key}\t的数据记录，{tablename} in {dbname}")
    conn.close()
    
# delitemfromdb(1582683260)


# -


def inserttimeitem2db(timestr: str):
    dbname = touchfilepath2depth(getdirmain() / 'data' / 'db' / 'wcdelay.db')
    conn = lite.connect(dbname)
    cursor = conn.cursor()
    tablename = 'wcdelay'
    def istableindb(tablename: str, dbname: str):
        cursor.execute("select * from sqlite_master where type='table'")
        table = cursor.fetchall()
        print(table)
        chali = [x for item in table for x in item[1:3]]
        print(chali)

        return tablename in chali
    
    if not istableindb(tablename, dbname):
        cursor.execute(f'create table {tablename} (time int primary key, delay int)')
        conn.commit()
        print(f"数据表：\t{tablename} 被创建成功。")
        
    timetup = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    timest = time.mktime(timetup)
    elsmin = (int(time.time()) - time.mktime(ttuple)) // 60
    cursor.execute(f"insert into {tablename} values(?, ?)", (timest, elsmin))
    print(f"数据成功写入{dbname}\t{(timest, elsmin)}")
    conn.commit()
    conn.close()


import datetime
time.localtime(1582683320)

inserttimeitem2db('2020-02-26 10:15:20')

timestr = '2020-02-26 10:14:20'
timetuple = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
timetupledt = datetime.datetime(*timetuple[:6])
import pandas as pd
dts = pd.to_datetime(timestr)

ttuple= time.strptime(timestr,'%Y-%m-%d %H:%M:%S')
time.mktime(ttuple)
(int(time.time()) - time.mktime(ttuple)) // 60

time.localtime(timestr)

date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
dte = pd.to_datetime(date_str)
dtd = dte - dts
dtd.total_seconds() // 60

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
    from muse.majjianghuojie import fetchmjfang, zhanjidesc
# -


excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
recorddf = pd.read_excel(excelpath)
rstdf = recorddf.copy(deep=True)
rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
rstdf

teams = list(set(rstdf['guest']))
print(teams)
playtimelst = []
for player in teams:
    playerindexlst = list(rstdf[rstdf.guest == player]['roomid'])
    print(player, playerindexlst)



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

excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
recorddf = pd.read_excel(excelpath)
rstdf = recorddf.copy(deep=True)

rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
gidds = rstdf.groupby(['guestid', 'guest']).count().reset_index(['guest'], drop=False).groupby(level='guestid').count()['roomid']
print(gidds)
gidds[gidds > 1].index

fixguestid = 1083558
fixguest = '徐晓锋'
needdf = rstdf[rstdf.guestid == fixguestid]
print(needdf)
# print(needdf[needdf.guest != '徐晓锋'])
needindexlst = needdf.index[:2]
print(needindexlst)
rstdf.loc[list(needindexlst), 'guest'] = fixguest
pd.DataFrame(rstdf.groupby(['guestid', 'guest']).count().index)

excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
excelwriter = pd.ExcelWriter(excelpath)
rstdf.to_excel(excelwriter, index=False, encoding='utf-8')
excelwriter.close()

rstdf = fangdf.copy(deep=True)
rstdf.groupby('name').first().index.values

rstdf

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


