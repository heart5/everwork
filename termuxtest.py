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

# %%
import pathmagic
import sys
sys.path.append('termux_python')
with pathmagic.context():
    import termux_python.termux as tm
    from func.wrapfuncs import lp_wrapper


# %%
@lp_wrapper()
def showmsgfromtermux():
    # print('开工啊')
    print(sys.path)
    print(tm.battery_status())
    print(tm.camera_info())
    # tm.termux_sms_list()


# %%
showmsgfromtermux()
