"""
真元信使
"""

import os
import shutil
import sqlite3 as lite
import pandas as pd
import xlrd
import random
import re

from xpinyin import Pinyin

import pathmagic

with pathmagic.context():
    from func.evernttest import evernoteapijiayi, makenote, getinivaluefromnote
    from func.first import dbpathworkplan, dbpathquandan, dirmainpath, ywananchor, touchfilepath2depth
    from func.configpr import getcfp
    from func.logme import log
    from func.pdtools import gengxinfou

print(f"{__file__} is loading now...")

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


def chuliquandan():
    """
    处理全单文件
    """
    workpath = dirmainpath / 'data/work'
    khqdnamelst = [x for x in os.listdir(workpath) if
                   x.find('全单统计管理') >= 0]
    # print(khqdnamelst)
    # 对获取的合格文件根据时间进行排序，升序
    khqdnamelst.sort(key=lambda fn:os.path.getmtime(workpath / fn))
    newestonlyname = khqdnamelst[-1]
    newestfn = workpath / newestonlyname
    targetfn = dirmainpath / 'data' / '全单统计管理最新.xlsm'
    cfpdata, cfpdatapath = getcfp('everdata')
    if not cfpdata.has_section('dataraw'):
        cfpdata.add_section('dataraw')
        cfpdata.write(open(cfpdatapath, 'w', encoding='utf-8'))
    if not cfpdata.has_option('dataraw', 'quandannewestname'):
        cfpdata.set('dataraw', 'quandannewestname', '')
        cfpdata.write(open(cfpdatapath, 'w', encoding='utf-8'))
    if cfpdata.get('dataraw', 'quandannewestname') != newestonlyname:
        shutil.copy(newestfn, targetfn)
        cfpdata.set('dataraw', 'quandannewestname', newestonlyname)
        cfpdata.write(open(cfpdatapath, 'w', encoding='utf-8'))
        log.info(f"《全单统计管理》有新文件：{newestonlyname}")
    cnx = lite.connect(dbpathquandan)
    if gengxinfou(targetfn, cnx, 'fileread') : # or True:
        # workbook = xlrd.open_workbook(targetfn, encoding_override="cp936")
        # workbook = xlrd.open_workbook(targetfn)
        # sheet = workbook.sheet_by_name('全单统计管理')
        # # sheet的名称，行数，列数
        # print (sheet.name,sheet.nrows,sheet.ncols)
        # datafromsheet = [sheet.row_values(i, 0 ,sheet.ncols) for i in
                         # range(0, sheet.nrows)]
        # # print(datafromsheet[:5])
        # df = pd.DataFrame(datafromsheet[1:], columns=datafromsheet[0])
        # df = df.loc[:, ['往来单位全名', '往来单位编号', '联系人', '联系电话', '地址']]
        df = pd.read_excel(targetfn, sheet_name='全单统计管理',
                           parse_dates=['订单日期', '送达日期', '收款日期'])
        print(df)
        itemnumberfromnote = getinivaluefromnote('datasource', 'randomnumber4customer')
        itemnunber2show = len(df) if len(df) < itemnumberfromnote else itemnumberfromnote
        print(df.loc[random.sample(range(0, len(df)), itemnunber2show), :])
        df.to_sql(name='quandantjgl', con=cnx, if_exists='replace')
        log.info(f"写入{len(df)}条记录到quandantjgl数据表中")
        # read_excel()对于无指定编码的excel文件读取时一直无法解决编码的问题
        # df = pd.read_excel(targetfn, encoding='cp936')
        # print(df)
    cnx.close()


def getbianmalst(args):
    cnx = lite.connect(dbpathquandan)
    df = pd.read_sql('select 往来单位全名, 往来单位编号, 联系人, 地址  from customeruid', con=cnx, index_col='往来单位全名')
    dfs = df
    # 无参数则随机输出笔记配置文件指定的数量，有则相应处置
    if len(args) == 0:
        itemnumberfromnote = getinivaluefromnote('datasource', 'randomnumber4customer')
        itemnunber2show = len(df) if len(df) < itemnumberfromnote else itemnumberfromnote
        dfs = df.iloc[random.sample(range(0, len(df)), itemnunber2show), :]
        resultlst = list(dfs['往来单位编号'])
    else:
        print(f"输入参数：{args[0]}")
        # 拆分出客户名称和区域等有效信息
        quyudaxielst = getinivaluefromnote('datasource',
                                           'quyudaxielst').split('[,，]')
        # print(f"{quyudaxielst}")
        cnamelst = [x for x in args[0] if not (x in quyudaxielst)]
        cquyulst = [x for x in args[0] if x in quyudaxielst]
        if len(cnamelst) == 0:
            cnamelst.append('.')
        print(f"客户名称拆解：{cnamelst}")
        print(f"区域名称拆解：{cquyulst}")
        cquyutlst = []
        # 转换区域为数字格式方便查询
        for qy in cquyulst:
            dfquyu = pd.read_sql(f"select * from quyu where 区域名称='{qy}'", con=cnx,
                                 index_col='index')
            # print(dfquyu)
            if dfquyu.shape[0] > 0:
                cquyutlst.append(dfquyu.iloc[0, 0])
        # 如果没有区域信息或者没有查找到有效区域信息，则添加任意适配符.
        if len(cquyutlst) == 0:
            cquyutlst.append('.')
        print(f"区域列表（数字）：{cquyutlst}")
        dfs = df
        for name in cnamelst:
            # 增加对客户编码的识别判断，最高优先级别
            ptnstr= "[0-3][0-9][0-6]0[0-9]{2}[1-9]"
            ptn = re.compile(f"^{ptnstr}")
            if re.match(ptn, name):
                dfs = dfs[dfs.往来单位编号.str.contains(f"^{name}")]
                break
            dfs = dfs[dfs.index.str.contains(f"{name}")]
        # 依据df的数据结构创建空表
        resultdf = pd.DataFrame(columns=df.columns)
        for quyu in cquyutlst:
            dfqy = dfs[dfs.往来单位编号.str.contains(f"^{quyu}")]
            if dfqy.shape[0] != 0:
                resultdf = resultdf.append(dfqy)
        resultlst = list(resultdf['往来单位编号'])
        # resultlst = [x[:7] for x in resultlst]
        # resultlst = [x[:7] for x in resultlst]
    cnx.close()

    # print(f"{resultdf}")
    print(f"客户编码查询结果：{resultlst}")

    return resultlst


def validfilename(prefix, args):
    if len(args) == 0:
        tezhengstr4filename = ''
    else:
        # 把中文字符转换为拼音
        py = Pinyin()
        tezhengstr4filename = '_'.join([py.get_pinyin(x, '') for x in args[0]])
    rdffile = dirmainpath / 'data' / 'webchat' / f'{prefix}_{tezhengstr4filename}.xls'
        # print(rdffile)
    return rdffile


def getresult(resultdf, prefix, args):
    number2showinapp = getinivaluefromnote('datasource', 'number2showinapp')
    if resultdf.shape[0] > number2showinapp:
        rdffile = validfilename(prefix, args)
        resultdf.to_excel(rdffile)
        rdffile = os.path.abspath(rdffile)
        rdfstr = resultdf[:number2showinapp].to_string() + f"\n...\n共有{resultdf.shape[0]}条结果，更多信息请查看表格附件"
    else:
        rdffile = None
        if resultdf.shape[0] == 0:
            rdfstr = '没有符合条件的查询结果'
        else:
            rdfstr = resultdf.to_string()

    return rdffile, rdfstr



def searchcustomer(*args, **kw):
    chulikhqd()
    targetbmlst = getbianmalst(args)

    cnx = lite.connect(dbpathquandan)
    # df = pd.read_sql('select 往来单位全名, substr(往来单位编号, 1, 7) as 往来单位编号, 联系人, 地址  from customeruid', con=cnx, index_col='往来单位全名')
    df = pd.read_sql('select 往来单位全名 as 名称, 往来单位编号 as 编码, 联系人, 地址  from customeruid', con=cnx, index_col='名称')
    cnx.close()
    resultdf = df[df.编码.isin(targetbmlst)]
    # resultdf['客户编码'] = resultdf['往来单位编号'].str.slice(0,7)
    resultdf['编码'] = resultdf['编码'].str.slice(0,7)
    # resultdf['拼接'] = resultdf['编码'].map(lambda x: x+'号')
    # resultdf['拼接'] = resultdf['编码'] + resultdf['编码']
    # resultdf['拼接'] = resultdf['编码'].str.cat(resultdf['编码'], sep='-')
    # resultdf = resultdf.loc[:,['往来单位编号', '联系人', '地址']]
    rdffile, rdfstr = getresult(resultdf, 'kfqd', args)

    return rdffile, rdfstr


# @profile
def searchqiankuan(*args, **kw):
    chuliquandan()
    targetbmlst = getbianmalst(args)

    cnx = lite.connect(dbpathquandan)
    # df = pd.read_sql('select (strftime("%Y-%m-%d",订单日期) || "-" || 单号) as 单号, substr(终端编码, 1, 7) as 终端编码, 终端名称, 送货金额, 应收金额, strftime("%Y-%m-%d", 送达日期) as 送达日期, 实收金额, strftime("%Y-%m-%d", 收款日期) as 收款日期 from quandantjgl', con=cnx)
    df = pd.read_sql('select (strftime("%Y-%m-%d",订单日期) || "-" || 单号) as 单号, 终端编码 as 编码, 终端名称, 送货金额, 应收金额, strftime("%Y-%m-%d", 送达日期) as 送达日期, 实收金额, strftime("%Y-%m-%d", 收款日期) as 收款日期 from quandantjgl', con=cnx)
    cnx.close()
    filterdf = df[df.编码.isin(targetbmlst)]
    resultdf = filterdf[(filterdf.收款日期.isnull()) & (filterdf.送达日期.notna())]
    resultdf['编码'] = resultdf['编码'].str.slice(0,7)

    rdffile, rdfstr = getresult(resultdf, 'khqk', args)

    return rdffile, rdfstr


if __name__ == '__main__':
    # global log
    log.info(f'文件\t{__file__}\t启动运行……')
    # cnxp = lite.connect(dbpathquandan)
    # dataokay(cnxp)
    qrylst = ['百佳 瑞安街 捌区'
              # , '0810012'
              # , '阿里之门 叁拾叁区 捌区'
              # , '零区'
              # , '千佛手'
              , '翼社区'
              ,
             ]

    # searchqiankuan()
    for qry in qrylst:
        rfile, rstr =  searchqiankuan(qry.split())
        print(rstr)
        
    # for qry in qrylst:
        # rfile, rstr =  searchcustomer(qry.split())
        # print(rstr)

    # searchcut(rstr)
    # fl, flstr = searchcustomer(qry1.split())
    # print(fl, flstr)
    # fl, flstr = searchcustomer(qry2.split())
    # print(fl, flstr)
    # fl, flstr = searchcustomer(qry3.split())
    # print(fl, flstr)

    log.info(f'文件\t{__file__}\t完成运行。')
