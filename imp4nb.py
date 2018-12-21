# encoding:utf-8

import sys
import calendar as cal

sys.path.insert(0, 'work')
sys.path.insert(0, 'life')
sys.path.insert(0, 'study')
sys.path.insert(0, 'func')
sys.path.insert(0, 'etc')
from func.everfunc import *


# plot中显示中文
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


# 显示DataFrame或Series的轮廓信息
# df，DataFrame或Series
def descdb(df):
    print(df.shape[0])
    # print(df.head(5))
    print(df.head(10))
    print(df.dtypes)
    if type(df) == pd.DataFrame:
        print(df.columns)
    print(df.describe())


# 显示SQlite数据库的各种信息
# cnx，数据库连接
def desclitedb(cnx):
    cur = cnx.cursor()
    result = cur.execute("select * from sqlite_master")
    for ii in result.fetchall():
        print(str(ii)+'\n')

    result = cur.execute("select name from sqlite_master where type = 'table' order by name")
    table_name_list = [tuple1[0] for tuple1 in result.fetchall()]
    print(table_name_list)
    for table1 in table_name_list:
        #        result = cur.execute("PRAGMA table_info(%s)" % table)
        #        for jj in result.fetchall():
        #            print(jj,end='\t')
        print("%s" % table1, end='\t')
        result = cur.execute("select * from %s" % table1)
        print(len(result.fetchall()), end='\t')
        # print(cur.description)
        col_name_list = [tuple1[0] for tuple1 in cur.description]
        print(col_name_list)


def swissknife(cnx):
    # desclitedb(cnx)
    # cnx.cursor().execute('drop table xiaoshoumingxi')
    # cnx.cursor().execute('drop table xiaoqu')
    # cnx.cursor().execute("insert into fileread values('白晔峰','万寿无疆','2016-06-12','43838883','4099','2016-09-30')")
    # cnx.cursor().execute("delete from xiaoshoumingxi where 单位全名 like \'%单位%\'")
    # cnx.commit()
    # log.warning('从数据表《销售明细》中删除‘单位全名’值为‘无单位’的纪录172条，值为‘无名单位’的纪录4条！！！')

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
    ddd = pd.to_datetime(ddd) + pd.DateOffset(months=-1)
    print(ddd)
    ddd = pd.to_datetime(ddd) + pd.DateOffset(years=-1)
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

