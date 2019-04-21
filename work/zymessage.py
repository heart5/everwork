"""
真元信使
"""

import os
import shutil
import sqlite3 as lite
import pandas as pd
import xlrd
import random
from xpinyin import Pinyin

import pathmagic

with pathmagic.context():
    from func.evernttest import evernoteapijiayi, makenote, getinivaluefromnote
    from func.first import dbpathworkplan, dbpathquandan, dirmainpath, ywananchor, touchfilepath2depth
    from func.configpr import getcfp
    from func.logme import log
    from func.pdtools import gengxinfou


def chulikhqd():
    """
    处理客户清单文档，有新文件则做相应更新
    """
    workpath = dirmainpath / 'data/work'
    khqdnamelst = [x for x in os.listdir(workpath) if
                   x.startswith('客户清单')]
    # print(khqdnamelst)
    # 对获取的合格文件根据时间进行排序，升序
    khqdnamelst.sort(key=lambda fn:os.path.getmtime(workpath / fn))
    newestonlyname = khqdnamelst[-1]
    newestfn = workpath / newestonlyname
    targetfn = dirmainpath / 'data' / '客户清单最新.xls'
    cfpdata, cfpdatapath = getcfp('everdata')
    if not cfpdata.has_section('dataraw'):
        cfpdata.add_section('dataraw')
        cfpdata.write(open(cfpdatapath, 'w', encoding='utf-8'))
    if not cfpdata.has_option('dataraw', 'khqdnewestname'):
        cfpdata.set('dataraw', 'khqdnewestname', '')
        cfpdata.write(open(cfpdatapath, 'w', encoding='utf-8'))
    if cfpdata.get('dataraw', 'khqdnewestname') != newestonlyname:
        shutil.copy(newestfn, targetfn)
        cfpdata.set('dataraw', 'khqdnewestname', newestonlyname)
        cfpdata.write(open(cfpdatapath, 'w', encoding='utf-8'))
        log.info(f"《客户清单》有新文件：{newestonlyname}")
    cnx = lite.connect(dbpathquandan)
    if gengxinfou(targetfn, cnx, 'fileread') : # or True:
        workbook = xlrd.open_workbook(targetfn, encoding_override="cp936")
        sheet = workbook.sheet_by_index(0)
        # sheet的名称，行数，列数
        print (sheet.name,sheet.nrows,sheet.ncols)
        datafromsheet = [sheet.row_values(i, 0 ,sheet.ncols) for i in
                         range(0, sheet.nrows)]
        # print(datafromsheet[:5])
        df = pd.DataFrame(datafromsheet[1:], columns=datafromsheet[0])
        df = df.loc[:, ['往来单位全名', '往来单位编号', '联系人', '联系电话', '地址']]
        # print(df)
        itemnumberfromnote = getinivaluefromnote('datasource', 'randomnumber4customer')
        itemnunber2show = len(df) if len(df) < itemnumberfromnote else itemnumberfromnote
        print(df.loc[random.sample(range(0, len(df)), itemnunber2show), :])
        df.to_sql(name='customeruid', con=cnx, if_exists='replace')
        log.info(f"写入{len(df)}条记录到customeruid数据表中")
        # read_excel()对于无指定编码的excel文件读取时一直无法解决编码的问题
        # df = pd.read_excel(targetfn, encoding='cp936')
        # print(df)
    cnx.close()


# @profile
def searchcustomer(*args, **kw):
    chulikhqd()
    cnx = lite.connect(dbpathquandan)
    df = pd.read_sql('select 往来单位全名, 往来单位编号, 联系人, 地址  from customeruid', con=cnx, index_col='往来单位全名')
    dfs = df
    # 无参数则随机输出笔记配置文件指定的数量，有则相应处置
    if len(args) == 0:
        itemnumberfromnote = getinivaluefromnote('datasource', 'randomnumber4customer')
        itemnunber2show = len(df) if len(df) < itemnumberfromnote else itemnumberfromnote
        dfs = df.loc[random.sample(range(0, len(df)), itemnunber2show), :]
        resultdf = dfs
    else:
        print(args[0])
        # 拆分出客户名称和区域等有效信息
        cnamelst = [x for x in args[0] if not x.endswith('区')]
        cquyulst = [x for x in args[0] if x.endswith('区')]
        if len(cnamelst) == 0:
            cnamelst.append('.')
        print(cnamelst)
        print(cquyulst)
        cquyutlst = []
        if len(cquyulst) == 0:
            cquyutlst.append('.')
        else:
            # 转换区域为数字格式方便查询
            for qy in cquyulst:
                dfquyu = pd.read_sql(f"select * from quyu where 区域名称='{qy}'", con=cnx,
                                     index_col='index')
                # print(dfquyu)
                cquyutlst.append(dfquyu.iloc[0, 0])
        print(cquyutlst)
        dfs = df
        for name in cnamelst:
            dfs = dfs[dfs.index.str.contains(f"{name}")]

        # 依据df的数据结构创建空表
        resultdf = pd.DataFrame(columns=df.columns)
        for quyu in cquyutlst:
            dfqy = dfs[dfs.往来单位编号.str.contains(f"^{quyu}")]
            if dfqy.shape[0] != 0:
                resultdf = resultdf.append(dfqy)
        # print(resultstr)
        

    number2showinapp = getinivaluefromnote('datasource', 'number2showinapp')
    if resultdf.shape[0] > number2showinapp:
        if len(args) == 0:
            tezhengstr4filename = ''
        else:
            py = Pinyin()
            tezhengstr4filename = '_'.join([py.get_pinyin(x, '') for x in args[0]])
            # tezhengstr4filename = '_'.join(args[0])
        rdffile = dirmainpath / 'data' / 'webchat' / f'khqd_{tezhengstr4filename}.xls'
        # print(rdffile)
        resultdf.to_excel(rdffile)
        rdffile = os.path.abspath(rdffile)
        rdfstr = resultdf[:number2showinapp].to_string() + f"\n...\n共有{resultdf.shape[0]}条结果，更多信息请查看表格附件"
    else:
        rdffile = None
        rdfstr = resultdf.to_string()

    cnx.close()

    return rdffile, rdfstr



if __name__ == '__main__':
    # global log
    log.info(f'文件\t{__file__}\t启动运行……')
    # cnxp = lite.connect(dbpathquandan)
    # dataokay(cnxp)
    # chulikhqd()
    qry1 = '百佳 瑞安街 捌区'
    qry2 = '叁拾叁区'
    qry3 = '芙蓉 叁拾叁区 捌区'
    # searchcustomer()
    fl, flstr = searchcustomer(qry1.split())
    print(fl, flstr)
    fl, flstr = searchcustomer(qry2.split())
    print(fl, flstr)
    fl, flstr = searchcustomer(qry3.split())
    print(fl, flstr)
    log.info(f'文件\t{__file__}\t完成运行。')
