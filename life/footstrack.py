# -*- coding: utf-8 -*-
"""
记录足迹
"""

from pylab import *

import pathmagic
with pathmagic.context():
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.first import dirmainpath
    from func.datatools import readfromtxt, write2txt
    from func.logme import log
    from func.wrapfuncs import timethis
    from func.termuxtools import termux_location, battery_status
    from etc.getid import getdeviceid
    from func.sysfunc import set_timeout, after_timeout, not_IPython


@set_timeout(240, after_timeout)
@timethis
def foot2record():
    """
    记录位置数据（经纬度等）
    """
    namestr = 'everloc'

    if (device_id := getcfpoptionvalue(namestr, namestr, 'device_id')):
        device_id = str(device_id)
    else:
        device_id = getdeviceid()
        setcfpoptionvalue(namestr, namestr, 'device_id', device_id)
    
    txtfilename = str(dirmainpath / 'data' / 'ifttt' /
                      f'location_{device_id}.txt')
    print(txtfilename)
    itemread = readfromtxt(txtfilename)
    numlimit = 5    # 显示项目数
    print(itemread[:numlimit])
    tlst = ['datetime', 'latitude', 'longitude', 'altitude', 'accuracy',
            'bearing', 'speed', 'elapsedMs', 'provider']
    locinfo = termux_location()
    print(locinfo)
    nowstr = datetime.datetime.now().strftime('%F %T')
    if locinfo == False:
        itemnewr = [f"{nowstr}\t{str(locinfo)}"]
    else:
        itemnewr = [f"{nowstr}\t{locinfo[tlst[1]]}\t{locinfo[tlst[2]]}"
                    f"\t{locinfo[tlst[3]]}\t{locinfo[tlst[4]]}"
                    f"\t{locinfo[tlst[5]]}\t{locinfo[tlst[6]]}"
                    f"\t{locinfo[tlst[7]]}\t{locinfo[tlst[8]]}"]
    itemnewr.extend(itemread)
    print(itemnewr[:numlimit])
    write2txt(txtfilename, itemnewr)


if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}……')    
    if (bsdict := battery_status())['percentage'] >= 20:
        foot2record()
    else:
        log.warning("手机电量低于20%，跳过GPS定位轮询")
    if not_IPython():
        print(f"完成文件{__file__}\t的运行")
