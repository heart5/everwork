# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     notebook_metadata_filter: -jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
"""
    everwork.four_test
    ~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2021 by YOUR_NAME.
    :license: LICENSE_NAME, see LICENSE for more details.
"""

# %% [markdown]
# -*- coding: utf-8 -*-

# %%
"""
File: four_test.py
Author: heart5
Email: baiyefeng@gmail.com
Github: https://github.com/heart5
Description: everwork.py four_test.py imp4nb.py main.py pathmagic.py
showfuncstruct.py
"""

# %%
# %matplotlib inline

# %%
import os

# %%
import pathmagic
with pathmagic.context():
    from func.first import getdirmain
    from func.logme import log


# %%
class myobj(object):
    def __init__(self):
        log.info("I'm here in a class whose name is myobj")
        print("I'm in a class.")
        myticket = 'Home'
        print(myticket)
        log.info(myticket)


# %%
def mylast(homestr, secondstr, thirdstr):
    """TODO: Docstring for mylast.

    :secondstr: TODO
    :thirdstr: TODO
    :returns: TODO

    """
    myline = "Home is wonderful"


# %%
if __name__ == '__main__':
    dm = getdirmain()
    print(f"I am strong", end='\n\n')

    mo = myobj()
    mo.__sizeof__()
    print(mo)

    print(os.path.abspath('.'))
    log.debug(mo)
    log.critical(mo)

    print("Home is warmful.")

# %%
