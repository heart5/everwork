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
# import datetime
# import xlrd
import pandas as pd
import numpy as np
import sqlite3 as lite
import evernote.edam.type.ttypes as Ttypes
import xlrd
from threading import Timer
from pathlib import Path

import pathmagic

with pathmagic.context():
    from func.configpr import cfp, cfpzysm, inizysmpath, cfpdata, inidatanotefilepath
    from func.evernt import get_notestore, imglist2note, tablehtml2evernote, evernoteapijiayi
    from func.logme import log
    from func.first import dirmain, dirmainpath, dbpathworkplan, dbpathquandan, dbpathdingdanmingxi
    from func.pdtools import dftotal2top, dataokay


def chulixls_order(orderfile: Path):
    try:
        content = xlrd.open_workbook(filename=orderfile, encoding_override='gb18030')
        df = pd.read_excel(content, index_col=0, parse_dates=True, engine='xlrd')
        log.info(f'读取{orderfile}')
        # print(list(df.columns))
    except UnicodeDecodeError as ude:
        log.critical(f'读取{orderfile}时出现解码错误。{ude}')
        return
    # ['日期', '单据编号', '摘要', '单位全名', '仓库全名', '商品编号', '商品全名', '规格', '型号', '产地', '单位', '数量', '单价', '金额', '数量1', '单价1',
    # '金额1', '数量2', '单价2', '金额2']
    totalin = ['%.2f' % df.loc[df.index.max()]['数量'], '%.2f' % df.loc[df.index.max()]['金额']]  # 从最后一行获取数量合计和金额合计，以备比较
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


def chulidataindir_order(pathorder: Path):
    cnxp = lite.connect(dbpathdingdanmingxi)
    tablename_order = 'orderdetails'
    sqlstr = "select count(*)  from sqlite_master where type='table' and name = '%s'" % tablename_order
    tablexists = pd.read_sql_query(sqlstr, cnxp).iloc[0, 0] > 0
    if tablexists:
        # dfresult = pd.DataFrame()
        dfresult = pd.read_sql('select * from \'%s\'' % tablename_order, cnxp, parse_dates=['日期'])
        log.info('订单数据表%s已存在， 从中读取%d条数据记录。' % (tablename_order, dfresult.shape[0]))
    else:
        log.info('订单数据表%s不存在，将创建之。' % tablename_order)
        dfresult = pd.DataFrame()

    notestr = '订单明细'
    if cfpzysm.has_section(notestr) is False:
        cfpzysm.add_section(notestr)
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
    files = os.listdir(str(pathorder))
    for fname in files:
        if fname.startswith('订单明细') and (fname.endswith('xls') or fname.endswith('xlsx')):
            yichulifilelist = list()
            if cfpzysm.has_option('订单明细', '已处理文件清单'):
                yichulifilelist = cfpzysm.get('订单明细', '已处理文件清单').split()
            if fname in yichulifilelist:
                continue
            print(fname, end='\t')
            dffname = chulixls_order(pathorder / fname)
            if dffname is None:
                continue
            dfresult = dfresult.append(dffname)
            print(dffname.shape[0], end='\t')
            print(dfresult.shape[0])
            yichulifilelist.append(fname)
            cfpzysm.set('订单明细', '已处理文件清单', '%s' % '\n'.join(yichulifilelist))
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

    # dfresult.drop_duplicates(['单据编号', '日期', '订单编号', '客户名称', '业务人员', '订单金额', '部门'], inplace=True)
    print(f'除重前有{dfresult.shape[0]}条记录，', end='\t')
    dfresult.drop_duplicates(inplace=True)
    # descdb(dfresult)
    dateqiyu = min(dfresult['日期'])
    datezhiyu = max(dfresult['日期'])
    print(f'除重后有{dfresult.shape[0]}条记录；数据起于{dateqiyu}，止于{datezhiyu}')
    dfttt = dfresult.drop_duplicates()
    if cfpzysm.has_option('订单明细', '记录数'):
        jilucont = cfpzysm.getint('订单明细', '记录数')
    else:
        jilucont = 0
    if dfttt.shape[0] > jilucont:
        dfttt.to_sql(tablename_order, cnxp, index=False, if_exists='replace')
        cfpzysm.set('订单明细', '记录数', '%d' % dfttt.shape[0])
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        log.info('增加有效订单明细数据%d条。' % (dfttt.shape[0] - jilucont))

    cnxp.close()

    return dfttt


def jiaoyanchanpinkehu():
    targetpath = dirmainpath / 'data' / 'work' / '订单明细'
    # chulixls_order(targetpath / '订单明细20180614.xls.xls')
    dforder = chulidataindir_order(targetpath)

    cnxp = lite.connect(dbpathquandan)
    dataokay(cnxp)

    dfchanpin = pd.read_sql(f'select * from product', cnxp, index_col='index')
    print(dfchanpin.columns)
    dfchanpingrp = dfchanpin.groupby(['商品全名']).count()
    print(dfchanpin.shape[0])

    # dforder = pd.read_sql(f'select 商品全名, 商品编号, 单价, 金额 from xiaoshoumingxi', cnxp)
    print(dforder.columns)
    dict_mapping = {'单价': 'max', '金额': 'sum'}
    dfordergrp = dforder.groupby(['商品全名', '商品编号'], as_index=False).agg(dict_mapping)
    dfordergrp.index = dfordergrp['商品全名']
    print(dfordergrp.shape[0])
    dfall = dfordergrp.join(dfchanpingrp, how='outer')
    # print(dfall)
    # dfall['商品编号'] = dfall['商品编号'].apply(lambda x: str(int(x)) if np.isnan(x) == False else x)
    dfduibichanpin = dfall[np.isnan(dfall.品牌名称)][['商品编号', '单价', '金额']]
    if dfduibichanpin.shape[0] > 0:
        chanpinnotin = list(dfduibichanpin.index)
        log.critical(f'产品档案需要更新，下列产品未包含：{chanpinnotin}')
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
        log.critical(f'客户档案需要更新，下列客户未包含：{kehunotin}')
        return False

    cnxp.close()


def showorderstat():
    # xlsfile = 'data\\work\\销售订单\\销售订单20180606__20180607034848_480667.xls'
    # dforder = chulixls_order(xlsfile)
    pathor = dirmainpath / 'data' / 'work' / '销售订单'
    dforder = chulidataindir_order(pathor)
    jiaoyanchanpinkehu()
    dforder = dforder.loc[:, ['日期', '订单编号', '区域', '类型', '客户名称', '业务人员', '订单金额']]
    dforder.sort_values(by=['日期', '订单编号', '业务人员'], ascending=False, inplace=True)
    zuixinriqi = dforder.groupby(['日期'])['日期'].size().index.max()
    orderdatestr = zuixinriqi.strftime('%F')
    print(orderdatestr, end='\t')
    dforderzuixinriqi = dforder[dforder.日期 == zuixinriqi]
    print(dforderzuixinriqi.shape[0])
    persons = list(dforderzuixinriqi.groupby('业务人员')['业务人员'].count().index)
    # print(persons)
    notestr = '每日销售订单核对'
    if cfpzysm.has_section(notestr) is False:
        cfpzysm.add_section(notestr)
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
    for person in persons:
        if cfpzysm.has_option(notestr + 'guid', person) is False:
            try:
                notestore = get_notestore()
                plannote = Ttypes.Note()
                plannote.title = notestr + person
                nbody = '<?xml version="1.0" encoding="UTF-8"?>'
                nbody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
                nbody += '<en-note>%s</en-note>' % plannote.title
                plannote.content = nbody
                global workplannotebookguid
                plannote.notebookGuid = workplannotebookguid
                global cfp
                token = cfp.get('evernote', 'token')
                note = notestore.createNote(token, plannote)
                evernoteapijiayi()
                cfpzysm.set(notestr + 'guid', person, '%s' % note.guid)
                cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
                log.info('成功创建%s的%s笔记' % (person, notestr))
            except Exception as ee:
                log.critical('创建%s的%s笔记时出现错误。%s' % (person, notestr, str(ee)))
                continue
        if cfpzysm.has_option(notestr + 'guid', person + '最新订单日期'):
            ordertoday = cfpzysm.get(notestr + 'guid', person + '最新订单日期')
            if zuixinriqi <= pd.to_datetime(ordertoday):  # and False:
                continue
        dfperson = dforderzuixinriqi[dforderzuixinriqi.业务人员 == person]
        dfpersonsum = dfperson.groupby('业务人员').sum()['订单金额']
        del dfperson['业务人员']
        del dfperson['日期']
        print(person, end='\t')
        print(dfpersonsum[0], end='\t')
        personguid = cfpzysm.get(notestr + 'guid', person)
        print(personguid)
        neirong = tablehtml2evernote(dftotal2top(dfperson), f'{orderdatestr}{notestr}——{person}', withindex=False)
        # print(neirong)
        try:
            notestore = get_notestore()
            imglist2note(notestore, [], personguid, '%s——%s（%s）' % (notestr, person, orderdatestr), neirong)
            cfpzysm.set(notestr + 'guid', person + '最新订单日期', '%s' % orderdatestr)
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        except Exception as eeee:
            log.critical('更新笔记%s——%s（%s）时出现严重错误。%s' % (notestr, person, orderdatestr, str(eeee)))
    else:
        log.info('下列人员的销售订单正常处置完毕：%s' % persons)

    yuechuriqi = pd.to_datetime(f"{zuixinriqi.strftime('%Y')}-{zuixinriqi.strftime('%m')}-01")
    dfsales = pd.DataFrame(dforder[dforder.日期 >= yuechuriqi])
    dfsales = dfsales.groupby(['区域', '类型', '客户名称', '业务人员'], as_index=False).sum()
    dfsales.sort_values(['区域', '订单金额'], inplace=True)
    notestr = '销售订单金额（月）'
    if cfpzysm.has_section(notestr) is False:
        cfpzysm.add_section(notestr)
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
    for person in persons:
        if cfpzysm.has_option(notestr, person) is False:
            try:
                notestore = get_notestore()
                plannote = Ttypes.Note()
                plannote.title = notestr + person
                nbody = '<?xml version="1.0" encoding="UTF-8"?>'
                nbody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
                nbody += '<en-note>%s</en-note>' % plannote.title
                plannote.content = nbody
                plannote.notebookGuid = workplannotebookguid
                # cfp, cfppath = getcfp('everwork')
                token = cfp.get('evernote', 'token')
                note = notestore.createNote(token, plannote)
                evernoteapijiayi()
                cfpzysm.set(notestr, person, '%s' % note.guid)
                cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
                log.info('成功创建%s的%s笔记' % (person, notestr))
            except Exception as ee:
                log.critical('创建%s的%s笔记时出现错误。%s' % (person, notestr, str(ee)))
                continue
        if cfpzysm.has_option(notestr, person + '最新订单日期'):
            ordertoday = cfpzysm.get(notestr, person + '最新订单日期')
            if zuixinriqi <= pd.to_datetime(ordertoday):  # and False:
                continue
        dfperson = dfsales[dfsales.业务人员 == person]
        dfpersonsum = dfperson['订单金额'].sum()
        del dfperson['业务人员']
        print(person, end='\t')
        print(dfpersonsum, end='\t')
        personguid = cfpzysm.get(notestr, person)
        print(personguid)
        neirong = tablehtml2evernote(dftotal2top(dfperson), f'{orderdatestr[:-3]}{notestr}', withindex=False)
        # print(neirong)
        try:
            notestore = get_notestore()
            imglist2note(notestore, [], personguid, '%s——%s（%s）' % (notestr, person, orderdatestr[:-3]), neirong)
            cfpzysm.set(notestr, person + '最新订单日期', '%s' % orderdatestr)
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        except Exception as eeee:
            log.critical('更新笔记%s——%s（%s）时出现严重错误。%s' % (notestr, person, orderdatestr, str(eeee)))
    else:
        log.info('下列人员的销售订单金额月度分析正常处置完毕：%s' % persons)


def showorderstat2note(jiangemiao):
    global workplannotebookguid
    workplannotebookguid = '2c8e97b5-421f-461c-8e35-0f0b1a33e91c'
    try:
        showorderstat()
    except Exception as ee:
        log.critical('处理订单核对统计笔记时出现错误。%s' % str(ee))
        raise ee

    global timer_showorderstat
    timer_showorderstat = Timer(jiangemiao, showorderstat2note, [jiangemiao])
    timer_showorderstat.start()


if __name__ == '__main__':
    log.info(f'测试文件\t{__file__}')

    jiaoyanchanpinkehu()
    print('Done.测试完毕。')
