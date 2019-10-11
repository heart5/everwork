# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext_format_version: '1.3'
#   jupytext_formats: py:light
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
# ---

import pathmagic
import sys
sys.path.append('termux_python')
with pathmagic.context():
    import termux_python.termux as tm
    from func.wrapfuncs import lpt_wrapper, timethis


@timethis
@lpt_wrapper()
def showmsgfromtermux():
    # print('开工啊')
    print(sys.path)
    print(tm.battery_status())
    print(tm.camera_info())
    # tm.termux_sms_list()


showmsgfromtermux()
