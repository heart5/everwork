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
检查是否有新的QR，有就发送邮件
"""

# %%
import os
import time
import pathmagic

# %%
with pathmagic.context():
    from func.logme import log
    from func.first import getdirmain
    from func.mailsfunc import findnewthenupdatenote


# %%
def findnewqrthensendmail():
    fl = 'QR.png'
    qrfile = getdirmain() / fl
    findnewthenupdatenote(qrfile, 'everwebchat', 'webchat', 'qr', 'QR微信二维码')


# %%
if __name__ == '__main__':
    # log.info(f'运行文件\t{__file__}')
    findnewqrthensendmail()
    # log.info(f"文件\t{__file__}\t运行结束。")
