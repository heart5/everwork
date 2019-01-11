
"""
记录足迹
"""

import os
# import urllib2
import re
import socket
import subprocess
import datetime
from threading import Timer

import pathmagic
with pathmagic.context():
    from func.configpr import getcfp
    from func.first import getdirmain, dirmainpath
    from func.datatools import readfromtxt, write2txt
    from func.evernt import token, get_notestore, imglist2note, evernoteapijiayi, makenote, readinifromnote
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.termuxtools import termux_telephony_deviceinfo, termux_telephony_cellinfo, termux_location


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
        outputdict = termux_telephony_deviceinfo()
        # print(outputdict)
        device_id = outputdict["device_id"].strip()
        cfp.set(namestr, 'device_id', device_id)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))
        log.info(f'获取device_id:\t{device_id}，并写入ini文件:\t{cfppath}')
    if not cfp.has_section(device_id):
        cfp.add_section(device_id)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))
    if cfp.has_option(device_id, 'guid'):
        guid = cfp.get(device_id, 'guid')
    else:
        global token
        note_store = get_notestore()
        parentnotebook = note_store.getNotebook(
            '4524187f-c131-4d7d-b6cc-a1af20474a7f')
        evernoteapijiayi()
        # note = ttypes.Note()
        title = f'手机_{device_id}_location更新记录'
        # note.title = "hengchu"
        print(title)
        note = makenote(token, note_store, title, notebody='',
                        parentnotebook=parentnotebook)
        guid = note.guid
        cfp.set(device_id, 'guid', guid)
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
        itemnewr = [f"{nowstr}\t{locinfo[tlst[1]]}\t{locinfo[tlst[2]]}\t{locinfo[tlst[3]]}'\t{locinfo[tlst[4]]}\t{locinfo[tlst[5]]}\t{locinfo[tlst[6]]}\t{locinfo[tlst[7]]}\t{locinfo[tlst[8]]}"]
    itemnewr.extend(itemread)
    print(itemnewr[:numlimit])
    write2txt(txtfilename, itemnewr)
    readinifromnote()
    cfpfromnote, cfpfromnotepath = getcfp('everinifromnote')
    namestr = 'ip'
    if cfpfromnote.has_option(namestr, device_id):
        device_name = cfpfromnote.get(namestr, device_id)
    else:
        device_name = device_id
    tlstitem = ["\t".join(tlst)]
    tlstitem.extend(itemnewr)
    imglist2note(get_notestore(), [], guid,
                 f'手机_{device_name}_location更新记录',
                 "<br></br>".join(tlstitem))


if __name__ == '__main__':
    # global log
    print(f'运行文件\t{__file__}')
    foot2record()
    print('Done.')
