# encoding:utf-8
# 处理配送全单数据
#

import pandas as pd, sqlite3 as lite, os, datetime, time, matplotlib.pyplot as plt,calendar
from pylab import *

# plot中显示中文
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

def descdb(df):
    print(df.head(5))
    print(df.tail(5))
    print(df.dtypes)
    if type(df) == pd.DataFrame:
        print(df.columns)
    print(len(df))
    # print(df.describe())

def gengxinfou(filename,conn,tablename='fileread'):
    rt = False
    try:
        create_tb_cmd = "CREATE TABLE IF NOT EXISTS %s ('文件名' TEXT,'绝对路径' TEXT, '修改时间' TIMESTAMP,'设备编号' INTEGER,'文件大小' INTEGER,'登录时间' TIMESTAMP); " %tablename
        conn.execute(create_tb_cmd)
    except:
        print("创建数据表%s失败！" %tablename)
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
        print("文件"+fn+"无记录，录入信息")
        result = c.execute("insert into %s values(?,?,?,?,?,?)" %tablename,(fn,fna,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)),str(fstat.st_dev),str(fstat.st_size),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())))
        print('添加成功。')
        rt = True
    else:
        print("文件"+fn+"已有 "+str(fncount)+" 条记录，看是否最新",'\t')
        sql = "select max(修改时间) as xg from %s where 文件名 = \'%s\'" %(tablename,fn)
        result = c.execute(sql)
        if time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)) > (result.fetchone())[0]:
            result = c.execute("insert into %s values(?,?,?,?,?,?)" %tablename,(fn,fna,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)),str(fstat.st_dev),str(fstat.st_size),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())))
            print('更新成功。')
            rt = True
        else:
            print('无需更新')
            rt = False
    # print(fstat.st_mtime, '\t', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_atime)),'\t', '\t', time.strftime('%Y-%m-%d %H:%M',time.localtime(fstat.st_mtime)),'\t', '\t', time.strftime('%Y-%m-%d %H:%M',time.localtime(fstat.st_ctime)),'\t', fstat.st_dev)
    conn.commit()

    return rt

def dataokay(cnx):
    if gengxinfou('data\\2017年全单统计管理.xlsm',cnx,'fileread'):
        df = pd.read_excel('data\\2017年全单统计管理.xlsm',sheetname='全单统计管理',na_values=[0])
        # descdb(df)
        sql_df=df.loc[:,['订单日期', '配货人', '配货准确', '业务主管', '终端编码', '终端名称', '积欠', '送货金额',
                         '实收金额', '收款方式', '退货金额', '客户拒收', '无货金额', '少配金额', '配错未要',
                         '送达日期', '车辆', '送货人', '收款日期', '收款人', '拒收品项']]
        df.to_sql(name='quandan', con=cnx, schema=sql_df, if_exists='replace', chunksize=1000)

    if gengxinfou('data\\jiaqi.txt',cnx):
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

def desclitedb(cnx):
    cur=cnx.cursor()
    result = cur.execute("select * from sqlite_master")
    for ii in result.fetchall():
        print(ii)

    result = cur.execute("select name from sqlite_master where type = 'table' order by name")
    table_name_list = [tuple[0] for tuple in result.fetchall()]
    print(table_name_list)

    for table in table_name_list:
        cur.execute("PRAGMA table_info(%s)" %table)
        # print (cur.fetchall())
        result = cur.execute("select * from %s" %table)
        print(len(result.fetchall()),end='\t')
        # print(cur.description)
        col_name_list = [tuple[0] for tuple in cur.description]
        print (col_name_list)


def ceshizashua(cnx):
    # desclitedb(cnx)
    # cnx.cursor().execute('drop table fileread')
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
    print(calendar.monthrange(2017,2)[1])

def fenxi(cnx):
    # df = pd.read_sql_query('select 收款日期,count(终端编码) as danshu,sum(实收金额) as jine from quandan where (配货人!=\'%s\' or 配货人 is null) and (订单日期 >\'%s\') group by 收款日期' %('作废','2016-03-29'),cnx)
    yibu = ('01','02','03','04','05','06','09')
    erbu = ('00','07','08','10','11','12','13')
    hankou = ('21','22','23','24','25','26')
    hanyang = ('31','32','33','34')
    zongbu = tuple(list(yibu)+list(erbu)+list(hankou)+list(hanyang))
    lxzd = ('A','B','C','S','W','Y')
    lxqd = ('O','P','Q')
    lxls = ('L','Z')
    lxqt = ('G','N','X')
    lxqb = tuple(list(lxzd)+list(lxqd)+list(lxls)+list(lxqt))
    df = pd.read_sql_query("select 订单日期,count(终端编码) as 单数,sum(送货金额) as 金额,substr(终端编码,1,2) as 区域 ,substr(终端编码,12,1) as 类型 from quandan where (配货人!=\'%s\') and (送达日期 is not null) and(区域 in %s) and(类型 in %s) group by 订单日期" %('作废',zongbu,lxqb),cnx)
    df = pd.read_sql_query('select 订单日期,sum(送货金额) as 金额, count(终端编码) as 单数 from quandan where (送货金额 is not null) group by 订单日期',cnx)
    # df = pd.read_sql_query('select 送达日期,count(终端编码) as danshu,sum(送货金额) as jine from quandan where (配货人!=\'%s\' and 收款日期 is null) and (订单日期 >\'%s\') group by 送达日期' %('作废','2010-11-04'),cnx)
    # descdb(df)
    df.index = pd.to_datetime(df['订单日期'])
    # df['单均'] = df['金额'] / df['单数']
    descdb(df)

    dangqianyue = pd.to_datetime('2017-06-01')
    for i in range(3):
        chubiaorileiji(df,dangqianyue+pd.DateOffset(months=i*(-1)),'金额')
        # chubiaorileiji(df,dangqianyue+pd.DateOffset(months=i*(-1)),'单数')


def rizi(df):
    return '%02d' %(df[0].day)

#riqi形如2017-08-29，代表2017年9月为标的物
def chubiaorileiji(df,riqi,xiangmu,quyu='',leixing=''):
    riqicur = pd.to_datetime(riqi)
    riqibefore = riqicur+pd.DateOffset(months=-1)
    riqilast = riqicur+pd.DateOffset(years=-1)
    tianshu = calendar.monthrange(riqicur.year,riqicur.month)[1]

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
    print(dates)
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
    descdb(df)
    if len(df) > 12:
        # print(len(df))
        df.cumsum().plot(title=leixing+quyu+xiangmu+'日累积')
    else:
        df.cumsum().plot(table=True,fontsize=12,figsize=(40,20))

    # plt.gca().set_xticklabels(list(zuobiao))  # 主刻度文本用min_formatter函数计算
    nianyue = '%04d%02d'%(riqicur.year,riqicur.month)
    plt.savefig('img\\'+leixing+quyu+nianyue+xiangmu+'.png' )
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

dataokay(cnx)
desclitedb(cnx)
fenxi(cnx)
# cur = cnx.cursor()
# result = cur.execute('PRAGMA count_changes')
# print(result.fetchone()[0])

# ceshizashua(cnx)

cnx.close()

