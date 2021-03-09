# encoding:utf-8
'''
测试文件，啥都试试
'''
# import func.first as first
from func.first import getdirmain

class myobj(object):
    def __init__(self):
        print("I'm in a class.")


if __name__ == '__main__':
    dm = getdirmain()
    print(f"I am strong", end='\n\n')
    print(dm)

    mo = myobj()
    print(mo)

    print("Home is warmful.")
