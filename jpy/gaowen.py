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

# +
import pandas as pd
import pathmagic
with pathmagic.context():
    from life.noteweather import getrainfromgoogledrive
    
dfinput = getrainfromgoogledrive()
print(dfinput)

# +
with pathmagic.context():
    from work.dutyon import showdutyonfunc
    from func.pdtools import isworkday
    from func.wrapfuncs import timethis
    from func.first import dbpathworkplan
   
df = dfinput.copy()
# dfworkday = showdutyonfunc(['2019-01-01'])
print(isworkday(df['riqi']).set_index('date'))
df['weekday'] = df['riqi'].dt.weekday


@timethis
def first():
    df = dfinput.copy()
    df['weekday'] = df['riqi'].dt.weekday
    df['workday'] = df['riqi'].apply(lambda x: isworkday([x])['work'])
    df.set_index('riqi', inplace=True)
    print(df)
    
@timethis
def second():
    df = dfinput.copy()
    df['weekday'] = df['riqi'].dt.weekday
    df.set_index('riqi', inplace=True)
    df['workday'] = isworkday(df.index).set_index('date')['work']
    
    return df

# first()

dfout = second()
dfout
# -

import sqlite3 as lite
cnxwp = lite.connect(dbpathworkplan)
dfhot = pd.read_sql('select *from hot', cnxwp, parse_dates=['date'])
cnxwp.close()
dfhot

dfinput.append(dfinput).drop_duplicates(['date'])

dftmp = dfinput.copy()
dftmp.append(dftmp)
dftmp
