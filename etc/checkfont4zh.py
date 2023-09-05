# encoding:utf-8
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %%
"""
查询linux系统下的可用中文字体
"""

import subprocess
from matplotlib.font_manager import FontManager
import pathmagic

with pathmagic.context():
    from func.logme import log


def getavailablezhfont():
    """
    获取系统中安装的中文字体列表
    """
    fm = FontManager()
    mat_fonts = set(f.name for f in fm.ttflist)

    output = subprocess.check_output(
        'fc-list :lang=zh -f "%{family}\n"', shell=True).decode('utf-8')
    # print '*' * 10, '系统可用的中文字体', '*' * 10
    # print output
    zh_fonts = set(f.split(',', 1)[0] for f in output.split('\n'))
    available = mat_fonts & zh_fonts

    print('*' * 10, '可用的字体', '*' * 10)
    for f in available:
        print(f'{f}')

if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    getavailablezhfont()

    print('Done.完毕。')
