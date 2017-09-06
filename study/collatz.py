#
# encoding:utf-8
# 这是一个数学中的Collatz序列。
# 任何整数，如果是偶数则除以2，如果是奇数则乘以3然后再加1，
# 如此迭代，最终总会得到1
import random

def collatz(number):
    while True:
        print(int(number))
        if number == 1:
            break
        if number % 2 == 0:
            number = number / 2
        else:
            number = number * 3 + 1


while True:
    print('请输入一个合格的整数值，或者输入exit退出')
    str_input = input()
    if str_input == 'exit':
        break
    try:
        num = int(str_input)
    except ValueError, NameError:
        num = random.randint(1,2000)
        print('请输入一个合格的整数值，或者输入exit退出\n为方便演示，自动帮您随机设定为一个2000之内的整数，这次是'+str(num)+'：')
    collatz(num)

