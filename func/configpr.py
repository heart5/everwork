# encoding:utf-8
"""
配置处理器相关的功能函数
"""

import re
from pathlib import Path
from configparser import ConfigParser, DuplicateSectionError
import pathmagic

with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.logme import log
    from func.sysfunc import not_IPython


def fixinifile(inipath, name):
#     print(inipath, name)
    with open(inipath, 'r') as f:
        fcontent = f.read()
        with open(str(inipath) + '.bak', 'w') as writer:
            writer.write(fcontent)
    ftn = re.compile(r"\[\w+\]")
    sectionlst = re.findall(ftn, fcontent)
    optionlst = re.split(ftn, fcontent)
    resultdict = dict()
    for i in range(len(sectionlst)):
        sname = sectionlst[i]
        if sname in resultdict.keys():
            thislen = len(resultdict[sname])
            thatlen = len(optionlst[i+1])
            log.critical(f"{sname}\t{thislen}\t{thatlen}")
            if thislen > thatlen:
                continue
        resultdict.update({sname:optionlst[i+1]})
    rstlst = [x for y in list(zip(resultdict.keys(), resultdict.values())) for x in y]
    correctcontent = ''.join(rstlst)
    with open(str(inipath), 'w') as writer:
        writer.write(correctcontent)
    return correctcontent


def removesection(cfpfilename: str, sectionname: str):
    """
    删除指定section，默认清除其下面的所有option
    """
    cfpin, cfpinpath = getcfp(cfpfilename)
    if cfpin.has_section(sectionname):
        cfpin.remove_section(sectionname)
        cfpin.write(open(cfpinpath, 'w', encoding='utf-8'))
        log.critical(f"成功清除{sectionname}下的所有option！！！")


def getcfp(cfpfilename: str):
    cfpson = ConfigParser()
    inipathson = Path(getdirmain()) / 'data' / (cfpfilename + '.ini')
    touchfilepath2depth(inipathson)
    try:
        cfpson.read(inipathson, encoding='utf-8')
    except DuplicateSectionError as dse:
        log.critical(f"ini文件《{inipathson}》中存在重复的section名称，备份文件并试图删除项目数量较少的section以修复文件……{dse}")
        ptn = re.compile("section \'(\w+)\'")
        sname = re.search(ptn, str(dse)).group(1)
        fixinifile(inipathson, '[' + sname + ']')
        try:
            cfpson.read(inipathson, encoding='utf-8')
        except Exception as e:
            log.critical(f"修复配置文件时失败！！！{e}")
            return

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
    if not_IPython():
        print(f'开始测试文件\t{__file__}')
#     cp, cppath = getcfp('everwork')
#     print(cp, cppath)
    cfpapiname = 'everapi'
    inipathson = Path(getdirmain()) / 'data' / (cfpapiname + '.ini')
    name = '[notestore]'
#     cp, cppath = getcfp(cfpapiname)
#     removesection(cfpapiname, nssectionname)
    ict = fixinifile(inipathson, name)
    if not_IPython():
        print('Done.')
