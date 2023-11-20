# encoding:utf-8
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
用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
"""

# %%
import pathmagic

# %%
with pathmagic.context():
    # from life.noteweather import weatherstattimer  # 调用同目录下其他文件（py）中的函数
    # from etc.log2note import log2notetimer
    # from work.order import showorderstat2note
    # from work.workplan import planfenxi
    # from func.pdtools import dataokay
    # from life.notejinchujilu import jinchustattimer
    # from life.peoplelog2note import peoplestattimer
    # from work.fetchdata import filegmailevernote2datacenter
    from work.notesaledetails import pinpaifenxido
    # from work.dutyon import duty_timer
    # from work.bankcard import financetimer
    # from etc.zip2onedrive import zipdata2one_timer
    # from func.evernt import get_notestore
    # from func.first import dbpathquandan
    from func.logme import log

# %%
log.debug(f'线程任务\t{__file__}\t启动……')
# pickstat(token, note_store, cnx, '1c0830d9-e42f-4ce7-bf36-ead868a55eca', '订单配货统计图', cum=True)
# desclitedb(cnx)
# swissknife(cnx)
# cnx.close()
# isnoteupdate(token, note_store, '1c0830d9-e42f-4ce7-bf36-ead868a55eca')

# %%
# filegmailevernote2datacenter(60 * 55)
# showorderstat2note(60 * 60 * 1 + 60 * 8)
# log2notetimer(60 * 45)
# weatherstattimer(60 * 60 * 1 + 60 * 5)
# jinchustattimer(60 * 60)
# peoplestattimer(60 * 25)
# planfenxi(60 * 65 * 2)
# duty_timer(60 * 60 * 24)
# financetimer(60 * 60 * 3 + 60 * 33)
# pinpaifenxi_timer(60 * 60 * 4)
pinpaifenxido()
# zipdata2one_timer(60 * 60 * 12 + 60 * 35)

# %%
# print(vars())
log.info(f"倒数第二行")
log.info('线程任务\t{__file__}\t执行完毕！')
