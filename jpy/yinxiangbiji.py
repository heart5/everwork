# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
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

# # 印象笔记

# +
import pathmagic
with pathmagic.context():
    from func.evernttest import findnotebookfromevernote, findnotefromnotebook
    from func.configpr import getcfpoptionvalue
    from etc.getid import getdeviceid
    
nbdf = findnotebookfromevernote()
ipnbguid = getcfpoptionvalue('everip', getdeviceid(), 'ipnbguid')
ipnbguid
# -


