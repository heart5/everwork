# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import numpy as np
import matplotlib.pyplot as plt
from pylab import *

# Fixing random state for reproducibility
np.random.seed(19680801)

mu, sigma = 100, 15
x = mu + sigma * np.random.randn(10000)

# the histogram of the data
n, bins, patches = plt.hist(x, 50, density=1, facecolor='g', alpha=0.75)


plt.xlabel('Smarts')
plt.ylabel('Probability')
plt.title('Histogram of IQ')
plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
plt.axis([40, 160, 0, 0.03])
plt.grid(True)
plt.show()

# +
import pathmagic
with pathmagic.context():
    from func.first import touchfilepath2depth, getdirmain, dirmainpath
    from work.zymessage import searchcustomer, searchqiankuan, searchpinxiang
    
print(getdirmain())
rstfile, rststr = searchqiankuan(['兴客隆', '汉阳'])
print(rststr)
linelist=rststr.split('\n')
print(linelist)
figure(figsize=(8,6), dpi=150)
for i in range(len(linelist)):
    plt.text(0.02, 0.9-i*0.07,linelist[i], fontsize=8, bbox=dict(facecolor='red', alpha=0.1))
plt.show()
# -


