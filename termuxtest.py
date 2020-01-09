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

import pathmagic
import sys
sys.path.append('termux_python')
with pathmagic.context():
    import termux_python.termux as tm
    from func.wrapfuncs import timethis
    from func.profilerlm import lpt_wrapper
    from func.logme import log


@timethis
@lpt_wrapper()
def showmsgfromtermux():
    # print('开工啊')
    print(sys.path)
    print(tm.battery_status())
    print(tm.camera_info())
    # tm.termux_sms_list()


if __name__ == '__main__':
    log.info(
        f'开始运行文件\t{__file__}\t{sys._getframe().f_code.co_name}\t{sys._getframe().f_code.co_filename}')
    showmsgfromtermux()
    log.info(f"文件\t{__file__}\t执行完毕")
