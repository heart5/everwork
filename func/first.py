# encoding:utf-8
"""
功能描述
"""
import os
import sys
from pathlib import Path
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())
import func.fordirmainonly as fdmo


# from func.logme import log


def touchfilepath2depth(filepath: Path):
    if not os.path.exists(os.path.split(str(filepath))[0]):
        os.makedirs(os.path.split(str(filepath))[0])
        print(f'目录《{os.path.split(str(filepath))[0]}》不存在，构建之。')
    # else:
    #     print(f'目录《{os.path.split(str(filepath))[0]}》已现实存在，不需要重新构建。')
    # if not os.path.exists(str(filepath)):
    #     fp = open(str(filepath), 'w', encoding='utf-8')
    #     fp.close()


def getdirmain():
    fdmodir = fdmo.__file__
    dirmainin = os.path.split(fdmodir)[0]
    dirmainin = os.path.split(dirmainin)[0]

    return Path(dirmainin)


dirmainpath = getdirmain()
dirmain = str(getdirmain())
dirlog = str(getdirmain() / 'log' / 'everwork.log')
dbpathworkplan = str(getdirmain() / 'data' / 'workplan.db')
dbpathquandan = str(getdirmain() / 'data' / 'quandan.db')
dbpathdingdanmingxi = str(getdirmain() / 'data' / 'dingdanmingxi.db')
ywananchor = 50000  # 纵轴标识万化锚点


path2include = ['etc', 'func', 'work', 'life', 'study']
for p2i in path2include:
    sys.path.append(str(dirmainpath / p2i))
# for dr in sys.path:
#     print(dr)

if __name__ == '__main__':
    print(f'开始测试文件\t{__file__}')
    print(getdirmain())
    for dr in sys.path:
        print(dr)
    print('Done.')
