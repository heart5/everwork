# encoding:utf-8
"""
输出相应的配置处理器
可用的处理有：everwork, everdatanote, everlife, everzysm, everworkplan
"""
import os
from configparser import ConfigParser
from func.first import getdirmain
from pathlib import Path

def getcfp(cfpfilename: str):
    pass
    cfp = ConfigParser()
    inipath = Path(getdirmain()) / 'data' / (cfpfilename + '.ini')
    if not os.path.exists(inipath):
        open(inipath, 'w', encoding='utf-8')
    cfp.read(inipath, encoding='utf-8')

    return cfp, inipath


cfp, inifilepath = getcfp('everwork')
cfpdata, inidatanotefilepath = getcfp('everdatanote')
cfplife, inilifepath = getcfp('everlife')
cfpzysm, inizysmpath = getcfp('everzysm')
cfpworkplan, iniworkplanpath = getcfp('everworkplan')


if __name__ == '__main__':
    cp, cppath = getcfp('everwork')
    print(cp, cppath)
