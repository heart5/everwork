# encoding:utf-8

from everfunc import *


# plot中显示中文
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

if not os.path.exists('data'):
    os.mkdir('data')
if not os.path.exists('data\\tmp'):
    os.mkdir('data\\tmp')
if not os.path.exists('img'):
    os.mkdir('img')
if not os.path.exists('img\\weather'):
    os.mkdir('img\\weather')
if not os.path.exists('img\\pick'):
    os.mkdir('img\\pick')
if not os.path.exists('img\\一部'):
    os.mkdir('img\\一部')
if not os.path.exists('img\\二部'):
    os.mkdir('img\\二部')
if not os.path.exists('img\\汉口'):
    os.mkdir('img\\汉口')
if not os.path.exists('img\\汉阳'):
    os.mkdir('img\\汉阳')
if not os.path.exists('img\\销售部'):
    os.mkdir('img\\销售部')


# 显示DataFrame或Series的轮廓信息
# df，DataFrame或Series
def descdb(df):
    print(len(df))
    # print(df.head(5))
    print(df.tail(5))
    print(df.dtypes)
    if type(df) == pd.DataFrame:
        print(df.columns)
        print(df.info())
        print(df.shape)
    print(df.describe())


# 显示SQlite数据库的各种信息
# cnx，数据库连接
def desclitedb(cnx):
    cur=cnx.cursor()
    result = cur.execute("select * from sqlite_master")
    for ii in result.fetchall():
        print(str(ii)+'\n')

    result = cur.execute("select name from sqlite_master where type = 'table' order by name")
    table_name_list = [tuple1[0] for tuple1 in result.fetchall()]
    print(table_name_list)
    for table in table_name_list:
#        result = cur.execute("PRAGMA table_info(%s)" % table)
#        for jj in result.fetchall():
#            print(jj,end='\t')
        print("%s" %table,end='\t')
        result = cur.execute("select * from %s" % table)
        print(len(result.fetchall()),end='\t')
        # print(cur.description)
        col_name_list = [tuple1[0] for tuple1 in cur.description]
        print (col_name_list)
