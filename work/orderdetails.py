#
# encoding:utf-8
#
"""
销售订单明细处理汇总

名称：人事管理    guid：3d927c7e-98a6-4761-b0c6-7fba1348244f    更新序列号：47266    默认笔记本：False
创建时间：2015-07-14 13:50:09    更新时间：2015-07-14 13:50:09    笔记本组：origin
992afcfb-3afb-437b-9eb1-7164d5207564 在职业务人员名单
"""
import os
# import sys
import datetime
# import xlrd
import pandas as pd
import numpy as np
import sqlite3 as lite
# import evernote.edam.type.ttypes as Ttypes
import xlrd
from threading import Timer
from pathlib import Path

import pathmagic

with pathmagic.context():
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    # from func.evernt import get_notestore, imglist2note, tablehtml2evernote, evernoteapijiayi
    from func.logme import log
    from func.first import dirmainpath, dbpathquandan, dbpathdingdanmingxi
    # from func.pdtools import dftotal2top, dataokay
    from func.pdtools import dataokay
    from func.datatools import str2hex
    from work.notesaledetails import pinpaifenxido


def chulixls_orderdetails(orderfile: Path):
    try:
        content = xlrd.open_workbook( filename=orderfile, encoding_override='gb18030')
        df = pd.read_excel(content, index_col=0, parse_dates=True, engine='xlrd')
        log.info(f'读取{orderfile}')
        # print(list(df.columns))
    except UnicodeDecodeError as ude:
        log.critical(f'读取{orderfile}时出现解码错误。{ude}')
        return
    # ['日期', '单据编号', '摘要', '单位全名', '仓库全名', '商品编号', '商品全名', '规格', '型号', '产地', '单位', '数量', '单价', '金额', '数量1', '单价1',
    # '金额1', '数量2', '单价2', '金额2']
    totalin = ['%.2f' % df.loc[df.index.max()]['数量'], '%.2f' %
               df.loc[df.index.max()]['金额']]  # 从最后一行获取数量合计和金额合计，以备比较
    print(df['日期'].iloc[1], end='\t')
    print(totalin, end='\t')
    # df[xiangmu[0]] = None
    # df = df.loc[:, ['日期', '单据编号', '单据类型', xiangmu[0], '摘要', '备注', '商品备注', xiangmu[1],
    #                 '单价', '单位', '数量', '金额', '单位全名', '仓库全名', '部门全名']]
    df = df.loc[:, df.columns[:-6]]
    df['日期'] = pd.to_datetime(df['日期'])
    # df['备注'] = df['备注'].astype(object)
    dfdel = df[
        (df.单位全名.isnull().values == True) & ((df.单据编号.isnull().values == True) | (df.单据编号 == '小计') | (df.单据编号 == '合计'))]
    hangdel = list(dfdel.index)
    # print(hangdel)
    df1 = df.drop(hangdel)  # 丢掉小计和合计行，另起DataFrame
    dfzhiyuan = df1[df1.单位全名.isnull().values == True]  # 提取出项目名称行号
    zyhang = list(dfzhiyuan.index)
    zyming = list(dfzhiyuan['单据编号'])  # 项目名称

    # 每次填充df到最后一行，依次滚动更新之
    df['员工名称'] = None
    for i in range(len(zyhang)):
        df.loc[zyhang[i]:, '员工名称'] = zyming[i]

    # 丢掉项目名称行，留下纯数据
    dfdel = df[df.单位全名.isnull().values == True]
    # print(dfdel[['日期', '单据编号', '数量', '金额']])
    hangdel = list(dfdel.index)
    # print(hangdel)
    dfout = df.drop(hangdel)
    dfout.index = range(len(dfout))
    dfout = pd.DataFrame(dfout)
    # print(dfout)
    # print(dfout.head(10))
    log.info('共有%d条有效记录' % len(dfout))
    # print(list(dfout.columns))
    if (totalin[0] == '%.2f' % dfout.sum()['数量']) & (totalin[1] == '%.2f' % dfout.sum()['金额']):
        dfgrp = dfout.groupby(['员工名称']).sum()[['数量', '金额']]
        dfgrp.loc['汇总'] = dfgrp.sum()
        print(dfgrp.loc['汇总'].values)
        return dfout
    else:
        log.warning(f'对读入文件《{orderfile}》的数据整理有误！总数量和总金额对不上！')
        return


def chulidataindir_orderdetails(pathorder: Path):
    notestr = '订单明细'
    cnxp = lite.connect(dbpathdingdanmingxi)
    tablename_order = 'orderdetails'
    sqlstr = "select count(*)  from sqlite_master where type='table' and name = '%s'" % tablename_order
    tablexists = pd.read_sql_query(sqlstr, cnxp).iloc[0, 0] > 0
    if tablexists:
        # dfresult = pd.DataFrame()
        dfresult = pd.read_sql('select * from \'%s\'' %
                               tablename_order, cnxp, parse_dates=['日期'])
        log.info('%s数据表%s已存在， 从中读取%d条数据记录。' %
                 (notestr, tablename_order, dfresult.shape[0]))
    else:
        log.info('%s数据表%s不存在，将创建之。' % (notestr, tablename_order))
        dfresult = pd.DataFrame()

    files = os.listdir(str(pathorder))
    for fname in files:
        if fname.startswith(notestr) and (fname.endswith('xls') or fname.endswith('xlsx')):
            yichulifilelist = list()
            if (yichulifile := getcfpoptionvalue('everzysm', notestr, '已处理文件清单')):
                yichulifilelist = yichulifile.split()
            if fname in yichulifilelist:
                continue
            print(fname, end='\t')
            dffname = chulixls_orderdetails(pathorder / fname)
            if dffname is None:
                continue
            dfresult = dfresult.append(dffname)
            print(dffname.shape[0], end='\t')
            print(dfresult.shape[0])
            yichulifilelist.append(fname)
            setcfpoptionvalue('everzysm', notestr, '已处理文件清单', '%s' % '\n'.join(yichulifilelist))

    # dfresult.drop_duplicates(['单据编号', '日期', '订单编号', '客户名称', '业务人员', '订单金额', '部门'], inplace=True)
    print(f'除重前有{dfresult.shape[0]}条记录，', end='\t')
    dfresult.drop_duplicates(inplace=True)
    # descdb(dfresult)
    dateqiyu = min(dfresult['日期'])
    datezhiyu = max(dfresult['日期'])
    log.info(f'除重后{notestr}数据有{dfresult.shape[0]}条记录；数据起于{dateqiyu.strftime("%F")}，止于{datezhiyu.strftime("%F")}')
    dfttt = dfresult.drop_duplicates()
    if not (jilucont := getcfpoptionvalue('everzysm', notestr, '记录数')):
        jilucont = 0
    if dfttt.shape[0] > jilucont:
        dfttt.to_sql(tablename_order, cnxp, index=False, if_exists='replace')
        cnxp.close()
        setcfpoptionvalue('everzysm', notestr, '记录数', '%d' % dfttt.shape[0])
        log.info('增加有效%s数据%d条。' % (notestr, dfttt.shape[0] - jilucont))
        hasnewrecords = True
    else:
        log.info(f'{notestr}数据无新增数据')
        hasnewrecords = False

    cnxp.close()
    return dfttt, hasnewrecords


def orderdetails_check4product_customer():
    targetpath = dirmainpath / 'data' / 'work' / '订单明细'
    # chulixls_order(targetpath / '订单明细20180614.xls.xls')
    dforder, hasnew = chulidataindir_orderdetails(targetpath)
    if (not hasnew)  and False:
        log.info(f'订单明细数据无新增数据，本次产品和客户校验跳过。')
        return

    cnxp = lite.connect(dbpathquandan)
    dataokay(cnxp)

    dfchanpin = pd.read_sql(f'select * from product', cnxp, index_col='index')
    print(dfchanpin.columns)
    dfchanpingrp = dfchanpin.groupby(['商品全名']).count()
    print(dfchanpin.shape[0])

    # dforder = pd.read_sql(f'select 商品全名, 商品编号, 单价, 金额 from xiaoshoumingxi', cnxp)
    print(dforder.columns)
    dict_mapping = {'单价': 'max', '金额': 'sum'}
    dfordergrp = dforder.groupby(
        ['商品全名', '商品编号'], as_index=False).agg(dict_mapping)
    dfordergrp.index = dfordergrp['商品全名']
    print(dfordergrp.shape[0])
    dfall = dfordergrp.join(dfchanpingrp, how='outer')
    # print(dfall)
    # dfall['商品编号'] = dfall['商品编号'].apply(lambda x: str(int(x)) if np.isnan(x) == False else x)
    dfduibichanpin = dfall[np.isnan(dfall.品牌名称)][['商品编号', '单价', '金额']]
    if dfduibichanpin.shape[0] > 0:
        chanpinnotin = list(dfduibichanpin.index)
        lasthash = getcfpoptionvalue('everdata', 'dataraw', 'chanpinhash')
        nowhash = hash(str(chanpinnotin))
        if nowhash != lasthash:
            chanpinnotinxlspath = dirmainpath / 'data' / 'work' / '未录入新品.xlsx'
            with pd.ExcelWriter(chanpinnotinxlspath, mode='a') as writer:
                nowstr = datetime.datetime.now().strftime("%Y%m%d")
                dfduibichanpin.to_excel(writer, sheet_name=f"{nowstr}({dfduibichanpin.shape[0]})")
            log.critical(f'产品档案需要更新，共有{dfduibichanpin.shape[0]}个产品未包含：{chanpinnotin[:5]}…...，输出至文件{chanpinnotinxlspath}')
            setcfpoptionvalue('everdata', 'dataraw', 'chanpinhash', f"{nowhash}")
        else:
            log.warning(f'产品档案需要更新，共有{dfduibichanpin.shape[0]}个产品未包含：{chanpinnotin[:5]}...，列表hash为{nowhash}')

        return False

    dfkehu = pd.read_sql(f'select * from customer', cnxp, index_col='index')
    print(dfkehu.columns)
    dfkehugrp = dfkehu.groupby(['往来单位']).count()
    print(dfkehugrp.shape[0])

    # dforder = pd.read_sql(f'select 单位全名, 数量, 金额 from xiaoshoumingxi', cnxp)
    print(dforder.columns)
    dict_mapping = {'数量': 'sum', '金额': 'sum'}
    dfordergrp = dforder.groupby(['单位全名'], as_index=False).agg(dict_mapping)
    dfordergrp.index = dfordergrp['单位全名']
    print(dfordergrp.shape[0])
    dfall = dfordergrp.join(dfkehugrp, how='outer')
    # print(dfall)
    # dfall['商品编号'] = dfall['商品编号'].apply(lambda x: str(int(x)) if np.isnan(x) == False else x)
    dfduibikehu = dfall[np.isnan(dfall.往来单位编号)][['往来单位编号', '数量', '金额']]
    if dfduibikehu.shape[0] > 0:
        kehunotin = list(dfduibikehu.index)
        for item in kehunotin:
            print(f"{item}\t{str2hex(item)}")
        lasthash = getcfpoptionvalue('everdata', 'dataraw', 'kehuhash')
        nowhash = hash(str(kehunotin))
        if nowhash != lasthash:
            kehunotinxlspath = dirmainpath / 'data' / 'work' / '未录入客户.xlsx'
            with pd.ExcelWriter(kehunotinxlspath, mode='a') as writer:
                nowstr = datetime.datetime.now().strftime("%Y%m%d")
                dfduibikehu.to_excel(writer, sheet_name=f"{nowstr}({dfduibikehu.shape[0]})")
            log.critical(f'客户档案需要更新，共有{dfduibikehu.shape[0]}个客户未包含：{kehunotin[:5]}…...，，输出至文件《{kehunotinxlspath}》')
            setcfpoptionvalue('everdata', 'dataraw', 'kehuhash', f"{nowhash}")
        else:
            log.warning(f'客户档案需要更新，共有{dfduibikehu.shape[0]}个客户未包含：{kehunotin[:5]}...，列表hash为{nowhash}')

        return False

    cnxp.close()

    # pinpaifenxido()


def showorderstat2note(jiangemiao):
    global workplannotebookguid
    workplannotebookguid = '2c8e97b5-421f-461c-8e35-0f0b1a33e91c'
    try:
        orderdetails_check4product_customer()
    except Exception as ee:
        log.critical('处理订单核对统计笔记时出现错误。%s' % str(ee))
        raise ee

    global timer_showorderstat
    timer_showorderstat = Timer(jiangemiao, showorderstat2note, [jiangemiao])
    timer_showorderstat.start()


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    orderdetails_check4product_customer()
    # showorderstat2note(60 * 15)
    log.info(f'{__file__}\t运行完毕。')
