# encoding:utf-8
"""
功能描述
"""
import os, sys
from pathlib import Path
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())
import func.fordirmainonly as fdmo


def touchfilepath2depth(filepath: Path):
    if not os.path.exists(os.path.split(str(filepath))[0]):
        os.makedirs(os.path.split(str(filepath))[0])
    if not os.path.exists(str(filepath)):
        fp = open(str(filepath), 'w', encoding='utf-8')
        fp.close()


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
path2include = ['etc', 'func', 'work', 'life', 'study']
for p2i in path2include:
    sys.path.append(str(dirmainpath / p2i))
# for dr in sys.path:
#     print(dr)

YWanAnchor = 50000  # 纵轴标识万化锚点

if __name__ == '__main__':
    print(f'开始测试文件\t{__file__}')
    print(getdirmain())
    for dr in sys.path:
        print(dr)
    print('Done.')
