# coding=utf8
"""
微信联系人管理
"""

from pathlib import Path
# import os
import sys
import random
# import numpy as np
import sqlite3 as lite
import pandas as pd
import itchat
# from binascii import hexlify, unhexlify

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.litetools import ifnotcreate
    from func.wrapfuncs import timethis
    from func.logme import log
    from func.sysfunc import uuid3hexstr
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue


def getownername():
    # pklabpath = os.path.relpath(touchfilepath2depth(getdirmain() / 'itchat.pkl'))
    pklabpath = getdirmain() / 'itchat.pkl'
    # print(pklabpath)
    if itchat.originInstance.alive:
        print(f"微信处于登录状态……")
    else:
        itchat.auto_login(hotReload=True, statusStorageDir=pklabpath)   #热启动你的微信sg['FromUserName']
        if not itchat.originInstance.alive:
            log.critical("微信未能热启动，仍处于未登陆状态，退出！")
            sys.exit(1)

    return itchat.search_friends()['NickName']


def getdbname(dbpath: str, ownername: str):
    return touchfilepath2depth(getdirmain() / dbpath / f"wccontact_{ownername}.db")


def checktable(dbpath: str, ownername: str):
    if not (ifcreated := getcfpoptionvalue('everwebchat', 'wcdb', ownername)):
        print(ifcreated)
        dbnameinner = getdbname(dbpath, ownername)
        tablename = "wccheadimg"
        csql = f"create table if not exists {tablename} (himgid INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT not null, himguuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, headimg BLOB NOT NULL)"
        ifnotcreate(tablename, csql, dbnameinner)

        tablename_cc = "wccontact"
        csql = f"create table if not exists {tablename_cc} (id INTEGER PRIMARY KEY AUTOINCREMENT, contactuuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, nickname TEXT, contactflag int, remarkname TEXT, sex int, signature TEXT, starfriend int, attrstatus int, province TEXT, city TEXT, snsflag int, keyword TEXT, appendtime datatime)"
        ifnotcreate(tablename_cc, csql, dbnameinner)

        setcfpoptionvalue('everwebchat', 'wcdb', ownername, str(True))
    else:
        # print(ifcreated)
        # print(f"{ownername}的联系人数据库和相关数据表已经存在。")
        pass


def getwcdffromfrdlst(frdlst: list, howmany: str='fixed', haveheadimg=False):

    def yieldrange(startnum: int, width: int = 20):
        endnum = (startnum + width, len(frdlst))[len(frdlst) < startnum + width]
        return range(startnum, endnum)

    # if type(howmany) is int:
    if isinstance(howmany, int):
        rang = yieldrange(howmany)
    elif isinstance(howmany, tuple):
        if len(howmany) == 1:
            rang = yieldrange(howmany[0])
        elif len(howmany) >= 2:
            rang = yieldrange(howmany[0], howmany[1])
    elif howmany.lower() == 'random':
        rang = random.sample(range(len(frdlst)), 5)
    elif howmany.lower() == 'fixed':
        rang = range(0, 5)
    elif howmany.lower() == 'all':
        rang = range(len(frdlst))
    else:
        logstr = "%s不是合法的参数" %(howmany)
        log.critical(logstr)
        return
    frdinfolst = list()
    attrlst = ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature',
               'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord']
    for ix in rang:
        frd = frdlst[ix]
        frdinfo = list()
        if 'UserName' in frd.keys():
            try:
                for attr in attrlst:
                    frdinfo.append(frd[attr])
    #                 print(attr, type(frd[attr]), frd[attr])
                # 显示所有key和value
        #         for key, value in frd.items():
        #             print(key, type(value), value)
            except Exception as eeee:
                log.critical(f"第【{ix}/{len(frdlst)}】条记录存在问题。{frd['NickName']}\t{frd['UserName']}\t{eeee}")
                continue

            if haveheadimg:
                headimg = itchat.get_head_img(frd["UserName"])
                # frdinfouuiswithnohead = uuid3hexstr(frdinfo)
    #             print(f"【{ix}/{len(frdlst)}】【{frdinfouuiswithnohead}】{frd['NickName']}\t{frd['RemarkName']}\t{frd['UserName']}\theadimg的长度为：\t{len(headimg)}。", end='\t')
    #             frdinfo.insert(0, frdinfouuiswithnohead)
    #             frdinfo.append(uuid3hexstr(headimg[:600]))
                frdinfo.append(headimg)
    #             frdinfo.append(pd.Timestamp.now())
    #             frdinfo.append(hexlify(headimg).decode())

                if (iblen := len(headimg)) == 0:
                    print(f"{frd['NickName']}\t图像字节长度为：{iblen}\t图像获取失败！")
                else:
    #                 print(f"内容示意：\t{headimg[:15]}")
    #                 print()
                    pass

            frdinfolst.append(frdinfo)
        else:
            print(f'不存在UserName键值')
    # print(f"{len(frdinfolst)}")
#     attrlst.insert(0, 'contactuuid')
    if haveheadimg:
        attrlst.extend(['headimg'])
#     attrlst.extend(['imguuid', 'headimg', 'appendtime'])
#     print(attrlst)
    frddf = pd.DataFrame(frdinfolst, columns=attrlst)

    return frddf


def dfuuid3nohead(inputdf: pd.DataFrame):
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'headimg']
    frddf2append = inputdf.copy(deep=True)
    # [NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord']
    clnamescleanlst = [cl for cl in list(frddf2append.columns.values) if cl.lower() not in ['username', 'headimg']]
#     print(clnamescleanlst)
    frddf2appendnoimguuid = frddf2append.loc[:, clnamescleanlst]
    frddf2appendnoimguuid['contactuuid'] = frddf2appendnoimguuid[clnamescleanlst].apply(lambda x: uuid3hexstr(list(x.values)), axis=1)
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'headimg', 'appendtime']
    frddf2appendnoimguuid['appendtime'] = pd.Timestamp.now()
    
    return frddf2appendnoimguuid


@timethis
def updatectdf(howmuch: str = "all"):
    owner = getownername()
    dbpath = Path("data")/ 'db'
    dbname = getdbname(dbpath, owner)

    frdlst = itchat.get_friends(update=True)

    width = 150
    spllst = [(i * width, width) for i in range((len(frdlst) // width) +1)]

    if howmuch == 'tail':
        startpos = -2
    elif howmuch == 'all':
        startpos = 0
    else:
        startpos = int(len(spllst) / 5)

    dftablename = 'wccontact'
    for sltuple in spllst[startpos:]:
        print(sltuple, '/', len(frdlst))
        conn = lite.connect(dbname)
        frddfready = dfuuid3nohead(getwcdffromfrdlst(frdlst, sltuple))
        frddfready.to_sql(dftablename, con=conn, if_exists='append', index=False)
        conn.close()


def just4test():
    """
    用于测试。实际上是想看看怎么才能做得上pylint的俘虏！
    """
    owner = getownername()
    print(owner)
    frdlst = itchat.get_friends(update=True)
    frddfttt = getwcdffromfrdlst(frdlst, 'I am fine.')

    print(frddfttt)


def getctdf():
    owner = getownername()
    dbpath = Path("data")/ 'db'
    dbname = getdbname(dbpath, owner)
    dftablename = 'wccontact'
    conn = lite.connect(dbname)
    frddfread = pd.read_sql(f'select * from {dftablename}', con=conn).set_index('id')
    conn.close()

    return frddfread


if __name__ == '__main__':
    logstr = f'运行文件\t{__file__}'
    log.info(logstr)

    # note_store = get_notestore()

    # just4test()

    updatectdf()

    dfread = getctdf()
    print(dfread.shape[0])
    logstr = dfread[list(dfread)[1:]].tail(30)
    log.info(logstr)

    # owner = getownername()
    # dbpath = Path("data")/ 'db'
    # checktable(dbpath, owner)

    logstr = f'{__file__}\t运行结束！'
    log.info(logstr)
