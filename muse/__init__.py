# encoding:utf-8
"""
功能描述
"""
import pathmagic

with pathmagic.context():
    from func.logme import log

if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')

    log.info(f'文件{__file__}运行结束')
