# encoding:utf-8
"""
sqlite数据库相关应用函数
"""

import sqlite3 as lite
import os
import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import dbpathquandan, dbpathworkplan, dbpathdingdanmingxi
    from func.wrapfuncs import timethis


def get_filesize(filepath):
    fsize = os.path.getsize(filepath)
    fsize = fsize / float(1024 * 1024)
    return round(fsize, 2)


def istableindb(tablenin: str, dbname: str):
    try:
        conn = lite.connect(dbname)
        cursor = conn.cursor()
        cursor.execute("select * from sqlite_master where type='table'")
        table = cursor.fetchall()
        # print(table)
        chali = [x for item in table for x in item[1:3]]
        # print(chali)
    except Exception as eee:
        log.critical(f"查询数据表是否存在时出错。{eee}")
    finally:
        conn.close()

    return tablenin in chali


def ifnotcreate(tablen: str, createsql: str, dbn: str):
    """
    如果没有相应数据表就创建一个
    :param tablen:
    :param dbn:
    :return:
    """

    if istableindb(tablen, dbn):
        return

    try:
        conn = lite.connect(dbn)
        cursor = conn.cursor()

        cursor.execute(createsql)
        conn.commit()
        log.info(f"数据表：\t{tablen} 被创建成功。\t{createsql}")

    except Exception as eee:
        log.critical(f"操作数据库时出现错误。{dbn}\t{eee}")
    finally:
        if conn:
            conn.close()


@timethis
def compact_sqlite3_db(dbpath):
    sizebefore = get_filesize(dbpath)
    conn = lite.connect(dbpath)
    conn.execute("VACUUM")
    conn.close()
    log.info(f"{dbpath}数据库压缩前大小为{sizebefore}MB，压缩之后为{get_filesize(dbpath)}MB。")


if __name__ == "__main__":
    log.info(f"运行文件\t{__file__}")
    # print(get_filesize(dbpathquandan))
    compact_sqlite3_db(dbpathquandan)
    compact_sqlite3_db(dbpathworkplan)
    compact_sqlite3_db(dbpathdingdanmingxi)

    print("Done.完毕。")
