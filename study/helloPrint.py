print('Hello')
print('World')
print('Hello')
print('World')
print('白','晔','峰')
print('白','晔','峰')

def spam(divideBy):
    try:
        return 42 / divideBy
    except ZeroDivisionError:
        print('Eror: Invalid argument')

print(spam(3))
print(spam(43))
print(spam(1))
print(spam(0))
print(spam(9))
