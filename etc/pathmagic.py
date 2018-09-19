# encoding:utf-8
"""
功能描述
"""

# import os
import sys

# bp = os.path.dirname(os.path.realpath('.')).split(os.sep)
# modpath = os.sep.join(bp + ['src'])
# sys.path.insert(0, modpath)
# sys.path.insert(0,os.sep.join(bp))
sys.path.extend(['..', '.'])

if __name__ == '__main__':
    print(f'运行文件\t{__file__}')
    for pp in sys.path:
        print(pp)
    print('Done.完毕。')
