# encoding:utf-8
"""
功能描述
"""
import os
import pandas as pd
import numpy as np
import sqlite3 as lite
from pathlib import Path

import xlrd

from func.first import dbpathdingdanmingxi, dirmainpath
from func.logme import log
from func.configpr import cfpzysm, inizysmpath


def chulixls_zhifubao(orderfile):
    try:
        content = xlrd.open_workbook(filename=orderfile, encoding_override='gb18030')
        df = pd.read_excel(content, index_col=0, header=2, parse_dates=True, engine='xlrd')[:-1]
        log.info(f'读取{orderfile}， 共有{df.shape[0]}条有效记录')
        # print(df)
        df.columns = ['日期', '支付宝交易号', '支付宝流水号', '商户订单号', '账务类型',
                      '收入（+元）', '支出（-元）', '账户余额（元）', '服务费（元）', '支付渠道', '签约产品',
                      '对方账户', '对方名称', '银行订单号', '商品名称', '备注']
        print(list(df.columns))
        return df
    except UnicodeDecodeError as ude:
        log.critical(f'读取{orderfile}时出现解码错误。{ude}')
        return


def chulidataindir(cnxp, tablename, mingmu, fnstart, notestr, pathorder: Path, chulixls):
    """

    :param cnxp: 数据库连接
    :param tablename: 表名
    :param mingmu: 名目
    :param fnstart: 文件名起字符串
    :param notestr: section名称
    :param pathorder: 待处理文件目录
    :param chulixls: 处理原始数据的函数
    :return:
    """
    sqlstr = "select count(*)  from sqlite_master where type='table' and name = '%s'" % tablename
    tablexists = pd.read_sql_query(sqlstr, cnxp).iloc[0, 0] > 0
    if tablexists:
        # dfresult = pd.DataFrame()
        dfresult = pd.read_sql('select * from \'%s\'' % tablename, cnxp, parse_dates=['日期'])
        log.info(f'{mingmu}数据表{tablename}已存在， 从中读取{dfresult.shape[0]}条数据记录。')
    else:
        log.info(f'{mingmu}数据表{tablename}不存在，将创建之。')
        dfresult = pd.DataFrame()

    # print(dfresult)
    if cfpzysm.has_section(notestr) is False:
        cfpzysm.add_section(notestr)
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
    files = os.listdir(str(pathorder))
    for fname in files:
        if fname.startswith(fnstart) and (fname.endswith('xls') or fname.endswith('xlsx')):
            yichulifilelist = list()
            if cfpzysm.has_option(notestr, '已处理文件清单'):
                yichulifilelist = cfpzysm.get(notestr, '已处理文件清单').split()
            if fname in yichulifilelist:
                continue
            print(fname, end='\t')
            dffname = chulixls(str(pathorder / fname))
            if dffname is None:
                continue
            dfresult = dfresult.append(dffname)
            print(dffname.shape[0], end='\t')
            print(dfresult.shape[0])
            yichulifilelist.append(fname)
            cfpzysm.set(notestr, '已处理文件清单', '%s' % '\n'.join(yichulifilelist))
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

    # dfresult.drop_duplicates(['单据编号', '日期', '订单编号', '客户名称', '业务人员', '订单金额', '部门'], inplace=True)
    print(f'除重前有{dfresult.shape[0]}条记录，', end='\t')
    dfresult.drop_duplicates(inplace=True)
    # descdb(dfresult)
    dateqiyu = min(dfresult['日期'])
    datezhiyu = max(dfresult['日期'])
    print(f'除重后有{dfresult.shape[0]}条记录；数据起于{dateqiyu}，止于{datezhiyu}')
    dfttt = dfresult.drop_duplicates()
    if cfpzysm.has_option(notestr, '记录数'):
        jilucont = cfpzysm.getint(notestr, '记录数')
    else:
        jilucont = 0
    if dfttt.shape[0] > jilucont:
        dfttt.to_sql(tablename, cnxp, index=False, if_exists='replace')
        cfpzysm.set(notestr, '记录数', '%d' % dfttt.shape[0])
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        log.info(f'增加有效{mingmu}明细数据{dfttt.shape[0] - jilucont}条。')

    cnxp.close()

    return dfttt


def fenliu2note(dfzhibubao):
    zhfromini = [[x, cfpzysm.get('支付宝账户', x).split()] for x in cfpzysm.options('支付宝账户')]
    # print(zhfromini)
    zhonlyone = [x for x in zhfromini if len(x[1][0].split(',')) == 1]
    print(zhonlyone)
    zhmulti = [x for x in zhfromini if len(x[1][0].split(',')) > 1]
    print(zhmulti)
    zhmultichaifen = [[[x[0], [y, x[1][1]]] for y in x[1][0].split(',')] for x in zhmulti]
    print(zhmultichaifen)
    zhmultichaifenchild = [x for y in zhmultichaifen for x in y]
    print(zhmultichaifenchild)
    zhresult = zhonlyone + zhmultichaifenchild
    print(zhresult)
    # zhfine = [x for y in zhresult for x in y]
    zhfine = [[x[0], ','.join([y for y in x[1]])] for x in zhresult]
    print(zhfine)
    zhdf = pd.DataFrame(zhfine, columns=['name', 'codename'])
    zhdf.index = zhdf['name']
    zhds = zhdf['codename']
    dfall['账户名称'] = dfall['对方账户'] + ',' + dfall['对方名称']
    dfall['名称'] = dfall['账户名称'].map(
        lambda x : zhds[zhds == x].index.values[0] if len(zhds[zhds == x].index.values) > 0 else np.NaN)
    dfall.sort_values('日期', ascending=False, inplace=True)
    cls = list(dfall.columns)
    clsnew = cls[:-2] + [cls[-1]]
    print(clsnew)

    return dfall.loc[:, clsnew]


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    cnxp = lite.connect(dbpathdingdanmingxi)
    pathalipay = dirmainpath / 'data' / 'finance' / 'alipay'
    dfall = chulidataindir(cnxp, 'alipay', '支付宝流水', '2088802968197536', '支付宝', pathalipay, chulixls_zhifubao)
    zhds = fenliu2note(dfall)
    print(zhds)
    cnxp.close()
    print('Done.完毕。')
