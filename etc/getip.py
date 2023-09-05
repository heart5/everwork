#!PREFIX/bin/python
# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %%
# + [markdown] magic_args="[markdown]"
# # 获取IP地址
# -

# %%
"""
获取ip地址
"""
# %% [markdown]
# ## 库引入
# %%
import socket
# %%
def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        sn = s.getsockname()
        print(sn)
        ip = sn[0]
    finally:
        s.close()
    return ip
# %%
if __name__ == '__main__':
    print(get_host_ip())
