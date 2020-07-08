# coding:utf-8
"""
微信联系人管理
"""

from pathlib import Path
from io import BytesIO
import time
import random
import sqlite3 as lite
from PIL import Image
import os
import sys
import pandas as pd
import numpy as np
import itchat
# from binascii import hexlify, unhexlify

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.evernttest import getinivaluefromnote
    from func.litetools import ifnotcreate, droptablefromdb, istableindb
    from func.wrapfuncs import timethis
    from func.logme import log
    from func.sysfunc import uuid3hexstr, sha2hexstr
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.filedatafunc import getdbname
    from func.wcfuncs import getownername


def checktable(dbpath: str, ownername: str):
    """
    检查数据表是否存在并根据情况创建
    """
    if not (ifcreated := getcfpoptionvalue('everwebchat', 'wcdb', ownername)):
        print(ifcreated)
        dbnameinner = getdbname(dbpath, ownername)

        tablename = "wcheadimg"
        if istableindb(tablename, dbnameinner):
            # 删表操作，危险，谨慎操作
            droptablefromdb(dbnameinner, tablename, confirm=True)        
        csql = f"create table if not exists {tablename} (himgid INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT not null, himguuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, headimg BLOB NOT NULL)"
        ifnotcreate(tablename, csql, dbnameinner)
        logstr = f"数据表{tablename}于{dbnameinner}中被删除并完成重构"
        log.critical(logstr)

        tablename_cc = "wccontact"
        if istableindb(tablename_cc, dbnameinner):
            # 删表操作，危险，谨慎操作
            droptablefromdb(dbnameinner, tablename_cc, confirm=True)        
        csql = f"create table if not exists {tablename_cc} (id INTEGER PRIMARY KEY AUTOINCREMENT, contactuuid TEXT NOT NULL UNIQUE ON CONFLICT IGNORE, nickname TEXT, contactflag int, remarkname TEXT, sex int, signature TEXT, starfriend int, attrstatus int, province TEXT, city TEXT, snsflag int, keyword TEXT, imguuid text, appendtime datatime)"
        ifnotcreate(tablename_cc, csql, dbnameinner)
        logstr = f"数据表{tablename_cc}于{dbnameinner}中被删除并完成重构"
        log.critical(logstr)
        
        setcfpoptionvalue('everwebchat', 'wcdb', ownername, str(True))


def getimguuid(inputbytes: bytes):
    imgfrombytes = Image.open(BytesIO(inputbytes))
    
    return sha2hexstr(np.array(imgfrombytes))


def getwcdffromfrdlst(frdlst: list, howmany: str='fixed', needheadimg=False):

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

            if needheadimg:
                headimg = itchat.get_head_img(frd["UserName"])
#                 print(str(headimg)[:100])
                if (iblen := len(headimg)) == 0:
                    print(f"{frd['NickName']}\t图像获取失败！")
                    frdimguuid = None
                else:
    #                 print(f"内容示意：\t{headimg[:15]}")
    #                 print()
                    frdimguuid = getimguuid(headimg)

                frdinfo.append(frdimguuid)
                frdinfo.append(headimg)

            frdinfolst.append(frdinfo)
        else:
            print(f'不存在UserName键值。\t{frd}')

    print(f"{len(frdinfolst)}")

    if needheadimg:
        attrlst.extend(['imguuid', 'headimg'])

    frddf = pd.DataFrame(frdinfolst, columns=attrlst)
    
    return frddf


def dfsha2noimg(inputdf: pd.DataFrame):
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'imguuid' 'headimg']
    frddf2append = inputdf.copy(deep=True)
    # [NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'imguuid']
    clnamescleanlst = [cl for cl in list(frddf2append.columns.values) if cl.lower() not in ['username', 'imguuid' , 'headimg', 'appendtime', 'contactuuid']]
#     print(clnamescleanlst)
#     frddf2appendnoimguuid = frddf2append.loc[:, clnamescleanlst]
    frddf2append['contactuuid'] = frddf2append[clnamescleanlst].apply(lambda x: sha2hexstr(list(x.values)), axis=1)
    # ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord', 'headimg', 'appendtime']
    frddf2append['appendtime'] = pd.Timestamp.now()
    
    return frddf2append


@timethis
def updatectdf(howmuch: str = "all", haveimg=False):
    owner = getownername()
    dbpath = Path("data")/ 'db'
    dbname = getdbname(dbpath, owner)
    checktable(dbpath, owner)

    frdlst = itchat.get_friends(update=True)

    width = 250
    spllst = [(i * width, width) for i in range((len(frdlst) // width) +1)]

    if howmuch == 'tail':
        startpos = -2
    elif howmuch == 'all':
        startpos = 0
    else:
        startpos = int(len(spllst) / 5)

    dftablename = 'wccontact'
    for sltuple in spllst[startpos:]:
        print(sltuple, '/', len(frdlst), end='\t')
        conn = lite.connect(dbname)
        readdf = getwcdffromfrdlst(frdlst, sltuple, needheadimg=haveimg)
        
        frddfready = dfsha2noimg(readdf)
        outcls = [cl for cl in list(frddfready.columns.values) if cl.lower() not in ['username', 'headimg']]
        frddfready[outcls].to_sql(dftablename, con=conn, if_exists='append', index=False)
        
        if haveimg:
            dftablenameimg = 'wcheadimg'
            frddfreadyforimg = readdf[readdf.imguuid.notnull()][['RemarkName', 'imguuid', 'headimg']]
            frddfreadyforimg.to_sql(dftablenameimg, con=conn, if_exists='append', index=False)
        
            # 如果涉及到拉取图片，避免系统认为有意干扰，每个间隔随机休息几秒
            sleepsecs = random.randint(0, 15)
            # print(f"{time.localtime()}随机休息{sleepsecs}秒……")
            time.sleep(sleepsecs)
        
        conn.close()

    print()


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
    frdfromdb = pd.read_sql(f'select * from {dftablename}', con=conn, parse_dates=['appendtime']).set_index('id')
    conn.close()

    return frdfromdb


def showwcsimply(inputdb: pd.DataFrame):
    frdfromdb = inputdb.copy(deep=True)
    # 用nickname填充remarkname为空的记录
    frdfromdb['remarkname'] = frdfromdb[['nickname', 'remarkname']].apply(lambda x: x.nickname if x.remarkname == '' else x.remarkname, axis=1)
    # 只保留明白含义的列值
    frdfromdb.drop_duplicates(['nickname', 'remarkname', 'contactflag', 'signature', 'starfriend', 'province', 'city'], keep='first', inplace=True)
    # 找出最近n天内有过更改的联系人清单，n从动态配置文件中获取，不成功则设置-1
    if (wcrecentdays := getinivaluefromnote('webchat', 'wcrecentdays')):
        pass
    else:
        wcrecentdays = -1
    startpoint = pd.Timestamp.now() + pd.Timedelta(f'{wcrecentdays}d')
    dsfortime = frdfromdb.groupby('remarkname').last()['appendtime']
    outready = frdfromdb.loc[frdfromdb['remarkname'].isin(list(dsfortime[dsfortime > startpoint].index))]
    outready['appendtime'] = outready['appendtime'].apply(lambda x: pd.to_datetime(x).strftime("%y-%m-%d %H:%M"))
    outdone = outready.groupby(['remarkname', 'appendtime']).first().sort_index(ascending=[True, False])
    outslim = outdone[['nickname', 'contactflag', 'signature', 'province', 'city']]
    
    return outslim


if __name__ == '__main__':

    try:
        logstr = f'运行文件\t{__file__}'
        log.info(logstr)
    except NameError as ne:
        log.info(f"于notebook环境中调试，无法正常调用参数：__file__。运行环境：{sys.executable}\t{os.path.abspath(sys.argv[0])}")
    # note_store = get_notestore()

    # just4test()

    updatectdf()

    dfread = getctdf()
    print(dfread.shape[0])
    logstr = showwcsimply(dfread).tail(30)
    log.info(logstr)

    # owner = getownername()
    # dbpath = Path("data")/ 'db'
    # checktable(dbpath, owner)

    try:
        logstr = f'{__file__}\t运行结束！'
        log.info(logstr)
    except NameError as ne:
        log.info(f"于notebook环境中调试，无法正常调用参数：__file__。运行环境：{sys.executable}\t{os.path.abspath(sys.argv[0])}")


