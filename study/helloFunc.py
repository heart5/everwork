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
# helloSec('白珍岩')

jiaqi = []
jiaqi.append([1,'2017-01-01','元旦',4])
jiaqi.append([2,'2017-05-01','五一',4])
jiaqi.append([3,'2017-10-01','十一',4])
print(jiaqi)

#[{'元旦', 1, 4, '2017-01-01'}, {'五一', 2, 4, '2017-05-01'}, {3, 4, '十一', '2017-10-01'}]
df = pd.DataFrame(jiaqi)
df.columns = ['xuhao', 'date', 'miaoshu', 'tianshu']

cnx = lite.connect('quandan.db')
sql_df=df.loc[:,['xuhao', 'date', 'miaoshu', 'tianshu']]
df.to_sql(name='jiaqi', con=cnx, schema=sql_df, if_exists='replace', chunksize=1000)

def yingdacal(x):
    ii = (x+pd.DateOffset(days=1)).strftime('%Y-%m-%d')
    dfall = pd.read_sql_query('select tianshu from jiaqi where date =\''+ii+'\'', cnx)
    # print(dfall.columns)
    # print(dfall['tianshu'])
    # print(len(dfall))
    print(int(x.strftime('%w')))
    if(len(dfall) > 0):
        return x+pd.DateOffset(days=int(dfall['tianshu'][0]))
    elif(int(x.strftime('%w')) == 6):
        return x+pd.DateOffset(days=2)
    else:
        return x + pd.DateOffset(days=1)

num = 24322222222222222222222222222222222222222222222222222222222222221111111111111111111111111111111111111111111111111111111111111.0
# num = 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
print(type(num))
print(type(num) in [float,int])
print(time.time())

# print(yingdacal(pd.to_datetime('2017-04-30')))
# print(yingdacal(pd.to_datetime('2017-05-30')))
# print(yingdacal(pd.to_datetime('2017-02-23')))
# print(yingdacal(pd.to_datetime('2017-03-24')))
# print(yingdacal(pd.to_datetime('2017-09-02')))
