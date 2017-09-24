# encoding:utf-8
# 处理配送全单数据
#

import pandas as pd, sqlite3 as lite, os, datetime, time

def descdb(df):
    # print(df.head(5))
    print(df.tail(5))
    print(df.dtypes)
    print(len(df))
    print(df.describe())

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
        sql = c.execute("insert into %s values(?,?,?,?,?,?)" %tablename,(fn,fna,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)),str(fstat.st_dev),str(fstat.st_size),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())))
        # conn.commit()
        rt = True
    else:
        print("文件"+fn+"有 "+str(fncount)+" 条记录，看是否最新",'\t')
        sql = "select max(修改时间) as xg from %s where 文件名 = \'%s\'" %(tablename,fn)
        result = c.execute(sql)
        if time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)) > (result.fetchone())[0]:
            result = c.execute("insert into %s values(?,?,?,?,?,?)" %tablename,(fn,fna,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)),str(fstat.st_dev),str(fstat.st_size),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())))
            # conn.commit()
            print('更新成功')
            rt = True
        else:
            print('无需更新')
            rt = False

    # print(fstat.st_mtime, '\t', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_atime)),'\t', '\t', time.strftime('%Y-%m-%d %H:%M',time.localtime(fstat.st_mtime)),'\t', '\t', time.strftime('%Y-%m-%d %H:%M',time.localtime(fstat.st_ctime)),'\t', fstat.st_dev)

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
        print(len(result.fetchall()))
        # print(cur.description)
        col_name_list = [tuple[0] for tuple in cur.description]
        print (col_name_list)

cnx = lite.connect('data\\quandan.db')

desclitedb(cnx)
# cnx.cursor().execute('drop table fileread')
# tt =time.localtime()
# print(tt)
# print(time.strftime("%Y-%m-%d %H:%M:%S",tt))
# print(pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S",tt)))

dataokay(cnx)

ttt = '2017-06-01'
result = cnx.cursor().execute('select * from jiaqi where 日期 > \'%s\'' %ttt)
for ii in result.fetchall():
    print(ii)

# result = cnx.cursor().execute('select * from quandan limit 5')
# for ii in result.fetchall():
#     print(ii)

# cnx.cursor().execute("insert into fileread values('白晔峰','万寿无疆','2016-06-12','43838883','4099','2016-09-30')")
# cnx.commit()
result = cnx.cursor().execute("select * from fileread where 修改时间 >\'%s\'" %ttt)
for ii in result.fetchall():
    print(ii)

result = cnx.cursor().execute('select min(修改时间) as xg from fileread')
print(result.fetchone()[0])

desclitedb(cnx)

cnx.close()

