# encoding:utf-8
'''
处理配送数据
'''

from imp4nb import *


def fenxiriyueleiji(note_store,sqlstr,xiangmu,notefenbudf,cnx):
    # df = pd.read_sql_query('select 收款日期,count(终端编码) as danshu,sum(实收金额) as jine from quandan where (配货人!=\'%s\' or 配货人 is null) and (订单日期 >\'%s\') group by 收款日期' %('作废','2016-03-29'),cnx)
    dfquyu= pd.read_sql('select * from quyu',cnx,index_col='index')
    # descdb(dfquyu)
    dfleixing= pd.read_sql('select * from leixing',cnx,index_col='index')
    # descdb(dfleixing)
    fenbulist = ['一部','二部','汉口','汉阳','销售部']
    leixinglist = ['终端客户','连锁客户','渠道客户','直销客户','公关客户','其他客户','全渠道']

    for leixingset in leixinglist:
        if leixingset == '全渠道':
            leixing = tuple(dfleixing['编码'])
        else:
            leixing = tuple((dfleixing[dfleixing['类型'] == leixingset])['编码'])

        if len(leixing) == 1:
            leixing = tuple(list(leixing)+['U'])

        df = pd.read_sql_query('select max(日期) from xiaoshoumingxi',cnx)
        dangqianyueri = pd.to_datetime(df.ix[0][0])
        log.debug(str(dangqianyueri)+'\t：\t'+leixingset)
        if leixingset == '终端客户':
            for fenbuset in fenbulist:
                imglist = []
                if fenbuset == '销售部':
                    fenbu = tuple(dfquyu['区域'])
                else:
                    fenbu = tuple((dfquyu[dfquyu['分部'] == fenbuset])['区域'])

                # df = pd.read_sql_query(
                #     "select 订单日期,count(终端编码) as 单数,sum(送货金额) as 金额,substr(终端编码,1,2) as 区域 ,substr(终端编码,12,1) as 类型 from quandan where (配货人!=\'%s\') and (送达日期 is not null) and(区域 in %s) and(类型 in %s) group by 订单日期" % (
                #     '作废', fenbu, leixing), cnx)
                # df = pd.read_sql_query("select 日期,count(*) as 单数,sum(金额) as 金额,substr(customer.往来单位编号,1,2) as 区域 ,substr(customer.往来单位编号,12,1) as 类型 from xiaoshoumingxi,customer where (customer.往来单位 = xiaoshoumingxi.单位全名) and(区域 in %s) and(类型 in %s) group by 日期" %(fenbu,leixing),cnx)
                log.debug(sqlstr % (xiangmu,fenbu, leixing))
                df = pd.read_sql_query(sqlstr % (xiangmu,fenbu, leixing), cnx)
                df.index = pd.to_datetime(df['日期'])
                # df['单均'] = df['金额'] / df['单数']
                for k in range(dangqianyueri.month):
                    if k==0:
                        riqiendwith = dangqianyueri
                    else:
                        shangyue = dangqianyueri + pd.DateOffset(months=k*(-1))
                        riqiendwith = pd.to_datetime("%04d-%02d-%02d" %(shangyue.year,shangyue.month,cal.monthrange(shangyue.year,shangyue.month)[1]))
                    chubiaorileiji(df,riqiendwith,xiangmu,leixing=leixingset,imglist=imglist,quyu=fenbuset,imgpath='img\\'+fenbuset+'\\')
                if len(imglist) >= 2:
                    imglist = imglist[:2]
                chubiaoyueleiji(df, dangqianyueri, xiangmu, leixing=leixingset, imglist=imglist, quyu=fenbuset,nianshu=5,imgpath='img\\'+fenbuset+'\\')
                imglist2note(note_store, imglist, notefenbudf.loc[fenbuset]['guid'],notefenbudf.loc[fenbuset]['title'])
        else:
            fenbu = tuple(dfquyu['区域'])
            log.debug(sqlstr % (xiangmu, fenbu, leixing))
            df = pd.read_sql_query(sqlstr % (xiangmu,fenbu, leixing), cnx)
            df.index = pd.to_datetime(df['日期'])
            # df['单均'] = df['金额'] / df['单数']
            for k in range(dangqianyueri.month):
                if k == 0:
                    riqiendwith = dangqianyueri
                else:
                    shangyue = dangqianyueri + pd.DateOffset(months=k * (-1))
                    riqiendwith = pd.to_datetime("%04d-%02d-%02d" % (shangyue.year, shangyue.month, cal.monthrange(shangyue.year, shangyue.month)[1]))
                chubiaorileiji(df,riqiendwith,xiangmu,leixing=leixingset,quyu='销售部')
                # chubiaorileiji(df,dangqianyue+pd.DateOffset(months=i*(-1)),'单数')
            chubiaoyueleiji(df,dangqianyueri,xiangmu,leixing=leixingset,quyu='销售部',nianshu=5)

def fenxiyueduibi(note_store,sqlstr,xiangmu,notefenbudf,cnx):
    # df = pd.read_sql_query('select 收款日期,count(终端编码) as danshu,sum(实收金额) as jine from quandan where (配货人!=\'%s\' or 配货人 is null) and (订单日期 >\'%s\') group by 收款日期' %('作废','2016-03-29'),cnx)
    dfquyu= pd.read_sql('select * from quyu',cnx,index_col='index')
    # descdb(dfquyu)
    dfleixing= pd.read_sql('select * from leixing',cnx,index_col='index')
    # descdb(dfleixing)
    fenbulist = ['一部','二部','汉口','汉阳','销售部']
    leixinglist = ['终端客户','连锁客户','渠道客户','直销客户','公关客户','其他客户','全渠道']

    for leixingset in leixinglist:
        if leixingset == '全渠道':
            leixing = tuple(dfleixing['编码'])
        else:
            leixing = tuple((dfleixing[dfleixing['类型'] == leixingset])['编码'])

        if len(leixing) == 1:
            leixing = tuple(list(leixing)+['U'])

        df = pd.read_sql_query('select max(日期) from xiaoshoumingxi',cnx)
        dangqianyueri = pd.to_datetime(df.ix[0][0])
        log.debug(str(dangqianyueri)+'\t：\t'+leixingset)
        if leixingset == '终端客户':
            for fenbuset in fenbulist:
                imglist = []
                if fenbuset == '销售部':
                    fenbu = tuple(dfquyu['区域'])
                else:
                    fenbu = tuple((dfquyu[dfquyu['分部'] == fenbuset])['区域'])

                # df = pd.read_sql_query(
                #     "select 订单日期,count(终端编码) as 单数,sum(送货金额) as 金额,substr(终端编码,1,2) as 区域 ,substr(终端编码,12,1) as 类型 from quandan where (配货人!=\'%s\') and (送达日期 is not null) and(区域 in %s) and(类型 in %s) group by 订单日期" % (
                #     '作废', fenbu, leixing), cnx)
                # df = pd.read_sql_query("select 日期,count(*) as 单数,sum(金额) as 金额,substr(customer.往来单位编号,1,2) as 区域 ,substr(customer.往来单位编号,12,1) as 类型 from xiaoshoumingxi,customer where (customer.往来单位 = xiaoshoumingxi.单位全名) and(区域 in %s) and(类型 in %s) group by 日期" %(fenbu,leixing),cnx)
                log.debug(sqlstr % (xiangmu,fenbu, leixing))
                df = pd.read_sql_query(sqlstr % (xiangmu,fenbu, leixing), cnx)
                df.index = pd.to_datetime(df['日期'])
                # df['单均'] = df['金额'] / df['单数']
                for k in range(dangqianyueri.month):
                    if k==0:
                        riqiendwith = dangqianyueri
                    else:
                        shangyue = dangqianyueri + pd.DateOffset(months=k*(-1))
                        riqiendwith = pd.to_datetime("%04d-%02d-%02d" %(shangyue.year,shangyue.month,cal.monthrange(shangyue.year,shangyue.month)[1]))
                    chubiaorileiji(df,riqiendwith,xiangmu,leixing=leixingset,imglist=imglist,quyu=fenbuset,imgpath='img\\'+fenbuset+'\\')
                if len(imglist) >= 2:
                    imglist = imglist[:2]
                chubiaoyueleiji(df, dangqianyueri, xiangmu, leixing=leixingset, imglist=imglist, quyu=fenbuset,nianshu=5,imgpath='img\\'+fenbuset+'\\')
                imglist2note(note_store, imglist, notefenbudf.loc[fenbuset]['guid'],notefenbudf.loc[fenbuset]['title'])
        else:
            fenbu = tuple(dfquyu['区域'])
            log.debug(sqlstr % (xiangmu, fenbu, leixing))
            df = pd.read_sql_query(sqlstr % (xiangmu,fenbu, leixing), cnx)
            df.index = pd.to_datetime(df['日期'])
            # df['单均'] = df['金额'] / df['单数']
            for k in range(dangqianyueri.month):
                if k == 0:
                    riqiendwith = dangqianyueri
                else:
                    shangyue = dangqianyueri + pd.DateOffset(months=k * (-1))
                    riqiendwith = pd.to_datetime("%04d-%02d-%02d" % (shangyue.year, shangyue.month, cal.monthrange(shangyue.year, shangyue.month)[1]))
                chubiaorileiji(df,riqiendwith,xiangmu,leixing=leixingset,quyu='销售部')
                # chubiaorileiji(df,dangqianyue+pd.DateOffset(months=i*(-1)),'单数')
            chubiaoyueleiji(df,dangqianyueri,xiangmu,leixing=leixingset,quyu='销售部',nianshu=5)



