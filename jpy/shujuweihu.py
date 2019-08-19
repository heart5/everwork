# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + {"pycharm": {"is_executing": false}}
# from imp4nb import *
import os
import sys
import datetime
import pandas as pd
from datetime import datetime
from pandas.tseries.offsets import *

now =datetime.now()
print(now)
now = pd.to_datetime('2016-12-31')
yuechu = now+MonthBegin(0)
print(yuechu)
yuemo = now + MonthEnd(0)
print(yuemo)
yuediri = (now + MonthEnd()).day
print(yuediri)
nianchu = now + YearBegin(-2)
print(nianchu)
print(nianchu <= pd.to_datetime('2015-01-01'))

# + {"pycharm": {"is_executing": false}}
import sqlite3 as lite
import pathmagic
with pathmagic.context():
    from func.first import dbpathquandan

cnx = lite.connect(dbpathquandan)
br = ['柒柒湘']
qrystrz = "select 日期,strftime('%Y%m',日期) as 年月,customer.往来单位编号 as 客户编码,sum(金额) as 退货金额," \
         "substr(customer.往来单位编号,1,2) as 区域 ,"  "substr(customer.往来单位编号,12,1) as 类型, " \
         "product.品牌名称 as 品牌 from xiaoshoumingxi, customer, product " \
         "where (customer.往来单位 = xiaoshoumingxi.单位全名) " \
         "and (product.商品全名 = xiaoshoumingxi.商品全名) " \
         "and (金额 >= 0)"
for i in range(0, len(br)):
    qrystrz += ' and (品牌 = \'%s\')' %br[i]
qrystrz += ' group by 日期,客户编码 order by 日期'
print(qrystrz)

qrystrf = "select 日期,strftime('%Y%m',日期) as 年月,customer.往来单位编号 as 客户编码,sum(金额) as 退货金额," \
         "substr(customer.往来单位编号,1,2) as 区域 ,"  "substr(customer.往来单位编号,12,1) as 类型, " \
         "product.品牌名称 as 品牌 from xiaoshoumingxi, customer, product " \
         "where (customer.往来单位 = xiaoshoumingxi.单位全名) " \
         "and (product.商品全名 = xiaoshoumingxi.商品全名) " \
         "and (金额 < 0)"
for i in range(0, len(br)):
    qrystrf += ' and (品牌 = \'%s\')' %br[i]
qrystrf += ' group by 日期,客户编码 order by 日期'
print(qrystrf)

# dfz =pd.read_sql(qrystrz,cnx,parse_dates='日期')
dfz =pd.read_sql(qrystrz,cnx)
print(dfz)
# dff =pd.read_sql(qrystrf,cnx,parse_dates='日期')
dff =pd.read_sql(qrystrf,cnx)
print(dff)

cnx.close()

# +
from imp4nb import *
import pandas as pd, sqlite3 as lite
cnx = lite.connect('data\\quandan.db')
# df = pd.read_sql('select * from fileread',cnx)
# sql = "update quandan set 无货金额 = NULL where 无货金额 like '%s'" %('.') #把无货金额字段中非法字符做妥善处理
# print(sql)
# result = cnx.cursor().execute(sql)
# print(result)
# cnx.commit()
# sql = "select * from quandan where 无货金额 like '%s'" %('.')
# print(sql)
try:
    df = pd.read_sql("select * from quandan",cnx) 
    df = df[df.配货人 != '作废']
    df['订单日期'] = pd.to_datetime(df['订单日期'])
    df['送达日期'] = pd.to_datetime(df['送达日期'])
    df['收款日期'] = pd.to_datetime(df['收款日期'])
except:
    pass

# descdb(df)

# dfpeihuoren= pd.read_sql("select 配货人 from quandan group by 配货人",cnx)
# descdb(dfpeihuoren)
dd = pd.DataFrame(df.groupby(['订单日期']).size(),columns=['订单数量'])
dd['订单金额'] = df.groupby(['订单日期']).sum()['送货金额']
print(dd)

ph = pd.DataFrame(df.groupby(['配货人']).size())
ph.columns = ['配单']
ph['配错'] = df.groupby(['配货人']).sum()['配货准确']

print(ph)

cnx.close()



# +
"""
=============================
Demo of the errorbar function
=============================

This exhibits the most basic use of the error bar method.
In this case, constant values are provided for the error
in both the x- and y-directions.
"""
import numpy as np
import matplotlib.pyplot as plt

# example data
x = np.arange(0.1, 4, 0.5)
y = np.exp(-x)

fig, ax = plt.subplots()
ax.errorbar(x, y, xerr=0.2, yerr=0.4)
ax.plot([0,0],[-0.25,1],'r--')
plt.show()

print(plt.colors())

# +
from imp4nb import *
rnd = np.random.randint(1,200)
for i in range(4):
    rnd = np.random.randint(1,10)
    time.sleep(rnd)
    print('睡了'+str(rnd)+'秒……')
cnx = lite.connect('data\\quandan.db')
df = pd.read_sql("select product.品牌名称 as 品牌, count(*) as 次数, sum(金额) as 销售额"
                 " from xiaoshoumingxi,product"
                 " where (product.商品全名 = xiaoshoumingxi.商品全名) group by 品牌 order by 销售额 desc",cnx) 
print(df['日期'].max())
print(df['日期'].min())
# print(df)

cnx.close()

# -

from imp4nb import *
cfp =ConfigParser()
inifilepath = 'data\\everwork.ini'
cfp.read(inifilepath,encoding='utf-8')
token = cfp.get('evernote','token')
ENtimes = cfp.get('evernote','apicount')
apilasttime = pd.to_datetime(cfp.get('evernote','apilasttime'))
print(apilasttime)
print((datetime.datetime.now()-apilasttime).seconds / 60)
print(datetime.datetime.now().minute)
apilasttimehouzhengdian = pd.to_datetime((apilasttime+datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:00:00'))
# print(apilasttimehouzhengdian)
if datetime.datetime.now() > apilasttimehouzhengdian:
    ENtimes = 0
print(ENtimes)
now = datetime.datetime.now()
print(now.day)
zhengdian = pd.to_datetime('%4d-%2d-%2d %2d:00:00' % (now.year, now.month, now.day, now.hour+1))
print(zhengdian)
print((zhengdian - now).seconds + 30)


