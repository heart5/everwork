# encoding:utf-8
"""
处理销售明细数据
"""

from imp4nb import *


def getgroupdf(dfs, xiangmu, period='month'):
    dfmoban = dfs.groupby('日期')[xiangmu].count()  # 获得按照日期汇总后的DataFrame，日期唯一，值其实随意，这里随意取了当天的销售额
    dfmoban = pd.DataFrame(dfmoban, index=pd.to_datetime(dfmoban.index))
    dates = pd.date_range(dfmoban.index.min(), periods=(dfmoban.index.max() - dfmoban.index.min()).days + 1,
                          freq='D')
    dfmoban = dfmoban.reindex(dates, fill_value=0)
    for ix in dfmoban.index:
        if period == 'year':
            ixyuechudate = pd.to_datetime("%04d-01-01" % (ix.year))
        else:
            ixyuechudate = pd.to_datetime("%04d-%02d-01" % (ix.year, ix.month))
        dftmp = ((dfs[(dfs.日期 >= ixyuechudate) & (dfs.日期 <= ix)]).groupby('客户编码'))[xiangmu].count()
        dfmoban.loc[ix][xiangmu] = dftmp.shape[0]

    return dfmoban


def fenximonthduibi(token, note_store, cnx, notefenbudf, noteleixingdf, xiangmu, pinpai='', cum=False):
    dfquyu = pd.read_sql('select * from quyu', cnx, index_col='index')
    dfleixing = pd.read_sql('select * from leixing', cnx, index_col='index')
    fenbulist = list(notefenbudf.index)
    # print(fenbulist)
    leixinglist = ['终端客户', '连锁客户', '渠道客户', '直销客户', '公关客户', '其他客户', '全渠道']

    qrystr = "select 日期,sum(金额) as 销售金额 from xiaoshoumingxi " \
             "where (金额 >= 0)"
    if len(pinpai) > 0:
        qrystr += ' and (品牌 = \'%s\')' % pinpai
    qrystr += ' group by 日期 order by 日期'

    dfz = pd.read_sql_query(qrystr, cnx)
    log.info(qrystr)
    print(dfz.shape[0])
    print(dfz.dtypes)
    if dfz.shape[0] == 0:
        log.info('%s数据查询为空，返回' % pinpai)
        return

    dfz['日期'] = pd.to_datetime(dfz['日期'])
    dfz.index = dfz['日期']
    del dfz['日期']
    print(dfz.loc[pd.to_datetime('2017-01-10')])
    print(dfz.tail(10))

    qrystr = "select 日期,sum(金额) as 退货金额 from xiaoshoumingxi " \
             "where (金额 < 0)"
    if len(pinpai) > 0:
        qrystr += ' and (品牌 = \'%s\')' % pinpai
    qrystr += ' group by 日期 order by 日期'

    dff = pd.read_sql_query(qrystr, cnx)
    log.info(qrystr)
    print(dff.shape[0])
    print(dff.dtypes)
    if dff.shape[0] == 0:
        log.info('%s数据查询为空，返回' % pinpai)
        return

    dff['日期'] = pd.to_datetime(dff['日期'])
    dff.index = dff['日期']
    del dff['日期']
    print(dff.loc[pd.to_datetime('2017-01-08')])
    print(dff.tail(10))

    dddd = dfz.join(dff, how='outer')
    print('………………')
    print(dddd.tail(10))
    print('………………')
    dddd = dddd.fillna(0)

    df = dddd.reindex(pd.date_range(dddd.index.min(), dddd.index.max()), fill_value=0)

    df = df[df.index < '2016-03-15']
    print(df.shape[0])
    print(df.dtypes)
    print(df.tail(10))

    # exit(5)

    for leixingset in leixinglist:
        if leixingset == '全渠道':
            leixing = tuple(dfleixing['编码'])
        else:
            leixing = tuple((dfleixing[dfleixing['类型'] == leixingset])['编码'])

        if len(leixing) == 1:
            leixing = tuple(list(leixing) + ['U'])

        log.debug(f'{str(df.index.max())}\t：\t{leixingset}')
        if leixingset == '终端客户':
            for fenbuset in fenbulist:
                if fenbuset == '所有分部':
                    fenbu = tuple(set(dfquyu['区域']))
                else:
                    fenbu = tuple((dfquyu[dfquyu['分部'] == fenbuset])['区域'])

                # dfs = df[(df.类型.isin(leixing).values == True) & (df.区域.isin(fenbu).values == True)]
                dfs = df
                if dfs.shape[0] == 0:
                    log.info(f'在客户类型为“{str(leixingset)}”且所在位置为“{fenbuset}”时无数据！')
                    continue
                if cum:
                    dfmoban = dfs
                else:
                    dfmoban = dfs

                print(dfmoban.shape[0])
                print(dfmoban.dtypes)
                print(dfmoban.tail(10))

                # exit(5)

                dangqianyueri = dfmoban.index.max()
                imglist = []
                for k in range(dangqianyueri.month):
                    if k == 0:
                        riqiendwith = dangqianyueri
                    else:
                        shangyue = dangqianyueri + pd.DateOffset(months=k * (-1))
                        riqiendwith = pd.to_datetime("%04d-%02d-%02d" % (
                        shangyue.year, shangyue.month, cal.monthrange(shangyue.year, shangyue.month)[1]))
                    for cln in dfmoban.columns:
                        chuturizhexian(dfmoban[cln], riqiendwith, cln, cum=cum, imglist=imglist, quyu=fenbuset,
                                       leixing=leixingset, pinpai=pinpai, imgpath='img\\' + fenbuset + '\\')
                if len(imglist) >= 2:
                    imglist = imglist[:2]
                # if not cum:
                #     dfmoban = getgroupdf(dfs, xiangmu,'year')
                chubiaoyuezhexian(dfmoban, dangqianyueri, xiangmu, cum=cum, leixing=leixingset, imglist=imglist,
                                  quyu=fenbuset, pinpai=pinpai, nianshu=5, imgpath='img\\' + fenbuset + '\\')
                # myrndsleep()
                # imglist2note(note_store, imglist, notefenbudf.loc[fenbuset]['guid'],notefenbudf.loc[fenbuset]['title'], token)
        else:
            # dfs = df[df.类型.isin(leixing).values == True]
            dfs = df
            if dfs.shape[0] == 0:
                log.info(f'在客户类型“{str(leixingset)}”中时无数据！')
                continue
            if cum:
                dfmoban = dfs
            else:
                dfmoban = dfs

            print(dfmoban.shape[0])
            print(dfmoban.dtypes)
            print(dfmoban.tail(10))

            exit(5)

            dangqianyueri = dfmoban.index.max()
            print(dangqianyueri)
            imglist = []
            for k in range(dangqianyueri.month):
                if k == 0:
                    riqiendwith = dangqianyueri
                else:
                    shangyue = dangqianyueri + pd.DateOffset(months=k * (-1))
                    riqiendwith = pd.to_datetime("%04d-%02d-%02d" % (
                    shangyue.year, shangyue.month, cal.monthrange(shangyue.year, shangyue.month)[1]))
                chuturizhexian(dfmoban, riqiendwith, xiangmu, cum=cum, leixing=leixingset, pinpai=pinpai,
                               imglist=imglist, imgpath='img\\' + leixingset + '\\')
            if len(imglist) >= 3:
                imglist = imglist[:3]
            # if not cum:
            #     dfmoban = getgroupdf(dfs, xiangmu, 'year')
            chubiaoyuezhexian(dfmoban, dangqianyueri, xiangmu, cum=cum, leixing=leixingset, pinpai=pinpai,
                              imglist=imglist, nianshu=5, imgpath='img\\' + leixingset + '\\')
            # targetlist = list(noteleixingdf.index)
            # # targetlist = []
            # if leixingset in targetlist:
            #     # myrndsleep()
            #     imglist2note(note_store, imglist, noteleixingdf.loc[leixingset]['guid'], noteleixingdf.loc[leixingset]['title'], token)
