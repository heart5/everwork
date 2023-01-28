# encoding:utf-8
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     notebook_metadata_filter: -jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# %%
"""
用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
"""
from func.logme import log
from etc.zip2onedrive import zipdata2one_timer
from work.bankcard import financetimer
from work.dutyon import duty_timer
from work.notesaledetails import pinpaifenxi_timer
from work.fetchdata import filegmailevernote2datacenter
from life.peoplelog2note import peoplestattimer
from life.notejinchujilu import jinchustattimer
from work.workplan import planfenxi
from work.order import showorderstat2note
from etc.log2note import log2notetimer
from life.noteweather import weatherstattimer  # 调用同目录下其他文件（py）中的函数
import sqlite3 as lite
# import imp4nb
import sys


# %%
# %%
sys.path.extend(['func', 'work', 'life', 'etc'])
# from func.pdtools import dataokay
# from func.evernt import get_notestore
# from func.first import dbpathquandan

# %%
# %%
log.debug('自动线程任务启动……')
# pickstat(token, note_store, cnx, '1c0830d9-e42f-4ce7-bf36-ead868a55eca', '订单配货统计图', cum=True)
# desclitedb(cnx)
# swissknife(cnx)
# cnx.close()
# isnoteupdate(token, note_store, '1c0830d9-e42f-4ce7-bf36-ead868a55eca')

# %%
# %%
filegmailevernote2datacenter(60 * 55)
showorderstat2note(60 * 60 * 1 + 60 * 8)
log2notetimer(60 * 45)
weatherstattimer(60 * 60 * 1 + 60 * 5)
jinchustattimer(60 * 60)
peoplestattimer(60 * 25)
planfenxi(60 * 65 * 2)
duty_timer(60 * 60 * 24)
financetimer(60 * 60 * 3 + 60 * 33)
pinpaifenxi_timer(60 * 60 * 24)
zipdata2one_timer(60 * 60 * 12 + 60 * 35)

# + [markdown] magic_args="[markdown] magic_args=\"[markdown]\""
# writeini()
# -

# %%
# %%
# findnotebookfromevernote(token)
# log.debug('程序结束！')
# print(vars())
log.info('自动线程任务启动完毕！')
