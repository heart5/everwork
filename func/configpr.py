# encoding:utf-8
"""
输出相应的配置处理器
可用的处理有：everwork, everdatanote, everlife, everzysm, everworkplan
"""
import os
from configparser import ConfigParser
from func.first import getdirmain


def getcfp(cfpfilename: str):
    pass
    cfp = ConfigParser()
    inipath = os.path.join(getdirmain(), 'data', cfpfilename + '.ini')
    if not os.path.exists(inipath):
        open(inipath, 'w', encoding='utf-8')
    cfp.read(inipath, encoding='utf-8')

    return cfp, inipath


if __name__ == '__main__':
    cp = getcfp('everwork')
    print(cp)
    # cfp = ConfigParser()
    # inifilepath = os.path.join('data', 'everwork.ini')
    # cfp.read(inifilepath, encoding='utf-8')
    # cfpdata = ConfigParser()
    # inidatanotefilepath = os.path.join('data', 'everdatanote.ini')
    # cfpdata.read(inidatanotefilepath, encoding='utf-8')
    # cfplife = ConfigParser()
    # inilifepath = os.path.join('data', 'everlife.ini')
    # cfplife.read(inilifepath, encoding='utf-8')
    # cfpzysm = ConfigParser()
    # inizysmpath = os.path.join('data', 'everzysm.ini')
    # cfpzysm.read(inizysmpath, encoding='utf-8')
    # cfpworkplan = ConfigParser()
    # iniworkplanpath = os.path.join('data', 'everworkplan.ini')
    # cfpworkplan.read(iniworkplanpath, encoding='utf-8')
    pass
