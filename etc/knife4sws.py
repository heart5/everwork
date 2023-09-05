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

# %% [markdown]
# # 瑞士军刀

# %%
"""
各种有用的小函数，称之为瑞士军刀
"""

# %% [markdown]
# ## 库引入

# %%
import os
import time
import math
import pandas as pd
from pathlib import Path
from pylab import plt

# %%
import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.first import getdirmain, touchfilepath2depth
    from etc.getid import getdeviceid
    from func.evernttest import get_notestore, imglist2note, \
        getinivaluefromnote, getnotecontent
    from func.sysfunc import not_IPython


# %% [markdown]
# ## 函数集合

# %% [markdown]
# ### showsource4note()

# %%
def showsource4note():
    """
    获取笔记的内容体并返回
    """
    deviceid = getdeviceid()
    guid = getinivaluefromnote('freemem', f'free_{deviceid}')
    source1 = getnotecontent(guid)
    return source1


# %% [markdown]
# ## 主函数

# %%
if __name__ == '__main__':
    if not_IPython():
        logstrouter = "运行文件\t%s……" % __file__
        log.info(logstrouter)
    result = showsource4note()
    print(result)
    if not_IPython():
        logstrouter = "文件%s运行结束" % (__file__)
        log.info(logstrouter)

# %%
