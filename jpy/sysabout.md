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
