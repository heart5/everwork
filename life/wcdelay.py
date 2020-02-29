# encoding:utf-8
"""
微信延迟管理文件
"""
import sqlite3 as lite
import pandas as pd
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


def inserttimeitem2db(timestampinput: int):
    dbname = touchfilepath2depth(getdirmain() / 'data' / 'db' / 'wcdelay.db')
    tablename = 'wcdelay'
    ifnotcreate(tablename, dbname)

    # timetup = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    # timest = time.mktime(timetup)
    elsmin = (int(time.time()) - timestampinput) // 60
    conn = lite.connect(dbname)
    try:
        cursor = conn.cursor()
        cursor.execute(f"insert into {tablename} values(?, ?)", (timestampinput, elsmin))
        print(f"数据成功写入{dbname}\t{(timestampinput, elsmin)}")
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
        print(tdfsize)
        # 增加当前时间，延时值引用最近一次的值，用于做图形展示的右边栏
        timedf = timedf.append(pd.DataFrame([timedf.iloc[-1]], index=[pd.to_datetime(time.ctime())]))
    else:
        log.info(f"数据表{tablename}还没有数据呢")

    timedf.loc[timedf.delay < 0] = 0
    print(timedf.iloc[:2])
    print(timedf.iloc[-5:])

    return timedf


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    tdf = getdelaydb()
    print(tdf.sort_index(ascending=False))
    log.info(f'文件{__file__}运行结束')
