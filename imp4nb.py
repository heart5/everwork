# encoding:utf-8

import pandas as pd, sqlite3 as lite, matplotlib.pyplot as plt, numpy as np,calendar as cal, random as rd, os, re, time
from pylab import *

# plot中显示中文
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

if not os.path.exists('data'):
    os.mkdir('data')
if not os.path.exists('img'):
    os.mkdir('img')


# 显示DataFrame或Series的轮廓信息
# df，DataFrame或Series
def descdb(df):
    print(len(df))
    # print(df.head(5))
    print(df.tail(5))
    print(df.dtypes)
    if type(df) == pd.DataFrame:
        print(df.columns)
        print(df.info())
    print(df.describe())


# 显示SQlite数据库的各种信息
# cnx，数据库连接
def desclitedb(cnx):
    cur=cnx.cursor()
    result = cur.execute("select * from sqlite_master")
    for ii in result.fetchall():
        print(ii)

    result = cur.execute("select name from sqlite_master where type = 'table' order by name")
    table_name_list = [tuple1[0] for tuple1 in result.fetchall()]
    print(table_name_list)
    for table in table_name_list:
        cur.execute("PRAGMA table_info(%s)" % table)
        # print (cur.fetchall())
        result = cur.execute("select * from %s" % table)
        print(len(result.fetchall()),end='\t')
        # print(cur.description)
        col_name_list = [tuple1[0] for tuple1 in cur.description]
        print (col_name_list)
