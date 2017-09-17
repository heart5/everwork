#
#encoding:utf-8
# Python金融大数据分析，第五章：数据可视化

import time, calendar, re
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d import Axes3D
from pylab import *


# plot中显示中文
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

def func(x):
    return 0.5* np.exp(x) +1

def arrayplot():
    np.random.seed(1000)
    y = np.random.standard_normal(20) #生成 20 个 标准 正态分布（ 伪） 随机数， 保存 在 一个 NumPy ndarray 中

    print (y)
    print (range(len(y))) #[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

    plt.plot(range(len(y)), y)

    print(y.cumsum()) #cumsum()，比如一个列表是这样[1,2,3,4,5]，返回是这样[1,3,6,10,15]

    plt.figure(figsize = (7,4))
    plt.plot(y.cumsum(), 'b', lw=1.5)
    plt.plot(y.cumsum(), 'r3')
    plt.grid(True)
    plt.axis('tight')
    plt.xlim(-1, 20)
    plt.ylim(min(y.cumsum())-1, max(y.cumsum())+1)
    plt.xlabel('index')
    plt.ylabel('value')
    plt.title(u'示例样图')

    plt.show()

def narrayplot():
    np.random.seed(2000)
    y = np.random.standard_normal((20,2)).cumsum(axis=0)
    # print y[:, 0] #二维数组第一列
    # print y[1] #数组第二行
    # print y

    #两列值曲线
    # y[:,0] = y[:,0] * 100 #测试不同数量级纵轴图片
    plt.figure(figsize = (7,4))
    plt.plot(y[:, 0], 'b', lw=1.5, label=u'第一')
    plt.plot(y[:, 1], 'm', lw=1.5, label=u'第二')
    plt.plot(y, 'r3')
    plt.legend(loc=0)
    plt.grid(True)
    plt.axis('tight')
    plt.xlabel('index')
    plt.ylabel('value')
    plt.title(u'示例样图')
    plt.close()

    # 双纵轴
    fig, ax1 = plt.subplots()
    plt.plot(y[:, 0], 'b', lw=1.5, label=u'第一')
    plt.plot(y[:,0], 'ro')
    plt.grid(True)
    plt.legend(loc=8)
    plt.axis('tight')
    plt.xlabel('index')
    plt.ylabel(u'第一数据')
    plt.title(u'示例样图')
    ax2 = ax1.twinx()
    plt.plot(y[:,1], 'g', lw=1.5, label=u'第二')
    plt.plot(y[:, 1], 'ro')
    plt.legend(loc=0)
    plt.ylabel(u'第二数据')
    plt.close()

    # 纵排三图
    plt.figure(figsize=(7, 9))
    plt.subplot(311)
    plt.plot(y[:, 0], 'b', lw=1.5, label=u'第一')
    plt.plot(y[:,0], 'ro')
    plt.grid(True)
    plt.legend(loc=0)
    plt.axis('tight')
    plt.xlabel('index')
    plt.ylabel(u'第一数据')
    plt.title(u'示例样图')
    plt.subplot(312)
    plt.plot(y[:,1], 'g', lw=1.5, label=u'第二')
    plt.plot(y[:, 1], 'ro')
    plt.legend(loc=0)
    plt.ylabel(u'第二数据')
    plt.subplot(313)
    plt.bar(np.arange(len(y)), y[:, 1], width=0.5, color='g', label=u'第三')
    plt.grid(True)
    plt.legend(loc=0)
    plt.axis('tight')
    plt.xlabel('index')
    plt.title(u'第三数据集合')
    plt.close()

    # 散点图
    y = np.random.standard_normal((1000, 2))
    plt.figure(figsize=(7, 5))
    plt.plot(y[:, 0], y[:, 1], 'ro')
    plt.grid(True)
    plt.xlabel(u'第一')
    plt.ylabel(u'第二')
    plt.title(u'散点图')
    plt.close()

    # 用scatter做散点图
    plt.figure(figsize=(7, 5))
    plt.scatter(y[:, 0], y[:, 1], marker='o')
    plt.grid(True)
    plt.xlabel(u'第一')
    plt.ylabel(u'第二')
    plt.title(u'另一种散点图')
    plt.close()

    # 用scatter做三维散点图
    c = np.random.randint(0, 10, len(y))
    plt.figure(figsize=(7, 5))
    plt.scatter(y[:, 0], y[:, 1], c=c, marker='o')
    plt.colorbar()
    plt.grid(True)
    plt.xlabel(u'第一')
    plt.ylabel(u'第二')
    plt.title(u'三维散点图')
    plt.close()

    # 做直方图
    plt.figure(figsize=(7, 4))
    plt.hist(y, label=[u'第一', u'第二'], color=['r', 'b'], stacked=True, bins=10)
    plt.grid(True)
    plt.legend(loc=0)
    plt.xlabel(u'值')
    plt.ylabel(u'频次')
    plt.title(u'频次直方图')
    plt.close()

    # 做箱形图
    fig, ax = plt.subplots(figsize=(7, 4))
    plt.boxplot(y)
    plt.grid(True)
    plt.setp(ax, xticklabels=[u'第一', u'第二'])
    plt.xlabel(u'数据集')
    plt.ylabel(u'值')
    plt.title(u'箱形图')
    plt.close()

    # 指数函数、积分面积和LaTeX标签
    a, b = 0.5, 1.5
    x = np.linspace(0, 2)
    y = func(x)
    # print x
    # print y
    fig, ax = plt.subplots(figsize=(7, 5))
    plt.plot(x, y, 'b', linewidth=2)
    plt.ylim(ymin=0)
    Ix = np.linspace(a, b)
    Iy = func(Ix)
    verts = [(a, 0)] + list(zip(Ix, Iy)) +[(b, 0)]
    poly = Polygon(verts, facecolor='0.7', edgecolor='0.5')
    ax.add_patch(poly)
    plt.text(0.5*(a+b), 1, r"$\int_a^b f(x)\mathrm{d}x$", horizontalalignment='center', fontsize=20)
    plt.figtext(0.9, 0.075, '$x$')
    plt.figtext(0.075, 0.9, '$f(x)$')
    ax.set_xticks((a, b))
    ax.set_xticklabels(('$a$', '$b$'))
    ax.set_yticks([func(a), func(b)])
    ax.set_yticklabels(('$f(a)$', '$f(b)$'))
    plt.grid(True)
    plt.close()

    # 3D绘图
    strike = np.linspace(50, 150, 24)
    ttm = np.linspace(0.5, 2.5, 24)
    strike, ttm = np.meshgrid(strike, ttm)
    iv = (strike - 100)** 2/(100* strike)/ ttm
    fig = plt.figure(figsize=(15, 10))
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(strike, ttm, iv, rstride=2, cstride=2, cmap=plt.cm.coolwarm, linewidth=0.5, antialiased=True)
    ax.set_xlabel('strike')
    ax.set_ylabel('time-to-maturity')
    ax.set_zlabel('implied volatility')
    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()


narrayplot()