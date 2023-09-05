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
#
# enconding:utf-8
#
# 各种函数、功能测试
#

# %%
from imp4nb import *

# %%
cnx = lite.connect(dbpathquandan)

# %%
desclitedb(cnx)

# %%
cnx.close()
