# encoding:utf-8
# 处理配送全单数据
#
from imp4nb import *


def gengxinfou(filename,conn,tablename='fileread'):
    rt = False
    try:
        create_tb_cmd = "CREATE TABLE IF NOT EXISTS %s " \
                        "('文件名' TEXT," \
                        "'绝对路径' TEXT, " \
                        "'修改时间' TIMESTAMP," \
                        "'设备编号' INTEGER," \
                        "'文件大小' INTEGER," \
                        "'登录时间' TIMESTAMP); " % tablename
        conn.execute(create_tb_cmd)
    except Exception:
        print("创建数据表%s失败！" % tablename)
        return rt

    fna = os.path.abspath(filename)
    fn = os.path.basename(fna)
    fstat = os.stat(filename)
    # print(fn)

    # sql = "delete from %s where 文件大小 > 0" %tablename
    # print(sql)
    # result = conn.cursor().execute(sql)
    # conn.commit()
    # print(('共删除了'+str(result.fetchone())[0])+'条记录')

    c = conn.cursor()
    sql = "select count(*) from %s where 文件名 = \'%s\'" %(tablename,fn)
    result = c.execute(sql)
    # print(result.lastrowid)
    # conn.commit()
    fncount = (result.fetchone())[0]
    if fncount == 0:
        print("文件《"+fn+"》无记录，录入信息！\t", end='\t')
        result = c.execute("insert into %s values(?,?,?,?,?,?)"
                           % tablename, (fn, fna,
                                         time.strftime('%Y-%m-%d %H:%M:%S',
                                                       time.localtime(fstat.st_mtime)),
                                         str(fstat.st_dev), str(fstat.st_size),
                                         time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        print('添加成功。')
        rt = True
    else:
        print("文件《"+fn+"》已有 "+str(fncount)+" 条记录，看是否最新？\t",end='\t')
        sql = "select max(修改时间) as xg from %s where 文件名 = \'%s\'" % (tablename,fn)
        result = c.execute(sql)
        if time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)) > (result.fetchone())[0]:
            result = c.execute("insert into %s values(?,?,?,?,?,?)" % tablename,(fn,fna,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)),str(fstat.st_dev),str(fstat.st_size),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())))
            print('更新成功！')
            rt = True
        else:
            print('无需更新。')
            rt = False
    # print(fstat.st_mtime, '\t', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_atime)),'\t', '\t', time.strftime('%Y-%m-%d %H:%M',time.localtime(fstat.st_mtime)),'\t', '\t', time.strftime('%Y-%m-%d %H:%M',time.localtime(fstat.st_ctime)),'\t', fstat.st_dev)
    conn.commit()

    return rt

def dataokay(cnx):
    if gengxinfou('data\\系统表.xlsx', cnx, 'fileread'):# or True:
        df = pd.read_excel('data\\系统表.xlsx', sheetname='区域')
        df['区域'] = pd.DataFrame(df['区域']).apply(lambda r: '%02d' %r, axis=1)
        print(df)
        df=df.loc[:,['区域','区域名称', '分部']]
        df.to_sql(name='quyu', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='小区')
        df['小区'] = pd.DataFrame(df['小区']).apply(lambda r: '%03d' %r, axis=1)
        print(df)
        df.to_sql(name='xiaoqu', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='终端类型')
        print(df)
        df.to_sql(name='leixing', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='产品档案',)
        print(df)
        df.to_sql(name='product', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='客户档案')
        df = df.loc[:,['往来单位','往来单位编号','地址']]
        print(df)
        df.to_sql(name='customer', con=cnx, if_exists='replace')

    if gengxinfou('data\\2017年全单统计管理.xlsm',cnx,'fileread'):
        df = pd.read_excel('data\\2017年全单统计管理.xlsm',sheetname='全单统计管理',na_values=[0])
        # descdb(df)
        df=df.loc[:,['订单日期', '配货人', '配货准确', '业务主管', '终端编码', '终端名称', '积欠', '送货金额',
                         '实收金额', '收款方式', '退货金额', '客户拒收', '无货金额', '少配金额', '配错未要',
                         '送达日期', '车辆', '送货人', '收款日期', '收款人', '拒收品项']]
        df.to_sql(name='quandan', con=cnx, if_exists='replace', chunksize=100000)

    # if gengxinfou('data\\xiaoshoushujumingxi.txt',cnx,'fileread'):# or True:
    #     # df = pd.read_csv('data\\xiaoshoushujumingxi.txt',sep='\t',header=None,parse_dates=[0],dtype={'5':np.str,'8':np.str,'12':np.float64,'14':np.float64})
    #     df = pd.read_csv('data\\xiaoshoushujumingxi.txt',sep='\t',header=None,parse_dates=[0],dtype={4:object,5:object,10:object},low_memory=False,verbose=True)
    #     # descdb(df)
    #     df.columns = ['日期','单据编号','单据类型','职员名称','摘要','备注','商品备注','规格','商品编号','商品全名','型号','产地','单价','单位','数量','金额','含税单价','价税合计','成本金额','单位全名','毛利','毛利率','仓库全名','部门全名']
    #     # descdb(df)
    #     # sql_df=df.loc[:,['日期','单据编号','单据类型','职员名称','职员销售明细表','备注','商品备注','规格','商品编号','商品全名','单价','单位','数量','金额','成本金额','单位全名','毛利','毛利率','仓库全名','部门全名']]
    #     df=df.loc[:,['日期','单据编号','单据类型','职员名称','摘要','备注','商品备注','商品编号','商品全名','单价','单位','数量','金额','单位全名','仓库全名','部门全名']]
    #     df['单价'] = (df['单价']).fillna(0)
    #     df['金额'] = (df['金额']).fillna(0)
    #     descdb(df)
    #     df.to_sql(name='xiaoshoumingxi', con=cnx, if_exists='replace', chunksize=100000)

    if gengxinfou('data\\jiaqi.txt',cnx,'fileread'):
        df = pd.read_csv('data\\jiaqi.txt',sep=',',header=None)
        dfjiaqi = []
        for ii in df[0]:
            slist = ii.split('，')
            slist[0] = pd.to_datetime(slist[0])
            slist[2] = int(slist[2])
            dfjiaqi.append(slist)
        df = pd.DataFrame(dfjiaqi)
        df.sort_values(by=[0], ascending=[1], inplace=True)
        df.columns = ['日期','假休','天数']
        # df.index = df['日期']
        # descdb(df)
        sql_df = df.loc[:,df.columns]
        df.to_sql(name='jiaqi',con=cnx,schema=sql_df,if_exists='replace')


def ceshizashua(cnx):
    # desclitedb(cnx)
    # cnx.cursor().execute('drop table xiaoshoumingxi')
    # cnx.cursor().execute('drop table xiaoqu')
    # cnx.cursor().execute("insert into fileread values('白晔峰','万寿无疆','2016-06-12','43838883','4099','2016-09-30')")
    # cnx.commit()

    ttt = '2017-09-01'
    # result = cnx.cursor().execute('select * from jiaqi where 日期 > \'%s\'' %ttt)
    # for ii in result.fetchall():
    #     print(ii)

    # result = cnx.cursor().execute('select * from quandan limit 10')
    # for ii in result.fetchall():
    #     print(ii)

    result = cnx.cursor().execute("select * from fileread where 修改时间 >\'%s\'" % ttt)
    for ii in result.fetchall():
        print(ii)

    result = cnx.cursor().execute('select max(修改时间) as xg from fileread')
    print(result.fetchone()[0])

    ddd = '2017-03-31'
    ddd =pd.to_datetime(ddd)+pd.DateOffset(months=-1)
    print(ddd)
    ddd =pd.to_datetime(ddd)+pd.DateOffset(years=-1)
    print(ddd)
    print('%02d' %ddd.month)
    print('%04d%02d' %(ddd.year,ddd.month))
    print(cal.monthrange(2017,2)[1])

    for i in range(10):
        nianfen = 2017-i
        print(str(nianfen),end='\t')
        print(cal.isleap(int(nianfen)))


    # lxzd = ('A', 'B', 'C', 'S', 'W', 'Y')
    # lxqd = ('O', 'P', 'Q')
    # lxls = ('L', 'Z')
    # lxqt = ('G', 'N', 'X')
    # lxqb = tuple(list(lxzd) + list(lxqd) + list(lxls) + list(lxqt))


def fenxi(cnx):
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

        df = pd.read_sql_query('select max(订单日期) from quandan',cnx)
        dangqianyue = pd.to_datetime(df.ix[0][0])
        dangqianyue = pd.to_datetime('%04d-%02d-01' %(dangqianyue.year,dangqianyue.month))
        print(dangqianyue)
        if leixingset == '终端客户':
            for fenbuset in fenbulist:
                if fenbuset == '销售部':
                    fenbu = tuple(dfquyu['区域'])
                else:
                    fenbu = tuple((dfquyu[dfquyu['分部'] == fenbuset])['区域'])

                # df = pd.read_sql_query(
                #     "select 订单日期,count(终端编码) as 单数,sum(送货金额) as 金额,substr(终端编码,1,2) as 区域 ,substr(终端编码,12,1) as 类型 from quandan where (配货人!=\'%s\') and (送达日期 is not null) and(区域 in %s) and(类型 in %s) group by 订单日期" % (
                #     '作废', fenbu, leixing), cnx)
                # df = pd.read_sql_query("select 日期,count(*) as 单数,sum(金额) as 金额,substr(customer.往来单位编号,1,2) as 区域 ,substr(customer.往来单位编号,12,1) as 类型 from xiaoshoumingxi,customer where (customer.往来单位 = xiaoshoumingxi.单位全名) and(区域 in %s) and(类型 in %s) group by 日期" %(fenbu,leixing),cnx)
                df = pd.read_sql_query(
                    "select 日期,count(*) as 单数,sum(金额) as 金额,substr(customer.往来单位编号,1,2) as 区域 ,"
                    "substr(customer.往来单位编号,12,1) as 类型,product.品牌名称  as 品牌 from xiaoshoumingxi,"
                    "customer,product where (customer.往来单位 = xiaoshoumingxi.单位全名) "
                    "and (product.商品全名 = xiaoshoumingxi.商品全名) and(区域 in %s) "
                    "and(类型 in %s) group by 日期" % (fenbu, leixing), cnx)
                df.index = pd.to_datetime(df['日期'])
                # df['单均'] = df['金额'] / df['单数']
                for k in range(dangqianyue.month):
                    chubiaorileiji(df,dangqianyue+pd.DateOffset(months=k*(-1)),'金额',leixing=leixingset,quyu=fenbuset)
                    # chubiaorileiji(df,dangqianyue+pd.DateOffset(months=i*(-1)),'单数')
                chubiaoyueleiji(df, dangqianyue, '金额', leixing=leixingset, quyu=fenbuset,nianshu=5)
        else:
            fenbu = tuple(dfquyu['区域'])
            # df = pd.read_sql_query("select 订单日期,count(终端编码) as 单数,sum(送货金额) as 金额,substr(终端编码,1,2) as 区域 ,substr(终端编码,12,1) as 类型 from quandan where (配货人!=\'%s\') and (送达日期 is not null) and(区域 in %s) and(类型 in %s) group by 订单日期" %('作废',fenbu,leixing),cnx)
            # df = pd.read_sql_query(
            #     "select 日期,count(*) as 单数,sum(金额) as 金额,substr(customer.往来单位编号,1,2) as 区域 ,substr(customer.往来单位编号,12,1) as 类型 from xiaoshoumingxi,customer where (customer.往来单位 = xiaoshoumingxi.单位全名) and(区域 in %s) and(类型 in %s) group by 日期" % (
            #     fenbu, leixing), cnx)
            df = pd.read_sql_query(
                "select 日期,count(*) as 单数,sum(金额) as 金额,substr(customer.往来单位编号,1,2) as 区域 ,"
                "substr(customer.往来单位编号,12,1) as 类型,product.品牌名称  as 品牌 from xiaoshoumingxi,"
                "customer,product where (customer.往来单位 = xiaoshoumingxi.单位全名) "
                "and (product.商品全名 = xiaoshoumingxi.商品全名) and(区域 in %s) "
                "and(类型 in %s) group by 日期" % (fenbu, leixing), cnx)
            df.index = pd.to_datetime(df['日期'])
            # df['单均'] = df['金额'] / df['单数']
            for k in range(dangqianyue.month):
                chubiaorileiji(df,dangqianyue+pd.DateOffset(months=k*(-1)),'金额',leixing=leixingset,quyu='销售部')
                # chubiaorileiji(df,dangqianyue+pd.DateOffset(months=i*(-1)),'单数')
            chubiaoyueleiji(df,dangqianyue,'金额',leixing=leixingset,quyu='销售部',nianshu=5)



#
# 把纵轴的刻度设置为万
#
def y_formatter(x, pos):
    return r"%d万" %(int(x/10000)) #%d


def rizi(df):
    return '%02d' %(df[0].day)


def yuezi(df):
    return '%02d' %(df[0]+1)


# 月度（全年，自然年度）累积对比图，自最早日期起，默认3年
# df，数据表，必须用DateTime做index
# riqi，当前月份，可以是DateTIme的各种形式，只要pd能识别成功，形如2017-10-01，代表2017年10月为标的月份
# xiangmu，主题，画图时写入标题
# quyu，销售区域或区域聚合（分部）
# leixing，终端类型
# nianshu，用来对比的年份数，从当前年份向回数
def chubiaoyueleiji(df,riqi,xiangmu,quyu='',leixing='',pinpai='',nianshu=3):
    riqicur = pd.to_datetime(riqi)
    nianlist = []
    for i in range(nianshu):
        nianlist.append(riqicur+pd.DateOffset(years=-(i)))

    ds = pd.DataFrame(df[xiangmu],index=df.index)#取出日期索引的数据列

    # 分年份生成按照每天日期重新索引的数据列
    dslist = []
    for i in range(nianshu):
        dstmp = ds.reindex(pd.date_range(pd.to_datetime(str(nianlist[i].year)+'-01-01'),periods=365,freq='D'),fill_value=0)
        dstmp = dstmp.resample('M').sum()
        dstmp.columns = ['%04d'%(nianlist[i].year)]
        dstmp.index = (range(12))
        dslist.append(dstmp)

    df = dslist[0]
    for i in range(nianshu-1):
        df = df.join(dslist[i+1])

    colnames = []
    for i in range(nianshu):
        colnames.append((dslist[i].columns)[0])
    # print(colnames)
    df = df[colnames]
    zuobiao = pd.DataFrame(df.index).apply(lambda r:yuezi(r),axis=1)
    df.index= zuobiao

    # descdb(df)

    nianyue = '%04d年'%(riqicur.year)
    biaoti = leixing+quyu+pinpai+nianyue+xiangmu
    df.cumsum().plot(title=('%s月累积' %biaoti))
    # df.cumsum().plot(table=True,fontsize=12,figsize=(40,20))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_formatter))  # 纵轴主刻度文本用y_formatter函数计算
    plt.savefig('img\\%s（月累积）.png' %biaoti)
    plt.close()
    df.plot(title=('%s月折线') %biaoti)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_formatter))  # 纵轴主刻度文本用y_formatter函数计算
    plt.savefig('img\\%s（月折线）.png' %biaoti)
    plt.close()
    # plt.show()
    # ds1.plot()
    #
    # ds2 = ds1.resample('M').sum()
    # descdb(ds2)
    # print(ds2.sum())
    # ds2.plot()
    # plt.show()

    # dfr = df.reindex(dates,fill_value=0)
    # descdb(dfr)
    # df['danshu'].plot()
    # plt.show()
    # df['jine'].plot()
    # plt.show()


#日（整月）累积对比图，当月、环比、同期比
#riqi形如2017-10-01，代表2017年10月为标的月份
def chubiaorileiji(df, riqi, xiangmu, quyu='', leixing='',pinpai=''):
    riqicur = pd.to_datetime(riqi)
    riqibefore = riqicur+pd.DateOffset(months=-1)
    riqilast = riqicur+pd.DateOffset(years=-1)
    tianshu = cal.monthrange(riqicur.year,riqicur.month)[1]

    ds = pd.DataFrame(df[xiangmu],index=df.index)
    # print(ds.index)
    # print(ds)
    dates = pd.date_range(riqibefore,periods=tianshu,freq='D')
    # print(dates)
    ds1 = ds.reindex(dates,fill_value=0)
    # ds1 = ds1.resample('M').sum()
    # descdb(ds1)
    ds1.index = (range(tianshu))
    ds1.columns = ['%04d%02d' %(riqibefore.year,riqibefore.month)]
    # descdb(ds1)

    dates = pd.date_range(riqilast,periods=tianshu,freq='D')
    # print(dates)
    ds3 = ds.reindex(dates,fill_value=0)
    # ds2 =ds2.resample('M').sum()
    # descdb(ds3)
    ds3.index = range(tianshu)
    ds3.columns = ['%04d%02d' %(riqilast.year,riqilast.month)]
    # descdb(ds3)

    dates = pd.date_range(riqicur,periods=tianshu,freq='D')
    # print(dates)
    ds2 = ds.reindex(dates,fill_value=0)
    # ds2 =ds2.resample('M').sum()
    # descdb(ds2)
    ds2.index = range(tianshu)
    ds2.columns = ['%04d%02d' %(riqicur.year,riqicur.month)]
    # descdb(ds2)

    df = ds2.join(ds1,how='left')
    df = df.join(ds3,how='left')
    df = df[['%04d%02d' %(riqicur.year,riqicur.month),'%04d%02d' %(riqibefore.year,riqibefore.month),'%04d%02d' %(riqilast.year,riqilast.month)]]
    # descdb(df)
    zuobiao = pd.DataFrame(dates).apply(lambda r:rizi(r),axis=1)
    df.index= zuobiao
    # descdb(df)
    nianyue = '%04d%02d'%(riqicur.year,riqicur.month)
    biaoti = leixing+quyu+pinpai+nianyue+xiangmu
    if len(df) > 12:
        # print(len(df))
        df.cumsum().plot(title=biaoti+'日累积')
    else:
        df.cumsum().plot(title=biaoti+'日累积')

    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_formatter))  # 纵轴主刻度文本用y_formatter函数计算
    plt.savefig('img\\'+biaoti+'（日累积月）.png' )
    # plt.show()
    plt.close()
    # ds1.plot()
    #
    # ds2 = ds1.resample('M').sum()
    # descdb(ds2)
    # print(ds2.sum())
    # ds2.plot()
    # plt.show()

    # dfr = df.reindex(dates,fill_value=0)
    # descdb(dfr)
    # df['danshu'].plot()
    # plt.show()
    # df['jine'].plot()
    # plt.show()


cnx = lite.connect('data\\quandan.db')
# cur = cnx.cursor()
# result = cur.execute('PRAGMA count_changes')
# print(result.fetchone()[0])
# cur.execute('PRAGMA count_changes=true')
# result = cur.execute('PRAGMA count_changes')
# print(result.fetchone()[0])

# ceshizashua(cnx)
dataokay(cnx)
# desclitedb(cnx)
# fenxi(cnx)

cnx.close()

