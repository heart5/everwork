# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       jupytext_version: 1.10.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %matplotlib inline

# + [markdown]
"""
    everwork.four_test
    ~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2021 by YOUR_NAME.
    :license: LICENSE_NAME, see LICENSE for more details.
"""

# +
# -*- coding: utf-8 -*-
# -

import os

# + [markdown]
"""
File: four_test.py
Author: heart5
Email: baiyefeng@gmail.com
Github: https://github.com/heart5
Description: everwork.py four_test.py imp4nb.py main.py pathmagic.py
showfuncstruct.py
"""
# -
import pathmagic
with pathmagic.context():
    from func.first import getdirmain
    from func.logme import log


class myobj(object):
    def __init__(self):
        log.info("I'm here in a class whose name is myobj")
        print("I'm in a class.")
        myticket = 'Home'
        print(myticket)
        log.info(myticket)


def mylast(homestr, secondstr, thirdstr):
    """TODO: Docstring for mylast.

    :secondstr: TODO
    :thirdstr: TODO
    :returns: TODO

    """
    myline = "Home is wonderful"


if __name__ == '__main__':
    dm = getdirmain()
    print(f"I am strong", end='\n\n')

    mo = myobj()
    print(mo)

    print(os.path.abspath('.'))
    
    log.debug(mo)
    
    print("Home is warmful.")
