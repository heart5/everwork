# -*- coding: utf-8 -*-
---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.3.1
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

## 系统相关功能调试


### `inspect`


[
FrameInfo(
    frame=<frame at 0x7a43f94800, file './func/evernttest.py', line 369, code evernoteapijiayi>, 
    filename='./func/evernttest.py', 
    lineno=369, 
    function='evernoteapijiayi', 
    code_context=['            log.critical(f"Evernote API\\t{nsstr4ini} 新生^_^{inspect.stack()}")\n'], 
    index=0), 
FrameInfo(
    frame=<frame at 0x7a43f8a040, file './func/evernttest.py', line 106, code getnotestore>, 
    filename='./func/evernttest.py', 
    lineno=106, function='getnotestore', 
    code_context=['        evernoteapijiayi()\n'], 
    index=0), 
FrameInfo(
    frame=<frame at 0x7a4571b810, file './func/nettools.py', line 191, code wrapper>, 
    filename='./func/nettools.py', 
    lineno=191, 
    function='wrapper', 
    code_context=['                    result = jutifunc(*args, **kwargs)\n'], 
    index=0), 
FrameInfo(
    frame=<frame at 0x7a4588d610, file './func/evernttest.py', line 110, code get_notestore>, 
    filename='./func/evernttest.py', 
    lineno=110, 
    function='get_notestore', 
    code_context=['    return getnotestore(forcenew)\n'], 
    index=0), 
FrameInfo(
    frame=<frame at 0x7a44a55c40, file './func/evernttest.py', line 538, code readinifromnote>, 
    filename='./func/evernttest.py', 
    lineno=538, 
    function='readinifromnote', 
    code_context=['    note_store = get_notestore()\n'], 
    index=0), 
FrameInfo(
    frame=<frame at 0x7a47b36710, file './func/nettools.py', line 191, code wrapper>, 
    filename='./func/nettools.py', 
    lineno=191, 
    function='wrapper', 
    code_context=['                    result = jutifunc(*args, **kwargs)\n'], 
    index=0), 
FrameInfo(
    frame=<frame at 0x7a44dc7c10, file './func/evernttest.py', line 566, code getinivaluefromnote>, 
    filename='./func/evernttest.py', 
    lineno=566, 
    function='getinivaluefromnote', 
    code_context=['    readinifromnote()\n'], 
    index=0), 
FrameInfo(
    frame=<frame at 0x7a47f29e40, file './func/wrapfuncs.py', line 27, code with_logging>, 
    filename='./func/wrapfuncs.py', 
    lineno=27, 
    function='with_logging', 
    code_context=["        if getinivaluefromnote('everwork', 'logdetails'):\n"], 
    index=0), 
FrameInfo(
    frame=<frame at 0x7a4b189440, file 'etc/footstrack.py', line 54, code <module>>, 
    filename='etc/footstrack.py', 
    lineno=54, 
    function='<module>', 
    code_context=['        foot2record()\n'], 
    index=0)
    ]

```python
inspectout = """[FrameInfo(frame=<frame at 0x7a43f94800, file './func/evernttest.py', line 369, code evernoteapijiayi>, filename='./func/evernttest.py', lineno=369, function='evernoteapijiayi', code_context=['            log.critical(f"Evernote API\\t{nsstr4ini} 新生^_^{inspect.stack()}")\n'], index=0), FrameInfo(frame=<frame at 0x7a43f8a040, file './func/evernttest.py', line 106, code getnotestore>, filename='./func/evernttest.py', lineno=106, function='getnotestore', code_context=['        evernoteapijiayi()\n'], index=0), FrameInfo(frame=<frame at 0x7a4571b810, file './func/nettools.py', line 191, code wrapper>, filename='./func/nettools.py', lineno=191, function='wrapper', code_context=['                    result = jutifunc(*args, **kwargs)\n'], index=0), FrameInfo(frame=<frame at 0x7a4588d610, file './func/evernttest.py', line 110, code get_notestore>, filename='./func/evernttest.py', lineno=110, function='get_notestore', code_context=['    return getnotestore(forcenew)\n'], index=0), FrameInfo(frame=<frame at 0x7a44a55c40, file './func/evernttest.py', line 538, code readinifromnote>, filename='./func/evernttest.py', lineno=538, function='readinifromnote', code_context=['    note_store = get_notestore()\n'], index=0), FrameInfo(frame=<frame at 0x7a47b36710, file './func/nettools.py', line 191, code wrapper>, filename='./func/nettools.py', lineno=191, function='wrapper', code_context=['                    result = jutifunc(*args, **kwargs)\n'], index=0), FrameInfo(frame=<frame at 0x7a44dc7c10, file './func/evernttest.py', line 566, code getinivaluefromnote>, filename='./func/evernttest.py', lineno=566, function='getinivaluefromnote', code_context=['    readinifromnote()\n'], index=0), FrameInfo(frame=<frame at 0x7a47f29e40, file './func/wrapfuncs.py', line 27, code with_logging>, filename='./func/wrapfuncs.py', lineno=27, function='with_logging', code_context=["        if getinivaluefromnote('everwork', 'logdetails'):\n"], index=0), FrameInfo(frame=<frame at 0x7a4b189440, file 'etc/footstrack.py', line 54, code <module>>, filename='etc/footstrack.py', lineno=54, function='<module>', code_context=['        foot2record()\n'], index=0)]"""

len(inspectout)
```

```python
eval(inspectout)
```

## 各种资源


#### anaconda安装清华源


https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/


## 用atilo安装使用linux


### 安装步骤


#### 更新apt安装源，并安装curl工具

<!-- #region -->
```bash
apt update
apt install -y curl
```
<!-- #endregion -->

#### 安装atilo


1.英文版

<!-- #region -->
```bash
curl -o $PREFIX/bin/atilo https://raw.githubusercontent.com/YadominJinta/atilo/master/atilo && chmod +x $PREFIX/bin/atilo
```
<!-- #endregion -->

2.中文版

<!-- #region -->
```bash
curl -o $PREFIX/bin/atilo https://raw.githubusercontent.com/YadominJinta/atilo/master/CN/atilo_cn && chmod +x $PREFIX/bin/atilo
```
<!-- #endregion -->

英文版比CN版多了CentOS、OpenSuSE、ParrotOS这3个系统


#### 补充必要运行库

<!-- #region -->
```bash
pip install tqdm prettytable
```
<!-- #endregion -->

### atilo命令


```
atilo [命令] [参数]
命令:
images                列出可用的Linux
remove              移除已安装的Linux
pull             拉取Linux镜像
run               运行linux镜像
clean           清除镜像的tmps
help                帮助
```


### 运行linux

<!-- #region -->
```bash
atilo images #列出可用的linux版本
atilo pull ubuntults #拉取ubuntu的bionic版本
atilo run ubuntults #运行，直接进入ubuntults，默认是root
```
<!-- #endregion -->

### 安装jupyterhub


#### 安装系统工具

<!-- #region -->
```bash
apt update #更新安装源
apt install -y nnn #安装nnn文件管理器，版本好老，1.7.1
```
<!-- #endregion -->

## AlgerNon



- Small self-contained web server with Lua, Markdown, QUIC, Redis and PostgreSQL support
- 默认访问端口是：3000


通过服务器渲染的方式展示md文件，可以正常显示文件中的中文字符。默认用的是lua语言。


号称终端下支持Markdown的mdp工具，不支持中文字符，没什么实用价值


## pip安装python库


### Pillow

<!-- #region -->
2020-03-01

直接安装提示错误，无法成功，查阅文档运行了
```bash
pkg install -y python ndk-sysroot clang make libjpeg-turbo 
```
然后再执行，```python -m pip install --upgrade Pillow```
安装成功

<!-- #endregion -->
