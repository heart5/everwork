# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %% [markdown]
# # sqlite学习笔记

# %% [markdown]
# ## 库准备

# %%
import sqlite3 as lite

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.logme import log
    from func.litetools import ifclexists
    
logstr = f"I\' ready for sqlite3 study."
log.info(logstr)

testdb = getdirmain() / 'data' / 'db' / 'just4test.db'

def dbsql(dbin, csqlin):
    """
    在指定数据库连接中执行sql语句，通过cursor
    """
    conn = lite.connect(dbin)
    cursor = conn.cursor()
    cursor.execute(csqlin)
    conn.commit()
    tcs = conn.total_changes
    logstr = f"数据库{dbin}中有{tcs}行数据被影响"
    log.info(logstr)
    conn.close()
    



# %% [markdown]
# ## 连接数据库文件并创建数据表

# %%
csql = "create table if not exists heart5 (id integer primary key autoincrement, name text, age int)"
dbsql(testdb, csql)

# %% [markdown]
# ## 删除数据表

# %%
dsql = "drop table heart5"
dbsql(testdb, dsql)


# %% [markdown]
# ## 显示数据库内容，数据表等

# %%
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


# %%
owner = '白晔峰'
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
print(dbname)
showtablesindb(dbname)
showtablesindb(testdb)

# %% [markdown]
# ## 查询数据表结构，返回列名是否存在，显示数据表的字段结构

# %%
import re

def ifclexists(dbin, tb, cl):
    conn = lite.connect(dbin)
    cursor = conn.cursor()
    structsql = f"SELECT sql FROM sqlite_master WHERE type = 'table' AND tbl_name = '{tb}';"
    tablefd = cursor.execute(structsql).fetchall()
    # [('CREATE TABLE heart5 (id integer primary key autoincrement, name text, age int, imguuid text)',)]
    conn.commit()
    tcs = conn.total_changes
    print(tcs)
    conn.close()

    if len(tablefd) == 0:
        print(f"数据表{tb}不存在")
        return False
              
    createsql =  [name for x in tablefd for name in x][0]
    print(createsql)
    ptn = re.compile("\((.+)\)")
    print(re.findall(ptn, createsql)[0])
    rstsplst = re.findall(ptn, createsql)[0].split(',')
    print([x.strip() for x in rstsplst])
    finallst = [x.strip().split()[:2] for x in rstsplst]
    print(finallst)
    targetdict = dict(finallst)
    if cl in targetdict:
        print(f"列{cl}已经在数据表{tb}中存在")
        return True
    else:
        print(f"列{cl}在数据表{tb}中尚未存在，可以新增")
        return False
    



# %%
ifclexists(testdb, 'heart5', 'imguuid')

# %% [markdown]
# ## 改变数据表结构，增加新列

# %%
if not ifclexists(testdb, 'heart5', 'imguuid'):
    asql = "alter table heart5 add column imguuid text"
    dbsql(testdb, asql)

# %%
owner = '白晔峰'
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"wccontact_{owner}.db")
print(dbname)

if not ifclexists(dbname, 'wccontact', 'imguuid'):
    asql = "alter table wccontact add column imguuid text"
    dbsql(dbname, asql)
# %%

