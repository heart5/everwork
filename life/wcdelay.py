# encoding:utf-8
"""
微信延迟管理文件
"""
import sqlite3 as lite
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
# import datetime
import time

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import touchfilepath2depth, getdirmain


def ifnotcreate(tablen: str, dbn: str):
    """
    如果没有相应数据表就创建一个
    :param tablen:
    :param dbn:
    :return:
    """
    conn = lite.connect(dbn)

    try:

        cursor = conn.cursor()

        def istableindb(tablenin: str):
            cursor.execute("select * from sqlite_master where type='table'")
            table = cursor.fetchall()
            # print(table)
            chali = [x for item in table for x in item[1:3]]
            # print(chali)

            return tablenin in chali

        if not istableindb(tablen):
            createsql = f'create table {tablen} (time int primary key, delay int)'
            cursor.execute(createsql)
            conn.commit()
            log.info(f"数据表：\t{tablen} 被创建成功。\t{createsql}")

    except Exception as eee:
        log.critical(f"操作数据库时出现错误。{dbn}\t{eee}")
    finally:
        conn.close()


def inserttimeitem2db(timestr: str):
    dbname = touchfilepath2depth(getdirmain() / 'data' / 'db' / 'wcdelay.db')
    tablename = 'wcdelay'
    ifnotcreate(tablename, dbname)

    timetup = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    timest = time.mktime(timetup)
    elsmin = (int(time.time()) - time.mktime(timetup)) // 60
    conn = lite.connect(dbname)
    try:
        cursor = conn.cursor()
        cursor.execute(f"insert into {tablename} values(?, ?)", (timest, elsmin))
        print(f"数据成功写入{dbname}\t{(timest, elsmin)}")
        conn.commit()
    except lite.IntegrityError as lie:
        log.critical(f"键值重复错误\t{lie}")
    finally:
        conn.close()


def getdelaydb():
    dbname = touchfilepath2depth(getdirmain() / 'data' / 'db' / 'wcdelay.db')
    tablename = 'wcdelay'

    ifnotcreate(tablename, dbname)

    conn = lite.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(f"select * from {tablename}")
    table = cursor.fetchall()
    conn.close()

    timedf = pd.DataFrame(table, columns=['time', 'delay'])
    timedf['time'] = timedf['time'].apply(
        lambda x: pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x))))
    timedf.set_index('time', inplace=True)

    if tdfsize := timedf.shape[0] != 0:
        print(f"延时记录共有{tdfsize}条")
        # 增加当前时间，延时值引用最近一次的值，用于做图形展示的右边栏
        timedf = timedf.append(pd.DataFrame([timedf.iloc[-1]], index=[pd.to_datetime(time.ctime())]))
    else:
        log.info(f"数据表{tablename}还没有数据呢")

    timedf.loc[timedf.delay < 0] = 0
    # print(timedf.iloc[:2])
    print(timedf.iloc[-3:])

    return timedf


def showdelayimg():
    timedf = getdelaydb()
    register_matplotlib_converters()

    plt.figure(figsize=(36, 6))
    plt.style.use('ggplot')  # 使得作图自带色彩，这样不用费脑筋去考虑配色什么的；
    tmin = timedf.index.min()
    tmax = timedf.index.max()
    shicha = tmax - tmin
    bianjie = int(shicha.total_seconds() / 40)
    print(bianjie)
    # plt.xlim(xmin=tmin-pd.Timedelta(f'{bianjie}s'))
    plt.xlim(xmin=tmin)
    plt.xlim(xmax=tmax + pd.Timedelta(f'{bianjie}s'))
    # plt.vlines(tmin, 0, int(timedf.max() / 2))
    plt.vlines(tmax, 0, int(timedf.max() / 2))
    plt.scatter(timedf.index, timedf, s=timedf)
    plt.scatter(timedf[timedf == 0].index, timedf[timedf == 0], s=0.5)
    plt.title('信息频率和延时')

    imgwcdelaypath = touchfilepath2depth(getdirmain() / 'img' / 'webchat' / 'wcdelay.png')

    plt.savefig(imgwcdelaypath)

    return imgwcdelaypath


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    tdf = getdelaydb()
    print(tdf.sort_index(ascending=False))
    log.info(f'文件{__file__}运行结束')
