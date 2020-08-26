# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_json: true
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + {"pycharm": {"is_executing": false}}
import os
import re
import pandas as pd
# -

# # just a title

# + {"pycharm": {"is_executing": false}}
import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.logme import log
    from func.configpr import getcfp, getcfpoptionvalue, setcfpoptionvalue
    from func.wrapfuncs import timethis, ift2phone
    from func.evernttest import getinivaluefromnote
    from work.chuqin import chuqinjiluzhengli, tongjichuqinjishigong, zonghetongji


# + {"pycharm": {"is_executing": false}}
def tongjichuqin():
    """
    人生自古
    """
    print(f"first line")
    print(f"first line")
    pass


# + {"pycharm": {"is_executing": false}}
def tongjichuqinixingzheng():
    pass


# -

qslst = chuqinjiluzhengli()

print(len(qslst))
for cqyue in qslst:
    title, date, number, yuangongdf, chuqindf = tuple(cqyue)
    print(title, date, number)
    ptsep = re.compile('[,， ]')
    jslst = re.split(ptsep, getinivaluefromnote('xingzheng', '计时工'))
    xzlst = re.split(ptsep, getinivaluefromnote('xingzheng', '行政岗位'))
    for name in chuqindf.columns:
        if name in jslst:
            chugongtianshu, fenzhongleiji, gongshi = tongjichuqinjishigong(chuqindf[name])
            print(f"计时工\t{name}\t{chugongtianshu}\t{fenzhongleiji}\t{gongshi}")
        elif name in xzlst:
            print(f"行政岗位\t{name}")
        else:
            print(f"正常岗位\t{name}")


log.info(f"this a just a show")


