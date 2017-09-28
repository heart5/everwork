#
# enconding:utf-8
#
# 各种函数、功能测试
#

import pandas as pd, datetime, time, sqlite3 as lite

def hello():
    print('老卢！')
    print('老卢！')
    print('这里，这里。')

# hello()

def helloSec(name):
    print('你好啊，'+name)

# helloSec('白珍石')


def yingdacal(dfy,cnx):
    df = []
    dfjiaqi = pd.read_sql_query('select 日期 from jiaqi',cnx)
    # print(dfjiaqi['日期'])
    for x in dfy:
        if type(x) == str:
            x = pd.to_datetime(x)
        datestr = str(x+pd.DateOffset(days=1))
        # print(datestr)

        # print(dfall.columns)
        # print(dfall['tianshu'])
        # print(len(dfall))
        # print(int(x.strftime('%w')))
        if(datestr in tuple(dfjiaqi['日期'])):
            dfjiaqitianshu = pd.read_sql_query('select 天数 from jiaqi where 日期 =\'' + datestr + '\'', cnx)
            ii = x+pd.DateOffset(days=int(dfjiaqitianshu['天数'][0]))
        elif(int(x.strftime('%w')) == 6):
            ii = x+pd.DateOffset(days=2)
        else:
            ii = x + pd.DateOffset(days=1)
        df.append(ii)

    return df


def guizheng():
    df1 =pd.DataFrame({'key':['b','b','a','c','a','a','b'],'data1':range(7)})
    df2 =pd.DataFrame({'key':['a','b','d'],'data2':range(3)})
    print(pd.merge(df1,df2,on='key'))

    df1 =pd.DataFrame({'lkey':['b','b','a','c','a','a','b'],'data1':range(7)})
    df2 =pd.DataFrame({'rkey':['a','b','d'],'data2':range(3)})
    print(pd.merge(df1,df2,left_on='lkey',right_on='rkey'))
    print(pd.merge(df1,df2,left_on='lkey',right_on='rkey',how='left'))
    print(pd.merge(df1,df2,left_on='lkey',right_on='rkey',how='right'))
    print(pd.merge(df1,df2,left_on='lkey',right_on='rkey',how='outer'))


def cstype():
    num = 24322222222222222222222222222222222222222222222222222222222222221111111111111111111111111111111111111111111111111111111111111.0
    # num = 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    print(type(num))
    print(type(num) in [float,int])
    print(time.time())

guizheng()

cnx = lite.connect('..\\data\\quandan.db')
ceshiriqi = ['2017-04-28','2017-06-08','2017-02-23','2017-03-24','2017-09-02','2017-09-30']
print(yingdacal(ceshiriqi,cnx))
