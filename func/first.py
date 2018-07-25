# encoding:utf-8
"""
功能描述
"""
import os, sys
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())
import func.fordirmainonly as fdmo


def getdirmain():
    fdmodir = fdmo.__file__
    dirmain = os.path.split(fdmodir)[0]
    dirmain = os.path.split(dirmain)[0]

    return dirmain


if __name__ == '__main__':
    print(getdirmain())
    print(sys.path)
