
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
    device_id = termux_telephony_deviceinfo()['device_id']
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
    print(itemread)
    locinfo = termux_location()
    print(locinfo)
    if locinfo == False:
        itemnewr = [f"{nowstr}\t{str(locinfo)}"]
    else:
        itemnewr = [f"{nowstr}\t{locinfo['latitude']}\t{locinfo['latitude']}\t{locinfo['longitude']}\t{locinfo['altitude']}'\t{locinfo['accuracy']}\t{locinfo['accuracy']}\t{locinfo['bearing']}\t{locinfo['speed']}\t{locinfo['elapseMs']}\t{locinfo['provider']}"]
    itemnewr.extend(itemread)
    print(itemnewr)
    write2txt(txtfilename, itemnewr)
    readinifromnote()
    cfpfromnote, cfpfromnotepath = getcfp('everinifromnote')
    namestr = 'ip'
    if cfpfromnote.has_option(namestr, device_id):
        device_name = cfpfromnote.get(namestr, device_id)
    else:
        device_name = device_id
    imglist2note(get_notestore(), [], guid,
                 f'手机_{device_name}_location更新记录',
                 "<br></br>".join(itemnewr))


if __name__ == '__main__':
    # global log
    print(f'运行文件\t{__file__}')
    output = termux_telephony_deviceinfo()
    # print(output)
    device_id = output["device_id"]
    print(device_id)
    output = termux_location()
    print(output)
    foot2record()
    print('Done.')
