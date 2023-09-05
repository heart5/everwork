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
import termux
# from termux import camera_info

# %%
# print(termux.battery_status())
# print(termux.camera_info())
print(termux.termux_location())
print(termux.termux_sms_list())
