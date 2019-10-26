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

race = lambda x: x**0.5
lop = race(23)
print(lop)

# +
import sqlite3 as lite
import pandas as pd

import pathmagic

with pathmagic.context():
    from func.first import dirmainpath

print(dirmainpath)
pathquandan = dirmainpath / 'data' / 'quandan.db'
cnx = lite.connect(pathquandan)

df = pd.read_sql_query("select * from xiaoshoumingxi",cnx)
print(len(df))

df = pd.read_sql_query("select * from alldata",cnx)
print(len(df))


cnx.close()
# -


