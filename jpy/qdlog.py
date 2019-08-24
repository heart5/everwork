# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
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
import pandas as pd

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.logme import log
    from func.configpr import getcfp, getcfpoptionvalue, setcfpoptionvalue
    from func.wrapfuncs import timethis, ift2phone
    from func.evernttest import getinivaluefromnote

def allin():
    print(dirmainpath)
    qdpath = dirmainpath / 'data' /'work'
    print(qdpath)
    ptn = re.compile('^20\d{2}年全单统计管理__(20\d{10}).*\.xlsm$')
    stopcount = 0
    fls = os.listdir(qdpath)
    print(len(fls))
    targetlst = []
    for fl in fls:
        timestamp = re.findall(ptn, fl)
        if timestamp:
            cld = []
            qddf = pd.read_excel(qdpath / fl, sheetname='全单统计管理')
            # print(qddf.tail(5))
            cld.append(fl)
            cld.append(timestamp[0])
            cld.append(qddf.shape[0])
            cld.append(qddf)
            targetlst.append(cld)
            # print(f"{fl}\t{timestamp[0]}\t{qddf.shape[0]}")
            # print(targetlst)
            stopcount += 1
        if stopcount >= 5:
            break

    return targetlst

qdlst = allin()
print(qdlst)
