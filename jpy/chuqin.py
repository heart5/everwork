# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import os
import re
import math
import pandas as pd
import numpy as np
from pandas import DataFrame

import pathmagic

with pathmagic.context():
    from func.first import dirmainpath
    from func.logme import log
    from func.configpr import getcfp, getcfpoptionvalue, setcfpoptionvalue
    from func.wrapfuncs import timethis, ift2phone
    from func.evernttest import getinivaluefromnote


def chuqinjiluzhengli():
    """
    整理原始出勤记录，输出有用信息
    :return: 有用信息列表
    """
    print(dirmainpath)
    qdpath = dirmainpath / 'data' / 'work' / '考勤记录'
    print(qdpath)
    ptn = re.compile('^员工出勤记录(20\\d{4}).*\\.xls$')
    stopcount = 0
    fls = os.listdir(qdpath)
    print(len(fls))
    targetlst = []
    for fl in fls:
        timestamp = re.findall(ptn, fl)
        if timestamp:
            cld = []
            qddf = pd.read_excel(qdpath / fl, sheet_name='考勤记录')
            shiduan = qddf.iloc[1, 2]  # 时间段
            """
            出勤统计时间段
            """
            zhibiao = qddf.iloc[1, 11]  # 制表时间
            jiludf = qddf.iloc[3:]
            cld.append(shiduan)
            cld.append(zhibiao)
            renshu = int(jiludf.shape[0] / 2)
            cld.append(f"{renshu}")
            clcount = len(jiludf.columns)
            jiludf.columns = range(1, clcount + 1)
            cllst = []
            jilulst = []
            danganlst = []
            for i in range(renshu):
                dangan = list()
                dangan.append(jiludf.iloc[i * 2, 2])
                dangan.append(jiludf.iloc[i * 2, 10])
                dangan.append(jiludf.iloc[i * 2, 20])
                danganlst.append(dangan)
                cllst.append(i + 1)
                jilulst.append(jiludf.iloc[i * 2 + 1])

            dangandf = pd.DataFrame(danganlst, columns=['number', 'name', 'bumen'])
            cld.append(dangandf)
            jiluoutdf = pd.DataFrame(jilulst)
            jiluoutdf = jiluoutdf.T
            # jiluoutdf.columns = cllst
            jiluoutdf.columns = list(dangandf['name'].values)
            cld.append(jiluoutdf)
            # cld.append(jilulst)
            targetlst.append(cld)
            # print(f"{fl}\t{timestamp[0]}\t{qddf.shape[0]}")
            # print(targetlst)
            stopcount += 1
        if stopcount >= 5:
            break

    return targetlst


def tongjichuqin():
    pass


def splitjs(jsstr: str):
    ptn = re.compile('\\d{2}:\\d{2}')
    findlst = re.findall(ptn, jsstr)
    if len(findlst) == 2:
        if (findlst[0] <= '12:00') & (findlst[1] >= '13:30'):
            findlst.insert(1, '13:30')
            findlst.insert(1, '12:00')
            log.info(f"计时工打卡记录条目({len(findlst)})增补中午休息间隔\t{findlst}")
        elif (findlst[0] >= '12:00') & (findlst[1] >= '13:30'):
            log.info(f"计时工打卡记录条目({len(findlst)})属于正常下午班")
        elif (findlst[0] <= '12:00') & (findlst[1] <= '13:30'):
            log.info(f"计时工打卡记录条目({len(findlst)})属于正常上午班")
        else:
            log.critical(f"出现不合规范的计时工打卡记录({len(findlst)})\t{findlst}")
            findlst = None
    elif len(findlst) == 3:
        if findlst[0] <= '12:00':
            findlst.insert(1, '12:00')
            log.info(f"计时工打卡记录条目({len(findlst)})增补中午休息间隔\t{findlst}")
        else:
            log.critical(f"出现不合规范的计时工打卡记录({len(findlst)})\t{findlst}")
            findlst = None
    elif len(findlst) == 1:
        if findlst[0] <= '12:00':
            findlst.append('12:00')
            log.info(f"计时工打卡记录条目({len(findlst)})增补中午休止\t{findlst}")
        elif findlst[0] >= '12:00':
            findlst.append('18:00')
            log.info(f"计时工打卡记录条目({len(findlst)})增补下午休止\t{findlst}")
        else:
            log.critical(f"出现不合规范的计时工打卡记录({len(findlst)})\t{findlst}")
            findlst = None
    elif len(findlst) == 4:
        pass
    elif len(findlst) != 0:
        log.critical(f"出现不合规范的计时工打卡记录({len(findlst)})\t{findlst}")
        findlst = None
    resultlst = findlst

    return resultlst


def computejishi(inputlst: list):
    if (len(inputlst) % 2) != 0:
        log.critical(f"打卡记录非偶数\t{inputlst}")
        return

    # print(inputlst)
    totalminute: int = 0
    for i in range(0, len(inputlst), 2):
        frtlst = inputlst[i].split(":")
        print(frtlst)
        frtmin = int(frtlst[0]) * 60
        frtmin += int(frtlst[1])
        seclst = inputlst[i+1].split(":")
        print(seclst)
        secmin = int(seclst[0]) * 60
        secmin += int(seclst[1])
        totalminute += secmin - frtmin

    return totalminute


def tongjichuqinjishigong(inputs: pd.Series):
    df = pd.DataFrame(inputs)
    df.columns = ['打卡记录']
    # print(df)
    df['整理'] = df[df.columns[0]].apply(lambda x: splitjs(str(x)) if x else None)
    df['分钟'] = df[df.columns[1]].apply(lambda x: computejishi(x) if x else None)

    return df, df['分钟'].sum()


def tongjichuqinixingzheng():
    pass


qdlst = chuqinjiluzhengli()
jilusdf = qdlst[0][4]
ptnsep = re.compile('[,，]')
jslst = re.split(ptnsep, getinivaluefromnote('xingzheng', '计时工'))
xzlst = re.split(ptnsep, getinivaluefromnote('xingzheng', '行政岗位'))
for name in jilusdf.columns:
    if name in jslst:
        dfperson: DataFrame
        heji: int
        dfperson, heji = tongjichuqinjishigong(jilusdf[name])
        print(f"计时工\t{name}\t{math.ceil(heji / 60)}")
    elif name in xzlst:
        print(f"行政岗位\t{name}")
    else:
        print(f"正常岗位\t{name}")
# print(qdlst)
