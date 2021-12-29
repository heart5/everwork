# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       jupytext_version: 1.13.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import os
import re
import pandas as pd
from pathlib import Path


# %%
def items2df(fl):
    print(fl)
    content = open(fl, 'r').read()
    rs1 = re.search("\((\w+)\)", fl)
    account = rs1.groups()[0]
    ptn = re.compile("(^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\t(True|False)\t(\S+)\t(\S+)\t", re.M)
    itemlst = re.split(ptn, content)
    itemlst = [im.strip() for im in itemlst if len(im) > 0]
    step = 5
    itemlst4pd1 = [itemlst[i : i + step] for i in range(0, len(itemlst), step)]
    df2 = pd.DataFrame(itemlst4pd1, columns=['time', 'send', 'sender', 'type', 'content'])
    df2['time'] = pd.to_datetime(df2['time'])
    df2['send'] = df2['send'].apply(lambda x : True if x == 'True' else False)

    dfout = df2.drop_duplicates().sort_values('time', ascending=False)
    
    return account, dfout


# %%
wcdatapath = Path("../data/webchat")
resultdflst = list()
fllst = [f for f in os.listdir(wcdatapath) if f.startswith("chatitems")]
for fl in fllst[::-1]:
        resultdflst.append(items2df(wcdatapath / fl))

# %%
names = [t[0] for t in resultdflst]
names

# %%
set(names)

# %%
dftmp[dftmp.sender == '徐晓锋']

# %%
dftmp[~dftmp.sender.str.contains("群")]

# %%
