#! /usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import matplotlib
from matplotlib.font_manager import FontManager

print(matplotlib.matplotlib_fname())    # 包含全路径的配置文件

fm = FontManager()

# print(fm.findfont(matplotlib.font_manager.FontProperties(), fontext='ttf'))
# mat_fonts = set(f.fname for f in fm.ttflist) # matplotlib可用的字体路径列表
# print(mat_fonts)
mat_fonts = set(f.name for f in fm.ttflist)  # matplotlib可用的字体列表
# print('*' * 10, 'matplotlib可用的字体', '*' * 10)
# print(mat_fonts)
output = subprocess.check_output('fc-list :lang=zh -f "%{family}\n"',
                                 shell=True)   # 列出系统可用的中文字体，仅linux下可运行fc-list命令
# print(output.decode('utf-8'))
outputsplit = output.decode('utf-8').split('\n')    # 解码bytes为str并分割
# print '*' * 10, '系统可用的中文字体', '*' * 10
zhfs = set(f.split(',', 1)[0] for f in outputsplit)
zhfs = set(f for f in zhfs if len(f) > 0)
# print(zhfs)
# zhfs.pop()
# print(zhfs)
zh_fonts = set(f.split(',', 1)[0]
               for f in outputsplit if len(f.split(',', 1)[0]) > 0)
# print(zh_fonts)
available = mat_fonts & zhfs    # matplotlib字体和操作系统字体取交集


@profile
def showfont():
    print(f"{'*' * 10}可用的中文字体（取交集）{'*' * 10}")
    for f in available:
        print(f)
    #     print(len(mat_fonts))
    print("All thing done.")

showfont()
