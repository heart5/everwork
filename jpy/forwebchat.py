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

# ## 火界

# ### 处理sharing中的开房信息

# +
import re
fangurl = "http://s0.lgmob.com/h5_whmj_qp/?d=217426"

ptnfang = re.compile("http://s0.lgmob.com/h5_whmj_qp/\\?d=(\d+)")
re.findall(ptnfang, fangurl)[0]
# -

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
    from life.wcdelay import getdelaydb, showdelayimg
    from func.litetools import ifnotcreate, showtablesindb, droptablefromdb, compact_sqlite3_db
    from func.wrapfuncs import timethis, logit
    from func.logme import log
    from func.sysfunc import uuid3hexstr, sha2hexstr
    from life.wccontact import updatectdf, getctdf, getownername
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
import pathmagic
with pathmagic.context():
    from life.wccontact import updatectdf, getctdf
    
updatectdf()
# -

# ##### 提取所有数据用于分析（留个备份）

frdfromdbrecords = getctdf()
frdfromdbrecords.shape[0]
frdfromdbrecords.dtypes
frdfromdbforfix = frdfromdbrecords.copy(deep=True)


# + [markdown] toc-hr-collapsed=true toc-nb-collapsed=true
# ### 输出结果处理
# -

# frdfromdb = frdfromdbrecords[frdfromdbrecords['imguuid'].notnull()].copy(deep=True)[list(frdfromdbrecords)]
frdfromdb = frdfromdbrecords.copy(deep=True)
frdfromdb

# + [markdown] toc-hr-collapsed=true toc-nb-collapsed=true jupyter={"source_hidden": true}
# #### *剔除无效数据，只保留有用的历史记录，并回填数据库中相应的数据表*
# -

# ##### 抛开变动列（contactuuid、appendtime和imguuid）根据前列去重，保留最早的记录

list(frdfromdb)[1:-2]
frddfafterdropduplites = frdfromdb.drop_duplicates(list(frdfromdb)[1:-2], keep='first')
frddfafterdropduplites


# ##### 更新contactuuid

# +
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
# -

# ##### 【删除该数据表，按结构重构】

# ##### 回填数据

owner = getownername()
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
dftablename = 'wccontact'
conn = lite.connect(dbname)
dfcleanafterupdatecontactuuid.to_sql(dftablename, con=conn, if_exists='append', index=False)
conn.close()

# #### 处理结果并输出简版的结果

# ##### 填充remarkname为空的记录（用nickname填充）

frdfromdb['remarkname'] = frdfromdb[['nickname', 'remarkname']].apply(lambda x: x.nickname if x.remarkname == '' else x.remarkname, axis=1)
# frdfromdb['appendtime'] = frdfromdb['appendtime'].apply(lambda x: pd.to_datetime(x.strftime("%y-%m-%d %H:%m")))
outdfraw = frdfromdb.copy(deep=True)
outdfraw

# ##### ~~过滤出有更改（appendtime有不止一个记录）的记录~~

# + [markdown] jupyter={"source_hidden": true}
# 逻辑失误，要先查找n天内有痕迹的记录就行，不用刻意判断是否有多条记录（当然，这个在数据初始化刚开始产生新记录时刻意降低一些冗余显示，但那又是另外一套逻辑了）

# + jupyter={"source_hidden": true, "outputs_hidden": true}
havechanged = outdfraw.groupby('remarkname').nunique()['appendtime'] > 2
# havechanged
hcds = havechanged[havechanged]
# hcds.index
outdfmulti = outdfraw.loc[outdfraw['remarkname'].isin(list(hcds.index))].copy(deep=True)
outdfmulti
# -

# ##### 过滤出最近一次修改是n天内发生的更改记录

id(outdfraw)
outdfmulti = outdfraw.copy(deep=True)
startpoint = pd.Timestamp.now() + pd.Timedelta('-1d')
startpoint
dsfortime = outdfmulti.groupby('remarkname').last()['appendtime']
outready = outdfmulti.loc[outdfmulti['remarkname'].isin(list(dsfortime[dsfortime > startpoint].index))]
outready

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

outclean = outready.groupby(['remarkname', 'appendtime']).first().sort_index(ascending=[True, False])
# outclean.dtypes
outclean[list(outclean)[1:-1]]

# frdfromdb.groupby('contactflag').agg(['unique'])
frdfromdb.groupby('contactflag').nunique()

frdfromdb[frdfromdb.contactflag == 515]

frdfromdb[frdfromdb.remarkname == '张玉']
frdfromdb[frdfromdb.nickname == 'KI']
frdfromdb[frdfromdb.starfriend == 1]

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
# -
# ## 消息处理


global innermsg
@itchat.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING, ATTACHMENT, VIDEO])
def handler_receive_msg(msg):
    global innermsg
    innermsg = msg


itchat.run()

innermsg


