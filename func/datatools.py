# encoding:utf-8
"""
txt数据文件操作函数
"""

import os
import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import dbpathquandan, dbpathworkplan, dbpathdingdanmingxi
    from func.wrapfuncs import timethis


def get_filesize(filepath):
    fsize = os.path.getsize(filepath)
    fsize = fsize/float(1024*1024)
    return round(fsize, 2)


@timethis
def compact_sqlite3_db(dbpath):
    sizebefore = get_filesize(dbpath)
    conn = lite.connect(dbpath)
    conn.execute("VACUUM")
    conn.close()
    log.info(f'{dbpath}数据库压缩前大小为{sizebefore}MB，压缩之后为{get_filesize(dbpath)}MB。')


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    # print(get_filesize(dbpathquandan))
    compact_sqlite3_db(dbpathquandan)
    compact_sqlite3_db(dbpathworkplan)
    compact_sqlite3_db(dbpathdingdanmingxi)

    print('Done.完毕。')
