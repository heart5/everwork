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
模块说明
"""
import pandas as pd
import numpy as np


# %%
def dfdsall():
    sere = pd.Series([1, 2, 3, 'heart5'])
    pass


# %%
def ninenine():
    print('\n'.join([''.join(['%s*%s=%-2s ' % (y, x, x * y) for y in range(1, x + 1)]) for x in range(1, 10)]))


# %%
if __name__ == '__main__':
    print(f'开始测试文件\t{__file__}')
    ninenine()
    dfdsall()
    print('Done.测试完成。')
