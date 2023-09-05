#!/usr/bin/python
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
# %%
# %%
"""
显示当前目录下所有py文件（包括子目录）的函数结构并更新至evernote
"""

# %%
# %%
# %%
import os
import re
import pathmagic
with pathmagic.context():
    from func.first import getdirmain
    from func.logme import log
    from func.configpr import setcfpoptionvalue, getcfpoptionvalue
    from func.evernttest import findnotebookfromevernote, gettoken
    from func.evernttest import createnotebook, makenote, findnotefromnotebook
    from func.evernttest import findnotefromnotebook, get_notestore, imglist2note


# %%
# %%
# %%
def findfilesincluedef(path, t, designext='.py'):
    """
    找到给出目录下所有（包含子目录）指定文件名后缀的文件，并检查是否包含了定义函数（形如：def sample()），返回查找结果的相对路径文件名列表t
    """
    files = os.listdir(path)
    ptn = re.compile(r"^def\s+((?:\w+)\(.*?\))\s*:", re.MULTILINE|re.DOTALL)
    for f in files:
        npath = path / f
        if os.path.isfile(npath):
            if os.path.splitext(npath)[1] == designext:
                with open(npath) as fo:
                    fcontent = fo.read()
                    if len(re.findall(ptn, fcontent)) > 0:
                        t.append(os.path.relpath(npath))
        if os.path.isdir(npath):
            if f[0] == '.':
                pass
            else:
                findfilesincluedef(npath, t, designext)


# %%
# %%
# %%
def checknewthenupdatenote():
    """
    查验程序文件是否有更新（文件时间作为判断标准）并更新至笔记
    """
    nbdf = findnotebookfromevernote()
    ttt = list()
    findfilesincluedef(getdirmain(), ttt, '.py')
    ptnfiledesc = re.compile(r"(?:^\"\"\"(.*?)\"\"\"$)", re.MULTILINE|re.DOTALL)
    ptnnamedesc = re.compile(r"""^def\s+((?:\w+)\(.*?\))\s*:\s*\n
                             (?:\s+\"\"\"(.*?)\"\"\")?""",
                             re.MULTILINE|re.DOTALL)
    protitle = 'p_ew_'
    netnblst = list(nbdf.名称)
    for fn in ttt:
        nbnamelst = fn.rsplit('/', 1)
        if len(nbnamelst) == 1:
            nbnamelst.insert(0, 'root')
        nbnamelst[0] = protitle + nbnamelst[0] # ['p_ew_jpy', 'chuqin.py']
        nbname, filename = nbnamelst[0], nbnamelst[1]
        if (ennotetime := getcfpoptionvalue('evercode', nbname, filename)) is None:
            # 获取笔记本的guid，笔记本不存在则构建之
            if (nbguid := getcfpoptionvalue('evercode', nbname, 'guid')) is None:
                logstr = f"笔记本《{nbname}》在ini中不存在，可能需要构造之。"
                log.info(logstr)
                if nbname in netnblst:
                    nbguid = nbdf[nbdf.名称 == nbname].index.values[0]
                    # print(nbguid)
                else:
                    notebook = createnotebook(nbname)
                    netnblst.append(nbname)
                    nbguid = notebook.guid
            setcfpoptionvalue('evercode', nbname, "guid", nbguid)
            # 获取笔记的guid，笔记不存在则构建之
            if (noteguid := getcfpoptionvalue('evercode', nbname, f'{filename}_guid')) is None:
                logstr = f"笔记《{filename}》在ini中不存在，可能需要构造之。"
                log.info(logstr)
                items = findnotefromnotebook(nbguid, filename)
                if len(items) > 0:
                    # [noteguid, notetitle, note.updateSequenceNum]
                    noteguid = items[-1][0]
                else:
                    note = makenote(gettoken(), get_notestore(), filename, parentnotebook=nbguid)
                    noteguid = note.guid
            setcfpoptionvalue('evercode', nbname, f'{filename}_guid', noteguid)
            ennotetime = 0
            setcfpoptionvalue('evercode', nbname, filename, f"{ennotetime}")
        noteguid = getcfpoptionvalue('evercode', nbname, f'{filename}_guid')
        ennotetime = getcfpoptionvalue('evercode', nbname, filename)
        print(nbname, filename, ennotetime, noteguid)
        filetimenow = os.stat(fn).st_mtime
        if filetimenow > ennotetime:
            with open(fn) as f:
                fcontent = f.read()
                outlst = list()
                outlst.extend(re.findall(ptnfiledesc, fcontent))
                outlst.extend(["*" * 40])
                for item in re.findall(ptnnamedesc, fcontent):
                    outlst.extend([x.strip() for x in item])
                    outlst.extend(['-' * 20 + "\n"])
                cleanoutlst = [x for x in outlst if len(x) > 0]
                print("\n".join(cleanoutlst))
                imglist2note(get_notestore(), [], noteguid, filename,
                             "<pre>" + "\n".join(cleanoutlst) + "</pre>")
            setcfpoptionvalue('evercode', nbname, filename, f"{filetimenow}")


# %%
# %%
# %%
if __name__ == '__main__':
    checknewthenupdatenote()
