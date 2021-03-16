# -*- coding: utf-8 -*-
"""
    everwork.four_test
    ~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2021 by YOUR_NAME.
    :license: LICENSE_NAME, see LICENSE for more details.
"""

# -*- coding: utf-8 -*-


"""
File: four_test.py
Author: heart5
Email: baiyefeng@gmail.com
Github: https://github.com/heart5
Description: everwork.py four_test.py imp4nb.py main.py pathmagic.py
showfuncstruct.py
"""
# TODO:format time string  <15-03-21, heart5> 2021-03-15 05:54 #

# Fold description {{{1 #
# 1}}} #

# Fold description {{{ #
# }}} Fold description #

###############################################################################
#                                   content                                   #
###############################################################################

#############
#  content  #
#############



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


def mytest(arg1):
    """TODO: Docstring for function.

    :arg1: TODO
    :returns: TODO

    """
    pass

def otherfunc(arg1):
    """TODO: Docstring for otherfunc.

    :arg1: TODO
    :returns: TODO

    """
    pass

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

    log.debug(mo)
    print("Home is warmful.")
