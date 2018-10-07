# encoding:utf-8
# ---
# jupyter:
#   jupytext_format_version: '1.3'
#   jupytext_formats: py:light
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
# ---

"""
功能描述
"""
import func.first as first
from func.evernt import *
from func.first import getdirmain

if __name__ == '__main__':
    dm = getdirmain()
    print(dm)
    get_notestore()
