# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ### 用于存储潜在异质数据的二维化表格数据结构，其大小可变，且拥有可标签化的轴。数学运算可以沿纵轴横轴两个方向开展。可以把它想象成Series对象的字典样式容器。属于pandas的基础数据类型。
# #### 从字典构建DataFrame

# + pycharm={"is_executing": false, "name": "#%%\n"}
import pandas as pd
import numpy as np

d = {'col1': [1, 2], 'col2': [3, 4]}
df = pd.DataFrame(data=d)
df

# + [markdown] pycharm={"name": "#%% md\n"}
# ##### 注意使用的数据类型默认是int64

# + pycharm={"is_executing": false, "name": "#%%\n"}
df.dtypes
# -

# ##### 当然也可以强行指定数据类型为单整数类型

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
dfs = pd.DataFrame(data=d, dtype=np.int8)
dfs.dtypes
# -

# #### 从numpy多维数列构建DataFrame
#

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
df2 = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), columns=['a', 'b', 'c'])
df2

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
df2.dtypes
# -

# ### DataFrame重置索引df.reset_index()
# #### 单索引的情况

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
dfi = pd.DataFrame([('bird', 389.0),
                    ('bird', 24.0),
                    ('mammal', 80.5),
                    ('mammal', np.nan)],
                   index=['falcon', 'parrot', 'lion', 'monkey'],
                   columns=('class', 'max_speed'))
dfi

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
dfi.index.name = 'animal'
dfi.reset_index()

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
dfi.reset_index(drop=True)
# -

# #### 多重索引的情况

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
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

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
dfm.reset_index(level='class')
# -

# ##### 如果不对索引做丢弃处理，它默认置于列标题的顶层。我们其实可以指定到特定的层：

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
dfm.reset_index(level='class', col_level=1)

# -

# ##### 这个时候，我们其实还可以对其所处的顶层进行赋值命名

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
dfm.reset_index(level='class', col_level=1, col_fill='species')

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
dfm.index

# + pycharm={"name": "#%%\n", "is_executing": false} jupyter={"outputs_hidden": false}
dfm.index.values
