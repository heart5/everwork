# encoding:utf-8
"""
微信延迟管理文件
"""
import sqlite3 as lite
import pandas as pd
import time

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import touchfilepath2depth, getdirmain


def inserttimeitem2db(timestr: str):
    dbname = touchfilepath2depth(getdirmain() / 'data' / 'db' / 'wcdelay.db')
    conn = lite.connect(dbname)
    cursor = conn.cursor()
    tablename = 'wcdelay'

    def istableindb(tablename: str, dbname: str):
        cursor.execute("select * from sqlite_master where type='table'")
        table = cursor.fetchall()
        # print(table)
        chali = [x for item in table for x in item[1:3]]
        # print(chali)

        return tablename in chali

    if not istableindb(tablename, dbname):
        cursor.execute(f'create table {tablename} (time int primary key, delay int)')
        conn.commit()
        log.info(f"数据表：\t{tablename} 被创建成功。")

    timetup = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    timest = time.mktime(timetup)
    elsmin = (int(time.time()) - time.mktime(timetup)) // 60
    cursor.execute(f"insert into {tablename} values(?, ?)", (timest, elsmin))
    print(f"数据成功写入{dbname}\t{(timest, elsmin)}")
    conn.commit()
    conn.close()


def getdelaydb():
    dbname = touchfilepath2depth(getdirmain() / 'data' / 'db' / 'wcdelay.db')
    tablename = 'wcdelay'
    conn = lite.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(f"select * from {tablename}")
    table = cursor.fetchall()
    print(table[:3])
    conn.close()

    timedf = pd.DataFrame(table, columns=['time', 'delay'])
    timedf['time'] = timedf['time'].apply(
        lambda x: pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x))))
    timedf.set_index('time', inplace=True)
    timedf.loc[timedf.delay < 0] = 0
    timedf.iloc[:5]

    return timedf


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')

    log.info(f'文件{__file__}运行结束')
