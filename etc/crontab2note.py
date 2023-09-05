# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %%
"""
检查crontab是否更新，有更新就更新相应笔记并并开关设置发送邮件
"""

# %%
from pathlib import Path
import os
import re

# %%
import pathmagic
with pathmagic.context():
    # from func.first import dirmainpath
    from func.logme import log
    from func.mailsfunc import findnewthenupdatenote
    from func.sysfunc import set_timeout, after_timeout, not_IPython


# %%
@set_timeout(300, after_timeout)
def findnewcronthenupdate():
    """
    查看当前登录用户的cron自动运行配置表是否有更新（修改时间），并视情况更新
    """

    # 获取用户名，方便适配不同的运行平台
    r = os.popen('whoami')
    me = r.read()[:-1]
    # print(me)
    # print("This is just a test for jupytext.")

    # 打开配置表，过滤掉注释并简单检查（由6部分构成）是否符合规范
    cronpath = Path('/data/data/com.termux/files/usr/var/spool/cron/crontabs')
    if (cronpath / me ).exists():
        cronfile = cronpath / me
    elif (cronpath.parent / me).exists():
        cronfile = cronpath.parent / me
    else:
        logstr = f"本机用户{me}的自动运行规划文件在{cronpath / me}和{cronpath.parent / me}都不存在！"
        log.critical(logstr)
        return

    print(cronfile)
    cfl = open(cronfile, 'r').readlines()
    # print(f"{cfl}")
    cflen = [len(x.split()) for x in cfl if not x.startswith('#')]
    # print(cflen)
    clean = True
    for it in cflen:
        clean = clean and (it >= 6)
        if not clean:
            break

    # 进入更新判断处置环节
    if clean:
        findnewthenupdatenote(cronfile, 'eversys', 'everwork', 'cron', 'cron自动运行排期表')
    else:
        logstr = f"自动运行排表有误，请检查。{len(cflen)}\t{cflen}"
        log.critical(logstr)


# %%
@set_timeout(300, after_timeout)
def findcronlogthenupdate():
    """
    构建待处理的目标日志或配置文件列表并处理之
    """
    logpath = "/data/data/com.termux/files/usr/var/log"
    # logpath = dirmainpath / 'log'
    logfiles = os.listdir(logpath)
    ptn = re.compile("ew_")
    # ptn = re.compile("ever")
    ewlogfiles = [x for x in logfiles if re.match(ptn, x) and x.endswith('.log')]
    ewlogfiles.append('.zshrc')
    ewlogfiles.append('.vimrc')
    ewlogfiles.append('.tmux.conf')
    print(ewlogfiles)
    for item in ewlogfiles:
        # pre = re.split(ptn, item)[1].replace('.', '_')
        print(item)
        pre = item.replace('.', '_').replace('ew_', '')
        if item.endswith('.log'):
            itempath = Path(logpath) / item
        else:
            itempath = Path('/data/data/com.termux/files/home') / item
        print(pre, itempath)
        findnewthenupdatenote(itempath, 'eversys', 'everwork', f"cron_{pre}", f"cron_{pre}日志")


# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')
    findnewcronthenupdate()
    findcronlogthenupdate()
    if not_IPython():
        log.info(f"文件\t{__file__}\t运行结束。")

# %%
