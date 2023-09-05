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
魔法路径
"""

# import os
import sys

# bp = os.path.dirname(os.path.realpath('.')).split(os.sep)
# modpath = os.sep.join(bp + ['src'])
# sys.path.insert(0, modpath)
# sys.path.insert(0,os.sep.join(bp))


class context:
    def __enter__(self):
        sys.path.extend(['..', '.'])

    def __exit__(self, *args):
        pass


if __name__ == '__main__':
    print(f'运行文件\t{__file__}')
    for pp in sys.path:
        print(pp)
    print('Done.完毕。')
