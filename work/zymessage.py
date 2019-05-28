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
    from func.first import dbpathworkplan, dbpathquandan, dbpathdingdanmingxi, dirmainpath, ywananchor, touchfilepath2depth
    from func.configpr import getcfp
    from func.logme import log
    from func.pdtools import gengxinfou, desclitedb

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
    df['全息'] = df.index + df['地址']
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
        fenbu = getinivaluefromnote('datasource', 'fenbulst')
        fenbulst = re.split('[,，]', fenbu)
        quyudaxie = getinivaluefromnote('datasource', 'quyudaxielst')
        quyudaxielst = re.split('[,，]', quyudaxie)
        # print(f"{quyudaxielst}")
        cnamelst = [x for x in args[0] if not (x in (quyudaxielst + fenbulst))]
        cfenbulst = [x for x in args[0] if x in fenbulst]
        cquyulst = [x for x in args[0] if x in quyudaxielst]
        if len(cnamelst) == 0:
            cnamelst.append('.')
        print(f"客户名称拆解：{cnamelst}")
        print(f"区域名称拆解：{cquyulst}")
        print(f"分部名称拆解：{cfenbulst}")
        cquyutlst = []
        # 转换分部为区域的数字格式方便查询
        for fb in cfenbulst:
            dfquyu = pd.read_sql(f"select 区域 from quyu where 分部='{fb}'", con=cnx)
            # print(f"{dfquyu}")
            fbqylst = (list(dfquyu['区域']))
            # print(f"{fbqylst}")
            if len(fbqylst) > 0:
                    for fbqy in fbqylst:
                        cquyutlst.append(fbqy)
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
        # print(f"区域列表（数字）：{cquyutlst}")
        cquyutset = list(set(cquyutlst))
        print(f"区域集合（数字）{cquyutset}")
        dfs = df
        for name in cnamelst:
            # 增加对客户编码的识别判断，最高优先级别
            ptnstr= "[0-3][0-9][0-6]0[0-9]{2}[1-9]"
            ptn = re.compile(f"^{ptnstr}")
            if re.match(ptn, name):
                dfs = dfs[dfs.往来单位编号.str.contains(f"^{name}")]
                break
            dfs = dfs[dfs.全息.str.contains(f"{name}")]
        # 依据df的数据结构创建空表
        resultdf = pd.DataFrame(columns=df.columns)
        for quyu in cquyutset:
            dfqy = dfs[dfs.往来单位编号.str.contains(f"^{quyu}")]
            if dfqy.shape[0] != 0:
                resultdf = resultdf.append(dfqy)
        resultlst = list(resultdf.往来单位编号)
        # resultlst = [x[:7] for x in resultlst]
        # resultlst = [x[:7] for x in resultlst]
    cnx.close()

    # print(f"{resultdf}")
    print(f"客户编码查询结果：{resultlst}")

    # set一下确保单一不重复，上个保险
    return list(set(resultlst))


def validfilename(prefix, args):
    if len(args) == 0:
        tezhengstr4filename = ''
    else:
        # 把中文字符转换为拼音
        py = Pinyin()
        tezhengstr4filename = '_'.join([py.get_pinyin(x, '') for x in args[0]])
    rdffile = dirmainpath / 'data' / 'webchat' / f'{prefix}_{tezhengstr4filename}.xlsx'
        # print(rdffile)
    return rdffile


def getresult(resultdf, prefix, args):
    number2showinapp = getinivaluefromnote('datasource', 'number2showinapp')
    if resultdf.shape[0] > number2showinapp:
        excelwriter = pd.ExcelWriter(validfilename(prefix, args))
        ixmaxcount = 0
        for ix in set(resultdf.index):
            ixcount = resultdf.loc[ix].shape[0]
            # print(f"{ix}\t{ixcount}")
            if ixcount > ixmaxcount:
                ixmaxcount = ixcount
        print(f"最大条目数为：{ixmaxcount}")
        maxcount2split = getinivaluefromnote('webchat', 'maxcount2split')
        if ixmaxcount > maxcount2split:
            for ix in set(resultdf.index):
                df2sheet = resultdf.loc[ix]
                if type(df2sheet) == pd.core.series.Series:
                    # 复制结构相同的DataFrame，并追加数据（类型是Series）
                    dftmp = pd.DataFrame(columns=resultdf.columns)
                    df2sheet = dftmp.append(df2sheet)
                    # print(f"{df2sheet}")
                df2sheet.to_excel(excelwriter,
                                          sheet_name=str(ix).replace('*',
                                                                     '').strip(), index=False)
        else:
            resultdf.to_excel(excelwriter)
        excelwriter.save()
        rdffile = os.path.abspath(excelwriter)
        rdfstr = resultdf[:number2showinapp].to_string() + f"\n...\n共有{resultdf.shape[0]}条结果，更多信息请查看表格附件"
    else:
        rdffile = None
        if resultdf.shape[0] == 0:
            rdfstr = '没有符合条件的查询结果'
        else:
            rdfstr = f"找到{resultdf.shape[0]}条记录\n" + resultdf.to_string()

    return rdffile, rdfstr


def notfoundshow():
    custsample = "“百佳 捌区”，勤丰 联城路“，”凯旋 汉阳“"
    return f"没有找到符合条件的客户。\n请减少关键字或扩大查询区域范围重新查找，另外一定注意用空格分隔客户信息关键词，比如{custsample}"


def searchcustomer(*args, **kw):
    chulikhqd()
    targetbmlst = getbianmalst(args)
    if len(targetbmlst) == 0:
        return None, notfoundshow()

    cnx = lite.connect(dbpathquandan)
    # df = pd.read_sql('select 往来单位全名, substr(往来单位编号, 1, 7) as 往来单位编号, 联系人, 地址  from customeruid', con=cnx, index_col='往来单位全名')
    # df = pd.read_sql('select 往来单位全名 as 名称, 往来单位编号 as 编码, 联系人, 地址  from customeruid', con=cnx, index_col='名称')
    df = pd.read_sql('select 往来单位全名 as 名称, 往来单位编号 as 编码, 联系人, 地址  from customeruid', con=cnx)
    cnx.close()
    resultdf = df[df.编码.isin(targetbmlst)]
    # resultdf['客户编码'] = resultdf['往来单位编号'].str.slice(0,7)
    resultdf['编码'] = resultdf['编码'].str.slice(0,7)
    resultdf.set_index('名称', inplace=True)
    # resultdf['拼接'] = resultdf['编码'].map(lambda x: x+'号')
    # resultdf['拼接'] = resultdf['编码'] + resultdf['编码']
    # resultdf['拼接'] = resultdf['编码'].str.cat(resultdf['编码'], sep='-')
    # resultdf = resultdf.loc[:,['往来单位编号', '联系人', '地址']]
    rdffile, rdfstr = getresult(resultdf, 'kfqd', args)

    return rdffile, rdfstr


def searchqiankuan(*args, **kw):
    chuliquandan()
    targetbmlst = getbianmalst(args)
    if len(targetbmlst) == 0:
        return None, notfoundshow()

    cnx = lite.connect(dbpathquandan)
    # df = pd.read_sql('select (strftime("%Y-%m-%d",订单日期) || "-" || 单号) as 单号, substr(终端编码, 1, 7) as 终端编码, 终端名称, 送货金额, 应收金额, strftime("%Y-%m-%d", 送达日期) as 送达日期, 实收金额, strftime("%Y-%m-%d", 收款日期) as 收款日期 from quandantjgl', con=cnx)
    df = pd.read_sql('select (strftime("%Y-%m-%d",订单日期) || "-" || 单号) as 单号, 终端编码 as 编码, 终端名称 as 单位全名, 送货金额, 应收金额, strftime("%Y-%m-%d", 送达日期) as 送达日期, 实收金额, strftime("%Y-%m-%d", 收款日期) as 收款日期 from quandantjgl', con=cnx)
    cnx.close()
    filterdf = df[df.编码.isin(targetbmlst)]
    resultdf = filterdf[(filterdf.收款日期.isnull()) & (filterdf.送达日期.notna())]
    resultdf['编码'] = resultdf['编码'].str.slice(0,7)
    resultdf.set_index('编码', inplace=True)

    rdffile, rdfstr = getresult(resultdf, 'khqk', args)

    return rdffile, rdfstr

def strlst2sqltuple(lst):
    """
    list转换成适合sql使用的括号包括的set
    """
    targetbmlst_quote = ['\'' + x + '\'' for x in lst]
    sqltuple = "(" + ','.join(targetbmlst_quote) + ')'
    print(f"{sqltuple }")

    return sqltuple


def searchpinxiang(*args, **kw):
    chuliquandan()
    targetbmlst = getbianmalst(args)
    if len(targetbmlst) == 0:
        return None, notfoundshow()

    cnx = lite.connect(dbpathquandan)
    # desclitedb(cnx)
    targetbmlst2str = strlst2sqltuple(targetbmlst)
    dfcustomer = pd.read_sql(f"select * from customer where 往来单位编号 in {targetbmlst2str}", con=cnx)
    ctlst = list(dfcustomer['往来单位'])
    # print(f"{ctlst}")
    customerstr4sql = strlst2sqltuple(ctlst)
    # 加参数探测特殊数据类型比如日期时间
    cnxmingxi = lite.connect(dbpathdingdanmingxi, detect_types=lite.PARSE_DECLTYPES|lite.PARSE_COLNAMES)
    # desclitedb(cnxmingxi)
    dfpinxiang = pd.read_sql(f"select * from orderdetails where 单位全名 in {customerstr4sql}", parse_dates=True, con=cnxmingxi)
    cnxmingxi.close()
    # print(f"{dfpinxiang.dtypes}")
    being = pd.to_datetime(getinivaluefromnote('webchat', 'datafrom'))
    df = dfpinxiang[dfpinxiang.日期 >= being]
    if df.shape[0] == 0:
        return None, f"没有找到客户{targetbmlst}自{being.strftime('%F')}起的品项纪录"
    dfpxjc = pd.read_sql(f"select 商品全名, 简称 from product where 简称 is not NULL", cnx, index_col=['商品全名'])
    cnx.close()
    dfpxjc = dfpxjc['简称']
    df['商品全名'] = df['商品全名'].apply(lambda x:
                                                          dfpxjc.loc[x] if (x in list(dfpxjc.index)) else x)
    dfpxsum = (df.groupby(['单位全名', '商品全名'], as_index=False)['金额', '数量'].sum())
    # print(f"{dfpxsum.dtypes}")
    # dfsort = dfpxsum.sort_values('金额', ascending=False)
    dfsort = dfpxsum.sort_values(['单位全名', '金额'], ascending=[True, False])
    dfsort.set_index('单位全名', inplace=True)
    # print(f"{dfsort}")
    # df = pd.read_sql('select (strftime("%Y-%m-%d",订单日期) || "-" || 单号) as 单号, substr(终端编码, 1, 7) as 终端编码, 终端名称, 送货金额, 应收金额, strftime("%Y-%m-%d", 送达日期) as 送达日期, 实收金额, strftime("%Y-%m-%d", 收款日期) as 收款日期 from quandantjgl', con=cnx)
    # df = pd.read_sql('select (strftime("%Y-%m-%d",订单日期) || "-" || 单号) as 单号, 终端编码 as 编码, 终端名称, 送货金额, 应收金额, strftime("%Y-%m-%d", 送达日期) as 送达日期, 实收金额, strftime("%Y-%m-%d", 收款日期) as 收款日期 from quandantjgl', con=cnx)
    # cnx.close()
    # filterdf = df[df.编码.isin(targetbmlst)]
    # resultdf = filterdf[(filterdf.收款日期.isnull()) & (filterdf.送达日期.notna())]
    # resultdf['编码'] = resultdf['编码'].str.slice(0,7)

    rdffile, rdfstr = getresult(dfsort, 'khpx', args)

    return rdffile, rdfstr


if __name__ == '__main__':
    # global log
    log.info(f'文件\t{__file__}\t启动运行……')
    # cnxp = lite.connect(dbpathquandan)
    # dataokay(cnxp)
    qrylst = [
              '联合一百 捌区'
              # , '天猫 飞翔'
              # , '天猫 '
              # , '飞翔 '
              # , '1020082'
              # , '阿里之门 叁拾叁区 捌区'
              # , '零区 汉口'
              # , '联合 零区 贰拾贰区 汉口'
              # , '学三'
              , '南苑'
              # , '千佛手'
              # , '翼社区 汉口'
             ]

    # searchqiankuan()
    # for qry in qrylst:
        # rfile, rstr =  searchpinxiang(qry.split())
        # print(rstr)
        
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
