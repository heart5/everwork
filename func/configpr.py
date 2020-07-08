# encoding:utf-8
"""
输出相应的配置处理器
可用的处理有：everwork, everdatanote, everlife, everzysm, everworkplan
"""
import re
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


def setcfpoptionvalue(cfpfilename: str, sectionname: str, optionname: str, optionvalue):
    cfpin, cfpinpath = getcfp(cfpfilename)
    if not cfpin.has_section(sectionname):
        cfpin.add_section(sectionname)
        cfpin.write(open(cfpinpath, 'w', encoding='utf-8'))
    cfpin.set(sectionname, optionname, optionvalue)
    cfpin.write(open(cfpinpath, 'w', encoding='utf-8'))


def getcfpoptionvalue(cfpfilename: str, sectionname: str, optionname: str):
    cfpin, cfpinpath = getcfp(cfpfilename)
    if not cfpin.has_section(sectionname):
        print(f"seticon {sectionname} is not exists. Then creating it now ...")
        cfpin.add_section(sectionname)
        cfpin.write(open(cfpinpath, 'w', encoding='utf-8'))
        return
    if not cfpin.has_option(sectionname, optionname):
        print(f"option {optionname} is not exists.")
        return

    targetvalue = str(cfpin.get(sectionname, optionname))

    # 处理布尔值
    if targetvalue.strip().lower() == 'true':
        return True

    if targetvalue.strip().lower() == 'false':
        return False

    # 处理整数
    ptn = re.compile(r"^[+-]?[0-9]+$")
    result = ptn.match(targetvalue)
    if result:
        targetvalue = int(result.group())
        return targetvalue
    
    # 处理小数
    ptn = re.compile(r"^[+-]?[0-9]+\.[0-9]+$")
    result = ptn.match(targetvalue)
    if result:
        targetvalue = float(result.group())
        return targetvalue
    # if isinstance(targetvalue, int):
        # targetvalue = int(targetvalue)
    # elif isinstance(targetvalue, float):
        # targetvalue = float(targetvalue)

    return targetvalue


# cfp, inifilepath = getcfp('everwork')
# cfpdata, inidatanotefilepath = getcfp('everdatanote')
# cfplife, inilifepath = getcfp('everlife')
# cfpzysm, inizysmpath = getcfp('everzysm')
# cfpworkplan, iniworkplanpath = getcfp('everworkplan')


if __name__ == '__main__':
    print(f'开始测试文件\t{__file__}')
    cp, cppath = getcfp('everwork')
    print(cp, cppath)
    print('Done.')
