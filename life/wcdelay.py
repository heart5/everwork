# encoding:utf-8
"""
微信延迟管理文件
"""
import os
import time
# import datetime
import sqlite3 as lite
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.first import touchfilepath2depth, getdirmain
    from func.litetools import ifnotcreate
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue


def checkwcdelaytable(dbname: str, tablename: str):
    """
    检查和dbname（绝对路径）相对应的延时数据表是否已经构建，设置相应的ini值避免重复打开关闭数据库文件进行检查
    """
    if not (wcdelaycreated := getcfpoptionvalue('everwebchat',
                                                os.path.abspath(dbname), 'wcdelay')):
        print(wcdelaycreated)
        csql = f"create table if not exists {tablename} (id INTEGER PRIMARY KEY AUTOINCREMENT, msgtime int, delay int)"
        ifnotcreate(tablename, csql, dbname)
        setcfpoptionvalue('everwebchat', os.path.abspath(dbname), 'wcdelay',
                          str(True))
        logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
        log.info(logstr)


def inserttimeitem2db(dbname: str, timestampinput: int):
    '''
    insert timestamp to wcdelay db whose table name is wcdelay
    '''
    tablename = "wcdelaynew"
    checkwcdelaytable(dbname, tablename)

    # timetup = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    # timest = time.mktime(timetup)
    elsmin = (int(time.time()) - timestampinput) // 60
    conn = False
    try:
        conn = lite.connect(dbname)
        cursor = conn.cursor()
        cursor.execute(
            f"insert into {tablename} values(?, ?)", (timestampinput, elsmin)
        )
#         print(f"数据成功写入{dbname}\t{(timestampinput, elsmin)}")
        conn.commit()
    except lite.IntegrityError as lie:
        logstr = f"键值重复错误\t{lie}"
        log.critical(logstr)
    finally:
        if conn:
            conn.close()


def getdelaydb(dbname: str, tablename="wcdelaynew"):
    """
    从延时数据表提取数据（DataFrame），返回最近延时值和df
    """
#     tablename = "wcdelaynew"
    checkwcdelaytable(dbname, tablename)

    conn = lite.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(f"select * from {tablename}")
    table = cursor.fetchall()
    conn.close()
    
    tmpdf = pd.DataFrame(table)
    if len(tmpdf.columns) == 3:
        timedf = pd.DataFrame(table, columns=["id", "time", "delay"], index='id')
        timedf["time"] = timedf["time"].apply(
            lambda x: pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x)))
        )
        timdfgrp = timedf.groupby('time').sum()
    #     timedf.set_index("time", inplace=True)
    elif len(tmpdf.columns) == 2:
        timedf = pd.DataFrame(table, columns=["time", "delay"])
        timedf["time"] = timedf["time"].apply(
            lambda x: pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x)))
        )
        timedfgrp = timedf.set_index("time")     
    else:
        return

    if (tdfsize := timedfgrp.shape[0]) != 0:
        print(f"延时记录共有{tdfsize}条")
        # 增加当前时间，延时值引用最近一次的值，用于做图形展示的右边栏
        #         nowtimestamp = time.ctime()
        #         timedf = timedf.append(pd.DataFrame([timedf.iloc[-1]],
                                        # index=[pd.to_datetime(time.ctime())]))
        timedfgrp = timedfgrp.append(
            pd.DataFrame([timedfgrp.iloc[-1]], index=[pd.to_datetime(time.ctime())])
        )
        jujinmins = int((timedfgrp.index[-1] - timedfgrp.index[-2]).total_seconds() / 60)
    else:
        jujinmins = 0
        logstr = f"数据表{tablename}还没有数据呢"
        log.info(logstr)

    timedfgrp.loc[timedfgrp.delay < 0] = 0
    # print(timedf.iloc[:2])
    print(timedf.iloc[-3:])

    return jujinmins, timedfgrp


def showdelayimg(dbname: str, jingdu: int = 300):
    '''
    show the img for wcdelay
    '''
    jujinm, timedf = getdelaydb(dbname)
#     timedf.iloc[-1]
    print(f"记录新鲜度：出炉了{jujinm}分钟")

    register_matplotlib_converters()

    plt.figure(figsize=(36, 12))
    plt.style.use("ggplot")  # 使得作图自带色彩，这样不用费脑筋去考虑配色什么的；

    def drawdelayimg(pos, timedfinner):
        # 画出左边界
        tmin = timedfinner.index.min()
        tmax = timedfinner.index.max()
        shicha = tmax - tmin
        bianjie = int(shicha.total_seconds() / 40)
        print(f"左边界：{bianjie}秒，也就是大约{int(bianjie / 60)}分钟")
        # plt.xlim(xmin=tmin-pd.Timedelta(f'{bianjie}s'))
        plt.subplot(pos)
        plt.xlim(xmin=tmin)
        plt.xlim(xmax=tmax + pd.Timedelta(f"{bianjie}s"))
        # plt.vlines(tmin, 0, int(timedf.max() / 2))
        plt.vlines(tmax, 0, int(timedfinner.max() / 2))

        # 绘出主图和标题
        plt.scatter(timedfinner.index, timedfinner, s=timedfinner)
        plt.scatter(timedfinner[timedfinner == 0].index, timedfinner[timedfinner == 0], s=0.5)
        plt.title("信息频率和延时")

    drawdelayimg(211, timedf[timedf.index > timedf.index.max() + pd.Timedelta('-2d')])
    drawdelayimg(212, timedf)

    imgwcdelaypath = touchfilepath2depth(
        getdirmain() / "img" / "webchat" / "wcdelay.png"
    )

    plt.savefig(imgwcdelaypath, dpi=jingdu)
    print(os.path.relpath(imgwcdelaypath))

    return imgwcdelaypath

if __name__ == "__main__":
    logstrouter = "运行文件\t%s" %__file__
    log.info(logstrouter)
    # owner = 'heart5'
    owner = '白晔峰'
    dbnameouter = touchfilepath2depth(getdirmain() / "data" / "db" / f"wcdelay_{owner}.db")
    xinxian, tdf = getdelaydb(dbnameouter)
    print(xinxian)
    print(tdf.sort_index(ascending=False))
    logstrouter = "文件%s运行结束" %(__file__)
    log.info(logstrouter)
