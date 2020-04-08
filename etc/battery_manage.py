# encoding:utf-8
"""
电池电量管理
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
    from etc.getid import getdeviceid
    from func.termuxtools import battery_status


def checkbatteryinfotable(dbname: str, tablename: str):
    """
    检查设备的电池信息数据表是否已经构建，设置相应的ini值避免重复打开关闭数据库文件进行检查
    """
    if not (batteryinfocreated := getcfpoptionvalue('everhard', str(getdeviceid()), 'batteryinfodb')):
        print(batteryinfocreated)
        csql = f"create table if not exists {tablename} (appendtime int PRIMARY KEY, percentage int, temperature float)"
        ifnotcreate(tablename, csql, dbname)
        setcfpoptionvalue('everhard', str(getdeviceid()), 'batteryinfodb', str(True))
        logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
        log.info(logstr)


def insertbattinfoitem2db(dbname: str, percentage: int, temperature: float):
    '''
    插入电池信息（电量百分比、温度）到数据表battinfo中
    '''
    tablename = "battinfo"
    checkbatteryinfotable(dbname, tablename)

    # timetup = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    # timest = time.mktime(timetup)
#     elsmin = (int(time.time()) - timestampinput) // 60
    conn = False
    try:
        conn = lite.connect(dbname)
        cursor = conn.cursor()
        cursor.execute(
            f"insert into {tablename} values(?, ?, ?)", (time.time(), percentage, temperature)
        )
#         print(f"数据成功写入{dbname}\t{(timestampinput, elsmin)}")
        conn.commit()
    except lite.IntegrityError as lie:
        logstr = f"键值重复错误\t{lie}"
        log.critical(logstr)
    finally:
        if conn:
            conn.close()

            
def batteryrecord2db(dbname: str):
    while (bsdict := battery_status())['plugged'].upper() == 'PLUGGED_AC':
        insertbattinfoitem2db(dbname, bsdict['percentage'], bsdict['temperature'])
        time.sleep(30)


def getbattinfodb(dbname: str, tablename="battinfo"):
    """
    从电池信息数据表提取数据（DataFrame）
    """
#     tablename = "wcdelaynew"
    checkbatteryinfotable(dbname, tablename)

    conn = lite.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(f"select * from {tablename}")
    table = cursor.fetchall()
    conn.close()
    
    timedf = pd.DataFrame(table, columns=["appendtime", "percentage", "temperature"])
    timedf["appendtime"] = timedf["appendtime"].apply(
            lambda x: pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x))))
    timedfgrp = timedf.set_index("appendtime")  

    if (tdfsize := timedfgrp.shape[0]) != 0:
        print(f"电池记录共有{tdfsize}条")
        jujinmins = int((pd.to_datetime(time.ctime()) - timedfgrp.index[-1]).total_seconds() / 60)
    else:
        jujinmins = 0
        logstr = f"数据表{tablename}还没有数据呢"
        log.info(logstr)

    print(timedfgrp.iloc[-3:])

    return jujinmins, timedfgrp


def showbattinfoimg(dbname: str, jingdu: int = 300):
    '''
    show the img for battery info
    '''
    jujinm, battinfodf = getbattinfodb(dbname)
    print(f"充电记录新鲜度：刚过去了{jujinm}分钟")

    register_matplotlib_converters()

    plt.figure(figsize=(36, 12))
    plt.style.use("ggplot")  # 使得作图自带色彩，这样不用费脑筋去考虑配色什么的；

    def drawdelayimg(pos, timedfinner, title):
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
    #     plt.vlines(tmax, 0, int(timedfinner.max() / 2))

        # 绘出主图和标题
        plt.scatter(timedfinner.index, timedfinner, s=timedfinner)
        plt.scatter(timedfinner[timedfinner == 0].index, timedfinner[timedfinner == 0], s=0.5)
        plt.title(title, fontsize=40)
        plt.tick_params(labelsize=20)
        plt.tight_layout()

    timedf = battinfodf['percentage']
    drawdelayimg(321, timedf[timedf.index > timedf.index.max() + pd.Timedelta('-2d')], "电量（%，最近两天）")
    plt.ylim(0, 110)
    drawdelayimg(312, timedf, "电量（%，全部）")
    plt.ylim(0, 110)
#     imgwcdelaypath = touchfilepath2depth(getdirmain() / "img" / "hard" / "battinfo.png")

    timedf = battinfodf['temperature']
    drawdelayimg(322, timedf[timedf.index > timedf.index.max() + pd.Timedelta('-2d')], "温度（℃，最近两天）")
    plt.ylim(20, 40)
    drawdelayimg(313, timedf, "温度（℃，全部）")
    plt.ylim(20, 40)
    fig1 = plt.gcf()

    imgwcdelaypath = touchfilepath2depth(getdirmain() / "img" / "hard" / "batttempinfo.png")
#     plt.show()
    fig1.savefig(imgwcdelaypath, dpi=jingdu)
    print(os.path.relpath(imgwcdelaypath))

    return imgwcdelaypath


if __name__ == "__main__":
    logstrouter = "运行文件\t%s" %__file__
    log.info(logstrouter)
    dbnameouter = touchfilepath2depth(getdirmain() / "data" / "db" / f"batteryinfo.db")
    xinxian, tdf = getbattinfodb(dbnameouter)
    print(xinxian)
    print(tdf.sort_index(ascending=False))
    logstrouter = "文件%s运行结束" %(__file__)
    log.info(logstrouter)
