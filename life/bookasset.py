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
# # Kindle书籍信息管理

# %%
from imp4nb import *

# %%
cnx = lite.connect('data\\book_asset.db')

desclitedb(cnx)

df = pd.read_sql_query('select * from Asset',cnx)
# descdb(df)

dfbook = pd.read_sql_query('select * from Book',cnx)
descdb(dfbook)

cnx.close()

# %%

# %%
