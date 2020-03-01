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
