---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.5.0
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

<!-- #region -->
### 解决git pull/push时每次需要输入密码的问题

如果我们git clone的下载代码的时候是连接的https:// 而不是git@git (ssh)的形式，当我们操作git pull/push到远程的时候，总是提示我们输入账号和密码才能操作成功，频繁的输入账号和密码会很麻烦。

**解决办法**：

git bash**进入你的项目目录**，输入：
```bash
git config --global credential.helper store
```
然后你会在你本地生成一个文本，上边记录你的账号和密码。当然这些你可以不用关心。

然后你使用上述的命令配置好之后，再操作一次git pull，然后它会提示你输入账号密码，这一次之后就不需要再次输入密码了。
<!-- #endregion -->

```python
print("I am git.")
```

### `git mv`移动文件

<!-- #region -->
```bash
git mv aaa.py bbb.py
```

操作之后需要commit生效
<!-- #endregion -->

### git reflog

```python
!git reflog
```

```python

```
