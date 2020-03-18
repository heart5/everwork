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

# ### 库准备

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

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from life.wcdelay import getdelaydb, showdelayimg
    from func.litetools import ifnotcreate
    from func.wrapfuncs import timethis, logit
    from func.logme import log


# -

# #### 小函数

# ##### 输出输入对象的UUID

# +
def uuid3hexstr(inputo: object):
#     inputstr = str(inputo)[:767]
    inputstr = str(inputo)
#     print(f"输入对象str化后长度为：{len(inputstr)}")
    uuidout = uuid.uuid3(uuid.NAMESPACE_URL, inputstr)

    return hex(hash(uuidout))[2:].upper()

strlst4text = [list(), tuple(), '微信', 'heart5', 'blog', '生产力', ['12', '23'], 'blog', '生产力', ('12', '23'), None, None, 123, 321, '12', '12']
for itm in strlst4text:
    pass
# -

uuidnsulst = ['heart5.com', 'python.com', 'jing.com']
for item in strlst4text:
    for nsu in uuidnsulst:
        print(nsu, item, uuid.uuid3(uuid.NAMESPACE_URL, str(item)))


# ##### 显示数据库文件中数据表信息

# +
def showtablesindb(dbname: str):
    conn = lite.connect(dbname)
    cursor = conn.cursor()
    tbnsql = f"SELECT tbl_name FROM sqlite_master WHERE type = 'table';"
    tablefd = cursor.execute(tbnsql).fetchall()
#     print(tablefd)
    tablesnamelst = [name for x in tablefd for name in x]
    print(tablesnamelst)
    for tname in tablesnamelst:
        structsql = f"SELECT sql FROM sqlite_master WHERE type = 'table' AND tbl_name = '{tname}';"
        tablefd = cursor.execute(structsql).fetchall()
        print(tname+":\t", [name for x in tablefd for name in x][0])
    conn.commit()
    tcs = conn.total_changes
    print(tcs)
    conn.close()

owner = '白晔峰'
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
showtablesindb(dbname)
# -

# #### 热启动微信服务

pklabpath = os.path.relpath(touchfilepath2depth(getdirmain() / 'itchat.pkl'))
print(pklabpath)
itchat.auto_login(hotReload=True, statusStorageDir=pklabpath)   #热启动你的微信

# ##### `itchat.web_init()`

# 初始化，成功则返回值为0，内容包括：

#     1. BaseResponse。0是成功，返回的错误信息为空字符串；否则
#     2. Count。待显示的最近联系人数量。
#     3. ContactList。最近联系人信息。
#     4. SyncKey。同步口令。有数量count，还有信息id？
#     5. User。登录者信息。
#     6. Chatset。聊天集？
#     7. 'SKey': '@crypt_8dc3f7b8_e63df55a027c431016c33d3135f2d9fa'
#     8. 'ClientVersion': 654314551,
#     9. 'SystemTime': 1584465493,
#     10. 'GrayScale': 1,
#     11. 'InviteStartCount': 40,
#     12. 'MPSubscribeMsgCount': 4, 待显示的公众号数量
#     13. 'MPSubscribeMsgList': 公众号信息列表
#     14. 'ClickReportInterval': 600000

# + jupyter={"outputs_hidden": true}
itchat.web_init()
# -

# ##### `itchat.get_contact()`

# 群列表。好像是所有群，就是不知道是按照什么顺序排列的，还是随意排？！

# + jupyter={"outputs_hidden": true}
ctlst = itchat.get_contact(update=True)
len(ctlst)
# [ct for ct in ctlst if ct['NickName'] == '白晔峰']
ctlst
# -

# ##### `itchat.originInstance.HotReloadDir`

# 热启动的pkg文件地址。

itchat.originInstance.hotReloadDir

os.path.abspath(itchat.originInstance.hotReloadDir)

uuid3hexstr(os.path.abspath(itchat.originInstance.hotReloadDir))

itchat.originInstance.receivingRetryCount

itchat.originInstance.loginInfo

dict(itchat.originInstance.loginInfo['User'])

itchat.originInstance.loginInfo

itchat.load_login_status('../itchat.pkl')



# #### 获取联系人列表
# 随机显示几个

frdlst = itchat.get_friends()
print(len(frdlst))
[fd for fd in frdlst if fd['NickName'] == 'heart5']
print('\n')
ranslice = random.sample(range(len(frdlst)), 5)
print(ranslice)
for i in ranslice:
    print(frdlst[i], '\n')

# #### 构造数据和相应数据表

# +
owner = 'heart5'
owner = '白晔峰'
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
from func.litetools import compact_sqlite3_db

compact_sqlite3_db(dbname)
# -

tablename = "wccheadimg"
csql = f"create table {tablename} (himgid INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT not null, himguuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, headimg BLOB NOT NULL)"
# conn = lite.connect(dbname)
# cursor = conn.cursor()
# cursor.execute(f'drop table {tablename}')
# # cursor.execute(f'drop table cinfo')
# conn.commit()
# tcs = conn.total_changes
# print(tcs)
# conn.close()
ifnotcreate(tablename, csql, dbname)

tablename_cc = "wccontact"
csql = f"create table {tablename_cc} (id INTEGER PRIMARY KEY AUTOINCREMENT, contactuuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, username TEXT not null, nickname TEXT, contactflag int, remarkname TEXT, sex int, signature TEXT, starfriend int, attrstatus int, province TEXT, city TEXT, snsflag int, keyword TEXT, headimg BLOB)"
# conn = lite.connect(dbname)
# cursor = conn.cursor()
# cursor.execute(f'drop table {tablename_cc}')
# conn.commit()
# tcs = conn.total_changes
# print(tcs)
# conn.close()
ifnotcreate(tablename_cc, csql, dbname)


# #### 查验数据并提取有用信息到list以及DataFrame中

# +
def getwcdffromfrdlst(frdlst: list, howmany: str = 'fixed'):
    if howmany.lower() == 'random':
        rang = random.sample(range(len(frdlst)), 5)
    elif howmany.lower() == 'fixed':
        rang = range(0, 5)
    elif howmany.lower() == 'all':
        rang = range(len(frdlst))
    else:
        log.critical(f"{howmany}不是合法的参数")
        return
    
    frdinfolst = list()
    attrlst = ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord']
    for ix in rang:
        frd = frdlst[ix]
        frdinfo = list()
        if 'UserName' in frd.keys():
            try:
                for attr in attrlst:
                    frdinfo.append(frd[attr])
    #                 print(attr, type(frd[attr]), frd[attr])
                # 显示所有key和value
        #         for key, value in frd.items():
        #             print(key, type(value), value)
            except Exception as eeee:
                log.critical(f"第【{ix}/{len(frdlst)}】条记录存在问题。{frd['NickName']}\t{frd['UserName']}\t{eeee}")
                continue

            headimg = itchat.get_head_img(frd["UserName"])
            frdinfouuiswithnohead = uuid3hexstr(frdinfo)
            print(f"【{ix}/{len(frdlst)}】【{frdinfouuiswithnohead}】{frd['NickName']}\t{frd['RemarkName']}\t{frd['UserName']}\theadimg的长度为：\t{len(headimg)}。", end='\t')
            frdinfo.append(headimg)
#             frdinfo.append(hexlify(headimg).decode())

            if (iblen := len(headimg)) == 0:
                print(f"图像获取失败！")
                pass
            else:
#                 print(f"内容示意：\t{headimg[:15]}")
                print()
                pass
            frdinfolst.append(frdinfo)
        else:
            print(f'不存在UserName键值')
    print(f"{len(frdinfolst)}")
    attrlst.append('headimg')
#     print(attrlst)
    frddf = pd.DataFrame(frdinfolst, columns=attrlst)
    
    return frddf

frddf = getwcdffromfrdlst(frdlst)


# -
# #### 联系人信息存入数据库中相应数据表

# ##### 不包含headimg的其他列生成uuid

def dfuuid3nohead(inputdf: pd.DataFrame):
    frddf2appendnoimguuid = inputdf.copy(deep=True)
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'headimg']
    clnamescleanlst = list(frddf2appendnoimguuid.columns.values)[1:-1]
    print(clnamescleanlst)
    frddf2appendnoimguuid['contactuuid'] = frddf2appendnoimguuid[clnamescleanlst].apply(lambda x: uuid3hexstr(list(x.values)), axis=1)
    
    return frddf2appendnoimguuid
dfuuid3nohead(getwcdffromfrdlst(frdlst))


# ##### 所有列（包含headimg）生成uuid（变动）

# 小函数测试uuid从多少长度开始变异

def testuuidlen(inputdf: pd.DataFrame):
    frddf2append = inputdf.copy(deep=True)
    # frddf2append = frddf
    frddf2append['contactuuid'] = frddf2append.apply(lambda x: uuid3hexstr(list(x.values)), axis=1)
    print(frddf2append[['NickName', 'contactuuid']])


# 传入获取的同一个DataFrame时不会出现uuid异常

frdwithimguuid = getwcdffromfrdlst(frdlst)
testuuidlen(frdwithimguuid)
testuuidlen(frdwithimguuid)

# 但是，如果每次都生成一个新的DataFrame则结果就不一样了

# +
frdwithimguuid = getwcdffromfrdlst(frdlst)
testuuidlen(frdwithimguuid)

testuuidlen(getwcdffromfrdlst(frdlst))
# -

# ##### 所有列（包含headimg）生成uuid（参照）

frddf2append = frddf.copy(deep=True)
frddf2append['contactuuid'] = frddf2append.apply(lambda x: uuid3hexstr(list(x.values)), axis=1)
frddf2append

# ##### DataFrame写入相应数据库，依赖数据表定义约束记录唯一
# ```sql
# create table wccontact (id INTEGER PRIMARY KEY AUTOINCREMENT, contactuuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, username TEXT not null, nickname TEXT, contactflag int, remarkname TEXT, sex int, signature TEXT, starfriend int, attrstatus int, province TEXT, city TEXT, snsflag int, keyword TEXT, headimg BLOB)
# ```
# DataFrame的to_sql()函数中参数if_exists如果是"append"则根据数据表数据结构定义增添新数据

owner = 'heart5'
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
dftablename = 'wccontact'
conn = lite.connect(dbname)
frddfready = dfuuid3nohead(getwcdffromfrdlst(frdlst, 'all'))
frddfready.to_sql(dftablename, con=conn, if_exists='append', index=False)
conn.close()

# #### 从数据库中读取

owner = 'heart5'
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
dftablename = 'wccontact'
conn = lite.connect(dbname)
frddfread = pd.read_sql(f'select * from {dftablename}', con=conn).set_index('id')
conn.close()
frddfread

# ##### 找出username重复的记录

frdgrpun = frddfread.groupby('remarkname', as_index=False).count()
frdtmp = frdgrpun[frdgrpun.contactuuid > 1]
frdtmp

testlst = frdtmp['username'].values
for test in testlst:
    print(frddfread[frddfread['username'] == test])

liemingyuanshi = frddf.columns
liemingxin = list(liemingyuanshi)[:-1]
frddftmp = frddf[liemingxin]
frddftmp['contactuuid'] = frddftmp.apply(lambda x: uuid3hexstr(list(x.values)), axis=1)
frddftmp

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

dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "wccontact.db")
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
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "wccontact.db")
conn = lite.connect(dbname)
try:
    cursor = conn.cursor()
    searchsql = f"select * from {tablename_cc} limit 3"
    print(searchsql)
    cursor.execute(searchsql)
    tablefinds = cursor.fetchall()
    print(f"成功查询出信息。{searchsql}")
    conn.commit()
except lite.IntegrityError as lie:
    log.critical(f"键值重复错误\t{lie}")
finally:
    conn.close()
 
clnmlst = ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'headimg']
clnmlst.insert(0, 'contactuuid')
clnmlst.insert(0, 'id')

uccdf = pd.DataFrame(tablefinds, columns=clnmlst).set_index('id')
# print(uccdf.dtypes)
uccdf
# -

# ##### 处理头像提取正常的联系人信息

# +
register_matplotlib_converters()

print(uuid.uuid1())
hilst = uccdf[['UserName', 'headimg']].values
print(len(hilst))
hionlylst = [[nm, uuid3hexstr(hi), hi] for nm, hi in hilst if len(hi) > 0]
# print(hionlylst)
print(len(hionlylst))
# print(hionlylst)
for nm, *tmp, hi in hionlylst:
    print(nm)
#     hiu = unhexlify(hi)
    imgfrombytes = Image.open(BytesIO(hi))
    # 转成array格式——常规
    imgnp = np.array(imgfrombytes)
    # 展示array代表的图像
    plt.imshow(imgnp)
    plt.show()
    print()
# -

# ##### 存入头像数据库

# +
tablenamehead = "wccheadimg"

try:
    conn = lite.connect(dbname)
    cursor = conn.cursor()
    insertsql = f"insert into {tablenamehead} (username, himguuid, headimg) values(?, ?, ?)"
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
tablenamehead = "wccheadimg"
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
    
uimgdf = pd.DataFrame(tablefinds, columns=['id', 'userid', 'imguuid', 'imghfl']).set_index('id')
print(uimgdf.dtypes)
uimgdf
# -

print(uimgdf.shape[0])
for ix in uimgdf.index:
    print(uimgdf.loc[ix, ['userid']].values[0])
#     simghfl = uimgdf.loc[ix, ['imghfl']].values[0]
#     simguhfl = unhexlify(simghfl)
    headimgin = uimgdf.loc[ix, ['imghfl']].values[0]
    imgfrombytes = Image.open(BytesIO(headimgin))
    # 转成array格式——常规
    simgnp = np.array(imgfrombytes)
    # 展示array代表的图像
    plt.imshow(simgnp)
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


