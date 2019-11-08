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

# + {"pycharm": {"is_executing": false}}
import os
import re
import pandas as pd

# + {"pycharm": {"is_executing": false}}
import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.logme import log
    from func.configpr import getcfp, getcfpoptionvalue, setcfpoptionvalue
    from func.wrapfuncs import timethis, ift2phone
    from func.evernttest import getinivaluefromnote


# + {"pycharm": {"is_executing": false}}
def chuqinjiluzhengli():
    """
    整理原始出勤记录，输出有用信息
    :return: 有用信息列表
    """
    print(dirmainpath)
    qdpath = dirmainpath / 'data' /'work' / '考勤记录'
    print(qdpath)
    ptn = re.compile('^员工出勤记录(20\d{4}).*\.xls$')
    stopcount = 0
    fls = os.listdir(qdpath)
    print(len(fls))
    targetlst = []
    for fl in fls:
        timestamp = re.findall(ptn, fl)
        if timestamp:
            cld = []
            qddf = pd.read_excel(qdpath / fl, sheet_name='考勤记录')
            shiduan = qddf.iloc[1, 2]   #时间段
            """
            出勤统计时间段
            """
            zhibiao = qddf.iloc[1, 11]  #制表时间
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
                dangan = []
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


# + {"pycharm": {"is_executing": false}}
def tongjichuqin():
    pass


# + {"pycharm": {"is_executing": false}}
def tongjichuqinjishigong():
    pass


# + {"pycharm": {"is_executing": false}}
def tongjichuqinixingzheng():
    pass


# + {"pycharm": {"is_executing": false}}
qdlst = chuqinjiluzhengli()
jiludf = qdlst[-1][4]
ptnsep = re.compile('[,，]')
jslst = re.split(ptnsep, getinivaluefromnote('xingzheng', '计时工'))
xzlst = re.split(ptnsep, getinivaluefromnote('xingzheng', '行政岗位'))
for name in jiludf.columns:
    if name in jslst:
        print(f"计时工\t{name}")
    elif name in xzlst:
        print(f"行政岗位\t{name}")
    else:
        print(f"正常岗位\t{name}")
# print(qdlst)

# + {"pycharm": {"is_executing": false}}

