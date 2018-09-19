# encoding:utf-8
"""
核算工资
"""
# from imp4nb import *
import numpy as np
import pandas as pd
import sqlite3 as lite

import pathmagic

with pathmagic.context():
    from func.first import dbpathquandan, dirmainpath
    from func.pdtools import descdb, dataokay, desclitedb
    from func.logme import log


def salesjiangjin(cnxs):
    feiqudaokehustr = '  and (leixing.类型 !=\'渠道客户\')'
    # feiqudaokehustr = ''
    qrystr = "select strftime('%Y%m',日期) as 年月, 职员名称 as 业务主管, substr(customer.往来单位编号,1,2) as 区域, " \
             "xiaoshoumingxi.商品全名 as 产品, product.推广等级 as 等级, 单位全名 as 客户名称, 单据编号, " \
             '金额 as 销售金额, 成本金额 as 成本金额, substr(customer.往来单位编号,12,1) as 类型编码 ' \
             'from xiaoshoumingxi, customer, product, leixing ' \
             'where (customer.往来单位 = xiaoshoumingxi.单位全名) and (product.商品全名 = xiaoshoumingxi.商品全名) and ' \
             ' (leixing.编码 = 类型编码)'
    qrystr += feiqudaokehustr
    qrystr += ' order by 年月, 业务主管'
    print(qrystr)
    df = pd.read_sql_query(qrystr, cnxs)

    df['销售金额净'] = df['销售金额'].apply(lambda x: x * 4 if x <= 0 else x)
    # descdb(df)
    df['成本金额净'] = df['成本金额'][df.销售金额 == 0] * 8
    df['成本金额净'] = df['成本金额'][df.销售金额 != 0]
    df['毛利净'] = df['销售金额净'] - df['成本金额净']
    descdb(df)
    ticheng = [0, 0.005, 0.01, 0.025, 0.035]
    df['提成比例'] = df['等级'].apply(lambda x: ticheng[x - 1])
    df['业绩奖金'] = df['销售金额净'] * df['提成比例']

    # print(df[df.业务主管 == '耿华忠'].groupby(['年月', '业务主管', '客户名称', '单据编号'])['销售金额净'].sum())

    dftarget = df[df.年月 >= '201801'].groupby(['年月', '业务主管', '等级', '产品'], as_index=False)['销售金额净', '毛利净', '业绩奖金'].sum()
    dfyd = dftarget.groupby(['年月', '业务主管', '等级'], as_index=False)['销售金额净', '毛利净', '业绩奖金'].sum()
    dfyt = dfyd.groupby(['年月', '业务主管', '等级'])['销售金额净', '毛利净', '业绩奖金'].sum().unstack().fillna(value=0).sort_index(
        ascending=False)
    dfyt.reset_index(inplace=True)
    descdb(dfyt)

    # global dirmainpath
    xlswriter = pd.ExcelWriter(str(dirmainpath / 'data' / '业绩奖金.xlsx'))
    dfyt.to_excel(xlswriter, '业绩奖金', freeze_panes=[2, 2])
    xlswriter.close()

    dfy = dftarget.groupby(['年月', '业务主管'], as_index=False)['销售金额净', '毛利净', '业绩奖金'].sum()
    print(dfy.tail(60))


def peisonghesuan(cnxp):
    qrystr = "select 订单日期,strftime('%Y%m',订单日期) as 年月订单, strftime('%Y%m',送达日期) as 年月送达, " \
             "strftime('%Y%m',收款日期) as 年月收款, 配货人, 配货准确 as 错配, 业务主管, " \
             "substr(终端编码,1,2) as 区域,  substr(终端编码,12,1) as 类型编码, leixing.类型 as 客户类型," \
             "送货金额 as 订单金额, 实收金额, 优惠, 退货金额,客户拒收,无货金额,少配金额,配错未要,送货人,收款日期" \
             " from quandan, leixing " \
             'where (leixing.编码 = 类型编码)'
    df = pd.read_sql_query(qrystr, cnxp)
    df['订单净值'] = df.fillna(0)['订单金额'] - df.fillna(0)['客户拒收'] - df.fillna(0)['无货金额'] \
                 - df.fillna(0)['少配金额'] - df.fillna(0)['配错未要']

    df['优惠'] = df['优惠'].fillna(0)
    df['优惠'] = df['优惠'].astype(float)
    # print(df.tail(10))
    xlswriter = pd.ExcelWriter(str(dirmainpath / 'data' / '全单统计.xlsx'))
    feipeihuoliebiao = ['陈列', '返利', '赠送', '作废', np.nan]
    df = df[(df.年月收款 >= '201801') & (df.配货人.isin(feipeihuoliebiao).values == False)]

    dfpeihuo = df.groupby(['年月订单', '配货人'], as_index=False)['订单日期', '错配'].count().sort_index(ascending=False)
    # print(dfpeihuo.tail(30))
    dfpeihuo.to_excel(xlswriter, '配货统计', freeze_panes=[1, 2])

    dfyewujushou = df.groupby(['年月送达', '业务主管'], as_index=False)['订单日期', '客户拒收'].count().sort_index(ascending=False)
    # print(dfyewujushou.head(20))
    dfyewujushou.to_excel(xlswriter, '业务订单拒收统计', freeze_panes=[1, 2])

    # print(df.dtypes)
    dfhuikuan = df.groupby(['年月收款', '业务主管'], as_index=False)[
        '订单净值', '实收金额', '优惠', '退货金额', '客户拒收', '无货金额', '少配金额', '配错未要'].sum()
    # print(dfhuikuan)
    dfhuikuan['回款净值'] = dfhuikuan['实收金额'] - dfhuikuan['优惠'] * 8 - dfhuikuan['退货金额'] * 4
    # print(dfhuikuan.tail(30))
    dfhuikuan.sort_index(ascending=False).to_excel(xlswriter, '业务回款统计', freeze_panes=[1, 2])

    dfhuikuan = df.groupby(['年月收款'], as_index=False)['订单净值', '实收金额', '优惠', '退货金额', '客户拒收', '无货金额', '少配金额', '配错未要'].sum()
    dfhuikuan['回款净值'] = dfhuikuan['实收金额'] - dfhuikuan['优惠'] * 8 - dfhuikuan['退货金额'] * 4
    print(dfhuikuan.tail(30))
    dfhuikuan.sort_index(ascending=False).to_excel(xlswriter, '公司回款统计', freeze_panes=[1, 2])

    df['客户类型'] = df['客户类型'].apply(lambda x: '非渠道客户' if (x != '渠道客户') else '渠道客户')
    dfkefu = df.groupby(['年月送达', '送货人', '客户类型']).agg(
        {'订单净值': ['sum', 'count'], '客户拒收': ['sum', 'count']}).unstack().sort_index(ascending=False)
    print(dfkefu.tail(20))
    dfkefu.fillna(0, inplace=True)
    dfkefu.to_excel(xlswriter, '配送统计', freeze_panes=[3, 2])
    xlswriter.close()

    # descdb(df)


if __name__ == '__main__':
    log.info(f'测试文件\t{__file__}')
    cnx = lite.connect(dbpathquandan)
    dataokay(cnx)
    desclitedb(cnx)
    salesjiangjin(cnx)
    peisonghesuan(cnx)
    cnx.close()
