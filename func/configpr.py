# encoding:utf-8
"""
输出相应的配置处理器
可用的处理有：everwork, everdatanote, everlife, everzysm, everworkplan
"""
from pathlib import Path
from configparser import ConfigParser
import pathmagic

with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth


def getcfp(cfpfilename: str):
    cfpson = ConfigParser()
    inipathson = Path(getdirmain()) / 'data' / (cfpfilename + '.ini')
    touchfilepath2depth(inipathson)
    cfpson.read(inipathson, encoding='utf-8')

    return cfpson, inipathson


cfp, inifilepath = getcfp('everwork')
cfpdata, inidatanotefilepath = getcfp('everdatanote')
cfplife, inilifepath = getcfp('everlife')
cfpzysm, inizysmpath = getcfp('everzysm')
cfpworkplan, iniworkplanpath = getcfp('everworkplan')


if __name__ == '__main__':
    print(f'开始测试文件\t{__file__}')
    cp, cppath = getcfp('everwork')
    print(cp, cppath)
    print(inizysmpath)
    print('Done.')
