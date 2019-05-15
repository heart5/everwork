import pip
from subprocess import call
from pip._internal.utils.misc import get_installed_distributions, get_installed_version

import pathmagic
with pathmagic.context():
    from func.configpr import getcfp
    from func.first import getdirmain, dirmainpath, touchfilepath2depth
    from func.datatools import readfromtxt, write2txt
    from func.evernttest import token, get_notestore, imglist2note, \
        evernoteapijiayi, makenote, readinifromnote
    from func.logme import log


def upgradeall():
    for dist in get_installed_distributions():
        call(f"pip install --upgrade {dist.project_name}", shell=True)


if __name__ == '__main__':
    # global log
    print(f'运行文件\t{__file__}')
    upgradeall()
    # showdis()
    print('Done.')
