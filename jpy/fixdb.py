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
#     display_name: Python 2
#     language: python
#     name: python2
# ---

# +
import os
import datetime
import xlrd
import pandas as pd
import sqlite3 as lite
import evernote.edam.type.ttypes as ttypes
from threading import Timer

import pathmagic

with pathmagic.context():
    from func.configpr import cfp, cfpzysm, inizysmpath, cfpdata, inidatanotefilepath
    from func.evernt import get_notestore, imglist2note, tablehtml2evernote, evernoteapijiayi
    from func.logme import log
    from func.first import dirmainpath, dbpathworkplan, dbpathquandan
    from func.pdtools import dftotal2top, descdb
    from work.orderdetails import jiaoyanchanpinkehu

cnxp = lite.connect(dbpathworkplan)
tablename_order = 'salesorder'
dfresult = pd.read_sql('select * from \'%s\'' % tablename_order, cnxp, parse_dates=['日期'])
print(dfresult[dfresult.客户名称.str.contains('交通')])
print(dfresult.columns)
cursor = cnxp.cursor()
sqlstr = f'select * from {tablename_order} where 业务人员 like \'%周莉%\''
print(sqlstr)
result = cursor.execute(sqlstr)
print(result.fetchall())
for row in result:
    print(row)
# -




