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
            dftmp = (
            (dfs[(dfs.日期 >= yuandiandate) & (dfs.日期 <= ix) & (dfs[xiangmu].isnull().values == False)]).groupby('客户编码'))[
                xiangmu].count()
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
    # print(df.tail(10))
    # df = df.fillna(0)
    kuangjiachutu(token, note_store, notefenbudf, noteleixingdf, df, xiangmu, cnx, pinpai, cum)


def kuangjiachutu(token, note_store, notefenbudf, noteleixingdf, df, xiangmu, cnx, pinpai, cum=False):
    dfquyu = pd.read_sql('select * from quyu', cnx, index_col='index')
    dfleixing = pd.read_sql('select * from leixing', cnx, index_col='index')
    fenbulist = list(notefenbudf.index)
    # print(fenbulist)
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
                htable = dfin[dfin.index > (dfin.index.max() + pd.Timedelta(days=-365))].sort_index(
                    ascending=False).to_html().replace('class="dataframe"', '')
                imglist2note(note_store, imglist, notefenbudf.loc[fenbuset]['guid'], notefenbudf.loc[fenbuset]['title'],
                             neirong=htable)
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
                htable = dfin[dfin.index > (dfin.index.max() + pd.Timedelta(days=-365))].sort_index(
                    ascending=False).to_html().replace('class="dataframe"', '')
                imglist2note(note_store, imglist, noteleixingdf.loc[leixingset]['guid'],
                             noteleixingdf.loc[leixingset]['title'], neirong=htable)


def pinpaifenxi(token, note_store, cnx, daysbefore=90, brandnum=30, fenbu='fenbu'):
    qrypinpai = "select max(日期) as 最近日期, sum(金额) as 销售金额, product.品牌名称 as 品牌 from xiaoshoumingxi,product " \
                "where (product.商品全名 = xiaoshoumingxi.商品全名) group by 品牌 order by 最近日期"
    dff = pd.read_sql_query(qrypinpai, cnx, parse_dates=['最近日期'])
    # print(dff)
    brandlist = list(dff[dff.最近日期 >= (dff.最近日期.max() + pd.Timedelta(days=daysbefore * (-1)))]['品牌'])
    if len(brandlist) > brandnum:
        brandlist = brandlist[brandnum * (-1):]
    # brandlist = list(dff['品牌'])
    brandlist.append('')
    # brandlist = brandlist[4:]
    print(brandlist)
    for br in brandlist:
        log.info('第%d个品牌：%s，共有%d个品牌' % (brandlist.index(br) + 1, br, len(brandlist)))
        updatesection(cfpdata, 'guid%snb' % fenbu, br + 'kehuguid%s' % fenbu, inidatanotefilepath, token, note_store,
                      br + '客户开发图表')
        updatesection(cfpdata, 'guid%snb' % fenbu, br + 'saleguid%s' % fenbu, inidatanotefilepath, token, note_store,
                      br + '销售业绩图表')
        updatesection(cfpdata, 'guidleixingnb', br + 'kehuguidleixing', inidatanotefilepath, token, note_store,
                      br + '客户开发图表')
        updatesection(cfpdata, 'guidleixingnb', br + 'saleguidleixing', inidatanotefilepath, token, note_store,
                      br + '销售业绩图表')

        # notelxxsdf = ['']
        notelxxsdf = readinisection2df(cfpdata, br + 'saleguidleixing', br + '销售图表')
        notefbxsdf = readinisection2df(cfpdata, br + 'saleguid%s' % fenbu, br + '销售图表')
        # print(notefbxsdf)

        qrystr = "select 日期,strftime('%%Y%%m',日期) as 年月,customer.往来单位编号 as 客户编码," + \
                 'sum(金额) as %s, substr(customer.往来单位编号,1,2) as 区域 ,substr(customer.往来单位编号,12,1) as 类型, ' \
                 'product.品牌名称 as 品牌 from xiaoshoumingxi, customer, product ' \
                 'where (customer.往来单位 = xiaoshoumingxi.单位全名) and (product.商品全名 = xiaoshoumingxi.商品全名) ' \
                 '%s %s group by 日期,客户编码 order by 日期'  # % (xmclause,jineclause, brclause)
        xiangmu = ['销售金额', '退货金额']
        fenxiyueduibi(token, note_store, qrystr, xiangmu, notefbxsdf, notelxxsdf, cnx, pinpai=br, cum=True)
        # fenximonthduibi(token, note_store, cnx, notefbxsdf, notelxxsdf, '金额', pinpai=br, cum=True)

        # notelxkhdf = ['']
        notelxkhdf = readinisection2df(cfpdata, br + 'kehuguidleixing', br + '客户图表')
        notefbkhdf = readinisection2df(cfpdata, br + 'kehuguid%s' % fenbu, br + '客户图表')
        # print(notefbkhdf)
        qrystr = "select 日期,strftime('%%Y%%m',日期) as 年月,customer.往来单位编号 as 客户编码," + \
                 'count(*) as %s, substr(customer.往来单位编号,1,2) as 区域 ,' \
                 'substr(customer.往来单位编号,12,1) as 类型, ' \
                 'product.品牌名称 as 品牌 from xiaoshoumingxi, customer, product ' \
                 'where (customer.往来单位 = xiaoshoumingxi.单位全名)  and (product.商品全名 = xiaoshoumingxi.商品全名) ' \
                 '%s %s group by 日期,客户编码 order by 日期'  # % (xmclause,jineclause, brclause)
        xiangmu = ['销售客户数', '退货客户数']
        fenxiyueduibi(token, note_store, qrystr, xiangmu, notefbkhdf, notelxkhdf, cnx, pinpai=br)
        # fenximonthduibi(token, note_store, '退货客户数', notefbkhdf, notelxkhdf, cnx, pinpai=br)


if __name__ == '__main__':
    cnx = lite.connect(dbpathquandan)
    dataokay(cnx)
    token = cfp.get('evernote', 'token')
    pinpaifenxi(token, get_notestore(), cnx, daysbefore=15, brandnum=1)
