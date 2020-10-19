# encoding:utf-8
"""
文件、数据相关功能函数集
"""

import datetime
import os
import pandas as pd
import numpy as np
import sqlite3 as lite
from pathlib import Path
import xlrd
import pygsheets

import pathmagic

with pathmagic.context():
    from func.evernttest import imglist2note, get_notestore, tablehtml2evernote
    from func.first import dbpathdingdanmingxi, dirmainpath, getdirmain, touchfilepath2depth
    from func.logme import log
    from func.configpr import getcfp


def removeblanklinesfromtxt(fname):
    """
    去除文本文件中的空行
    """
    with open(fname, 'r') as f:
        fcontent = f.read()
        flst = fcontent.split('\n')
        blanklst = [x for x in flst if len(x) == 0]
        itemlst = [x for x in flst if len(x) > 0]
        log.info(f"文件《{fname}》内容行数量为：\t{len(itemlst)}，空行数量为：\t{len(blanklst)}")
    if len(blanklst) != 0:
        with open(fname, 'w') as writer:
            writer.write('\n'.join(itemlst))
        log.info(f"文件《{fname}》只保留内容行（去除了空行），成功写入！！！")


def getdbname(dbpath: str, ownername: str, title='wccontact'):
    return touchfilepath2depth(getdirmain() / dbpath / f"{title}_{ownername}.db")


def gettopicfilefromgoogledrive(topic: str, neirong: str):
    """
    从googledrive读取文件名包含某关键词的文件并读取数据返回DataFrame
    """
    # 验证登录
#     gc = pygsheets.authorize(service_file=str(dirmainpath / 'data' / 'imp' / 'everwork-6a7e225e9947.json'))
    gc = pygsheets.authorize(service_file=str(dirmainpath / 'data' / 'imp' / 'ewjinchu.json'))
#     files = gc.spreadsheet_titles()
#     print(files)
    files = gc.list_ssheets()
    dffiles = pd.DataFrame(files)
    # print(dffiles.head())

    dfboot = dffiles[dffiles.name.str.contains(topic).values == True]
    print(list(dfboot['name']))

    dfboottrails = pd.DataFrame()
    for ix in dfboot.index:
        dts = gc.get_range(dfboot.loc[ix][0], neirong)
        df = pd.DataFrame(dts)
        dfboottrails = dfboottrails.append(df, True)
        print(df.head())

    return dfboottrails


def chulixls_zhifubao(orderfile):
    try:
        content = xlrd.open_workbook(filename=orderfile, encoding_override='gb18030')
        df = pd.read_excel(content, index_col=0, header=2, parse_dates=True, engine='xlrd')[:-1]
        log.info(f'读取{orderfile}， 共有{df.shape[0]}条有效记录')
        # print(df)
        df.columns = ['日期', '支付宝交易号', '支付宝流水号', '商户订单号', '账务类型',
                      '收入（+元）', '支出（-元）', '账户余额（元）', '服务费（元）', '支付渠道', '签约产品',
                      '对方账户', '对方名称', '银行订单号', '商品名称', '备注']
        df['日期'] = pd.to_datetime(df['日期'])
        print(df.columns)
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
    cfpzysm, inizysmpath = getcfp('everzysm')
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
        jilucount = cfpzysm.getint(notestr, '记录数')
    else:
        jilucount = 0
    if dfttt.shape[0] > jilucount:
        dfttt.to_sql(tablename, cnxp, index=False, if_exists='replace')
        cfpzysm.set(notestr, '记录数', '%d' % dfttt.shape[0])
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        log.info(f'增加有效{mingmu}明细数据{dfttt.shape[0] - jilucount}条。')

    cnxp.close()

    return dfttt


def fenliu2note(dfall):
    cfpzysm, inizysmpath = getcfp('everzysm')
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
        lambda x: zhds[zhds == x].index.values[0] if len(zhds[zhds == x].index.values) > 0 else np.NaN)
    dfall.sort_values('日期', ascending=False, inplace=True)
    cls = list(dfall.columns)
    # clsnew = cls[:-2] + [cls[-1]]
    clsnew = cls
    print(clsnew)

    dfout = dfall.loc[:, clsnew]
    # dfout['date'] = dfout['日期'].map(lambda x : pd.to_datetime(x.strftime('%F')))
    dfout['date'] = dfout['日期']
    dfout['ru'] = dfout['收入（+元）'].map(lambda x: False if x == ' ' else True)
    dfout['jine'] = dfout['收入（+元）'] + dfout['支出（-元）']

    def showmingmu(ru, shangpinmingcheng, beizhu, zhanghumingcheng, mingcheng):
        if not ru:
            return
        if pd.isnull(mingcheng) & (zhanghumingcheng != ' , '):
            return '货款，' + '|'.join([shangpinmingcheng, beizhu, zhanghumingcheng])
        elif (mingcheng != '白晔峰') & (not pd.isnull(mingcheng)):
            return '货款，' + '|'.join([shangpinmingcheng, beizhu, zhanghumingcheng]) + ',经手人' + mingcheng
        else:
            return

    dfout['mingmu'] = dfout.apply(lambda x: showmingmu(x.ru, x.商品名称, x.备注, x.账户名称, x.名称), axis=1)
    dfout['card'] = '支付宝白晔峰流水条目'
    dfout['guid'] = 'f5bad0ca-d7e4-4148-99ac-d3472f1c8d80'

    dffine = dfout[dfout.mingmu.isnull() == False].loc[:, ['date', 'ru', 'jine', 'mingmu', 'card', 'guid']]

    return dffine


def alipay2note():
    cnxp = lite.connect(dbpathdingdanmingxi)
    pathalipay = dirmainpath / 'data' / 'finance' / 'alipay'
    dfall = chulidataindir(cnxp, 'alipay', '支付宝流水', '2088802968197536', '支付宝', pathalipay, chulixls_zhifubao)
    zhds = fenliu2note(dfall)
    cnxp.close()

    financesection = '财务流水账'
    item = '支付宝白晔峰流水条目'
    cfpzysm, inizysmpath = getcfp('everzysm')
    if not cfpzysm.has_option(financesection, item):
        count = 0
    else:
        count = cfpzysm.getint(financesection, item)
    if count == zhds.shape[0]:
        log.info(f'{item}\t{zhds.shape[0]}\t无内容更新。')
        return zhds
    else:
        log.info(f'{item}\t{zhds.shape[0]}\t内容有更新。')
    nowstr = datetime.datetime.now().strftime('%F %T')
    imglist2note(get_notestore(), [], 'f5bad0ca-d7e4-4148-99ac-d3472f1c8d80', f'支付宝白晔峰流水（{nowstr}）',
                 tablehtml2evernote(zhds, tabeltitle='支付宝白晔峰流水', withindex=False))
    cfpzysm.set(financesection, item, f'{zhds.shape[0]}')
    cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

    return zhds


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    zhds = alipay2note()
    # print(zhds)
    print('Done.完毕。')
