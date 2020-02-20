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

# ### 获取笔记本信息

# +
import sqlite3 as lite
import pandas as pd

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.evernttest import getsampledffromdatahouse
# -
# #### 获取火界麻将数据集

ntdf = getsampledffromdatahouse('火界')

ntdf.dtypes


ntdf[ntdf['closetime'].notnull()]

findsomenotest2showornote(ntdf.loc[ntdf.名称 == 'datahouse'].index.values[-1], '火界')

soup = getnotecontent('aa817eb9-4824-4599-ab9c-cdfeed8c549c')

soupstrlst = [item.text.split(',') for item in soup.find_all('div') if len(item.text) > 0]
pd.DataFrame(soupstrlst[1:], columns=soupstrlst[0])

int(1.0)


