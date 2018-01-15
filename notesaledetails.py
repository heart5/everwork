# encoding:utf-8
"""
处理销售明细数据
"""


from imp4nb import *


def getgroupdf(dfs, xiangmus, period='month'):
    dfmobans = dfs.groupby('日期')[xiangmus].sum()  # 日期唯一，就是求个框架，值其实随意，这里随意取了当天的sum（对数值有效）
    dfout = pd.DataFrame()
    for xiangmu in xiangmus:
        if xiangmu in list(dfmobans.columns):
            dfmoban = dfmobans[xiangmu]
        else:
            log.info(str(set(dfs['品牌'])) + xiangmu + '无数据')
            continue
        dfmoban = dfmoban.dropna()  # 去除空值避免干扰
        if dfmoban.shape[0] == 0:  # 无有效数据则轮空，不循环
            continue
        dates = pd.date_range(dfmoban.index.min(), periods=(dfmoban.index.max() - dfmoban.index.min()).days + 1,
                              freq='D')
        dfman = dfmoban.reindex(dates)
        for ix in dfman.index:
            if period == 'year':
                yuandiandate = pd.to_datetime('%4d-01-01' % ix.year)  # MonthEnd()好坑，处理不好月头月尾的数据
                # yuandiandate = ix + YearBegin(-1)  # MonthEnd()好坑，处理不好月头月尾的数据
            else:
                yuandiandate = pd.to_datetime('%4d-%2d-01' % (ix.year, ix.month))
                # yuandiandate = ix + MonthBegin(-1)
            dftmp = ((dfs[(dfs.日期 >= yuandiandate) & (dfs.日期 <= ix)]).groupby('客户编码'))[xiangmu].count()
            dfman[ix] = dftmp.shape[0]
        dfout = dfout.join(pd.DataFrame(dfman), how='outer')

    return dfout


def fenxiyueduibi(token, note_store, sqlstr, xiangmu, notefenbudf, noteleixingdf, cnx, pinpai='', cum=False):

    log.info(sqlstr)
    xmclause = xiangmu[0]
    jineclause = ' and (金额 >= 0) '
    brclause = ''
    if len(pinpai) > 0:
        brclause += ' and (品牌 = \'%s\') ' % pinpai
    sqlz = sqlstr % (xmclause, jineclause, brclause)
    dfz = pd.read_sql_query(sqlz, cnx, parse_dates=['日期'])
    log.info(sqlz)

    xmclause = xiangmu[1]
    jineclause = ' and (金额 < 0) '
    sqlf = sqlstr % (xmclause, jineclause, brclause)
    dff = pd.read_sql_query(sqlf, cnx, parse_dates=['日期'])
    log.info(sqlf)

    df = pd.merge(dfz, dff, how='outer', on=['日期', '年月', '客户编码', '区域', '类型', '品牌'], sort=True)
    print(df.tail(10))
    # df = df.fillna(0)
    kuangjiachutu(token, note_store, notefenbudf, noteleixingdf, df, xiangmu, cnx, pinpai, cum)


def kuangjiachutu(token, note_store, notefenbudf, noteleixingdf, df, xiangmu, cnx, pinpai, cum=False):
    dfquyu = pd.read_sql('select * from quyu', cnx, index_col='index')
    dfleixing = pd.read_sql('select * from leixing', cnx, index_col='index')
    fenbulist = list(notefenbudf.index)
    print(fenbulist)
    leixinglist = ['终端客户', '连锁客户', '渠道客户', '直销客户', '公关客户', '其他客户', '全渠道']

    if df.shape[0] == 0:
        log.info('%s数据查询为空，返回' % pinpai)
        return

    for leixingset in leixinglist:
        if leixingset == '全渠道':
            leixing = tuple(dfleixing['编码'])
        else:
            leixing = tuple((dfleixing[dfleixing['类型'] == leixingset])['编码'])

        if len(leixing) == 1:
            leixing = tuple(list(leixing) + ['U'])

        if leixingset == '终端客户':
            for fenbuset in fenbulist:
                if fenbuset == '所有分部':
                    fenbu = tuple(set(dfquyu['区域']))
                else:
                    fenbu = tuple((dfquyu[dfquyu['分部'] == fenbuset])['区域'])

                log.debug(str(df['日期'].max()) + '\t：\t' + leixingset + '\t，\t' + fenbuset)
                dfs = df[(df.类型.isin(leixing).values == True) & (df.区域.isin(fenbu).values == True)]
                if dfs.shape[0] == 0:
                    log.info('在客户类型为“' + str(leixingset) + '”且所在位置为“' + fenbuset + '”时无数据！')
                    continue  # 对应fenbuset
                if cum:
                    dfin = dfs.groupby('日期').sum()
                else:
                    dfin = getgroupdf(dfs, xiangmu)
                imglist = dfin2imglist(dfin, cum=cum, leixingset=leixingset, fenbuset=fenbuset, pinpai=pinpai)
                imglist2note(note_store, imglist, notefenbudf.loc[fenbuset]['guid'], notefenbudf.loc[fenbuset]['title'],
                             token)
        else:
            log.debug(str(df['日期'].max()) + '\t：\t' + leixingset)
            dfs = df[df.类型.isin(leixing).values == True]
            if dfs.shape[0] == 0:
                log.info('在客户类型“' + str(leixingset) + '”中时无数据！')
                continue
            if cum:
                dfin = dfs.groupby('日期').sum()
                dfin = pd.DataFrame(dfin, index=pd.to_datetime(dfin.index))
            else:
                dfin = getgroupdf(dfs, xiangmu)
            imglist = dfin2imglist(dfin, cum=cum, leixingset=leixingset, pinpai=pinpai)
            targetlist = list(noteleixingdf.index)
            if leixingset in targetlist:
                imglist2note(note_store, imglist, noteleixingdf.loc[leixingset]['guid'],
                             noteleixingdf.loc[leixingset]['title'], token)