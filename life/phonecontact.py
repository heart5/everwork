# encoding:utf-8
"""
手机联系人管理
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
    from func.termuxtools import termux_contact_list
    from etc.getid import getdeviceid
    from func.pdtools import lststr2img


def checkphoneinfotable(dbname: str, tablename: str):
    """
    检查联系人数据表是否已经构建，设置相应的ini值避免重复打开关闭数据库文件进行检查
    """
    if not (phonecontactdb := getcfpoptionvalue('everpim', str(getdeviceid()), 'phonecontactdb')):
        print(phonecontactdb)
        csql = f"create table if not exists {tablename} (number str PRIMARY KEY not null unique on conflict ignore, name str, appendtime datetime)"
        ifnotcreate(tablename, csql, dbname)
        setcfpoptionvalue('everpim', str(getdeviceid()), 'phonecontactdb', str(True))
        logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
        log.info(logstr)


def phone2db():
    dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "phonecontact.db")
    conn = lite.connect(dbname)
    ctstr = termux_contact_list()
    ctlst = eval(ctstr)
    ctdf = pd.DataFrame(ctlst)
    ctdf['number'] = ctdf['number'].apply(lambda x: x.replace(" ", ''))
    ctdf.drop_duplicates('number', inplace=True)
    ctdf['appendtime'] = time.time()
    print(ctdf.shape[0])
    tablename = "phone"
    checkphoneinfotable(dbname, tablename)
    recordctdf = pd.read_sql(f"select * from {tablename}", con=conn)
    ctdf.to_sql(tablename, con=conn, if_exists="append", index=False)
    afterinsertctdf = pd.read_sql(f"select * from {tablename}", con=conn)
    conn.close()
    logstr = f"联系人记录既有数量：\t{recordctdf.shape[0]}，" + f"待添加的联系人记录数量为：\t{ctdf.shape[0]}，" + f"添加后的联系人记录数量总计为：\t{afterinsertctdf.shape[0]}"
    log.info(logstr)


def getphoneinfodb():
    """
    从联系人信息数据表提取数据（DataFrame）
    """
#     tablename = "wcdelaynew"
    dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "phonecontact.db")
    tablename="phone"
    checkphoneinfotable(dbname, tablename)

    conn = lite.connect(dbname)
    recordctdf = pd.read_sql(f"select * from {tablename}", con=conn)
    conn.close()
    
    recordctdf["appendtime"] = recordctdf["appendtime"].apply(
            lambda x: pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", 
                   time.localtime(x))))

    if (tdfsize := recordctdf.shape[0]) != 0:
        print(f"联系人记录共有{tdfsize}条")
        jujinmins = int((pd.to_datetime(time.ctime()) - recordctdf['appendtime'].max()).total_seconds() / 3600)
    else:
        jujinmins = 0
        logstr = f"数据表{tablename}还没有数据呢"
        log.info(logstr)

    print(recordctdf.iloc[-3:])

    return jujinmins, recordctdf


def showphoneinfoimg(jingdu: int = 300):
    '''
    show the img for phone info
    
    '''
    jujinm, ctdf = getphoneinfodb()
    print(f"记录新鲜度：刚过去了{jujinm}小时")

    register_matplotlib_converters()

    contactoutstr = f"目前联系人共有{ctdf.shape[0]}个，有效添加次数为：{ctdf.groupby('appendtime').count().shape[0]}，最近一次添加时间为：{ctdf['appendtime'].max()}。\n"

    dayrange = 30
    descbegintime = pd.to_datetime(time.ctime()) + pd.Timedelta(f'-{dayrange}d')

    contactoutstr += f"最近{dayrange}天添加的联系人如下(前20位）：\n"
    ctrecentstr = ctdf[ctdf.appendtime > descbegintime][-20:].to_string(justify='left', show_dimensions=True, index=False)
    contactoutstr += ctrecentstr

    return lststr2img(contactoutstr, title="手机联系人综合描述")


if __name__ == "__main__":
    logstrouter = "运行文件\t%s" %__file__
    log.info(logstrouter)
    phone2db()
    xinxian, tdf = getphoneinfodb()
    print(xinxian)
    print(tdf.sort_index(ascending=False))
    logstrouter = "文件%s运行结束" %(__file__)
    log.info(logstrouter)
