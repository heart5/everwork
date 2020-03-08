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

# 安装termux到Android手机并部署python环境


## termux和termux-api安装
termux在谷歌商店的最新版本是0.92。之前一直用的是0.65（2018年），后来升级到0.66（2019年）。因为termux-api不再支持短信读取等涉及个人隐私的功能（谷歌商店限制），担心termux主版本会自动关联这个阉割，就一直没有升级。这次黑鲨升级系统，到论坛看了下貌似整体搬迁到小米（哦，不对，应该是官宣的“将JOYUI的游戏特性与MIUI完美结合”），坛友抱怨甚多，问题反馈集中在易耗电、发热甚至不稳定，所以一直没动。昨天手痒，想着termux大版本都升级那么多，应该有不少好东东，一激动就把termux和termux-api都升级了。麻烦就此来了！


先安装`pkg install openssh`（这中间还犯了个输入错误，误输入成openssl，还奇怪怎么没有生成`.ssh`目录呢），添加电脑生成的公匙，然后用putty登录在电脑上操作。按照原来的笔记步骤，要更新成清华源并追加pointless源，速度快些还方便装难以搞定的numpy。但奇怪的是`apt update`并`apt upgrade`后总是莫名出错，不是系统自带命令不见了（连ls都操作不了），就是各种库报错，连apt都用不了了。把termux重装了几次都不行，恨不得怀疑人生。实在耗不过了，突然想就用官方源试试再说（其实速度也还可以，还是在vpn科学上网的状态下），结果一路绿灯，基本系统和工具安装顺利。后面就是各种对装不上pandas的折腾，下文再讲。jupyterlab也装起来，虽然插件因为nodejs的问题一直无法使用，但基本的程序还是可以跑起来的，然后一狠心，就把手机的操作系统也一起升级到JOYUI11，华丽丽的的变化很大，也放到后面讲。试车的时候发现获取位置和ip的脚本老是挂在那里跑不动。python一切正常，那问题就在termux-api上了。


在终端中运行`termux-location`等命令，挂起无反应，怀疑是版本不匹配的问题。termux-api最新的版本是0.41，手里还有0.31（还支持短信等敏感操作）和0.32（从这个版本其就不支持敏感操作了）。把三个版本逐次试了下，按照之前的经验，先要在终端中卸载`pkg uninstall termux-api`，每次更改termux-api版本安装后再次`pkg install termux-api`，状况依旧，还是挂起没商量。然后在新版本系统的手机上对termux和termux-api授予各种权限，没有任何反应。静下来仔细想了下，决定从头来过，用轮换的方法把各个组合都试一下。


出于对新版本的艳羡，先从谷歌商店的最新版开始。手机上安装termux（0.92）和termux-api（0.41），然后直接在termux窗口命令行中`pkg install termux-api`，安装成功后试运行`termux-location`，弹出提示无权限。可把我给激动坏了，终于有动静了啊。进入手机设置对termux-pai各种授权，然后回到termux窗口再次运行，哎，输出结果了。然后测试`termux-sms-list`，调试信息显示“谷歌已经不允许读取短信”。心里明白了问题所在（这个硬件相关和系统api接口需要在手机上运行并授权），卸载0.41的api，大胆的安装了termux-api（0.31），再次在手机上运行`termux-sms-list`，okay，显示正确结果。问题彻解于此！


### termux-api安装成功操作步骤


1.**手机上**安装termux和termux-api的App程序

2.在手机系统“设置”中对termux-api进行各种授权（存储空间、位置、短信等）

3.在**手机上进入termux终端命令行**：`pkg install termux-api`

4.运行测试命令：`termux-location`，okay


### termux工具集 


#### 挂接手机系统内部存储空间
在手机termux窗口命令行（还是考虑授权问题，其实如果做好了各种授权，在ssh登录的远程客户端也是一样）运行：`termux-setup-storage`，home目录下出现storage目录，里面是dcim  downloads  movies  music  pictures  shared等子目录，其中`shared`就是**手机内部存储空间的根目录**，其他几个是为了便捷存取的软连接目录。


#### 工具箱预备

`pkg install curl wget p7zip htop git`


#### proot，给termux一个root权限的入口
```
pkg install proot
```
安装后对应的命令是`termux-chroot`，运行命令进入root模式，`exit`退出。
进去后命令行提示符有些许变化，其他未知。


#### vim，上古神之编辑器


有些插件需要支持python的vim版本，官方源里面有，这里我们直接安装：
```zsh
pkg install vim-python
```
相关库大小有43M，看了下，默认把python也给装好了^_^


#### nnn文件管理器


运行`pkg install nnn`命令安装后直接使用


#### zsh，功能强大的shell


##### 安装


运行如下命令拉下脚本直接运行
`sh -c "$(curl -fsSL https://github.com/Cabbagec/termux-ohmyzsh/raw/master/install.sh)"`，过程中背景色和字体的选择，我分别选的是14和6，个人喜好而已。

**重启termux终端使之生效**。再进来就是带彩的了，还有各种好用的命令，功能十分强大，有兴趣的可以慢慢把玩o(*￣︶￣*)o


##### 给code库创建软连接（参dcim、downloads们），方便读取使用

`ln -s storage/shared/0code codebase`


##### 修改完善配置


配置文件地址：`~/.zshrc`


给系统指定编辑器（很多程序会默认调用，比如nnn、apt edit-sources），在合适的位置添加一行：
```
export EDITOR=vim
```

在配置文件尾部添加几行：
```zsh
~/sbase/startcronserver.sh    # 启动cron服务器且通过脚本确保仅启动一次
sshd # 启动ssh服务，接受远程登录
termux-wake-lock # 避免termux睡死
```


#### tmux，多窗口服务器型 终端


##### 安装
需要root权限（不知道是否必要，反正这么搞可以正常运行）
```zsh
termux-chroot # 进入root模式
apt-get install tmux
exit # 退出root模式，回归正常
```


##### 修改优化配置

<!-- #region -->
调整默认的前缀键为Ctrl-b和\`，配置文件是`~/.tmux.conf`，如果不存在就创建一个
```bash
set -g prefix C-a #
unbind-key C-b # C-b即Ctrl+b键，unbind意味着解除绑定
bind-key C-a send-prefix # 绑定Ctrl+a为新的指令前缀
# 从tmux v1.6版起，支持设置第二个指令前缀
set-option -g prefix2 ` # 设置一个不常用的`键作为指令前缀，按键更快些
bind-key r source-file ~/.tmux.conf \; display "Config reloaded.."
```
<!-- #endregion -->

##### 不足
多窗口用起来很爽，但美中不足的是和host操作系统的粘贴板无法贯通，不像putty中鼠标右键粘贴、选中后左键复制来的方便。所以在安装期，想从资料中复制粘贴还是待在putty中的好。


## python必要工作库

<!-- #region -->
```bash
pip install bs4 evernote3 py2ifttt xlrd oauth2 oauth2client openpyxl xpinyin yagmail itchat wrapt  google_auth_oauthlib odps cython
pip install pygsheets==1.1.4 # 高版本搞不好，就只能这个了
pip install jupytext==1.3.1 # ipynb适配git的插件。不知道咋地，备份系统上版本升不上去，为了避免meta变化导致没必要的签入签出，强制两边版本一样算了，就低。
pip install cython # 安装line_profiler时需要
```
<!-- #endregion -->

### 安装line_profiler库

<!-- #region -->
```bash
git clone https://github.com/rkern/line_profiler.git
find line_profiler -name '*.pyx' -exec cython {} \;
cd line_profiler && pip install . --user
```
<!-- #endregion -->

### 安装lxml库

<!-- #region -->
先安装依赖库
```bash
apt-get --assume-yes install libxslt openssl-tool
```
然后再运行
```bash
pip install lxml
```
<!-- #endregion -->

```python

```
