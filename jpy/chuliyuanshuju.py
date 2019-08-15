# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

import datetime
print(datetime.datetime.now())
print(f'\n')

# +
# encoding:utf-8
# 改名客户统计

import re
from imp4nb import *

cnx = lite.connect('data\\quandan.db')
df = pd.read_excel('data\\系统表.xlsx', sheetname='客户档案')
# df.info()

dfccw = df.duplicated('往来单位编号')

for i in list(dfccw[dfccw == True].index):
    wldwmz = (df[df.往来单位编号 == df.loc[i,'往来单位编号']])[['往来单位编号','往来单位']].values
    print(str(i)+'-'+str(len(wldwmz)),end='\t')
    # dfww = pd.read_sql_query('select 单位全名 from xiaoshoumingxi where 单位全名 =\'%s\'' % dfcc.loc[wldwcm[i]]['往来单位'],cnx)
    # print(dfww)



# writer = pd.ExcelWriter('data\\结果输出.xlsx')
# dfcc.to_excel(writer,sheet_name='客户档案',freeze_panes={1,2})
# writer.save()
# 
# writer.close()
# -



print(datetime.datetime.now())

# +
# 数据验证周全性

from imp4nb import *

cnx = lite.connect('data\\quandan.db')

dataokay(cnx)

df = pd.read_sql_query('select xiaoshoumingxi.商品全名,xiaoshoumingxi.商品编号,product.* from xiaoshoumingxi left outer join product on '
                       'xiaoshoumingxi.商品全名 = product.商品全名 where product.商品全名 is null',cnx)
df.describe()
print(df)

df = pd.read_sql_query('select xiaoshoumingxi.单位全名,customer.* from xiaoshoumingxi left outer join customer on '
                       'xiaoshoumingxi.单位全名 = customer.往来单位 where customer.往来单位 is null',cnx)
df = df.groupby('单位全名').sum()
df.describe()
print(df)

df = pd.read_sql_query('select * from xiaoshoumingxi',cnx)
df.info()
df.describe()
dfqc = df.drop_duplicates()
dfqc.info()

cnx.close()
# -



# +
# 统计品牌销售
from imp4nb import *

cnx = lite.connect('data\\quandan.db')
df = pd.read_sql_query(
                    "select 日期,xiaoshoumingxi.单位全名 as 客户名称,customer.往来单位编号 as 编号,金额,substr(customer.往来单位编号,1,2) as 区域 ,"
                    "substr(customer.往来单位编号,12,1) as 类型,product.品牌名称  as 品牌 from xiaoshoumingxi,"
                    "customer,product where (customer.往来单位 = xiaoshoumingxi.单位全名) "
                    "and (product.商品全名 = xiaoshoumingxi.商品全名)" , cnx)
# df.index = df['日期']
# df = df[df.区域.isin(('33','34'))]
df['日期'] = pd.to_datetime(df['日期'])
df = df[df.日期 >= pd.to_datetime('2017-12-01')]
df = df.groupby('品牌').sum()
df = df.sort_values('金额',ascending=False)
print(type(df))
print(df.head(10))

cnx.close()

# +
# 

from imp4nb import *

# plot中显示中文
# mpl.rcParams['font.sans-serif'] = ['SimHei']
# mpl.rcParams['axes.unicode_minus'] = False

conn = lite.connect('data\\quandan.db')
cursor = conn.cursor()
# df = pd.read_sql('select max(日期) as 日期 from xiaoshoumingxi',conn)
# print(df)
df = pd.read_sql('select 日期,sum(金额) as 销售额 from xiaoshoumingxi group by 日期', conn)
# df = df[df.日期 > '2017-01-01']
df.index = pd.to_datetime(df['日期'])
print(df.dtypes)
print(df.columns)
ds = df['销售额']
print(ds.dtypes)
print(type(ds))
# print(ds)
ds.plot()
df = df.resample('M').sum()
df.plot()
plt.show()
plt.close()

conn.close()

# +
# 某品牌，随机n家客户
import pandas as pd, sqlite3 as lite, matplotlib.pyplot as plt, numpy as np,calendar
import random as rd
from pylab import *
from tempfile import NamedTemporaryFile
import os

dbpath = os.path.join('..', 'data', 'quandan.db')
zaibuzai = os.path.exists(dbpath)
daxiao = os.path.getsize(dbpath)
print(f'{dbpath}\t{zaibuzai}\t{daxiao}')

cnx = lite.connect(dbpath)
# df = pd.read_sql_query(
#                     "select 日期,xiaoshoumingxi.单位全名 as 客户名称,customer.往来单位编号 as 编号,金额,substr(customer.往来单位编号,1,2) as 区域 ,"
#                     "substr(customer.往来单位编号,12,1) as 类型,product.品牌名称  as 品牌 from xiaoshoumingxi,"
#                     "customer,product where (customer.往来单位 = xiaoshoumingxi.单位全名) "
#                     "and (product.商品全名 = xiaoshoumingxi.商品全名)" , cnx)
df = pd.read_sql_query(
                    "select xiaoshoumingxi.单位全名 as 客户名称,customer.往来单位编号 as 编号,customer.地址 as 地址,"
                    "sum(金额) as 销售额,substr(customer.往来单位编号,1,2) as 区域 from xiaoshoumingxi,"
                    "customer,product where (customer.往来单位 = xiaoshoumingxi.单位全名) "
                    "and (product.商品全名 = xiaoshoumingxi.商品全名) "
                    "and (product.品牌分类 like \'%卫龙袋3%\') "
                    "and (xiaoshoumingxi.日期 >= \'2018-01-01\') "
                    "group by 编号 order by 销售额 desc" , cnx)
# df.index = df['日期']
# df = df[df.区域.isin(('33','34'))]
print(df.shape[0])
# print(df.columns)
df.index = range(len(df))
# ls = range(len(df))
# print(ls)
randomls = rd.sample(ls, len(df))
dfselect = df.loc[randomls, ['编号', '客户名称', '销售额']]
# dfselect = df

danganpath = os.path.join('..', 'data', '客户档案20181124.xls')
dfcustomer = pd.read_excel(danganpath)
# print(dfcustomer.columns)

dffinal = pd.merge(dfselect, dfcustomer, how='inner', left_on='编号', right_on='往来单位编号')

print(dffinal.columns)

dfresult = dffinal.loc[:, ['编号', '客户名称', '地址', '销售额']]
dfresult.sort_values(['编号'], inplace=True)
dfout = dfresult[dfresult.销售额 > 120]

dfout.to_excel('data\\结果输出.xlsx', sheet_name='卫龙袋客户清单')  
print(dfout.shape[0])
print(dfout)
# -


