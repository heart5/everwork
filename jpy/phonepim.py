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

# # 手机个人信息管理

# ## 库准备

# +
import os
import itchat
import pandas as pd
import numpy as np
import re
import sqlite3 as lite
import time

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath, touchfilepath2depth, getdirmain
    from life.wcdelay import showdelayimg
    from life.phonecontact import getphoneinfodb, checkphoneinfotable
    from func.pdtools import lststr2img
    from func.sysfunc import sha2hexstr, set_timeout, after_timeout
    from etc.getid import getdeviceid
    from func.termuxtools import *
    from func.litetools import droptablefromdb, ifnotcreate
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from life.phonecontact import showphoneinfoimg
# -

# ## 综合输出

# +
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"phonecontact_{getdeviceid()}.db")

tablename="phone"
checkphoneinfotable(dbname)

conn = lite.connect(dbname)
recorddf_back = pd.read_sql(f"select * from {tablename}", con=conn)
tablename = 'sms'
recordsms_back = pd.read_sql(f"select type, sent, name, number, time, content from {tablename}", con=conn)
conn.close()
# -

ctdf = recorddf_back.copy(deep=True)
ctdf.dtypes
ctdf
smsdf = recordsms_back.copy(deep=True)
smsdf.dtypes

namestr = "范小华"
findset = set(ctdf[ctdf.name.str.contains(namestr).values == True]['number'])
findset

print(smsdf[smsdf.number.isin(findset)].sort_values('time', ascending=False).to_string())

# ## 联系人

# ### 输出成果

jujinm, ctdf = getphoneinfodb()

showphoneinfoimg(showincell=True)

# ### 数据转库

# +
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "phonecontact.db")
# dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"phonecontact_{getdeviceid()}.db")

tablename="phone"
checkphoneinfotable(dbname)

conn = lite.connect(dbname)
recordctdf_back = pd.read_sql(f"select * from {tablename}", con=conn)
conn.close()
# -

ctdonedf = recordctdf_back
ctdonedf

droptablefromdb(dbname, 'phone', confirm=True)

# 联系人数据表检查构建
if not (phonecontactdb := getcfpoptionvalue('everpim', str(getdeviceid()), 'phonecontacttable')) or True:
    tablename = "phone"
    print(phonecontactdb, tablename)
    csql = f"create table if not exists {tablename} (number str PRIMARY KEY not null unique on conflict ignore, name str, appendtime datetime)"
    ifnotcreate(tablename, csql, dbname)
    setcfpoptionvalue('everpim', str(getdeviceid()), 'phonecontacttable', str(True))
    logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
    log.info(logstr)

dbname

dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"phonecontact_{getdeviceid()}.db")
tablename="phone"
conn = lite.connect(dbname)
ctdonedf.to_sql(tablename, con=conn, if_exists="append", index=False)
conn.close()

# ## 短信和通话记录

# ### 读取所有记录并留存备份df

# +
# dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "phonecontact.db")
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"phonecontact_{getdeviceid()}.db")

tablename="sms"
checkphoneinfotable(dbname)

conn = lite.connect(dbname)
recordctdf_back = pd.read_sql(f"select * from {tablename}", con=conn)
conn.close()
# -

# ### 深度拷贝（用于分析）并显示概貌

recordctdf = recordctdf_back.copy(deep=True)
recordctdf

# ### 找出mysms中标题栏目只有两项导致错位的记录

recordctdf[recordctdf.number.str.contains('\(\d{1,2}/\d{4}\)').values == True]

recordctdf[recordctdf.number.str.contains('\(\D').values == True]

# ### 修正number栏目

witherrordf = recordctdf[recordctdf.number.str.contains('\(\d{1,2}/\d{4}\)').values == True]
list(witherrordf.index.values)

for ix in list(witherrordf.index.values):
    recordctdf.loc[ix, 'number'] = recordctdf.loc[ix, 'name']

recordctdf

# ### 规范number中的数据（其实就是去除可能的前缀+86或者86）

import re
recordctdf['number'] = recordctdf['number'].apply(lambda x: re.sub('^\+?(86)', "", str(x)) if len(str(x)) > 8 else str(x))

recordctdf

# ### 重构uuid（不再包含name列）

recordctdf['smsuuid'] = recordctdf[['sent', 'number', 'time', 'content']].apply(lambda x: sha2hexstr(list(x.values)), axis=1)

recordctdf

# ### 检查重复项

recordctdf[recordctdf['smsuuid'].duplicated().values == False]

chongfudf = recordctdf[recordctdf['smsuuid'].duplicated().values == True]

recordctdf[recordctdf.smsuuid.isin(list(chongfudf['smsuuid'])).values == True].sort_values('smsuuid')

smsdonedf = recordctdf.drop_duplicates('smsuuid')
smsdonedf

getdeviceid()

# ### 【数据清洗入库】

# #### 新数据库文件名

dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"phonecontact_{getdeviceid()}.db")
dbname

# #### 在新的数据文件中构建表

if not (phonecontactdb := getcfpoptionvalue('everpim', str(getdeviceid()), 'phonesmstable')) or True:
    tablename = "sms"
    print(phonecontactdb, tablename)
    # smsdfdone.columns = ['sent', 'sender', 'number', 'time', 'content', 'smsuuid']
    csql = f"create table if not exists {tablename} (type str,sent bool, name str, number str, time datetime, content str,smsuuid str PRIMARY KEY not null unique on conflict ignore)"
    ifnotcreate(tablename, csql, dbname)
    setcfpoptionvalue('everpim', str(getdeviceid()), 'phonesmstable', str(True))
    logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
    log.info(logstr)

# #### 整理后的sms和call记录入库

conn = lite.connect(dbname)
smsdonedf.to_sql(tablename, con=conn, if_exists="append", index=False)
conn.close()


