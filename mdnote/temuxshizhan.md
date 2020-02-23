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

### 2020-02-23


#### 升级系统软件
昨天升级openssh、zsh和git后在terminal中出现错误，每次按键都会出现错误提示，另外putty也无法ssh到服务器上了。后来按照感觉分别载卸重装zsh、openssh和git后恢复正常。期间，对于打开的频繁弹出错误提示的terminal窗口Ctrl+c强行关闭。
好处也不是没有，nnn升级后e快捷键能自动用vim打开文件了，不再像上一版非得用o打开，输入编辑器选择vim，然后再选择cli还是gui。但是p还是不能用。
无端执行软件升级导致生产环境异常的事情发生了几次，要控制住这种无由冲动，稳定好用的生产力环境才是一切的重中之重。


#### putty的弃用
升级系统软件时出现了无法通过putty软件ssh上去的问题（可能是openssh即时运行环境被升级破坏导致的），只好通过jupyter-lab的terminal功能替代。唉，一替代不要紧，发现很好用：
* 打开网页就可以使用
* 终端内容可以复制粘贴
* 字体渲染那也是比putty强好多倍（毕竟是浏览器渲染根底）
* 也不用什么密匙公匙的（当然要加强jupyter-lab的安全性为前提）

那就先这样，windows 10 任务栏上的固定按钮putty可以取消了。

```python

```
