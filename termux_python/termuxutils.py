# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import pathmagic
with pathmagic.context():
    from func.first import touchfilepath2depth, getdirmain
    from termux_python.termux import battery_status
    
battery_status()
# -


