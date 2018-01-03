# encoding:utf-8
'''
处理配送数据
'''

from imp4nb import *

def getgroupdf( dfs,xiangmu,period='month'):
    dfmoban = dfs.groupby('日期')[xiangmu].count()  # 获得按照日期汇总后的DataFrame，日期唯一，值其实随意，这里随意取了当天的销售额
    dfmoban = pd.DataFrame(dfmoban,index=pd.to_datetime(dfmoban.index))
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


def fenxiyueduibi(note_store, sqlstr, xiangmu, notefenbudf, noteleixingdf, cnx, pinpai='', cum=False):
    dfquyu= pd.read_sql('select * from quyu',cnx,index_col='index')
    dfleixing= pd.read_sql('select * from leixing',cnx,index_col='index')
    fenbulist = list(notefenbudf.index)
    print(fenbulist)
    leixinglist = ['终端客户','连锁客户','渠道客户','直销客户','公关客户','其他客户','全渠道']

    df = pd.read_sql_query(sqlstr, cnx)
    log.info(sqlstr)

    df['日期'] = pd.to_datetime(df['日期'])
    print(df.tail(5))

    for leixingset in leixinglist:
        if leixingset == '全渠道':
            leixing = tuple(dfleixing['编码'])
        else:
            leixing = tuple((dfleixing[dfleixing['类型'] == leixingset])['编码'])

        if len(leixing) == 1:
            leixing = tuple(list(leixing)+['U'])

        log.debug(str(df['日期'].max())+'\t：\t'+leixingset)
        if leixingset == '终端客户':
            for fenbuset in fenbulist:
                if fenbuset == '所有分部':
                    fenbu = tuple(set(dfquyu['区域']))
                else:
                    fenbu = tuple((dfquyu[dfquyu['分部'] == fenbuset])['区域'])

                dfs = df[(df.类型.isin(leixing).values == True) & (df.区域.isin(fenbu).values == True)]
                if dfs.shape[0] == 0:
                    log.info('在客户类型为“'+str(leixingset)+'”且所在位置为“'+fenbuset+'”时无数据！')
                    continue
                if cum:
                    dfmoban = dfs.groupby('日期')[xiangmu].sum()
                    dfmoban = pd.DataFrame(dfmoban, index=pd.to_datetime(dfmoban.index))
                    # dfmoban.columns = [xiangmu]
                else:
                    dfmoban = getgroupdf(dfs, xiangmu)

                dangqianyueri = dfmoban.index.max()
                imglist = []
                for k in range(dangqianyueri.month):
                    if k==0:
                        riqiendwith = dangqianyueri
                    else:
                        shangyue = dangqianyueri + pd.DateOffset(months=k*(-1))
                        riqiendwith = pd.to_datetime("%04d-%02d-%02d" %(shangyue.year,shangyue.month,cal.monthrange(shangyue.year,shangyue.month)[1]))
                    chubiaorizhexian(dfmoban, riqiendwith, xiangmu, cum=cum, leixing=leixingset, imglist=imglist, quyu=fenbuset, pinpai=pinpai, imgpath='img\\'+fenbuset+'\\')
                if len(imglist) >= 2:
                    imglist = imglist[:2]
                # if not cum:
                #     dfmoban = getgroupdf(dfs, xiangmu,'year')
                chubiaoyuezhexian(dfmoban, dangqianyueri, xiangmu, cum =cum, leixing=leixingset, imglist=imglist, quyu=fenbuset, pinpai=pinpai, nianshu=5, imgpath='img\\'+fenbuset+'\\')
                # myrndsleep()
                imglist2note(note_store, imglist, notefenbudf.loc[fenbuset]['guid'],notefenbudf.loc[fenbuset]['title'])
        else:
            dfs = df[df.类型.isin(leixing).values == True]
            if dfs.shape[0] == 0:
                log.info('在客户类型“' + str(leixingset) + '”中时无数据！')
                continue
            if cum:
                dfmoban = dfs.groupby('日期')[xiangmu].sum()
                dfmoban = pd.DataFrame(dfmoban,index=pd.to_datetime(dfmoban.index))
            else:
                dfmoban = getgroupdf(dfs, xiangmu)

            dangqianyueri = dfmoban.index.max()
            print(dangqianyueri)
            imglist = []
            for k in range(dangqianyueri.month):
                if k == 0:
                    riqiendwith = dangqianyueri
                else:
                    shangyue = dangqianyueri + pd.DateOffset(months=k * (-1))
                    riqiendwith = pd.to_datetime("%04d-%02d-%02d" % (shangyue.year, shangyue.month, cal.monthrange(shangyue.year, shangyue.month)[1]))
                chubiaorizhexian(dfmoban, riqiendwith, xiangmu, cum=cum, leixing=leixingset, pinpai=pinpai, imglist=imglist, imgpath='img\\'+leixingset+'\\')
            if len(imglist) >= 3:
                imglist = imglist[:3]
            # if not cum:
            #     dfmoban = getgroupdf(dfs, xiangmu, 'year')
            chubiaoyuezhexian(dfmoban, dangqianyueri, xiangmu, cum=cum, leixing=leixingset, pinpai=pinpai, imglist=imglist, nianshu=5, imgpath='img\\'+leixingset+'\\')
            targetlist = list(noteleixingdf.index)
            # targetlist = []
            if leixingset in targetlist:
                # myrndsleep()
                imglist2note(note_store, imglist, noteleixingdf.loc[leixingset]['guid'], noteleixingdf.loc[leixingset]['title'])



