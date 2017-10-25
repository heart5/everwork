import pandas as pd, sqlite3 as lite, matplotlib.pyplot as plt, numpy as np,calendar as cal, random as rd, os
import re as re
from pylab import *

# plot中显示中文
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

if not os.path.exists('data'):
    os.mkdir('data')

if not os.path.exists('img'):
    os.mkdir('img')