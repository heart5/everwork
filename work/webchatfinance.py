# -*- coding: utf-8 -*-
"""
微信支付账单处理
"""

# +
import os
import pandas as pd
import numpy as np
import sqlite3 as lite
import xlrd

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, dirmainpath
    from func.logme import log
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.litetools import istableindb, ifnotcreate, droptablefromdb, checktableindb


# -

# ### 提取账单记录输出为DataFrame格式数据

def chuliweixinzhifuzhangdan(dmpath):
    """
    处理“微信支付账单”文件，生成DataFrame输出
    """

    file_list = os.listdir(dmpath)
#     print(file_list)
    fnlst = [ x for x in file_list if (x.startswith('微信支付账单') and (x.endswith('csv') or x.endswith('xlsx'))) ]
    fnlst.sort(key=lambda fn: os.path.getmtime(dmpath / fn))

    rstdf = pd.DataFrame()
    for fn in fnlst:
        if not (filerecorded := getcfpoptionvalue('everwebchat', 'wczhifufile', str(fn))):
            if fn.endswith('.csv'):
                singledf = pd.read_csv(dmpath / fn, header=16, parse_dates=True)
            elif fn.endswith('.xlsx'):
                content = xlrd.open_workbook(filename=dmpath / fn)
                singledf = pd.read_excel(content, header=16, parse_dates=True, engine='xlrd')
            else:
                logstr = f"读取《微信支付账单》文件时失败：\t{fn}"
                log.critical(logstr)
                continue

            rstdf = rstdf.append(singledf, ignore_index=True)
            print(rstdf.shape[0], end='\t')
            setcfpoptionvalue('everwebchat', 'wczhifufile', str(fn), str(True))

    if rstdf.shape[0] == 0:
        return
    
    print()
    rstdf.drop_duplicates(inplace=True)
    rstdf['交易时间'] = rstdf['交易时间'].apply(lambda x: pd.to_datetime(x))
    rstdf['交易单号'] = rstdf['交易单号'].apply(lambda x: x.strip('\t') if type(x) is str else x)
    rstdf['商户单号'] = rstdf['商户单号'].apply(lambda x: x.strip("\t") if type(x) is str else x)
    rstdf['商户单号'] = rstdf['商户单号'].astype(object)
    rstdf['商品'] = rstdf['商品'].apply(lambda x: str(x)) # 莫名其妙把201808272231355994079232识别成了数字，强制转换成字符串
    rstdf['金额(元)'] = rstdf['金额(元)'].apply(lambda x: str(x).replace("¥", "")) # 解决csv文件中金额中自带的人民币符号
    rstdf['金额(元)'] = rstdf['金额(元)'].astype(float)
    rstdf.replace('/', np.nan, inplace=True)
    rstdf.drop_duplicates(inplace=True)
    
    return rstdf.sort_values('交易时间', ascending=False)


def wczhifufile2table():
    dmpath = dirmainpath / "data" / "webchat" / "微信支付下载"
    # print(f"{dmpath}")
    if (wxzfzddf := chuliweixinzhifuzhangdan(dmpath)) is None:
#         print(wxzfzddf)
        return    
    
    ininame = 'everwebchat'
    dbpath = dirmainpath / 'data' / 'db'/ 'finance.db'
    tablename = 'wczhifu'
    csql = f"create table if not exists {tablename} (交易时间 datetime, 交易类型 text, 交易对方 text, 商品 text, '收/支' text, '金额(元)' float, 支付方式 text, 当前状态 text, 交易单号 blob NOT NULL UNIQUE ON CONFLICT IGNORE, 商户单号 text, 备注 text)"
    checktableindb(ininame, str(dbpath), tablename, csql, confirm=True)

    conn = lite.connect(dbpath)
    wxzfzddf.to_sql(tablename, con=conn, if_exists='append', index=False, dtype={"交易单号": 'text', "商品": 'blob', "商户单号": 'text', "交易时间": 'datetime'})
    conn.close()


def getwczhifudf():
    wczhifufile2table()
    dbname = dirmainpath / 'data' / 'db'/ 'finance.db'
    dftablename = 'wczhifu'
    conn = lite.connect(dbname)
    frdfromdb = pd.read_sql(f'select * from {dftablename}', con=conn, parse_dates=['交易时间'])
    frdfromdb['商品'] = frdfromdb['商品'].apply(lambda x: x.split(":")[-1] if x is not None else x)
    frdfromdb['交易对方'] = frdfromdb['交易对方'].apply(lambda x: x[2:] if (x is not None) and (x.startswith("发")) else x)
    conn.close()

    return frdfromdb


wxzfzddf = getwczhifudf()

wxzfzddf.shape[0]
wxzfzddf.columns
wxzfzddf.dtypes
wxzfzddf[:10]

wxzfzddf.groupby('交易对方').count()

wxzfzddf.describe()
wxzfzddf.dtypes
wxzfzddf.describe()

wxzfzddf['交易单号'].describe()
wxzfzddf['商户单号'].describe()
wxzfzddf['交易时间'].describe()

wxzfzddf.groupby('交易类型').count()

# ### 红包相关

wxzfzddf[wxzfzddf.交易类型.isin([None])]

wxzfzddf[~wxzfzddf.备注.isin([None])]

set([len(x) for x in set(list(wxzfzddf.交易单号))])

set(list(wxzfzddf.备注))

import re
[ x for x in set(list(wxzfzddf.当前状态)) if not re.findall("\d", x)]

wxzfzddf[(wxzfzddf.当前状态.str.find('退') != -1)][-20:]

wxzfzddf[(wxzfzddf.交易类型.str.find('商户消费') > -1)][-20:]

wxzfzddf[15380:15583]

ztlst = [x for x in set(list(wxzfzddf.交易类型)) if (x is not None) and (x.find("红包") >= 0) ]
print(ztlst)
hongbaodf = wxzfzddf[wxzfzddf.交易类型.isin(ztlst)]
hongbaodf[~(hongbaodf.交易类型.str.find('群') != -1)][:20]

# ### 公司财务相关

ztlst = [x for x in set(list(wxzfzddf.交易类型)) if (x is not None) and (x.find("红包") >= 0) ]
ztlst
cofitems = ['二维码收款', '转账']
cofitems
cofitems + ztlst
caiwudf = wxzfzddf[wxzfzddf.交易类型.isin(cofitems + ztlst)]

caiwudf

ztlst = [x for x in set(list(caiwudf.当前状态)) if x.find("退") >= 0 ]
print(ztlst)
caiwudf[~caiwudf.当前状态.isin(ztlst)]

caiwudf.groupby(['交易类型', '当前状态']).count()


def showfinance():
    showjinzhang()
    showshoukuan()


if __name__ == '__main__':
#     log.info(f'开始测试文件\t{__file__}')
    showfinance()
#     log.info(f'对\t{__file__}\t的测试结束。')



