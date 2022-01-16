# encoding:utf-8
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       jupytext_version: 1.13.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 系统函数 

# %% [markdown]
# ## 引入库

# %%
import os
import traceback
import inspect
import sys
import platform
import signal
import time
import datetime
import uuid
import re
from IPython import get_ipython
from hashlib import sha256
# import wmi_client_wrapper as wmi

import pathmagic
with pathmagic.context():
    from func.logme import log


# %% [markdown]
# ## 功能函数集

# %% [markdown]
# ### extract_traceback4exception(tbtuple, func_name, sleeptime=None)

# %%
def extract_traceback4exception(tbtuple, func_name, sleeptime=None):
    """
    格式化指定异常的详细信息（tuple）并返回（字符串），默认只返回堆栈的首位各两个元素，除非显性指定显示全部
    """
    # by pass the recyle import, nit recommendded
    from func.configpr import getcfpoptionvalue
    # 通sys函数获取eee的相关信息
    eee_type, eee_value, tblst = tbtuple
    if not (brief := getcfpoptionvalue("everinifromnote", "nettools", "brief")):
        brief = False
    if not (shownums := getcfpoptionvalue("everinifromnote", "nettools", "shownums")):
        shownums = 3
    if not (alltraceback := getcfpoptionvalue("everinifromnote", "nettools", "tracebackall")):
        alltraceback = True
    if alltraceback:
        rsttb = tblst
    else:
        rsttb = [x for x in tblst[:shownums]]
        rsttb.append('\t...\t')
        rsttb.extend([x for x in tblst[(-1 * shownums):]])
    if brief:
        rsttb = [x.replace("/data/data/com.termux/files", "/d/d/c/f") for x in rsttb]
    nowstr = datetime.datetime.strftime(datetime.datetime.now(), "%F %T")
    rststr = f"&&&\t{sleeptime}\t&&& in [{func_name}] at {nowstr},\t"
    rststr += f"type is\t[{eee_type}]\t, value is \t[{eee_value}],\t"
    tbstr = '\t'.join(rsttb)
    rststr += f"traceback is \t{tbstr}"

    return rststr


# %% [markdown]
# ### not_IPython()

# %%
def not_IPython():
    """
    判断是否在IPython环境下运行
    """
    return get_ipython() is None


# %% [markdown]
# ### convertframe2dict(frame)

# %%
def convertframe2dic(frame):
    framestr = str(frame)
    filename = re.findall("filename=(.+)\s", framestr)[0].strip()
    lineno = re.findall("lineno=(.+)\s", framestr)[0].strip()
    code_context = [line.strip() for line in eval(re.findall("code_context=(.+)\s", framestr)[0].strip())]

    return filename, lineno, code_context


# %% [markdown]
# ### set_timeout(num, callback)

# %%
def set_timeout(num, callback):
    def wrap(func):
        def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                if (sysstr := platform.system()) == "Linux":
#                     print(sysstr)
                    signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                    signal.alarm(num)  # 设置 num 秒的闹钟
#                     print('start alarm signal.')
                    r = func(*args, **kwargs)
#                     print('close alarm signal.')
                    signal.alarm(0)  # 关闭闹钟
                    return r
                else:
                    r = func(*args, **kwargs)
                    logstr = f"{sysstr}\t非linux系统，啥也没做。"
                    log.warning(logstr)
                    return r

            except RuntimeError as e123:
                logstr = f"{func}出现错误。\t{e123}"
                log.warning(logstr)
                callback()

        return to_do

    return wrap


# %% [markdown]
# ### after_timeout()

# %%
def after_timeout():
    """
    超时后的处理函数
    """
    log.critical(("运行超出预设时间，强制退出!", traceback.extract_stack()))


# %% [markdown]
# ### uuid3hexstr(iniputo: object)

# %%
def uuid3hexstr(inputo: object):
    inputstr = str(inputo)

    return hex(hash(uuid.uuid3(uuid.NAMESPACE_URL, inputstr)))[2:].upper()


# %% [markdown]
# ### sha2hexstr(inputo: object)

# %%
def sha2hexstr(inputo: object):
    if type(inputo) == bytes:
        targetb = inputo
    else:
        targetb = str(inputo).encode('utf-8')
    hhh = sha256(targetb)

    return hhh.hexdigest().upper()


# %% [markdown]
# ### execcmd(cmd)

# %%
@set_timeout(9, after_timeout)
def execcmd(cmd):
    try:
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text.strip("\n")
    except Exception as e:
        log.critical(f"执行命令 {cmd} 时出现错误，返回空字符串。{e}")
        return ""


# %% [markdown]
# ## main主函数

# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')
    # outgetstr = execcmd("uname -a")
    outgetstr = execcmd("echo $PATH")
    print(outgetstr.strip("\n"))
    print(uuid3hexstr(outgetstr))
    print(sha2hexstr(outgetstr))
    log.critical(outgetstr)
    if not_IPython():
        log.info(f'文件\t{__file__}\t测试完毕。')

# %%
