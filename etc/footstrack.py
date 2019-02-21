"""
记录足迹
"""

from pylab import *

import pathmagic
with pathmagic.context():
    from func.configpr import getcfp
    from func.first import dirmainpath
    from func.datatools import readfromtxt, write2txt
    from func.logme import log
    from func.wrapfuncs import timethis
    from func.termuxtools import termux_location
    from etc.getid import getdeviceid


@timethis
def foot2record():
    namestr = 'everloc'
    cfp, cfppath = getcfp(namestr)
    if not cfp.has_section(namestr):
        cfp.add_section(namestr)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))
    if cfp.has_option(namestr, 'device_id'):
        device_id = cfp.get(namestr, 'device_id')
    else:
        # outputdict = termux_telephony_deviceinfo()
        # device_id = outputdict["device_id"].strip()
        device_id = getdeviceid()
        cfp.set(namestr, 'device_id', device_id)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))
        log.info(f'获取device_id:\t{device_id}，并写入ini文件:\t{cfppath}')
    if not cfp.has_section(device_id):
        cfp.add_section(device_id)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))

    txtfilename = str(dirmainpath / 'data' / 'ifttt' /
                      f'location_{device_id}.txt')
    print(txtfilename)
    nowstr = datetime.datetime.now().strftime('%F %T')
    itemread = readfromtxt(txtfilename)
    numlimit = 5    # 显示项目数
    print(itemread[:numlimit])
    tlst = ['datetime', 'latitude', 'longitude', 'altitude', 'accuracy',
            'bearing', 'speed', 'elapsedMs', 'provider']
    locinfo = termux_location()
    print(locinfo)
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
    # global log
    print(f'运行文件\t{__file__}')
    foot2record()
    # showdis()
    print('Done.')
