# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %%
"""
让微信常驻运行，并保留有效pkg文件以便下次热启动而不用重新扫码
"""

import os
import shutil

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath, touchfilepath2depth
    from func.logme import log
    from etc.guanliprocess import judgeprocess


def keeplivewebchat():
    srcdir = dirmainpath
    trtdir = dirmainpath / 'data' / 'webchat'
    touchfilepath2depth(trtdir)
    fname = 'itchat.pkl'
    if judgeprocess("python life/webchat.py"):
        print(f"微信程序正常运行")
        shutil.copy(srcdir / fname, trtdir / fname)
    else:
        shutil.copy(trtdir / fname, srcdir / fname)
        stdout = os.popen(f"cd {dirmainpath};python life/webchat.py")
        print(f"{stdout.read()}")


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    keeplivewebchat()
    log.info(f"文件\t{__file__}\t运行结束。")
