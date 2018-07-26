# encoding:utf-8
"""
功能描述
"""
import os, sys
from pathlib import Path
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())
import func.fordirmainonly as fdmo


def getdirmain():
    fdmodir = fdmo.__file__
    dirmain = os.path.split(fdmodir)[0]
    dirmain = os.path.split(dirmain)[0]

    return Path(dirmain)


dirmainpath = getdirmain()
dirmain = str(getdirmain())
dirlog = str(getdirmain() / 'log' / 'everwork.log')
dbpathworkplan = str(getdirmain() / 'data' / 'workplan.db')
dbpathquandan = str(getdirmain() / 'data' / 'quandan.db')

YWanAnchor = 50000  # 纵轴标识万化锚点

if __name__ == '__main__':
    print(getdirmain())
    for dr in sys.path:
        print(dr)
