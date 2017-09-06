# 这是一个猜数字游戏
import random
secretNumber = random.randint(1,20)
print('我出一个20以内的整数')

# 最多猜六次
for gussesTaken in range(1,7):
    print('来猜来猜')
    guess = int(input())

    if guess < secretNumber:
        print('猜小了')
    elif guess > secretNumber:
        print('猜大咯')
    else:
        break #这下是猜中了

if guess == secretNumber:
    print('牛！'+str(gussesTaken)+'次你就猜中啦！')
else:
    print('唉。我出的数字是'+str(secretNumber))
