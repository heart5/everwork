# encoding:utf-8
"""
txt数据文件操作函数
部分文件功能函数
"""

import os
import sqlite3 as lite
import binascii

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import dbpathquandan, dbpathworkplan, dbpathdingdanmingxi, touchfilepath2depth
    # from func.wrapfuncs import timethis

# print(f"{__file__} is loading now...")


def str2hex(string):
    """
    转换字符串为hex字符串（大写）
    """
    str_bin = string.encode('utf-8')

    return binascii.hexlify(str_bin).decode('utf-8').upper()


def getfilepathnameext(tfile):
    tfile = os.path.abspath(tfile)
    (filepath, tmpfilename) = os.path.split(tfile)
    (shotename, fileext) = os.path.splitext(tmpfilename)

    return filepath, tmpfilename, shotename, fileext


def write2txt(weathertxtfilename, inputitemlist):
    # print(inputitemlist)
    fileobject = open(weathertxtfilename, 'w', encoding='utf-8')
    # fileobject = open(weathertxtfilename, 'w', encoding='ISO8859-1')
    if inputitemlist is not None:
        for item in inputitemlist:
            # print(item)
            fileobject.write(str(item) + '\n')
    fileobject.close()


def readfromtxt(weathertxtfilename):
    if not os.path.exists(weathertxtfilename):
        touchfilepath2depth(weathertxtfilename)
        write2txt(weathertxtfilename, None)
    items = []
    # with open(weathertxtfilename, 'r', encoding='ISO8859-1') as ftxt:
    with open(weathertxtfilename, 'r', encoding='utf-8') as ftxt:
        items = [line.strip() for line in ftxt]  # strip()，去除行首行尾的空格
        # for line in ftxt:
            # try:
                # items.append(line.strip())
            # except UnicodeDecodeError as ude:
                # log.error(f"{line}\n{ude}")
    return items


def get_filesize(filepath):
    fsize = os.path.getsize(filepath)
    fsize = fsize/float(1024*1024)
    return round(fsize, 2)


# @timethis
def compact_sqlite3_db(dbpath):
    sizebefore = get_filesize(dbpath)
    conn = lite.connect(dbpath)
    conn.execute("VACUUM")
    conn.close()
    log.info(f'{dbpath}数据库压缩前大小为{sizebefore}MB，压缩之后为{get_filesize(dbpath)}MB。')


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    # print(get_filesize(dbpathquandan))
    # compact_sqlite3_db(dbpathquandan)
    # compact_sqlite3_db(dbpathworkplan)
    # compact_sqlite3_db(dbpathdingdanmingxi)
    (*aaa, ext) = getfilepathnameext(__file__)
    print(ext)

    outputstr = str2hex('天富 1  29')
    print(outputstr)
    log.info(f"文件\t{__file__}\t运行结束。")
