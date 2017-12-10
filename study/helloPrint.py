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

import numpy as np
import matplotlib.pyplot as plt

# example data
x = np.arange(0.1, 4, 0.5)
y = np.exp(-x)

fig, ax = plt.subplots()
ax.errorbar(x, y, xerr=0.2, yerr=0.4)
plt.show()

print(plt.colors())
