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

# 用于存储潜在异质数据的二维化表格数据结构，其大小可变，且拥有可标签化的轴。数学运算可以沿纵轴横轴两个方向开展。可以把它想象成Series对象的字典样式容器。属于pandas的基础数据类型。

# + [markdown] toc-hr-collapsed=true
# ## 构建DataFrame

# + [markdown] toc-hr-collapsed=true toc-hr-collapsed=true
# ### 从字典构建DataFrame

# + pycharm={"is_executing": false, "name": "#%%\n"}
import pandas as pd
import numpy as np

d = {'col1': [1, 2], 'col2': [3, 4]}
dfd = pd.DataFrame.from_dict(d)
print(dfd)
df = pd.DataFrame(data=d)
df

# + [markdown] pycharm={"name": "#%% md\n"}
# ##### 注意使用的数据类型默认是int64
# -

zidianlst = {"名称":"datahouse", "guid":"cb057271-2435-4e06-9f77-f2a679e0813c", "更新序列号":"1477754"}
print(pd.Series(zidianlst))
print(pd.DataFrame.from_dict(zidianlst, orient='index'))
print(pd.DataFrame.from_dict(zidianlst, orient='index').T)

# + pycharm={"is_executing": false, "name": "#%%\n"}
df.dtypes
# -

# #### 当然也可以强行指定数据类型为单整数类型

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
dfs = pd.DataFrame(data=d, dtype=np.int8)
dfs.dtypes
# -

# ### 从numpy多维数列构建DataFrame
#

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
df2 = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), columns=['a', 'b', 'c'])
df2

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
df2.dtypes
# -

# ## 多重索引

# 多级索引：在一个轴上有多个(两个以上）的索引，能够以低维度形式来表示高维度的数据。单级索引是Index对象，多级索引是MultiIndex对象。

# ### 创建多重索引

# #### 隐式创建，即给DataFrame的index或columns参数传递两个或更多的数组。

# +
import pandas as pd
import numpy as np
df1 = pd.DataFrame(np.random.randint(80, 120, size=(2, 4)),
                   index= ['girl', 'boy'],
                   columns=[['English', 'English', 'Chinese', 'Chinese'],
                         ['like', 'dislike', 'like', 'dislike']])

print(df1)    # 创建多级 列 索引
# -

# #### 显示创建，推荐使用较简单的pd.MultiIndex.from_product方法

df2 = pd.DataFrame(np.random.randint(80, 120, size=(6, 2)), 
                   columns= ['girl', 'boy'],
                   index=pd.MultiIndex.from_product([['English','Chinese'],
                                                    ['like','dislike', 'ilike']]))
print(df2)    # 创建多级 行 索引

df1.Chinese.like

df1.loc['girl'].dtypes

# + [markdown] toc-hr-collapsed=true
# ### DataFrame重置索引df.reset_index()
# -

# #### 单索引的情况

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
dfi = pd.DataFrame([('bird', 389.0),
                    ('bird', 24.0),
                    ('mammal', 80.5),
                    ('mammal', np.nan)],
                   index=['falcon', 'parrot', 'lion', 'monkey'],
                   columns=('class', 'max_speed'))
dfi

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
dfi.index.name = 'animal'
dfi.reset_index()

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
dfi.reset_index(drop=True)

# + [markdown] toc-hr-collapsed=true
# #### 多重索引的情况

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
index = pd.MultiIndex.from_tuples([('bird', 'falcon'),
                                   ('bird', 'parrot'),
                                   ('mammal', 'lion'),
                                   ('mammal', 'monkey')],
                                  names=['class', 'name'])
columns = pd.MultiIndex.from_tuples([('speed', 'max'),
                                     ('species', 'type')])
dfm = pd.DataFrame([(389.0, 'fly'),
                    (24.0, 'fly'),
                    (80.5, 'run'),
                    (np.nan, 'jump')],
                   index=index,
                   columns=columns)
dfm

# -

# ##### 多重索引情况下，我们重置多重索引的某个子集

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
dfm.reset_index(level='class')
# -

# 如果不对索引做丢弃处理，它默认置于列标题的顶层。我们其实可以指定到特定的层：

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
dfm.reset_index(level='class', col_level=1)

# -

# 这个时候，我们其实还可以对其所处的顶层进行赋值命名

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
dfm.reset_index(level='class', col_level=1, col_fill='species')

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
dfm.index

# + jupyter={"outputs_hidden": false} pycharm={"is_executing": false, "name": "#%%\n"}
dfm.index.values

# + [markdown] toc-hr-collapsed=false
# ## DataFrame值修改、选择和过滤
# -

# ### Pandas DataFrame值修改
# When setting values in a pandas object, care must be taken to avoid what is called chained indexing. 
#
# 要修改pandas--DataFrame中的值要注意避免在链式索引上得到的DataFrame的值
#

dfmi = pd.DataFrame([list('abcd'), list('efgh'), list('ijkl'), list('mnop')], columns=pd.MultiIndex.from_product([['one','two'], ['first','second']]))
dfmi

# - 所谓***链式索引***：dfmi['one']['first'].iloc[0]，正确做法（不会引起警告且能正确赋值）：dfmi.loc[0, ('one', 'first')]。个人理解就是要一次性指定到位而不是靠层层链接过去。
# - pd有***专门的选项设置***，查看该选项：pd.get_option('mode.chained_assignment')，为该选项设定值：pd.set_option('mode.chained_assignment', 'raise')

print(pd.get_option('mode.chained_assignment'))
dfmi['one']['first'].iloc[0] = 'Aerror'
dfmi.loc[0, ('one', 'first')] = 'A1'
dfmi

dfmi.loc[:,('one','first')]

dfmi.iloc[:,[0, 3]] = 'Just a test'
dfmi

# ### 数据集中数据和选取和过滤

# #### 数据准备

import sys
import pandas as pd
import numpy as np
import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.evernttest import getsampledffromdatahouse
sampledf = getsampledffromdatahouse('火界')
backsampledf = sampledf.copy(deep=True)

sampledf.loc[:, 'maxtime'] = pd.to_datetime(sampledf['maxtime'])
sampledf.loc[:, 'mintime'] = pd.to_datetime(sampledf['mintime'])
sampledf.loc[:, 'closetime'] = pd.to_datetime(sampledf['closetime'])
def convert2int(x):
    if type(x) == str:
        if len(x) == 0:
            return np.nan
        else:
            return int(float(x))
    return int(float(x))
sampledf.loc[:, 'roomid'] = sampledf['roomid'].apply(lambda x: convert2int(x))
sampledf.loc[:, 'count'] = sampledf['count'].apply(lambda x: convert2int(x))
sampledf.loc[:, 'consumemin'] = sampledf['consumemin'].apply(lambda x: convert2int(x))
sampledf.loc[:, 'playmin'] = sampledf['playmin'].apply(lambda x: convert2int(x))
sampledf

sampledf.dtypes

# #### 通过[]来选取

# + [markdown] toc-hr-collapsed=true
# ##### 选取一列或几列
# -

sampledf['mintime']

sampledf[['mintime', 'maxtime', 'closetime']]

# ##### 选取一行或几行

sampledf[0:3]

# #### 通过loc选取数据

# ##### 单索引的loc用法

sampledf.loc[0:5,['roomid', 'count']]

# ##### 多重索引的loc用法

sampledf4grp = sampledf.copy(deep=True)
sampledf4grp.loc[:, 'closedate']= sampledf4grp['closetime'].apply(lambda x: pd.to_datetime(x.strftime("%Y-%m-%d")) if x is not pd.NaT else x)
grpcount = sampledf4grp.groupby(['closedate', 'name']).count()['roomid']
grpcount

grpcount.loc['2020-02-11', '徐晓锋']

# #### 通过iloc选取数据

sampledf.iloc[0:5,0:2]

# #### 通过iat获取某一个cell的值

sampledf.iat[1, 3]

# #### 通过[]过滤一些值
# []中是一个boolean 表达式，凡是计算为 True 的行就会被选取。

sampledf[sampledf['count'] > 2]

sampledf[sampledf.apply(lambda x: x['maxtime'] > x['mintime'], axis=1)]

# #### 使用isin
# 1. 在过滤条件前加~，就是取反（not）的意思
# 2. 过滤条件可以取或（or）|,取且（and）&

sampledf[(~(sampledf['name'].isin(['余晗'])))&(sampledf['mintime'].notnull())]

# ## pd常用函数和功能

# ### notnull()和isnull()

nndf = pd.DataFrame([['zhenxing', 26], ['zhenshi', 10], ['zhenhe', 7]], columns=['name', 'age'], index=['da', 'zhong', 'xiao'])
print(nndf)
nndf.iloc[1, 1] = None
nndf.iloc[2, 0] = None
print(nndf)

nndf.notnull()

nndf[nndf['age'].notnull()]

nndf.isnull()

# + [markdown] toc-hr-collapsed=true
# ### 连接数据集，concat、merge
# -

# Pandas操作数据集非常的方便，其中体现在就是有些在SQL语句中常用的方法，比如在合并数据集、left join、right join、full join、inner join，在Pandas中都可以使用concat和merge简单的实现
#

# #### 数据集准备

df1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
                    'B': ['B0', 'B1', 'B2', 'B3'],
                    'C': ['C0', 'C1', 'C2', 'C3'],
                    'D': ['D0', 'D1', 'D2', 'D3']},
                    index=[0, 1, 2, 3])
df1

df2 = pd.DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],
                    'B': ['B4', 'B5', 'B6', 'B7'],
                    'C': ['C4', 'C5', 'C6', 'C7'],
                    'D': ['D4', 'D5', 'D6', 'D7']},
                    index=[4, 5, 6, 7])
df2

df3 = pd.DataFrame({'A': ['A8', 'A9', 'A10', 'A11'],
                    'B': ['B8', 'B9', 'B10', 'B11'],
                    'C': ['C8', 'C9', 'C10', 'C11'],
                    'D': ['D8', 'D9', 'D10', 'D11']},
                    index=[8, 9, 10, 11])
df3

df4 = pd.DataFrame({'B': ['B2', 'B3', 'B6', 'B7'],
                    'D': ['D2', 'D3', 'D6', 'D7'],
                    'F': ['F2', 'F3', 'F6', 'F7']},
                    index=[2, 3, 6, 7])
df4

# + [markdown] toc-hr-collapsed=true toc-hr-collapsed=true
# #### 使用concat
# -

# contact的语法形式
# ```python
# pd.concat(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False)
# ```

# 纵向合并数据集

pd.concat([df1, df2, df3])

# 使用key为每个数据集指定块标记，并使用块标记提取信息

resultdf = pd.concat([df1, df2, df3],keys=['x','y','z'])
resultdf

print(resultdf.ix['x'])
print(resultdf.loc['y'])

# - .loc 基于标签的索引
# - .iloc 基于位置的索引
# - .ix *将来会被弃用，不建议使用*

# concat默认join='outer'，所以纵向合并，没有值补缺失值，索引可以为重复

pd.concat([df1,df4, df1], sort=False)

# concat默认join='outer'，把重复的索引合并，索引没有重复

pd.concat([df1,df4],axis=1)

# concat修改join='inner'，只保留重复的索引合并

pd.concat([df1,df4],axis=1,join='inner')

# concat按照其中一个索引合并，意同left或者right

pd.concat([df1,df4],axis=1,join_axes=[df1.index])

pd.concat([df1,df4],axis=1).reindex(df4.index)

# #### 使用append

df1.append(df2)

df1.append([df2,df3])

# #### 横向合并连接一个DataFrame和Series

s1 = pd.Series(['X0', 'X1', 'X2', 'X3'], name='X')
pd.concat([df1,s1],axis=1)

# #### 纵向合并连接一个DataFrame和Series
# 纵向合并时需要Series的index是DataFrame列名的子集，否则合并后的DataFrame会在列名上横向展开
# 参数方面必须设定ignore_index为False或者指定name作为index名，否则会报错无法运行

s2 = pd.Series(['X0', 'X1', 'X2', 'X3'], index=['A', 'B', 'C', 'D'], name='X')
df1.append(s2)

# #### 使用merge

# ##### 语法形式
# ```python
# merge(left, right, how='inner', on=None, left_on=None, right_on=None, left_index=False, right_index=False, sort=True, suffixes=('_x', '_y'), copy=True, indicator=False)
# ```

# ##### 按照某相同列名连接

left = pd.DataFrame({'key': ['K0', 'K1', 'K2', 'K3'],
                    'keyother': ['K0', 'K1', 'K0', 'K3'],
                    'A': ['A0', 'A1', 'A2', 'A3'],
                    'B': ['B0', 'B1', 'B2', 'B3']})
right = pd.DataFrame({'key': ['K0', 'K1', 'K2', 'K3'],
                    'C': ['C0', 'C1', 'C2', 'C3'],
                    'D': ['D0', 'D1', 'D2', 'D3']})
print(left)
print(right)
joinlst = ['inner', 'outer', 'left', 'right']
for joinstyle in joinlst:
    print(joinstyle+"\n", pd.merge(left.iloc[:-1,:], right, how=joinstyle, on='key'))

# ##### 依照不同列名进行连接

joinlst = ['inner', 'outer', 'left', 'right']
for joinstyle in joinlst:
    print(joinstyle+"\n", pd.merge(left, right, how=joinstyle, left_on=left['keyother'], right_on=right['key']))

# #### 使用join，默认是按照索引进行连接

left = pd.DataFrame({'A': ['A0', 'A1', 'A2'],
                    'B': ['B0', 'B1', 'B2']},
                    index=['K0', 'K1', 'K2'])
right = pd.DataFrame({'C': ['C0', 'C2', 'C3'],
                            'D': ['D0', 'D2', 'D3']},
                            index=['K0', 'K2', 'K3'])
joinlst = ['inner', 'outer']
for jstyle in joinlst:
    print(jstyle+'\n', left.join(right, how=jstyle))

leftother = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
                    'B': ['B0', 'B1', 'B2', 'B3'],
                    'key': ['K0', 'K1', 'K0', 'K1']})
print(leftother)
print(right)
joinlst = ['inner', 'outer']
for jstyle in joinlst:
    print(jstyle+'\n', leftother.join(right, how=jstyle, on='key'))

# ### 数据聚合和分组运算

# pandas提供了一个灵活高效的groupby功能，它使你能以一种自然的方式对数据集进行切片、切块、摘要等操作。根据一个或多个键（可以是函数、数组或DataFrame列名）拆分pandas对象。计算分组摘要统计，如计数、平均值、标准差，或用户自定义函数。对DataFrame的列应用各种各样的函数。应用组内转换或其他运算，如规格化、线性回归、排名或选取子集等。计算透视表或交叉表。执行分位数分析以及其他分组分析。

sampledf.dtypes

sampledf[:5]

# lambda 中如果有if，则必须有else配对
sampledf.loc[:, 'closedate'] = sampledf['closetime'].apply(lambda x: pd.to_datetime(x.strftime("%Y-%m-%d")) if (x is not pd.NaT) else x)
sampledf

# #### 单列分组

sampledf.groupby('closedate').count()['roomid']

sampledf.groupby('closedate').count()['roomid'].index

# #### 多列分组

grpcounts = sampledf[['roomid', 'playmin']].groupby([sampledf['closedate'], sampledf['name']]).count()
grpcounts.size, type(grpcounts), grpcounts, grpcounts.index[:3]

# 通过两个键对数据进行了分组，得到的Series或DataFrame具有一个层次化索引（由唯一的键对组成）。
# 值可以通过loc提取

grpcounts.loc["2020-02-10":"2020-02-12"]

grpcounts.loc["2020-02-11", '余晗']

# - [ ] 提取层次索引的第二层无法实现
#

# 分组键可以是任何**长度适当**的数组

firstlst, secondlst = list(), list()
for i in range(18):
    firstlst.extend(np.random.permutation(5))
    secondlst.extend(np.random.permutation(5))
firstlst = firstlst[:-1]
secondlst = secondlst[:-1]
print(firstlst, secondlst)
print(sampledf[['roomid', 'playmin']].groupby([firstlst, secondlst]).count())

# unstack解堆，可以把层次索引的第二层翻转成列标题

grpcounts.unstack()

# 拆离层次索引的某层到数据集中，一般在输出的时候用，便于浏览

grpcounts.reset_index('closedate')['何龙飞':'徐晓锋']

# #### 将列名（可以是字符串、数字或其他Python对象）用作分组

grptwo = sampledf.groupby(['closedate', 'name']).count()
grptwo

grptwo.groupby(level='closedate').count()

# 如何使用groupby，它都会有一个size方法，可以返回一个含有分组大小的Series

sampledf.groupby(['closedate', 'name']).size()

# #### groupby对象支持迭代

# +
for (k1, k2), group in sampledf.groupby(['closedate', 'name'])[['roomid', 'playmin']]:
#     print(k1, k2)
#     print(group)
    pass

iamkey = list(sampledf.groupby(['closedate', 'name']))[0][0]
print(iamkey)
dict(list(sampledf.groupby(['closedate', 'name'])))[iamkey]
# -

# 获取数据用loc，key的话需要构造合适格式的数据

shuanggrp = sampledf.groupby(['closedate', 'name'])[['roomid', 'playmin']].count()
shuanggrp.loc[pd.to_datetime('2020-2-11'), '徐晓锋']

# 对这些数据片段做任何操作。比如：将这些数据片段做成一个字典

pieces = dict(list(sampledf.groupby('name')))
type(pieces['余晗']), pieces['余晗']

# #### axis=1，横向分组

grphengxiang = sampledf.groupby(sampledf.dtypes, axis=1)
pieceshengxiang = list(grphengxiang)
grphengxiang.count()

# #### 通过字典或Series分组

mapping = {'roomid':'shuzhi', 'count':'shuzhi', 'maxtime':'shijian', 'mintime':'shijian', 'name':'zifuchuan', 'consumetime':'shuzhi', 'closetime':'shijian', 'playmin':'shuzhi', 'closedate':'shijian'}
dict(list(sampledf.groupby(mapping, axis=1)))['shuzhi'].sum()

mapseries = pd.Series(mapping)
mapseries

sampledf.groupby(mapseries, axis=1).count()

# #### 通过函数进行分组

# 相较于字典或Series，Python函数在定义分组映射关系时可以更有创意且更为抽象。任何被当做分组键的函数都会在各个**索引值**上被调用一次，其返回值就会被用作分组名称。

sampleother = sampledf.copy(deep=True)

sampleother = sampleother.set_index('closedate')


def fenzudate(x):
    if x < pd.to_datetime('2020-02-10'):
        return 'shangxun'
    else:
        return 'zhongxun'


sampleother.groupby(fenzudate).count()

jikaifou = sampledf['count'].apply(lambda x: 'jikai' if x == 1.0 else 'tuoyan')

sampleother.groupby([fenzudate, list(jikaifou)]).count()

# #### 根据索引级别进行分组

# 层次化索引数据集最方便的地方在于它能够根据索引级别进行聚合。要实现该目的，通过level关键字传入级别编号或名称即可。

columns = pd.MultiIndex.from_arrays([list(mapping.values()), list(mapping.keys())], names=['guishu', 'name'])
columns

sampleanother = pd.DataFrame(sampledf.values, columns=columns)
sampleanother

sampleanother.groupby(level='guishu', axis=1).count()

# ## 公式表达式

# $e^{i\pi} + 1 = 0$

# $$e^x=\sum_{i=0}^\infty \frac{1}{i!}x^i$$


