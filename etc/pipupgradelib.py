# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.10.3
# ---

# %%
"""
检查全部库文件并升级至最新版本
"""
import pip
from subprocess import call
from pip._internal.utils.misc import get_installed_distributions, get_installed_version

# %%
import pathmagic
with pathmagic.context():
    from func.configpr import getcfp
    from func.first import getdirmain, dirmainpath, touchfilepath2depth
    from func.datatools import readfromtxt, write2txt
    from func.evernttest import token, get_notestore, imglist2note, \
        evernoteapijiayi, makenote, readinifromnote
    from func.logme import log


# %%
def upgradeall():
    dislst = get_installed_distributions()
    log.info(f"当前python系统共有\t{len(dislst)}\t个有效库。")
    for dist in dislst:
        call(f"pip install --upgrade {dist.project_name}", shell=True)


# %%
if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    upgradeall()
    log.info(f"文件\t{__file__}\t运行结束。")
