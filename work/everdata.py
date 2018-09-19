# encoding:utf-8
# 整理并导入原始数据
# from imp4nb import *

import datetime
import pandas as pd
import re
import sqlite3 as lite
from odps.df import DataFrame

import pathmagic

with pathmagic.context():
    from func.first import dirmainpath, dbpathquandan
    from func.logme import log
    from func.pdtools import dataokay, desclitedb
    from func.pdtools import descdb


def chengbenjiaupdatedf(dfsall, cnxxc):
    """
    :param dfsall: 按照日期排序的销售明细记录
    :param cnxxc: 数据库连接，为了查询生成产品价格变动记录
    :return:
    """

    # 读取进货记录（排除退货记录）
    dfpros = pd.read_sql_query('select 产品名称, strftime(\'%Y%m\',日期) as 年月, 金额 as 进货金额, 数量 as 进货数量, '
                               '单价 as 进货单价 from jinghuomingxi where 金额 >=0 order by 年月, 产品名称', cnxxc)
    dfpros = DataFrame(dfpros)
    descdb(dfpros[dfpros.进货金额 == 0].to_pandas())

    # 按照月份汇总，生成成本单价并按照月份分组汇总，生成价格调整记录
    dfpro = dfpros.groupby(['产品名称', '年月']).agg(进货金额=dfpros.进货金额.sum(), 进货数量=dfpros.进货数量.sum())
    dfpro = dfpro[dfpro, (dfpro.进货金额 / dfpro.进货数量).round(2).rename('单价')]
    descdb(dfpro.to_pandas())
    dfpro = dfpro.groupby(['产品名称', '单价']).agg(年月=dfpro.年月.min(), 进货金额=dfpro.进货金额.sum()).sort(['产品名称', '年月'])
    descdb(dfpro.to_pandas())
    log.info('共有%d条产品价格记录，共有%d条产品价格记录（含调价）'
             % (dfpro.groupby('产品名称').agg(dfpro.单价.count()).to_pandas().shape[0], dfpro.to_pandas().shape[0]))

    log.info('共有%d条销售明细记录' % dfsall.shape[0])
    dfsall['年月'] = dfsall['日期'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m'))
    dfprosall = dfsall.groupby('商品全名', as_index=False)['金额'].sum()
    dfprosall.rename(columns={'商品全名': '产品名称', '金额': '销售金额'}, inplace=True)

    # 连接进货产品目录和销售产品目录，查看各自的空记录
    dfproall = pd.merge(dfpro.groupby(['产品名称']).agg(进货金额=dfpro.进货金额.sum()).to_pandas(), dfprosall, how='outer')
    descdb(dfproall)
    log.info('以下进货产品在本期无销售记录：%s' % list(dfproall[dfproall.销售金额.isnull().values == True]['产品名称']))

    dfsall['成本单价'] = 0
    dfpro = dfpro.to_pandas()
    for idx in dfpro.index:
        dfsall.loc[dfsall[(dfsall.商品全名 == dfpro.loc[idx]['产品名称']) & (dfsall.年月 >= dfpro.loc[idx]['年月'])].index,
                   ['成本单价']] = dfpro.loc[idx]['单价']

    dfsall['成本金额'] = dfsall['成本单价'] * dfsall['数量']
    dfsall['毛利'] = dfsall['金额'] - dfsall['成本金额']
    descdb(dfsall)
    del dfsall['年月']  # 删除过程数据
    descdb(dfsall)

    return dfsall


def chengbenjiaupdateall(cnxc):
    dfsall = pd.read_sql_query('select * from xiaoshoumingxi order by 日期, 单据编号', cnxc, parse_dates=['日期'])
    del dfsall['index']
    dfsall = chengbenjiaupdatedf(dfsall, cnxc)
    dfsall.to_sql(name='xiaoshoumingxi', con=cnxc, if_exists='replace', chunksize=10000)
    log.info('要更新%d记录中的成本价和毛利内容' % len(dfsall))
    dfsall['年月'] = dfsall['日期'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m'))
    print(dfsall.groupby('年月', as_index=False)[['数量', '成本金额', '金额', '毛利']].sum())


def details2db(filename, sheetname, xiangmu, tablename):
    """

    :param filename:
    :param sheetname:
    :param xiangmu: =['职员名称','商品全名']，['产品名称','经办人']
    :param tablename:
    :return:
    """
    df = pd.read_excel(str(dirmainpath / 'data' / filename), sheetname='%s' % sheetname, index_col=0, parse_dates=True)
    log.info('读取%s' % filename)
    print(list(df.columns))
    #  ['日期', '单据编号', '摘要', '单据类型', '备注', '商品备注', '商品编号', '商品全名',
    #  '规格', '型号', '产地', '单位', '数量', '单价', '金额', '含税单价', '价税合计', '成本金额', '毛利', '毛利率',
    # '单位全名', '仓库全名', '部门全名']
    totalin = ['%.2f' % df.loc[df.index.max()]['数量'], '%.2f' % df.loc[df.index.max()]['金额']]  # 从最后一行获取数量合计和金额合计，以备比较
    # print(totalin)
    df[xiangmu[0]] = None
    df = df.loc[:, ['日期', '单据编号', '单据类型', xiangmu[0], '摘要', '备注', '商品备注', xiangmu[1],
                    '单价', '单位', '数量', '金额', '单位全名', '仓库全名', '部门全名']]
    df['日期'] = pd.to_datetime(df['日期'])
    df['备注'] = df['备注'].astype(object)
    dfdel = df[
        (df.单位全名.isnull().values == True) & ((df.单据编号.isnull().values == True) | (df.单据编号 == '小计') | (df.单据编号 == '合计'))]
    hangdel = list(dfdel.index)
    df1 = df.drop(hangdel)  # 丢掉小计和合计行，另起DataFrame
    dfzhiyuan = df1[df1.单位全名.isnull().values == True]  # 提取出项目名称行号
    zyhang = list(dfzhiyuan.index)
    zyming = list(dfzhiyuan['单据编号'])  # 项目名称

    # 每次填充df到最后一行，依次滚动更新之
    for i in range(len(zyhang)):
        df.loc[zyhang[i]:, xiangmu[0]] = zyming[i]

    # 丢掉项目名称行，留下纯数据
    dfdel = df[df.单位全名.isnull().values == True]
    # print(dfdel[['日期', '单据编号', '数量', '金额']])
    hangdel = list(dfdel.index)
    # print(hangdel)
    dfout = df.drop(hangdel)
    dfout.index = range(len(dfout))
    log.info('共有%d条有效记录' % len(dfout))

    # return dfout
    # print(dfout.head(10))

    # 读取大数据的起止日期，不交叉、不是前置则可能是合法数据，二次检查后放行
    cnxp = lite.connect(dbpathquandan)

    # dfout.to_sql(name=tablename, con=cnx, if_exists='replace', chunksize=10000)
    # log.info('成功从数据文件《%s》中添加%d条记录到总数据表中。' %(filename, len(dfout)))

    if (totalin[0] == '%.2f' % dfout.sum()['数量']) & (totalin[1] == '%.2f' % dfout.sum()['金额']):
        dfall = pd.read_sql_query('select 日期, sum(金额) as 销售额 from %s group by 日期 order by 日期' % tablename, cnxp,
                                  parse_dates=['日期'])
        datestr4data = '【待插入S：%s，E：%s】【目标数据S：%s，E：%s】' \
                       % (dfout['日期'].min(), dfout['日期'].max(), dfall['日期'].min(), dfall['日期'].max())
        if (dfall['日期'].max() >= dfout['日期'].min()) or (dfall['日期'].min() >= dfout['日期'].max()):
            log.warning('时间交叉了，请检查数据！%s' % datestr4data)
            # exit(2)
        else:
            print(dfout.tail())
            if (xiangmu[0] == '职员名称'):
                dfout = chengbenjiaupdatedf(dfout, cnxp)
                log.info('要更新%d记录中的成本价和毛利内容' % dfout.shape[0])
            print('请仔细检查！%s' % datestr4data)
            print('如果确保无误，请放行下面两行代码')
            # dfout.to_sql(name=tablename, con=cnxp, if_exists='append', chunksize=10000)
            # log.info('成功从数据文件《%s》中添加%d条记录到总数据表中。' % (filename, len(dfout)))
    else:
        log.warning('对读入文件《%s》的数据整理有误！总数量和总金额对不上！' % filename)

    cnxp.close()

    return dfout


def customerweihu2systable():
    """
    处理客户档案维护记录，规整（填充日期、取有效数据集、板块排序、拆分内容后取有效信息并填充、抽取改编码客户、抽出重复录入纪录）后输出，对改编码客户进行条码更新，手工进入《系统表》
    :return:
    """
    writer = pd.ExcelWriter(str(dirmainpath / 'data' / '结果输出.xlsx'))

    df = pd.read_csv(str(dirmainpath / 'data' / 'kehudanganweihu.txt'), sep=']', header=None, names=['日期', '内容'],
                     na_filter=True,
                     skip_blank_lines=True, skipinitialspace=True)
    # print(df)
    df.to_excel(writer, sheet_name='原始数据整理', freeze_panes={1, 2})
    dfriqi = df[df['内容'].isnull().values == True]  # 找到日期行，获取日期、索引（即行号）
    # print(dfriqi)
    # print(dfriqi.index.values)

    dfout = df
    for i in list(dfriqi.index):
        dfout.loc[i:, ['日期']] = dfriqi.loc[i, '日期']  # 滚动填充日期

    dfout = dfout[df['内容'].isnull().values == False]  # 获取填充日期后的有效数据
    print(len(dfout))

    # print(dfout.dtypes)
    # print(dfout.columns)

    # 转换日期格式，从形如2017年8月/10日转换成标准日期
    # 传入参数为Series

    def riqistr2std(instr):
        riqiokay = ''
        itempattern = re.compile('\s*(?P<year>\d{4})\s*年(?P<month>\d+)月/?(?P<day>\d+)日')
        for j in re.findall(itempattern, instr):  # 形如('2017','8','10')
            # print(j)
            riqiokay = pd.to_datetime(str(j[0]) + '-' + str(j[1]) + '-' + str(j[2]))

        return riqiokay

    dfout.loc[:, '日期'] = dfout['日期'].apply(lambda x: riqistr2std(x))
    dfout.loc[:, '索引'] = dfout.index
    dfout.to_excel(writer, sheet_name='档案整理', freeze_panes={1, 2})
    dfoutsort = dfout.sort_values(by=['日期', '索引'], ascending=True)
    dfoutsort.index = range(len(dfoutsort))  # 重新索引，固化排序
    # dfoutsort.info()
    # print(dfoutsort)
    # print(dfoutsort.head(3))

    dfoutsort['往来单位'] = None
    dfoutsort['往来单位编号'] = None
    dfoutsort['动作'] = None
    dfoutsort['往来单位老'] = None
    dfoutsort['往来单位编号老'] = None
    # dfoutsort.columns = list(list(dfoutsort.columns)+['n1','n2','n3'])
    lsbianma = list()  # 改编码的需要单独处理，索引存入list
    for i in list(dfoutsort.index):
        # 22100430030SXXD/天富（后湖五路） 13871189017 /改成/天富（后湖五路） 13018016563/改店名
        nrsp = ((dfoutsort['内容'])[i]).split('/')
        # print(nrsp)
        if len(nrsp) == 3:
            # ['02300320000SXXD', '小七便利店 18636004123', '新店']
            dfoutsort.loc[i, ['往来单位编号', '往来单位', '动作']] = [nrsp[0].strip(), nrsp[1].strip(), nrsp[2].strip()]
        elif len(nrsp) == 5:
            if '编码' in (nrsp[4].strip()):
                lsbianma.append(i)
                # ['05200100000XXXD', '同丰泰副食 86828538', '改成', '05200100000PXXD', '改编码']
                dfoutsort.loc[i, ['往来单位编号', '往来单位', '动作', '往来单位编号老']] = [nrsp[3].strip(), nrsp[1].strip(),
                                                                         nrsp[4].strip(), nrsp[0].strip()]
                # print(dfoutsort.loc[i])
            else:
                # ['22200680030SXXD', '新北门超市 82310216', '改成', '雅堂小超新北门超市 82310216', '改店名']
                dfoutsort.loc[i, ['往来单位编号', '往来单位', '动作', '往来单位老']] = [nrsp[0].strip(), nrsp[3].strip(),
                                                                       nrsp[4].strip(), nrsp[1].strip()]
    # dfoutsort.info()
    # print(dfoutsort)
    # print(dfoutsort.head(3))
    print(lsbianma)
    dfoutsort.to_excel(writer, sheet_name='档案整理排序', freeze_panes={1, 2})
    dfbm = dfoutsort.loc[lsbianma]
    dfbm.to_excel(writer, sheet_name='编码调整客户', freeze_panes={1, 2})

    lszc = list(set(dfoutsort.index) - set(lsbianma))  # 去掉改编码的纪录
    dfzh = dfoutsort.loc[lszc, ['往来单位', '往来单位编号']]
    # dfzh.info()

    # cnx = lite.connect('data\\quandan.db')
    dfys = pd.read_excel(str(dirmainpath / 'data' / '系统表.xlsx'), sheetname='客户档案')
    # dfys.info()

    dfzh = pd.concat([dfys, dfzh])
    dfzh = pd.DataFrame(dfzh)
    # dfzh.info()
    dfzh.to_excel(writer, sheet_name='合并客户全集', freeze_panes={1, 2})
    dfzh.index = range(len(dfzh))

    dddd = dfzh.duplicated(['往来单位', '往来单位编号'])
    ffff = dddd[dddd == True]
    dfzhcm = dfzh.loc[list(ffff.index)]
    dfzhcm.to_excel(writer, sheet_name='重复录入客户', freeze_panes={1, 2})
    dfzh.info()
    dfzh = dfzh.drop_duplicates(['往来单位', '往来单位编号'])  # 去重
    dfzh.info()
    dfzh = dfzh.drop_duplicates('往来单位')  # 去重
    dfzh.info()

    for i in list(lsbianma):
        print(dfoutsort.loc[i]['往来单位'] + '\t' + dfoutsort.loc[i]['往来单位编号'], end='\t')
        idx = list(dfzh[dfzh.往来单位 == dfoutsort.loc[i]['往来单位']].index)
        print(idx, end='\t')
        print(dfzh.loc[idx, '往来单位编号'].values, end='\t')
        dfzh.loc[idx, '往来单位编号'] = dfoutsort.loc[i, '往来单位编号']
        print(dfzh.loc[idx, '往来单位编号'].values)

    dfzh = dfzh[['往来单位', '往来单位编号', '地址', '助记码', '传真', '联系电话', '联系人', '停用']]
    dfzh.to_excel(writer, sheet_name='整理输出', freeze_panes={1, 2})

    writer.save()
    writer.close()
    pass


def jiaoyankehuchanpin():
    cnx = lite.connect(dbpathquandan)

    dataokay(cnx)

    df = pd.read_sql_query(
        'select xiaoshoumingxi.商品全名 as 品名,xiaoshoumingxi.商品编号,product.* from xiaoshoumingxi left outer join product on '
        'xiaoshoumingxi.商品全名 = product.商品全名 where product.商品全名 is null', cnx)
    df.describe()
    # print(df)
    print(df.groupby(['品名']).count())

    df = pd.read_sql_query('select xiaoshoumingxi.单位全名,customer.* from xiaoshoumingxi left outer join customer on '
                           'xiaoshoumingxi.单位全名 = customer.往来单位 where customer.往来单位 is null', cnx)
    df = df.groupby('单位全名').sum()
    df.describe()
    print(df)

    df = pd.read_sql_query('select * from xiaoshoumingxi', cnx)
    df.info()
    df.describe()
    dfqc = df.drop_duplicates()
    dfqc.info()

    cnx.close()


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    # dfs = details2db('职员销售明细表（2018.7.1-7.31）.xls__20180803165312_602795.xls', '职员销售明细表（2018.7.1-7.31）.xls',
    #                  ['职员名称', '商品全名'], 'xiaoshoumingxi')
    # print(dfs.columns)
    # dfgs = dfs.groupby(['日期', '职员名称'], as_index=False)['数量', '金额'].count()
    # # dfgs['日期', '职员名称'] = dfgs.index
    # descdb(dfgs)
    # dfg = dfgs.groupby(['职员名称'], as_index=False).apply(lambda t: t[t.金额 == t.金额.max()]) \
    #     .sort_values(['金额'], ascending=False)
    # print(dfg.shape[0])
    # print(dfg.tail(30))

    # dfp = details2db('商品进货明细表（2018.7.1-2018.7.31）.xls__20180803165312_635711.xls',
    #                  '商品进货明细表（2018.7.1-2018.7.31）.xls',
    #                  ['产品名称', '经办人'],
    #                  'jinghuomingxi')
    # writer = pd.ExcelWriter(str(dirmainpath / 'data' /'进货分析.xlsx'))
    # dfp.to_excel(writer, sheet_name='商品进货记录', freeze_panes={1, 2})
    # dfg = dfp.groupby(['产品名称', '单价'], as_index=False) \
    #     .apply(lambda t: t[t.日期 == t.日期.min()][['产品名称', '日期', '单价']]).sort_values(['产品名称', '日期'])
    # print(dfg.shape[0])
    # print(dfg.tail(10))
    # dfg.to_excel(writer, sheet_name='进货价格变动记录', freeze_panes={1, 2})
    # writer.close()

    cnxx = lite.connect(dbpathquandan)
    desclitedb(cnxx)
    dataokay(cnxx)
    # jiaoyankehuchanpin()

    # for i in range(len(dfs)):
    #     dfs.loc[i, '成本单价'] = chengbenjia(dfs.iloc[i]['商品全名'], dfs.iloc[i]['日期'], dfgqc)

    # descdb(dfs)
    #
    # dfgg = dfp.groupby(['产品名称'], as_index=False).apply(lambda t: t[t.日期 == t.日期.max()])\
    #     .sort_values(['日期'], ascending=False)
    # dfgg.to_excel(writer, sheet_name='进货价格最新', freeze_panes={1, 2})
    #
    # writer.save()
    # writer.close()
    customerweihu2systable()
    # chengbenjiaupdateall(cnxx)

    cnxx.close()
    print('Done')
