# coding:utf-8

import pygsheets
import pandas as pd
import time

# 验证登录
gc = pygsheets.authorize(service_file='ewjinchu.json')
files = gc.list_ssheets()
dffiles = pd.DataFrame(files)
# print(dffiles.head())

dfboot = dffiles[dffiles.name.str.contains('boots trail').values == True]
print(dfboot.head())

dfboottrails = pd.DataFrame()
for ix in dfboot.index:
    # print(ix, end='\t')
    # print(dfboot.loc[ix])
    dts = gc.get_range(dfboot.loc[ix][0], 'A:E')
    # print(dts[:3])
    # print(dts[-3:])
    df = pd.DataFrame(dts)
    dfboottrails = dfboottrails.append(df, True)
    # print(df.head())
dfboottrails.columns = ['atime', 'entered', 'xingzhi', 'tu', 'tulian']
dfboottrails = pd.concat([dfboottrails, dfboottrails['xingzhi'].str.split(r' ', expand=True)], axis=1)
dfboottrails.rename(columns={0: 'shuxing', 1: 'address'}, inplace=True)
dfboottrails.drop_duplicates(inplace=True)
dfbout = dfboottrails.loc[:, ['atime', 'entered', 'shuxing', 'address']]
dfbout['atime'] = dfbout['atime'].apply(
    lambda x: pd.to_datetime(time.strftime('%Y-%m-%d %H:%M', time.strptime(x, '%B %d, %Y at %I:%M%p'))))
dfbout['atime'] = dfbout['atime'].astype(pd.datetime)
dfbout.index = dfbout['atime']
dfbout = dfbout.sort_index()
dfout = dfbout[['entered', 'shuxing', 'address']]
print(dfout.tail())
# print(dfbout)

# sh = gc.open('boots trail')
# sh = gc.open_by_key('1e-louzaHWBifMi8OzFrIDG9E2xMTTr92tGn9NcoRlHY')
#
# print(sh)
# wks = sh[0]
# print(wks)
