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

# ## 字符串化后输出成图片

# +
import os
import pandas as pd
from PIL import Image, ImageFont, ImageDraw
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, dirmainpath
    from func.pdtools import db2img, lststr2img
    from life.wccontact import getctdf, showwcsimply
# -

# lststr2img("我的祖国", showincell=True)
lststr2img("我的祖国", fontpath=dirmainpath / 'font' / 'msyh.ttf')

# ### `plt`参数默认值

fig = plt.figure()
size = fig.get_size_inches()*fig.dpi # size in pixels
size[1]

plt.rcParams.get('figure.figsize')
plt.rcParams.get('figure.dpi')

# + jupyter={"outputs_hidden": true}
plt.rcParams
# -

outdone = showwcsimply(getctdf())

outdonestr1 = outdone.to_string(justify='left', show_dimensions=True)[:1500]
print(outdonestr1)
print()
outdonestr2 = str(outdone.to_string())[:1500]
outdonestr2
print(outdonestr2)

outdone

db2img(outdone)

# +
text = u"这是一段测试文本，test 123。"
register_matplotlib_converters()

font = ImageFont.truetype("../font/simhei.ttf", 12)
# fontpath = str(getdirmain() / "simhei.ttf")
# fontpath
# os.path.abspath(fontpath)
# font = ImageFont.load(os.path.abspath(fontpath))
# font = ImageFont.load_default()
text2 = "甲天下的是不是桂林？City guilin"
font.getsize(text)
# font.getsize(text2)
# dr.text((10, 5), text, font=font, fill="#000000")
# dr.text((10, 5), text, font=font, fill="#000000")
# dr.text((10, 20), text2, font=font, fill="#000000")
dflines = outdone.to_string(justify='left', show_dimensions=True).split('\n')
rows = len(dflines)
collenmax = max([len(x) for x in dflines])
print(rows, collenmax)
colwidthmax = max([font.getsize(x)[0] for x in dflines])
rowwidth = max([font.getsize(x)[1] for x in dflines])
print(rowwidth, colwidthmax)
print(rowwidth * len(dflines), colwidthmax)

im = Image.new("RGB", (colwidthmax, rowwidth * len(dflines)), (255, 255, 255))
dr = ImageDraw.Draw(im)

i = 0
for line in dflines:
    dr.text((0, 0 + rowwidth * i), line, font=font, fill="#000000")
    i += 1

# im.show()
plt.figure(dpi=600)
plt.axis('off') 
# font = ImageFont.truetype("../msyh.ttf", 12)
plt.title("联系人信息变更记录")
plt.imshow(im)


# -

def lststr2img_test(inputcontent, fontpath=dirmainpath / 'font' / 'simhei.ttf', title=None, showincell=False, fontsize=12, dpi=300) :
    if type(inputcontent) == str:
        dflines = inputcontent.split('\n')
    elif type(inputcontent) == list:
        dflines = inputcontent
    else:
        logstr = f"传入参数类型为：\t{type(inputcontent)}，既不是str也不是list，暂不做处理返回None"
        log.critical(logstr)
        return 
    
    rows = len(dflines)
    collenmax = max([len(x) for x in dflines])
    print(f"行数和行最长长度（字符）：\t{(rows, collenmax)}")
    font = ImageFont.truetype(str(fontpath), fontsize)
    print(str(fontpath))
    colwidthmax = max([font.getsize(x)[0] for x in dflines])
    rowwidth = max([font.getsize(x)[1] for x in dflines])
    print(f"行高度、所有行总高度和所有列宽度（像素）：\t{(rowwidth, rowwidth * len(dflines), colwidthmax)}")

    print(f"画布宽高（像素）：\t{(colwidthmax, rowwidth * len(dflines))}")
    im = Image.new("RGB", (colwidthmax, rowwidth * len(dflines)), (255, 255, 255))
    dr = ImageDraw.Draw(im)

    i = 0
    for line in dflines:
        dr.text((0, 0 + rowwidth * i), line, font=font, fill="#000000")
        i += 1

    # im.show()
    figdefaultdpi = plt.rcParams.get('figure.dpi')
    figwinchs = round(colwidthmax * (dpi / figdefaultdpi) / figdefaultdpi / 10, 3)
    fighinchs = round(rowwidth * len(dflines) * (dpi / figdefaultdpi) / figdefaultdpi / 10, 3)
    print(f"输出图片的画布宽高（英寸）：\t{(figwinchs, fighinchs)}")
    plt.figure(figsize=(figwinchs, fighinchs),dpi=dpi)
    plt.axis('off') 
    # font = ImageFont.truetype("../msyh.ttf", 12)
    if title:
        plt.title(title)
    plt.imshow(im)
    imgtmppath = dirmainpath / 'img'/ 'dbimgtmp.png'
    plt.axis('off') 
    plt.savefig(imgtmppath)
    if not showincell:
        plt.close()
    
    return imgtmppath


# + jupyter={"outputs_hidden": true}
samplestr = "今天是三月最后一天。据说4月8日，也就是壹周之后，武汉要解封了！"
lststr2img_test(samplestr, fontsize=12, showincell=True)
lststr2img_test(samplestr, fontsize=12, showincell=True, dpi=72)


# -

def db2img_test(inputdf: pd.DataFrame, title=None, showincell=True, fontsize=12, dpi=300):
    dflines = inputdf.to_string(justify='left', show_dimensions=True).split('\n')
    
    return lststr2img_test(dflines, title=title, dpi=dpi, showincell=showincell, fontsize=fontsize)


db2img_test(outdone, dpi=600)

# ## 消息处理


global innermsg
@itchat.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING, ATTACHMENT, VIDEO])
def handler_receive_msg(msg):
    global innermsg
    innermsg = msg


# ## 微信延时

# #### 库准备

# +
import time
import os
import pandas as pd
import sqlite3 as lite
from line_profiler import LineProfiler
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

import pathmagic
with pathmagic.context():
    from func.first import touchfilepath2depth, getdirmain
    from life.wcdelay import getdelaydb, showdelayimg
    from func.litetools import droptablefromdb, ifnotcreate
# -
# #### 【显示延时图】

# lp = LineProfiler()
# # lp.add_function(getdelaydb)
# lpwrapper = lp(showdelayimg(dbname))
# lpwrapper()
# lp.print_stats()
men_wc = 'heart5'
men_wc = '白晔峰'
dbname = getdirmain() / 'data' / 'db' / f"wcdelay_{men_wc}.db"
showdelayimg(dbname)

# #### 重构数据表

# ##### 重构数据结构

# ###### 构建新数据表

tablename_wcdelay_new = "wcdelaynew"
csql = f"create table if not exists {tablename_wcdelay_new} (id INTEGER PRIMARY KEY AUTOINCREMENT, msgtime int, delay int)"
ifnotcreate(tablename_wcdelay_new, csql, dbname)

# ###### 【删除新表】用于新数据表构建时的调试

droptablefromdb(dbname, tablename=tablename_wcdelay_new, confirm=True)

# ###### 从原数据表读入所有数据写入新的数据表

fresh, dfold = getdelaydb(dbname, tablename="wcdelay")

# 去掉附加的最后一条记录（提取数据时的时间和实际的最后一条延时），重置index回数据列
dffromold = dfold.iloc[:-1, :].reset_index()

# 赋值列名，匹配数据表的列名
dffromold.columns = ['msgtime', 'delay']
dffromold
dffromold.dtypes

from datetime import datetime
dfolddone = dffromold.copy(deep=True)
dfolddone['msgtime'] = dfolddone['msgtime'].apply(lambda x: datetime.timestamp(x))
dfolddone
print(f"{dfolddone.iloc[0, 0]}")

# +
dbname
# conn.close()
conn = lite.connect(dbname)

dfolddone.to_sql(tablename_wcdelay_new, con=conn, if_exists='replace', index=False)
conn.close()


# -

# #### 画图函数

# +
def showdelayimg(dbname: str, jingdu: int = 300):
    '''
    show the img for wcdelay 
    '''
    jujinm, timedf = getdelaydb(dbname)
#     timedf.iloc[-1]
    print(f"记录新鲜度：出炉了{jujinm}分钟")

    register_matplotlib_converters()

    plt.figure(figsize=(36, 12))
    plt.style.use("ggplot")  # 使得作图自带色彩，这样不用费脑筋去考虑配色什么的；

    def drawdelayimg(pos, timedfinner):
        # 画出左边界
        tmin = timedfinner.index.min()
        tmax = timedfinner.index.max()
        shicha = tmax - tmin
        bianjie = int(shicha.total_seconds() / 40)
        print(f"左边界：{bianjie}秒，也就是大约{int(bianjie / 60)}分钟")
        # plt.xlim(xmin=tmin-pd.Timedelta(f'{bianjie}s'))
        plt.subplot(pos)
        plt.xlim(xmin=tmin)
        plt.xlim(xmax=tmax + pd.Timedelta(f"{bianjie}s"))
        # plt.vlines(tmin, 0, int(timedf.max() / 2))
        plt.vlines(tmax, 0, int(timedfinner.max() / 2))

        # 绘出主图和标题
        plt.scatter(timedfinner.index, timedfinner, s=timedfinner)
        plt.scatter(timedfinner[timedfinner == 0].index, timedfinner[timedfinner == 0], s=0.5)
        plt.title("信息频率和延时")

    drawdelayimg(211, timedf[timedf.index > timedf.index.max() + pd.Timedelta('-2d')])
    drawdelayimg(212, timedf)
        
    imgwcdelaypath = touchfilepath2depth(
        getdirmain() / "img" / "webchat" / "wcdelay.png"
    )

    plt.savefig(imgwcdelaypath, dpi=jingdu)
    print(os.path.relpath(imgwcdelaypath))

    return imgwcdelaypath

showdelayimg(dbname)
# -

# #### 函数学习调试

pd.to_datetime([1, 2, 3], unit='D', origin=pd.Timestamp('1976-10-6'))

jujinm, timedf = getdelaydb(dbname)
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


# #### 功能函数

# ##### 删除条目

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


# ##### 插入条目

# ###### **新库函数3.0**

def inserttimeitem2db(dbname: str, timestampinput: int):
    '''
    insert timestamp to wcdelay db whose table name is wcdelay
    '''
    tablename = "wcdelaynew"
    checkwcdelaytable(dbname, tablename)

    # timetup = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    # timest = time.mktime(timetup)
    elsmin = (int(time.time()) - timestampinput) // 60
    conn = False
    try:
        conn = lite.connect(dbname)
        cursor = conn.cursor()
        cursor.execute(
            f"insert into {tablename} values(?, ?)", (timestampinput, elsmin)
        )
#         print(f"数据成功写入{dbname}\t{(timestampinput, elsmin)}")
        conn.commit()
    except lite.IntegrityError as lie:
        logstr = f"键值重复错误\t{lie}"
        log.critical(logstr)
    finally:
        if conn:
            conn.close()



def checkwcdelaytable(dbname: str, tablename: str):
    """
    检查和dbname（绝对路径）相对应的延时数据表是否已经构建，设置相应的ini值避免重复打开关闭数据库文件进行检查
    """
    if not (wcdelaycreated := getcfpoptionvalue('everwebchat',
                                                os.path.abspath(dbname), 'wcdelay')):
        print(wcdelaycreated)
        csql = f"create table if not exists {tablename} (id INTEGER PRIMARY KEY AUTOINCREMENT, msgtime datatime, delay int)"
        ifnotcreate(tablename, csql, dbname)
        setcfpoptionvalue('everwebchat', os.path.abspath(dbname), 'wcdelay',
                          str(True))
        logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
        log.info(logstr)


# ###### ~~老库函数2.0~~

def checkwcdelaytable(dbname: str, tablename: str):
    """
    检查和dbname（绝对路径）相对应的延时数据表是否已经构建，设置相应的ini值避免重复打开关闭数据库文件进行检查
    """
    if not (wcdelaycreated := getcfpoptionvalue('everwebchat',
                                                os.path.abspath(dbname), 'wcdelay')):
        print(wcdelaycreated)
        csql = f"create table if not exists {tablename} (time int primary key, delay int)"
        ifnotcreate(tablename, csql, dbname)
        setcfpoptionvalue('everwebchat', os.path.abspath(dbname), 'wcdelay',
                          str(True))
        logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
        log.info(logstr)


def inserttimeitem2db(dbname: str, timestampinput: int):
    '''
    insert timestamp to wcdelay db whose table name is wcdelay
    '''
    tablename = "wcdelay"
    checkwcdelaytable(dbname, tablename)

    # timetup = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    # timest = time.mktime(timetup)
    elsmin = (int(time.time()) - timestampinput) // 60
    conn = False
    try:
        conn = lite.connect(dbname)
        cursor = conn.cursor()
        cursor.execute(
            f"insert into {tablename} values(?, ?)", (timestampinput, elsmin)
        )
#         print(f"数据成功写入{dbname}\t{(timestampinput, elsmin)}")
        conn.commit()
    except lite.IntegrityError as lie:
        logstr = f"键值重复错误\t{lie}"
        log.critical(logstr)
    finally:
        if conn:
            conn.close()
    conn.close()


# ###### ~~老库函数1.0~~

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

# ## 联系人处理

# #### 库准备

# +
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

import uuid
import os
import random
import itchat

import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片
from pandas.plotting import register_matplotlib_converters
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

import numpy as np
import pandas as pd
import sqlite3 as lite
from binascii import hexlify, unhexlify
from itchat.content import *

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.evernttest import getinivaluefromnote
    from life.wcdelay import getdelaydb, showdelayimg
    from func.litetools import ifnotcreate, showtablesindb, droptablefromdb, compact_sqlite3_db
    from func.wrapfuncs import timethis, logit
    from func.logme import log
    from func.sysfunc import uuid3hexstr, sha2hexstr
    from life.wccontact import updatectdf, getctdf, getownername, showwcsimply
# -

# #### 函数准备

# ##### getdbname

# +
from pathlib import Path

def getdbname(dbpath: str, ownername: str):
    return touchfilepath2depth(getdirmain() / dbpath / f"wccontact_{ownername}.db")


# -

# ##### getctdf_i

def getctdf_i():
    owner = getownername()
    dbpath = Path("data")/ 'db'
    dbname = getdbname(dbpath, owner)
    dftablename = 'wccontact'
    conn = lite.connect(dbname)
    frddfread = pd.read_sql(f'select * from {dftablename}', con=conn, parse_dates=['appendtime']).set_index('id')
    conn.close()

    return frddfread


# ##### sha3hexstr，输出输入对象的hash值

# +
from hashlib import sha256, md5, blake2b

def sha2hexstr(inputo: object):
    if type(inputo) == bytes:
        targetb = inputo
    else:
        targetb = str(inputo).encode('utf-8')
    hhh = sha256(targetb)

    return hhh.hexdigest().upper()

sha2hexstr('heart5')


# -

# ~~尸体，在这里吃了好大的亏！~~一直怀疑是和运行环境相关，是变化的，今天才算找到问题所在，hash就是基于运行环境的，hashlib才用于永久存储

# + jupyter={"source_hidden": true}
def uuid3hexstr(inputo: object):
#     inputstr = str(inputo)[:767]
    inputstr = str(inputo)
#     print(f"输入对象str化后长度为：{len(inputstr)}")
    uuidout = uuid.uuid3(uuid.NAMESPACE_URL, inputstr)

    return hex(hash(uuidout))[2:].upper()


# +
strlst4text = [list(), tuple(), '微信', 'heart5', ['blog', '12'], '生产力', ['12', '23'], 'blog', '生产力', ('12', '23'), None, None, 123, 321, '12', '12']
for itm in strlst4text:
    pass

for item in strlst4text[:5]:
    sha3hexstr(item), item
# -

sha3hexstr(list())
sha3hexstr('微信')

sha3hexstr('微信' *10000000 +"titch")

# ### 【更新联系人信息，输出数据集】

# ##### 更新记录集

# +
import pandas as pd

import pathmagic
with pathmagic.context():
    from life.wccontact import updatectdf, getctdf
    from func.first import getdirmain, touchfilepath2depth
    from func.evernttest import getinivaluefromnote
# -

updatectdf()

# ##### 提取所有数据用于分析（留个备份）

frdfromdbrecords = getctdf()
frdfromdbrecords.shape[0]
frdfromdbrecords.dtypes
# frdfromdbforfix = frdfromdbrecords.copy(deep=True)


# + [markdown] toc-hr-collapsed=true toc-nb-collapsed=true
# ### 输出结果处理
# -

# frdfromdb = frdfromdbrecords[frdfromdbrecords['imguuid'].notnull()].copy(deep=True)[list(frdfromdbrecords)]
frdfromdb = frdfromdbrecords.copy(deep=True)
frdfromdb

# + [markdown] toc-hr-collapsed=true toc-nb-collapsed=true jupyter={"source_hidden": true} toc-hr-collapsed=true toc-nb-collapsed=true
# #### *剔除无效数据，只保留有用的历史记录，并回填数据库中相应的数据表*

# + [markdown] jupyter={"source_hidden": true}
# ##### 抛开变动列（contactuuid、appendtime和imguuid）根据前列去重，保留最早的记录

# + jupyter={"source_hidden": true, "outputs_hidden": true}
list(frdfromdb)[1:-2]
frddfafterdropduplites = frdfromdb.drop_duplicates(list(frdfromdb)[1:-2], keep='first')
frddfafterdropduplites


# + [markdown] jupyter={"source_hidden": true}
# ##### 更新contactuuid

# + jupyter={"source_hidden": true, "outputs_hidden": true}
def dfsha2udpatecontactuuid(inputdf: pd.DataFrame):
    # ['contactuuid', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'appendtime', 'imguuid']
    frddf2append = inputdf.copy()
#     print(frddf2append.dtypes)
    # [NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord']
    clnamescleanlst = [cl for cl in list(frddf2append.columns.values) if cl.lower() not in ['contactuuid', 'imguuid', 'appendtime']]
    print(clnamescleanlst)
#     frddf2appendnoimguuid = frddf2append.loc[:, clnamescleanlst]
    frddf2append['contactuuid'] = frddf2append[clnamescleanlst].apply(lambda x: sha2hexstr(list(x.values)), axis=1)
    
    return frddf2append

dfcleanafterupdatecontactuuid = dfsha2udpatecontactuuid(frddfafterdropduplites)
dfcleanafterupdatecontactuuid

# + [markdown] jupyter={"source_hidden": true}
# ##### 【删除该数据表，按结构重构】

# + [markdown] jupyter={"source_hidden": true}
# ##### 回填数据

# + jupyter={"source_hidden": true}
owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
dftablename = 'wccontact'
conn = lite.connect(dbname)
dfcleanafterupdatecontactuuid.to_sql(dftablename, con=conn, if_exists='append', index=False)
conn.close()
# -

# #### 处理结果并输出简版的结果

# ##### 填充remarkname为空的记录（用nickname填充）

frdfromdb['remarkname'] = frdfromdb[['nickname', 'remarkname']].apply(lambda x: x.nickname if x.remarkname == '' else x.remarkname, axis=1)
# frdfromdb['appendtime'] = frdfromdb['appendtime'].apply(lambda x: pd.to_datetime(x.strftime("%y-%m-%d %H:%m")))
outdfraw = frdfromdb.copy(deep=True)
outdfraw

# ##### 暂时只保留能看懂的列值

outdfraw.drop_duplicates(['nickname', 'remarkname', 'contactflag', 'signature', 'starfriend', 'province', 'city'], keep='first', inplace=True)
outdfraw

# ##### 过滤出最近一次修改是n天内发生的更改记录

# +
id(outdfraw)
outdfmulti = outdfraw.copy(deep=True)

# 找出最近n天内有过更改的联系人清单，n从动态配置文件中获取，不成功则设置-1
if (wcrecentdays := getinivaluefromnote('webchat', 'wcrecentdays')):
    pass
else:
    wcrecentdays = -1
wcrecentdays
startpoint = pd.Timestamp.now() + pd.Timedelta(f'{wcrecentdays}d')
startpoint
dsfortime = outdfmulti.groupby('remarkname').last()['appendtime']
outready = outdfmulti.loc[outdfmulti['remarkname'].isin(list(dsfortime[dsfortime > startpoint].index))]
outready
# -

# ##### 排序输出结果

# **属性值**
#
# 1. contactflag。
#     1. 515。聊天静音。
#     2. 3。正常。
# 2. sex。
#     1. 1。男。
#     2. 2。女。
#     3. 0。未知。
# 3. starfriend。星标朋友。
# 4. attrstatus。
#     1. 135271。
#     2. 4199。
#     3. 233509
#     4. 102473
#     5. 2147714407
#     6. 102591
#     7. 102439
#     

outready['appendtime'] = outready['appendtime'].apply(lambda x: pd.to_datetime(x).strftime("%y-%m-%d %H:%M"))
outclean = outready.groupby(['remarkname', 'appendtime']).first().sort_index(ascending=[True, False])
# outclean.dtypes
outdone = outclean[list(outclean)[1:-1]]
outdone

# ##### 各种测试

# frdfromdb.groupby('contactflag').agg(['unique'])
frdfromdb.groupby('contactflag').nunique()

frdfromdb[frdfromdb.contactflag == 515]

frdfromdb[frdfromdb.remarkname == '张玉']
frdfromdb[frdfromdb.nickname == 'KI']
frdfromdb[frdfromdb.starfriend == 1]

# ##### ~~过滤出有更改（appendtime有不止一个记录）的记录~~

# + [markdown] jupyter={"source_hidden": true}
# 逻辑失误，要先查找n天内有痕迹的记录就行，不用刻意判断是否有多条记录（当然，这个在数据初始化刚开始产生新记录时刻意降低一些冗余显示，但那又是另外一套逻辑了）

# + jupyter={"outputs_hidden": true, "source_hidden": true}
havechanged = outdfraw.groupby('remarkname').nunique()['appendtime'] > 2
# havechanged
hcds = havechanged[havechanged]
# hcds.index
outdfmulti = outdfraw.loc[outdfraw['remarkname'].isin(list(hcds.index))].copy(deep=True)
outdfmulti
# -

# ### 处理联系人信息入库

# ### 热启动微信服务

pklabpath = os.path.relpath(touchfilepath2depth(getdirmain() / 'itchat.pkl'))
print(pklabpath)
itchat.auto_login(hotReload=True, statusStorageDir=pklabpath)   #热启动你的微信

# #### 生成uuid区分不同的登录（按照pkl的存放地儿）

uuid3hexstr(os.path.abspath(itchat.originInstance.hotReloadDir))

# #### 获取联系人列表
# 随机显示几个

frdlst = itchat.get_friends()
len(frdlst)

[fd for fd in frdlst if fd['NickName'] == 'heart5']
ranslice = random.sample(range(len(frdlst)), 3)
ranslice
for i in ranslice:
    print(frdlst[i], '\n')

itchat.search_friends(userName="@48c801cab3eb33774da5bad4cbeec8ec")
itchat.search_friends(wechatAccount="heart57479")

# #### 获取聊天群列表

qunlst = itchat.get_chatrooms()

len(qunlst)
qunsample = qunlst[20]
print(qunsample.keys())
for key, value in dict(qunsample).items():
    print(key, value)


# #### 构造数据和相应数据表

# ##### 显示数据库文件中数据表信息

owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
# droptablefromdb(dbname, 'wcheadimgtmp', confirm=True)
showtablesindb(dbname)

# ##### 压缩数据库文件

# +
# owner = 'heart5'
owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")

compact_sqlite3_db(dbname)
# -

# ##### 构造数据表

# 【**删除数据表，慎用**】

droptablefromdb(dbname, 'wccontact', confirm=True)

# 联系人基本信息数据表

tablename_cc = "wccontact"
csql = f"create table if not exists {tablename_cc} (id INTEGER PRIMARY KEY AUTOINCREMENT, contactuuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, nickname TEXT, contactflag int, remarkname TEXT, sex int, signature TEXT, starfriend int, attrstatus int, province TEXT, city TEXT, snsflag int, keyword TEXT, imguuid text, appendtime datatime)"
# conn = lite.connect(dbname)
# cursor = conn.cursor()
# cursor.execute(f'drop table {tablename_cc}')
# conn.commit()
# tcs = conn.total_changes
# print(tcs)
# conn.close()
ifnotcreate(tablename_cc, csql, dbname)

# 联系人头像数据表

tablename = "wcheadimg"
csql = f"create table if not exists {tablename} (himgid INTEGER PRIMARY KEY AUTOINCREMENT,remarkname TEXT not null, imguuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, headimg BLOB NOT NULL)"
# conn = lite.connect(dbname)
# cursor = conn.cursor()
# cursor.execute(f'drop table {tablename}')
# # cursor.execute(f'drop table cinfo')
# conn.commit()
# tcs = conn.total_changes
# print(tcs)
# conn.close()
ifnotcreate(tablename, csql, dbname)


# #### 查验数据并提取有用信息到list以及DataFrame中

# ##### 生成imguuid的函数

# +

def getimguuid(inputbytes: bytes):
    imgfrombytes = Image.open(BytesIO(inputbytes))
    
    return sha3hexstr(np.array(imgfrombytes))


# -

# ##### 查验frd列表，生成DataFrame

# +
def getwcdffromfrdlst(frdlst: list, howmany: str = 'fixed', needheadimg = False):
    
    def yieldrange(startnum: int, width: int = 20):
        endnum = (startnum + width, len(frdlst))[len(frdlst) < startnum + width]
        return range(startnum, endnum)
    
    if type(howmany) is int:
        rang = yieldrange(howmany)
    elif type(howmany) is tuple:
        if len(howmany) == 1:
            rang = yieldrange(howmany[0])
        elif len(howmany) >= 2:
            rang = yieldrange(howmany[0], howmany[1])
    elif howmany.lower() == 'random':
        rang = random.sample(range(len(frdlst)), 5)
    elif howmany.lower() == 'fixed':
        rang = range(0, 5)
    elif howmany.lower() == 'all':
        rang = range(len(frdlst))
    else:
        log.critical(f"{howmany}不是合法的参数")
        return
    
    print(rang)
    frdinfolst = list()
    attrlst = ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord']
    for ix in rang:
        frd = frdlst[ix]
        frdinfo = list()
        if 'UserName' in frd.keys():
            try:
                for attr in attrlst:
                    frdinfo.append(frd[attr])

            except Exception as eeee:
                log.critical(f"第【{ix}/{len(frdlst)}】条记录存在问题。{frd['NickName']}\t{frd['UserName']}\t{eeee}")
                continue

            if needheadimg:
                headimg = itchat.get_head_img(frd["UserName"])
#                 print(str(headimg)[:100])
                if (iblen := len(headimg)) == 0:
                    print(f"{frd['NickName']}\t图像获取失败！")
                    frdimguuid = None
                else:
    #                 print(f"内容示意：\t{headimg[:15]}")
    #                 print()
                    frdimguuid = getimguuid(headimg)

                frdinfo.append(frdimguuid)
                frdinfo.append(headimg)

            frdinfolst.append(frdinfo)
        else:
            print(f'不存在UserName键值')
    print(f"{len(frdinfolst)}")
#     attrlst.insert(0, 'contactuuid')

    if needheadimg:
        attrlst.extend(['imguuid', 'headimg'])
#     attrlst.extend(['imguuid', 'headimg', 'appendtime'])
#     print(attrlst)
    frddf = pd.DataFrame(frdinfolst, columns=attrlst)
    
    return frddf

# getwcdffromfrdlst(frdlst, haveheadimg=True)

readfromfrddf = getwcdffromfrdlst(frdlst, needheadimg=True)
readfromfrddf
imgforsample = readfromfrddf.loc[2, 'imguuid']
imgforsample
# sha2hexstr(imgforsample)
# getwcdffromfrdlst(frdlst)
# getwcdffromfrdlst(frdlst, (len(frdlst) - 8, 3))
# -
# ##### 对比从网上取回来的图片bytes值

readfromfrddf = getwcdffromfrdlst(frdlst, needheadimg=True)
readfromfrddf
imgforsample1 = readfromfrddf.loc[2, 'imguuid']

# **比较一下看，没有一个True**

type(imgforsample)
len(imgforsample)
len(imgforsample1)
id(imgforsample)
id(imgforsample1)
imgforsample == imgforsample1
# imgforsample.hex() == imgforsample1.hex()
# type(imgforsample1.hex()[:200])
# imgforsample1.hex()[:200]

# ##### 从bytes直接显示图片

# +
from io import BytesIO

def showpngimgfrombytes(inputbytes: bytes):
    imgfrombytes = Image.open(BytesIO(inputbytes))
#     print(imgfrombytes._getexif()) # 拉回来的bytes中不包含任何exif值
#     print(sha3hexstr(imgfrombytes.getdata())) # 但是data就是不一样啊
#     print(sha3hexstr(imgfrombytes)) # bytes图片数据集就更不用说了，就是不一样
    # 转成array格式——常规
    simgnp = np.array(imgfrombytes)
    print(sha3hexstr(simgnp)) # 尼玛，转换成np数组倒是终于一样了^_^。我的老天爷啊！好吧
#     imgbytestmp = BytesIO()
#     imgfrombytes.save(imgbytestmp, format='PNG')
#     print(sha3hexstr(imgbytestmp.getvalue()))
    # 展示array代表的图像
    plt.imshow(simgnp)
#     plt.show()
    imgtmppath = getdirmain() / 'img' / 'wcheadimg.png'
    plt.savefig(imgtmppath)
    print(sha3hexstr(np.array(Image.open(imgtmppath)))) # 非得写入文件，再提取回来序列值就一样了，唉


# + jupyter={"source_hidden": true, "outputs_hidden": true}
showpngimgfrombytes(imgforsample)
showpngimgfrombytes(imgforsample1)
showpngimgfrombytes(imgforsample2)

# + [markdown] jupyter={"source_hidden": true}
# ##### 强力再参

# + jupyter={"source_hidden": true, "outputs_hidden": true}
showpngimgfrombytes(imgforsample)
showpngimgfrombytes(imgforsample1)
showpngimgfrombytes(imgforsample2)

# + [markdown] jupyter={"source_hidden": true}
# ##### 老规矩，留参

# + jupyter={"source_hidden": true, "outputs_hidden": true}
showpngimgfrombytes(imgforsample)
showpngimgfrombytes(imgforsample1)
showpngimgfrombytes(imgforsample2)


# -

# #### 联系人信息存入数据库中相应数据表

# ##### 不包含headimg、imguuid的其他列生成uuid

# +
def dfsha2noimg(inputdf: pd.DataFrame):
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'imguuid', 'headimg']
    frddf2append = inputdf.copy()
#     print(frddf2append.dtypes)
    # [NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'imguuid']
    clnamescleanlst = [cl for cl in list(frddf2append.columns.values) if cl.lower() not in ['username', 'imguuid', 'headimg']]
    print(clnamescleanlst)
#     frddf2appendnoimguuid = frddf2append.loc[:, clnamescleanlst]
    frddf2append['contactuuid'] = frddf2append[clnamescleanlst].apply(lambda x: sha2hexstr(list(x.values)), axis=1)
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'headimg', 'appendtime']
    frddf2append['appendtime'] = pd.Timestamp.now()
    
    return frddf2append

# %time 
dfneedsha = getwcdffromfrdlst(frdlst, needheadimg=True)
outputdf = dfsha2noimg(dfneedsha)
outcls = [cl for cl in list(outputdf.columns.values) if cl.lower() not in ['username', 'headimg']]
outputdf[outcls]


# -

# ###### 【*用于修复*】重置contactuuid更新入数据库。~~后来才想起来是无用功！！！~~逻辑上没有任何价值！！！

def dfsha2noheadjustforfix(inputdf: pd.DataFrame):
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'imguuid', 'headimg']
    frddf2append = inputdf.copy(deep=True)
#     print(frddf2append.dtypes)
    # [NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'imguuid']
    clnamescleanlst = [cl for cl in list(frddf2append.columns.values) if cl.lower() not in ['username', 'imguuid', 'headimg', 'appendtime']]
    print(clnamescleanlst)
#     frddf2appendnoimguuid = frddf2append.loc[:, clnamescleanlst]
    frddf2append['contactuuid'] = frddf2append[clnamescleanlst].apply(lambda x: sha2hexstr(list(x.values)), axis=1)
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'headimg', 'appendtime']
#     frddf2appendnoimguuid['appendtime'] = pd.Timestamp.now()
    
    return frddf2append
# %time 
# dfneedsha = getwcdffromfrdlst(frdlst, needheadimg=True)
# dfneedsha
dfsha2noheadjustforfix(frdfromdbforfix)


# ~~坑坑坑，划掉dfuuid3nohead~~

# + jupyter={"outputs_hidden": true, "source_hidden": true}
def dfuuid3nohead(inputdf: pd.DataFrame):
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'imguuid', 'headimg']
    frddf2append = inputdf.copy(deep=True)
    # [NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord']
    clnamescleanlst = [cl for cl in list(frddf2append.columns.values) if cl.lower() not in ['username', 'headimg']]
#     print(clnamescleanlst)
    frddf2appendnoimguuid = frddf2append.loc[:, clnamescleanlst]
    frddf2appendnoimguuid['contactuuid'] = frddf2appendnoimguuid[clnamescleanlst].apply(lambda x: uuid3hexstr(list(x.values)), axis=1)
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'headimg', 'appendtime']
    frddf2appendnoimguuid['appendtime'] = pd.Timestamp.now()
    
    return frddf2appendnoimguuid
# %time
dfuuid3nohead(getwcdffromfrdlst(frdlst))


# -

# ##### 所有列（包含headimg）生成uuid（变动）

# 小函数测试uuid从多少长度开始变异

def testuuidlen(inputdf: pd.DataFrame):
    frddf2append = inputdf.copy(deep=True)
    # frddf2append = frddf
    frddf2append['contactuuid'] = frddf2append.apply(lambda x: uuid3hexstr(list(x.values)), axis=1)
    print(frddf2append[['NickName', 'contactuuid']])


# 传入获取的同一个DataFrame时不会出现uuid异常

# + jupyter={"outputs_hidden": true, "source_hidden": true}
frdwithimguuid = getwcdffromfrdlst(frdlst)
testuuidlen(frdwithimguuid)
testuuidlen(frdwithimguuid)

# + [markdown] jupyter={"source_hidden": true}
# 但是，如果每次都生成一个新的DataFrame则结果就不一样了

# + jupyter={"outputs_hidden": true, "source_hidden": true}
frdwithimguuid = getwcdffromfrdlst(frdlst)
testuuidlen(frdwithimguuid)

testuuidlen(getwcdffromfrdlst(frdlst))

# + [markdown] jupyter={"source_hidden": true}
# ##### 所有列（包含headimg）生成uuid（参照）

# + jupyter={"source_hidden": true, "outputs_hidden": true}
frddf2append = frddf.copy(deep=True)
frddf2append['contactuuid'] = frddf2append.apply(lambda x: uuid3hexstr(list(x.values)), axis=1)
frddf2append
# -

# ##### 【DataFrame写入相应数据库，依赖数据表定义约束记录唯一】
# ```sql
# create table wccontact (id INTEGER PRIMARY KEY AUTOINCREMENT, contactuuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, nickname TEXT, contactflag int, remarkname TEXT, sex int, signature TEXT, starfriend int, attrstatus int, province TEXT, city TEXT, snsflag int, keyword TEXT, imguuid text, appendtime datetime)
# ```
# DataFrame的to_sql()函数中参数if_exists如果是"append"则根据数据表数据结构定义增添新数据

# ###### 联系人信息入库

owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
dftablename = 'wccontact'
conn = lite.connect(dbname)
frddfready = dfsha2nohead(getwcdffromfrdlst(frdlst, len(frdlst) - 10))
frddfready.to_sql(dftablename, con=conn, if_exists='append', index=False)
conn.close()

# ###### 【**修复改变数据库结构后的数据专用**】

owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
dftablename = 'wccontact'
conn = lite.connect(dbname)
frddfready = dfsha2noheadjustforfix(getwcdffromfrdlst(frdlst, len(frdlst) - 10))
frddfready.to_sql(dftablename, con=conn, if_exists='append', index=False)
conn.close()

# ###### 头像数据入库

# frddfready = readfromfrddf[readfromfrddf.imguuid.notnull()].loc[:, ['RemarkName', 'imguuid', 'headimg']]
frddfready = readfromfrddf[readfromfrddf.imguuid.notnull()][['RemarkName', 'imguuid', 'headimg']]
frddfready

owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
dftablename = 'wcheadimg'
conn = lite.connect(dbname)
frddfready = readfromfrddf[readfromfrddf.imguuid.notnull()].loc[:, ['RemarkName', 'imguuid', 'headimg']]
frddfready.to_sql(dftablename, con=conn, if_exists='append', index=False)
conn.close()

# ##### 【遍历所有联系人并判断存入】

# 【生成数据段】

width = 150
spllst = [(i * width, width) for i in range((len(frdlst) // width) +1)]
spllst

# 【存入数据，按照分好的段】

owner = '白晔峰'
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
dftablename = 'wccontact'
# %time
for sltuple in spllst[3:]:
    conn = lite.connect(dbname)
    frddfready = dfuuid3nohead(getwcdffromfrdlst(frdlst, sltuple))
    frddfready.to_sql(dftablename, con=conn, if_exists='append', index=False)
    conn.close()
# %time

# #### 从数据库中读取

owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
dftablename = 'wccontact'
conn = lite.connect(dbname)
frddfread = pd.read_sql(f'select * from {dftablename}', con=conn, parse_dates=['appendtime']).set_index('id')
conn.close()
frddfread

str(frddfread[list(frddfread)[1:]].tail(10).values)

# ##### 找出remarkname重复的记录

frdgrpun = frddfread.groupby('remarkname', as_index=False).count()
frdtmp = frdgrpun[frdgrpun.contactuuid > 1]
frdtmp

# #### 用sql语句处理数据记录

# ##### 从DataFrame中准备数据记录列表

# +
frddf = getwcdffromfrdlst(frdlst)
cinfolst = frddf.values
clnames = frddf.columns
print(list(clnames.values)[:-1])
cinforeadylst = list()
for ix in frddf.index[:10]:
    cinfocleanlst = list(frddf.loc[ix].values[:-1])
#     print(cinfocleanlst)
    cuuid = uuid3hexstr(cinfocleanlst)
#     print(ix, cuuid)
    cinfocleanlst.insert(0, cuuid)
    print(cinfocleanlst)
    cinforeadylst.append(cinfocleanlst)

print(cinforeadylst)
# -

# ##### 尝试用sql语句写入数据表
# 因为有数据表结构定义约束，contactuuid重复的记录不会计入数据表

owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
tablename_cc = 'wccontact'
try:
    conn = lite.connect(dbname)
    cursor = conn.cursor()
    insertsql = f"insert into {tablename_cc} (contactuuid, username, nickname, contactflag, remarkname, sex, signature, starfriend, attrstatus, province, city, snsflag, keyword) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    print(f"插入sql语句：\t{insertsql}")
    for item in cinforeadylst:
        cursor.execute(insertsql, item)
        
    print(f"数据表《{tablename_cc}》中有{conn.total_changes}条记录发生变化（增删改）")
    conn.commit()
except lite.IntegrityError as lie:
    log.critical(f"键值重复错误\t{lie}")
finally:
    conn.close()

# ##### 用sql语句提取数据记录生成DataFrame

# +
owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
tablename_cc = "wcheadimg"
conn = lite.connect(dbname)
try:
    cursor = conn.cursor()
    searchsql = f"select * from {tablename_cc} limit 5"
    print(searchsql)
    cursor.execute(searchsql)
    tablefinds = cursor.fetchall()
    print(f"成功查询出信息。{searchsql}")
    conn.commit()
except lite.IntegrityError as lie:
    log.critical(f"键值重复错误\t{lie}")
finally:
    conn.close()
 
# clnmlst = ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'headimg']
# clnmlst.insert(0, 'contactuuid')
# clnmlst.insert(0, 'id')

uccdf = pd.DataFrame(tablefinds)
uccdf
# -

# #### 处理头像提取正常的联系人信息

# +
register_matplotlib_converters()

# print(uuid.uuid1())
# hilst = uccdf[['UserName', 'headimg']].values
hilst = uccdf[[1, 3]].values
# print(len(hilst))
hionlylst = [[nm, getimguuid(hi), hi] for nm, hi in hilst if len(hi) > 0]
# print(hionlylst)
print([x[:2] for x in hionlylst])
# print(hionlylst)
for nm, *tmp, hi in hionlylst:
    print(nm)
#     hiu = unhexlify(hi)
    imgfrombytes = Image.open(BytesIO(hi))
    # 转成array格式——常规
    imgnp = np.array(imgfrombytes)
    # 展示array代表的图像
    plt.imshow(imgnp)
    plt.axis('off') # 不显示坐标轴
    plt.show()
    print()
# -

# ##### 存入头像数据库

# +
tablenamehead = "wcheadimg"

try:
    conn = lite.connect(dbname)
    cursor = conn.cursor()
    insertsql = f"insert into {tablenamehead} (remarkname, imguuid, headimg) values(?, ?, ?)"
    print(f"插入sql语句：\t{insertsql}")
#             paratuple = (f"{frd['UserName']}", f"{id}", lite.Binary(headimg),)
    for item in hionlylst:       
        print(f"headimg的内存地址为：\t{memoryview(item[2])}")
        cursor.execute(insertsql, item)
#             print(type(conn), conn)
    print(f"数据表《{tablenamehead}》中有{conn.total_changes}条记录发生变化（增删改）")
    conn.commit()
except lite.IntegrityError as lie:
    log.critical(f"键值重复错误\t{lie}")
finally:
    conn.close()
# -

# ##### 从数据库中提取出来，显示图像

# +
register_matplotlib_converters()
tablenamehead = "wcheadimg"
import pandas as pd
conn = lite.connect(dbname)
try:
    cursor = conn.cursor()
    searchsql = f"select * from {tablenamehead}"
    print(searchsql)
    cursor.execute(searchsql)
    tablefinds = cursor.fetchall()
    print(f"成功查询出信息。{searchsql}")
    conn.commit()
except lite.IntegrityError as lie:
    log.critical(f"键值重复错误\t{lie}")
finally:
    conn.close()
    
uimgdf = pd.DataFrame(tablefinds, columns=['id', 'remarkname', 'imguuid', 'headimg']).set_index('id')
print(uimgdf.dtypes)
uimgdf
# -

print(uimgdf.shape[0])
for ix in uimgdf.index:
    print(uimgdf.loc[ix, ['remarkname']].values[0])
#     simghfl = uimgdf.loc[ix, ['imghfl']].values[0]
#     simguhfl = unhexlify(simghfl)
    headimgin = uimgdf.loc[ix, ['headimg']].values[0]
    imgfrombytes = Image.open(BytesIO(headimgin))
    # 转成array格式——常规
    simgnp = np.array(imgfrombytes)
    # 展示array代表的图像
    plt.imshow(simgnp)
    plt.axis('off') # 不显示坐标轴
    plt.show()
    print('\n')

# #### QR图像显示

# +
import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
 
lena = mpimg.imread('../QR.png') # 读取和代码处于同一目录下的 lena.png
# 此时 lena 就已经是一个 np.array 了，可以对它进行任意处理
print(lena.shape) #(512, 512, 3)
plt.imshow(lena) # 显示图片
plt.axis('off') # 不显示坐标轴
plt.show()
