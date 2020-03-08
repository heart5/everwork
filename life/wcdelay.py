# encoding:utf-8
"""
微信延迟管理文件
"""
import os
import sqlite3 as lite
import pandas as pd
import matplotlib.pyplot as plt
import time
import datetime
from pandas.plotting import register_matplotlib_converters

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import touchfilepath2depth, getdirmain
    from func.litetools import ifnotcreate


def inserttimeitem2db(timestampinput: int):
    dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "wcdelay.db")
    tablename = "wcdelay"
    csql = f"create table {tablename} (time int primary key, delay int)"
    ifnotcreate(tablename, csql, dbname)

    # timetup = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    # timest = time.mktime(timetup)
    elsmin = (int(time.time()) - timestampinput) // 60
    conn = lite.connect(dbname)
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"insert into {tablename} values(?, ?)", (timestampinput, elsmin)
        )
        print(f"数据成功写入{dbname}\t{(timestampinput, elsmin)}")
        conn.commit()
    except lite.IntegrityError as lie:
        log.critical(f"键值重复错误\t{lie}")
    finally:
        conn.close()


def getdelaydb():
    dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "wcdelay.db")
    tablename = "wcdelay"

    csql = f"create table {tablename} (time int primary key, delay int)"
    ifnotcreate(tablename, csql, dbname)

    conn = lite.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(f"select * from {tablename}")
    table = cursor.fetchall()
    conn.close()

    timedf = pd.DataFrame(table, columns=["time", "delay"])
    timedf["time"] = timedf["time"].apply(
        lambda x: pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x)))
    )
    timedf.set_index("time", inplace=True)

    if (tdfsize := timedf.shape[0]) != 0:
        print(f"延时记录共有{tdfsize}条")
        # 增加当前时间，延时值引用最近一次的值，用于做图形展示的右边栏
        #         nowtimestamp = time.ctime()
        #         timedf = timedf.append(pd.DataFrame([timedf.iloc[-1]], index=[pd.to_datetime(time.ctime())]))
        timedf = timedf.append(
            pd.DataFrame([timedf.iloc[-1]], index=[pd.to_datetime(time.ctime())])
        )
        jujinmins = int((timedf.index[-1] - timedf.index[-2]).total_seconds() / 60)
    else:
        jujinmins = 0
        log.info(f"数据表{tablename}还没有数据呢")

    timedf.loc[timedf.delay < 0] = 0
    # print(timedf.iloc[:2])
    print(timedf.iloc[-3:])

    return jujinmins, timedf


def showdelayimg(jingdu: int = 300):
    jujinm, timedf = getdelaydb()
    print(f"记录新鲜度：出炉了{jujinm}分钟")

    register_matplotlib_converters()

    plt.figure(figsize=(36, 6))
    plt.style.use("ggplot")  # 使得作图自带色彩，这样不用费脑筋去考虑配色什么的；

    # 画出左边界
    tmin = timedf.index.min()
    tmax = timedf.index.max()
    shicha = tmax - tmin
    bianjie = int(shicha.total_seconds() / 40)
    print(f"左边界：{bianjie}秒，也就是大约{int(bianjie / 60)}分钟")
    # plt.xlim(xmin=tmin-pd.Timedelta(f'{bianjie}s'))
    plt.xlim(xmin=tmin)
    plt.xlim(xmax=tmax + pd.Timedelta(f"{bianjie}s"))
    # plt.vlines(tmin, 0, int(timedf.max() / 2))
    plt.vlines(tmax, 0, int(timedf.max() / 2))

    # 绘出主图和标题
    plt.scatter(timedf.index, timedf, s=timedf)
    plt.scatter(timedf[timedf == 0].index, timedf[timedf == 0], s=0.5)
    plt.title("信息频率和延时")

    imgwcdelaypath = touchfilepath2depth(
        getdirmain() / "img" / "webchat" / "wcdelay.png"
    )

    plt.savefig(imgwcdelaypath, dpi=jingdu)
    print(os.path.relpath(imgwcdelaypath))

    return imgwcdelaypath


if __name__ == "__main__":
    log.info(f"运行文件\t{__file__}")
    xinxian, tdf = getdelaydb()
    print(xinxian)
    print(tdf.sort_index(ascending=False))
    log.info(f"文件{__file__}运行结束")