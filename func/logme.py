# encoding:utf-8
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:light
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
# ---

"""
构建日志，格式化日志输出内容，限定每个日志文件大小为1M，在25个日志文件内循环
"""

import logging as lg
import logging.handlers as lgh
import os

import pathmagic
with pathmagic.context():
    from func.first import dirlog, touchfilepath2depth


def mylog():
    """
    日志函数，定义输出文件和格式等内容
    :returns    返回log对象
    """
    logew = lg.getLogger('ewer')
    touchfilepath2depth(dirlog)
    loghandler = lgh.RotatingFileHandler(str(dirlog), encoding='utf-8',
                                         # 此处指定log文件的编码方式，否则可能乱码
                                         maxBytes=1024 * 1024, backupCount=23)
    formats = lg.Formatter('%(asctime)s\t%(filename)s - [%(funcName)s]'
                           '\t%(levelname)s: %(message)s',
                           datefmt='%Y-%m-%d %H:%M:%S')
    loghandler.setFormatter(formats)
    logew.setLevel(lg.DEBUG)
    logew.addHandler(loghandler)

    ################################################################################################
    # 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = lg.StreamHandler()
    console.setLevel(lg.DEBUG)
    formatter = lg.Formatter('%(asctime)s\t%(threadName)s - %(thread)d , '
                             '%(processName)s - %(process)d: '
                             '%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    lg.getLogger('').addHandler(console)
    # logew.addHandler(console)
    ################################################################################################

    return logew


log = mylog()

if __name__ == '__main__':
    cwd = os.getcwd()
    print(cwd)
    log.info('测试func下的log，主要看路径')
