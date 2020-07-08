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

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true -->
## termux和termux-api安装
termux在谷歌商店的最新版本是0.92。之前一直用的是0.65（2018年），后来升级到0.66（2019年）。因为termux-api不再支持短信读取等涉及个人隐私的功能（谷歌商店限制），担心termux主版本会自动关联这个阉割，就一直没有升级。这次黑鲨升级系统，到论坛看了下貌似整体搬迁到小米（哦，不对，应该是官宣的“将JOYUI的游戏特性与MIUI完美结合”），坛友抱怨甚多，问题反馈集中在易耗电、发热甚至不稳定，所以一直没动。昨天手痒，想着termux大版本都升级那么多，应该有不少好东东，一激动就把termux和termux-api都升级了。麻烦就此来了！
<!-- #endregion -->

先安装`pkg install openssh`（这中间还犯了个输入错误，误输入成openssl，还奇怪怎么没有生成`.ssh`目录呢），启动sshd服务，然后添加电脑生成的公匙（把客户端生成的公匙内容追加到服务器端`~/.ssh/authorized_keys`文件中），然后用putty登录在电脑上操作。按照原来的笔记步骤，要更新成清华源并追加pointless源，速度快些还方便装难以搞定的numpy。但奇怪的是`apt update`并`apt upgrade`后总是莫名出错，不是系统自带命令不见了（连ls都操作不了），就是各种库报错，连apt都用不了了。把termux重装了几次都不行，恨不得怀疑人生。实在耗不过了，突然想就用官方源试试再说（其实速度也还可以，还是在vpn科学上网的状态下），结果一路绿灯，基本系统和工具安装顺利。后面就是各种对装不上pandas的折腾，下文再讲。jupyterlab也装起来，虽然插件因为nodejs的问题一直无法使用，但基本的程序还是可以跑起来的，然后一狠心，就把手机的操作系统也一起升级到JOYUI11，华丽丽的的变化很大，也放到后面讲。试车的时候发现获取位置和ip的脚本老是挂在那里跑不动。python一切正常，那问题就在termux-api上了。


在终端中运行`termux-location`等命令，挂起无反应，怀疑是版本不匹配的问题。termux-api最新的版本是0.41，手里还有0.31（还支持短信等敏感操作）和0.32（从这个版本其就不支持敏感操作了）。把三个版本逐次试了下，按照之前的经验，先要在终端中卸载`pkg uninstall termux-api`，每次更改termux-api版本安装后再次`pkg install termux-api`，状况依旧，还是挂起没商量。然后在新版本系统的手机上对termux和termux-api授予各种权限，没有任何反应。静下来仔细想了下，决定从头来过，用轮换的方法把各个组合都试一下。


出于对新版本的艳羡，先从谷歌商店的最新版开始。手机上安装termux（0.92）和termux-api（0.41），然后直接在termux窗口命令行中`pkg install termux-api`，安装成功后试运行`termux-location`，弹出提示无权限。可把我给激动坏了，终于有动静了啊。进入手机设置对termux-pai各种授权，然后回到termux窗口再次运行，哎，输出结果了。然后测试`termux-sms-list`，调试信息显示“谷歌已经不允许读取短信”。心里明白了问题所在（这个硬件相关和系统api接口需要在手机上运行并授权），卸载0.41的api，大胆的安装了termux-api（0.31），再次在手机上运行`termux-sms-list`，okay，显示正确结果。问题彻解于此！

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true -->
### termux-api安装成功操作步骤
<!-- #endregion -->

1.**手机上**安装termux和termux-api的App程序

2.在手机系统“设置”中对termux-api进行各种授权（存储空间、位置、短信等）

3.在**手机上进入termux终端命令行**：`pkg install termux-api`

4.运行测试命令：`termux-location`，okay

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true -->
### 脚本和系统变量
<!-- #endregion -->

#### 系统变量


##### 当前系统变量

```python
!echo $PATH
# /data/data/com.termux/files/home/sbase:/data/data/com.termux/files/home/sbase:/data/data/com.termux/files/usr/bin:/data/data/com.termux/files/usr/bin/applets
```

##### 临时添加路径

```python
!export PATH=/data/data/com.termux/files/home/codebase/everwork/:$PATH
```

用冒号`:`分隔。如果需要，可以添加到`.zshrc`中，这样在shell启动时就启动加上了。


#### 脚本


开启一个tmux服务运行jupyter-lab

<!-- #region -->
```bash
#!/bin/bash
#jl - start jupyterlab in tmux

sess_name="jupyterlab"

export DISABLE_AUTO_TITLE="true"

cd ~/codebase/everwork

tmux has-session -t $sess_name
if [ $? = 0 ];then
	echo $sess_name "already exist. attaching..."
	tmux attach-session -t $sess_name
else
	echo $sess_name "doesn't exist.creating..."
	tmux new -d -s $sess_name -n home
	tmux send-keys -t $sess_name:0 "jupyter lab" Enter
fi
```
<!-- #endregion -->

保存后，`chmod +x jl`使之可执行，然后丢到前面已经加入环境路径的脚本目录中，随时随地可调用。

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true -->
### termux工具集 
<!-- #endregion -->

#### 挂接手机系统内部存储空间
在手机termux窗口命令行（还是考虑授权问题，其实如果做好了各种授权，在ssh登录的远程客户端也是一样）运行：`termux-setup-storage`，home目录下出现storage目录，里面是dcim  downloads  movies  music  pictures  shared等子目录，其中`shared`就是**手机内部存储空间的根目录**，其他几个是为了便捷存取的软连接目录。


#### 工具箱预备

`pkg install curl wget p7zip htop git nnn openssh`


#### ssh，远程登陆、管理（上传下载等）


##### 安装

<!-- #region -->
```bash
pkg install openssh
```
<!-- #endregion -->

安装完成候会自动生成密匙对。


##### 启动服务

<!-- #region -->
```bash
sshd
```
<!-- #endregion -->

##### 公匙登陆（服务器端设置）


启动服务后就可以接受客户端的接入请求了。


如果是公匙方式登陆，需要提前把客户端生成密匙对的公匙传进来，写入`~/.ssh/authorized_keys`文件（每个公匙占用一行）


**`~/.ssh`、`athorized_keys`和公匙密匙文件的权限必须是600，其他可能出错并且错的莫名其妙**


##### 公匙i登陆（客户端设置）


客户端可以配置`~/.ssh/config`方便登陆

```ini
Host termux-bs2pro
    HostName 192.168.31.191
    Port 8022
    IdentityFile ~/.ssh/id_rsa # 和传入服务器端的相应密匙文件地址
    PreferredAuthentications publickey # 指定登陆方式仅为密匙对
    User u0_a133
```


##### 上传下载


以`~/.ssh/config`配置好为前提。


###### 下载文件

<!-- #region -->
```bash
scp termux-bs2pro:~/sbase.zip . # 下载sbase.zip到当前目录。经测试，同局域网内下载速度为726KB/s
```
<!-- #endregion -->

###### 上传文件

<!-- #region -->
```bash
scp testforscp.txt termux-bs2pro:~/testfromscpfrom_8xmax.txt
```
<!-- #endregion -->

###### 下载目录

<!-- #region -->
```bash
scp -r termux-bs2pro:~/ghub ghub
```
<!-- #endregion -->

#### proot，给termux一个root权限的入口
```
pkg install proot
```
安装后对应的命令是`termux-chroot`，运行命令进入root模式，`exit`退出。
进去后命令行提示符有些许变化，其他未知。


#### vim，上古神之编辑器


##### 安装


有些插件需要支持python的vim版本，官方源里面有，这里我们直接安装：
```zsh
pkg install vim-python
```
相关库大小有43M，看了下，默认把python也给装好了^_^


##### 安装solarized主题

<!-- #region -->
1.下载主题并解压到vim相应版本的主程序相应目录colors中
```bash
cd ~
cd ..
cd usr/share/vim/vim82/colors
wget https://github.com/altercation/vim-colors-solarized/archive/master.zip
7z l master.zip # 列印压缩包中的文件，看看主题（后缀名是.vim）在哪里
7z e master.zip vim-colors-solarized-master/colors/solarized.vim # 从压缩包中提取指定文件到当前目录
```
2.在`.vimrc`中增加配置行
```ini
let g:solarized_termcolors=256 "solarized主题设置在终端下的设置"
set background=dark "设置背景色"
colorscheme solarized
```
<!-- #endregion -->

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


**配置文件地址：`~/.zshrc`**

<!-- #region -->
1. 给系统指定编辑器（很多程序会默认调用，比如nnn、apt edit-sources），在合适的位置添加一行：
```ini
export EDITOR=vim
```
2. 添加脚本库目录到环境变量
```ini
export PATH=~/sbase:$PATH
```
3. 个性化脚本和必要服务、设置，在配置文件尾部添加几行：
```bash
~/sbase/startcronserver.sh    # 启动cron服务器且通过脚本确保仅启动一次
sshd # 启动ssh服务，接受远程登录
termux-wake-lock # 避免termux睡死
```
<!-- #endregion -->

#### tmux，多窗口服务器型终端


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

##### 基本概念和操作


1. session包含window，window包含panel。


2. 启动和退出
    1. 启动tmux
        1. 新启动并命名session名称    
    ```bash
    tmux new -t everwork
    ```
        2. 接入一个已经存在的session
        ```bash
        tmux a -t everwork
        ```
        3. 直接接入session列表中第一个会话
        ```bash
        tmux a
        ```
    2. 退出tmux
        1. 临时退出但不删除，可以通过`tmux a`回来
        **bind-key d**
        2. 在会话中退出并删除session（该命令也可以在命令行中使用）
        **bind-key :kill-session**
        3. 在会话中并删除所有session（该命令也可以在命令行中使用）
        **bind-key :kill-server**


3. 窗口和窗格中各种按键操作
    1. 窗口（window）的各种按键操作（在会话界面中）
        1. **bind-key s** 获取会话列表
        2. **bind-key c** 创建新的窗口
        3. **bind-key 1** 跳转到指定窗口
        4. **bind-key l** 在相邻的两个窗口轮换
        5. **bind-key n** 跳往下一个窗口
        6. **bind-key p** 跳往下一个窗口
        7. **bind-key &** 删除所在窗口，需要yes or no的手工确认
    2. 窗格（panel）的各种按键操作（在会话界面中）
        1. **bind-key "** 横切创建新窗格
        2. **bind-key %** 竖切创建新窗格
        3. **bind-key o** 在窗格中游走
        4. **bind-key "** 横切创建新窗格
        5. **bind-key o** 在窗格中游走
        6. **bind-key ↑↓←→** 切换到上下左右窗格（一次按一个箭头）
        7. **bind-key :resize-pane -UDLR** 调整当前窗格的大小，四个方向
        8. **bind-key x** 删除当前窗格，需要确认
        9. **bind-key 空格** 切换当前窗口中所有窗格的各种布局（layout）
        10. **bind-key !** 移动当前窗格道新的窗口，独立啦
        11. **bind-key :join-pane -t everwork** 移动当前窗格到指定的窗口中
        12. **bind-key Ctrl+o** 按顺序移动窗格位置，顺时针转一圈
        13. **bind-key q** 显示当前窗口中所有窗格的编号
        14. **bind-key t** 在窗格中显示时间
        15. **bind-key z** 最大化最小化当前窗格，toggle


4. 在复制模式中滚动、拷贝、粘贴

    1. ***浏览***。`bind-key [`进入复制模式，然后就可以用整套vim的键码来浏览屏幕缓冲区信息，比如`Ctrl+f`翻页、`/`查找、`gg`到页首等。`Enter`回车键退出复制模式，回归正常的窗格操作。
    2. ***拷贝***。移动到选择字符，按下`SPACE`空格开始选择，通过移动键选好后按下`Enter`结束选择，所选内容就自动存入`buffer`缓存区了。
    3. ***粘贴***。`bind-key ]`执行粘贴。（vim中如要粘贴内容不出现缩进混乱，需要进入`paste`模式，命令`:set paste`，一切都好了后再恢复`:set nopaste`）


##### 不足
多窗口用起来很爽，但美中不足的是和host操作系统的粘贴板无法贯通，不像putty中鼠标右键粘贴、选中后左键复制来的方便。所以在安装期，想从资料中复制粘贴还是待在putty中的好。

【**目前的折中解决方案是用jupyterlab，浏览器端开启terminal，即使在tmux中的窗口好像也是可以接受粘贴复制的。**】

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true -->
### vim设置和插件
<!-- #endregion -->

这个玩意儿配置好了可以上天，所以在此专条讲述


#### 【打包备份】

<!-- #region -->
全部安装设置好后，进入home目录：
```bash
7z a vim.zip .vim/ .vimrc
```

然后把打包好的vim.zip备份到云盘之类的好地儿，以后需要的时候下载下来解压`7z x vim.zip`即可。
<!-- #endregion -->

#### 按键精灵


按键|功能
:--|:--
u|恢复上次的修改操作
Ctrl+r|重做，redo
.|重复上一组修改操作


#### ~~下载源码编译使之支持各种性能，如粘贴板等~~


##### 下载源码

<!-- #region -->
在`home`目录下建立一个专门下载源码的目录`mkdir ghub`后`cd ghub`进入之
```bash
git clone https://github.com/vim/vim.git
```
进到src里面`cd vim/src`

编译语句：
```bash
make clean
./configure --with-features=huge --enable-python3interp --enable-pythoninterp --with-python-config-dir=/data/data/com.termux/files/usr/lib/python3.8/config-3.8 --enable-rubyinterp --enable-luainterp --enable-perlinterp --with-python-config-dir=/data/data/com.termux/files/usr/lib/python2.7/config --enable-multibyte --enable-cscope --enable-gui=auto  --with-x --prefix=/data/data/com.termux/files/usr
make install
```
~~编译没有成功，放弃了，再说通过其它方式解决了ycm服务无法启动的问题~~
<!-- #endregion -->

#### `.vimrc`设置文件


##### 高亮设置


```ini
highlight Visual ctermfg=yellow # 设置可视模式选择范围的前景色
highlight Function cterm=bold,underline ctermbg=black ctermfg=green # 设置函数（function）的字体style和背景色、前景色
```


设置后保存，因为配置文件末尾有`autocmd BufWritePost $MYVIMRC source $MYVIMRC`使之即时生效，所以上面高亮配置就起作用了。但是，每次启动vim并不能让这些设定生效。查了些资料，以及在vim中`:help highlight`，通过自动命令`autocommand`把以上设置置入针对python文件类型的设置中，可以正常工作了。


```ini
" 配置Function高亮，可视模式选择范围的前景色设置成yellow
au Filetype python highlight Function cterm=Bold,underline ctermbg=black ctermfg=green
au Filetype python highlight Visual ctermfg=yellow
"一旦一行的字符超出80个的话就把那些字符的背景设为红色"
au Filetype python highlight OverLength ctermbg=red ctermfg=white guibg=#592929
au Filetype python match OverLength /\%81v.\+/
```


##### leader，是所谓前导键。
它是在vim中通过按键运行复合命令时率先要按下的键。
```ini
let mapleader=";"
```


#### 插件安装配置


##### 插件总管Vundle

<!-- #region -->
需要**手动安装**。

    1. 先创建目录
```bash
cd ~
mkdir .vim/bundle
```

    2. 然后拉库置入
```bash
git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
```
    3. 修改`.vimrc`，增加配置内容行
```ini
filetype off
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
Plugin 'VundleVim/Vundle.vim'
Plugin 'Lokaltog/vim-powerline'    “用powerline示例，如需其他插件依次增加在begin()和end()之间即可
call vundle#end()
filetype on
filetype plugin indent on
```
保存对`.vimrc`的修改退出`:wq`重新进入vim使之生效，然后`:PluginInstall`即可完成安装。
<!-- #endregion -->

##### YouCompleteMe
自动补全神器，是一款编译型的插件。

<!-- #region -->
1. 通过Vundle安装
```ini
Plugin 'Valloric/YouCompleteMe'
```
2. 手工编译。

    1. 需要安装`cmake`和`clang`:
``` pkg install cmake clang```

    2. 然后进目录编译
```bash
cd ~/.vim/bundle/YouCompleteMe
./install.py --clang-completer # 安装好多东西，需要一点时间
```
    3. *启动vim显示ycm服务无法启动，查看`usr/tmp`下的log文件提示找不到`libbd1.so.2`，google之，在[靠谱的链接](https://github.com/ycm-core/YouCompleteMe/issues/3262)发现是因为The upstream libclang binaries are not compatible with your platform.这样install的时候增加如上`--system-clang`命令就行了。*
```bash
cd ~/.vim/bundle/YouCompleteMe
./install.py --clang-completer --system-clang
```

3. `.vimrc`中配置。
```ini
"默认配置文件路径"
let g:ycm_global_ycm_extra_conf = '~/.ycm_extra_conf.py'
"打开vim时不再询问是否加载ycm_extra_conf.py配置"
let g:ycm_confirm_extra_conf=0
set completeopt=longest,menu
"python解释器路径"
let g:ycm_path_to_python_interpreter='/usr/local/bin/python'
"是否开启语义补全"
let g:ycm_seed_identifiers_with_syntax=1
"是否在注释中也开启补全"
let g:ycm_complete_in_comments=1
let g:ycm_collect_identifiers_from_comments_and_strings = 0
"开始补全的字符数"
let g:ycm_min_num_of_chars_for_completion=2
"补全后自动关机预览窗口"
let g:ycm_autoclose_preview_window_after_completion=1
" 禁止缓存匹配项,每次都重新生成匹配项"
let g:ycm_cache_omnifunc=0
"字符串中也开启补全"
let g:ycm_complete_in_strings = 1
"离开插入模式后自动关闭预览窗口"
autocmd InsertLeave * if pumvisible() == 0|pclose|endif
```
4. 用法。
tab键循环选项，shift tab倒着来。
<!-- #endregion -->

##### taglist，显示程序文件的结构（函数、变量等）方便跳转

<!-- #region -->
1. 安装ctags程序，这是插件依赖的开展工作的玩意儿
```bash
pkg instal ctags
```
2. `.vimrc`里面插件部分中添加
```ini
Plugin vim-scripts/taglist.vim.git
```
然后，在`vim`中`:`进入命令，`PluginInstall`

3. 相关配置行
```ini
filetype on
let g:ctrlp_map='<C-p>'
let Tlist_Ctags_Cmd = '~/../usr/bin/ctags'    "指定ctags的路径
let Tlist_Show_One_File = 1        "不同时显示多个文件的tag，只显示当前文件的
let Tlist_Exit_OnlyWindow = 1      "如果taglist窗口是最后一个窗口，则退出vim
let Tlist_Use_Right_Window = 1     "在右侧窗口中显示taglist窗口
let Tlist_GainFous_on_ToggleOpen=1    "taglist小窗口打开，立即切换回主编辑窗口
map <leader>ct :! ctags -R --languages=python<CR>    "运行ctags程序，生成tags
map <leader>tt :TlistToggle<CR>    "开关TagList小窗口的快捷键
```
<!-- #endregion -->

*`vim`窗口中切换，在tag窗口和主编辑窗口来回切换。__ctrl+w+j/k，通过j/k可以上下切换，或者:ctrl+w加上下左右键，还可以通过快速双击ctrl+w依次切换窗口。__*


##### autopep8是PEP8规范自动格式化插件

<!-- #region -->
1. 需要系统命令autopep8，手动安装
```bash
pip install --upgrade autopep8
```


2. `.vimrc`里面插件部分中添加
```ini
Plugin tell-k/vim-autopep8
```
<!-- #endregion -->

##### ale是异步化运行的代码静态检查插件

<!-- #region -->
1. 需要python工具包pylint，手动安装并配置
```bash
pip install pylint
```
<!-- #endregion -->

```python
!pylint --version
```

    1. 在当前目录下生成配置文件

```python
!pylint --persistent=n --generate-rcfile > pylint.conf
```

    2. 配置文件生效的地方

``
pylintrc in the current working directory
.pylintrc in the current working directory
If the current working directory is in a Python module, Pylint searches up the hierarchy of Python modules until it finds a pylintrc file. This allows you to specify coding standards on a module-by-module basis. Of course, a directory is judged to be a Python module if it contains an __init__.py file.
The file named by environment variable PYLINTRC
if you have a home directory which isn’t /root:
.pylintrc in your home directory
.config/pylintrc in your home directory
/etc/pylintrc
``

***记得将生成的`pylint.conf`更改为`pylintrc`才能自动生效***


    3. 文档中使用

<!-- #region -->
        1. 模块级别

```python
#! usr/bin/python
#pylint: disable=invalid-name
 
''' Docstring... '''
```
        2. 行级别
```python
def file_travesal(dirtectory='.', file_list=[]): # pylint: disable=W0102
    '''
    Get file list from the directory including files in its subdirectories.
    '''
    file_list += [join(dirtectory, f) for f in listdir(dirtectory)
                if isfile(join(dirtectory, f))]
    for item in listdir(dirtectory):
        if isdir(join(dirtectory, item)):
            file_travesal(join(dirtectory, item), file_list)
```
<!-- #endregion -->

```python
!pylint --rcfile=pylint.conf wiki.py
```

```python
!ls
```

2. `.vimrc`里面插件部分添加
```ini
Plugin w0rp/ale
```


3. 相关配置内容
```ini
"ale
"是否始终开启标志列
let g:ale_sign_column_always = 0
let g:ale_set_highlights = 1
"自定义error和warning图标
let g:ale_sign_error = '✗'
let g:ale_sign_warning = '⚡'
"在vim自带的状态栏中整合ale
let g:ale_statusline_format = ['✗ %d', '⚡ %d', '✔ OK']
"显示Linter名称,出错或警告等相关信息
let g:ale_echo_msg_error_str = 'E'
let g:ale_echo_msg_warning_str = 'W'
let g:ale_echo_msg_format = '[%linter%] %s [%severity%]'
"普通模式下，sp前往上一个错误或警告，sn前往下一个错误或警告
nmap sp <Plug>(ale_previous_wrap)
nmap sn <Plug>(ale_next_wrap)
"<Leader>s触发/关闭语法检查。这个超实用，平时关闭即可，必要的时候再打开。
nmap <Leader>as :ALEToggle<CR>
"<Leader>d查看错误或警告的详细信息，实测没啥卵用，就是在代码上侧开了个quickfix，并没有显示更进一步的所谓详尽内容
nmap <Leader>ad :ALEDetail<CR>
"设置状态栏显示的内容。ale在状态栏上方新开了一行显示，下面配不配置影响也不大，不影响使用
set statusline=%F%m%r%h%w\ [FORMAT=%{&ff}]\ [TYPE=%Y]\ [POS=%l,%v][%p%%]\ %{strftime(\"%d/%m/%y\ -\ %H:%M\")}\ %{ALEGetStatusLine()}
"文件内容发生变化时不进行检查
let g:ale_lint_on_text_changed = 'never'
"打开文件时不进行检查
let g:ale_lint_on_enter = 0
```

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true -->
## termux实用工具
<!-- #endregion -->

### 传输文件，netcat

<!-- #region -->
#### 先安装netcat工具：
```bash
pkg install netcat
```
<!-- #endregion -->

#### 单文件传输

<!-- #region -->
接受文件的电脑运行：（首先运行 `ip addr show` 获取该电脑的内网 ip）
```bash
nc -lp 9999 > 2018-8-15.png
```

发送文件的电脑运行：（将下面的 ip 替换为接收文件电脑的内网 ip）

```bash
nc 192.168.1.103 9999 < 2018-8-15.png
```

就是这么简单，使用上很畅快，没有门槛可言。
<!-- #endregion -->

#### 传输文件夹

<!-- #region -->
接收电脑
```bash
nc -lp 9999 | tar -x
```

主机（文件所在）
```bash
tar -c 一个纯洁的路径 | nc 192.168.1.103 9999
```
<!-- #endregion -->

### 压缩解压工具，`7z`

<!-- #region -->
#### 语法
```bash
7z <命令行> [<选项>...] <基本档案名称> [<参数变量>...]
```
<!-- #endregion -->

#### 压缩文件

<!-- #region -->
```bash
7z a vim.zip vim/ # 压缩包中包含vim目录名称
7z a vim.zip vim/* -r # 压缩包中不包含vim目录名称
```
~~7z a sbasesh.zip *.sh -r # 压缩当前目录和所有子目录下的sh文件，测试存在问题，不能读取所有sh文件，奇怪！~~

<!-- #endregion -->

<!-- #region -->
#### 更新压缩包
```bash
7z u vim.zip vim/ # 只把更新过的文件重新压入
```
<!-- #endregion -->

<!-- #region -->
#### 解压压缩包
```bash
7z x vim.zip # 带路径结构一块解压到当前目录下
```
<!-- #endregion -->

### `git`

<!-- #region -->
1. 配置git用户名和邮箱
```bash
git config --global user.name "heart5"
git config --global user.email "baiyefeng@gmail.com"
```
在config后加上 --global 即可全局设置用户名和邮箱

2. 生成ssh key
`ssh-keygen -t rsa -C "baiyefeng@gmail.com"`

    默认在~/.ssh 目录下生成id_rsa和id_rsa.pub两个文件。如果更改了默认名称，则在当前目录下生成相应的两个文件。
    *需要给公匙私匙设置适合的文件权限600才能正确读取使用*
```bash
chmod -777 id_rsa_github*
chmod +600 id_rsa_github*
```
3. 上传key到github
    1. 复制id_rsa.pub中文本内容（也就是key）到粘贴板。`python etc/mailfun.py ~/.ssh/id_rsa_github.pub -to note`
    2. 登录github
    3. 右上方Accounting setting
    4. 选择SSH 和 GPG keys
    5. 点击Add SSH key。注意给予合适的命名，建议和运行平台计算机名称关联起来方便以后查阅。
    
4. 解决本地多个ssh key的问题
    1. 配置git用户名和邮箱
    2. 生成ssh key时指定保存的文件名
    3. 新增并配置config文件。如果config文件不存在，先添加；存在则直接修改
touch ~/.ssh/config
添加如下内容：
```ini
Host *github.com
IdentityFile ~/.ssh/id_rsa_github
User heart5
```
注意事项：如果known_hosts中有无效的key请删除，否则github.com回发出反探测警告并拒绝连接。

5. 测试是否配置成功
```bash
ssh -T git@github.com
```

6. 进入代码项目目录下，操作时不成功需要重新初始化
git init
然后本地代码基地目录再拉库（会自动建立以项目名称命名的文件夹）
git clone https://github.com/heart5/everwork
<!-- #endregion -->

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true -->
## python的各种必须工作库
<!-- #endregion -->

### numpy、pandas、scipy和jupyter等等


每次重装termux到了这一步都是痛苦的不要不要的，压根儿搞不懂pandas等必要库是否能够安装成功，这次也不例外。numpy可以直接`pip install numpy`，版本到了1.18.1。安装pandas时又是各种满屏的红色错误提示。重复了好几次，都没有办法按照原来成功的路径搞定。再次搜索，终于在[Installing-ML-In-Termux-Python](https://github.com/sanheensethi/Installing-ML-In-Termux-Python "把机器学习环境装入termux")找到了一个解决办法。虽然是机器学习相关，但是和我这种还没到那一步的还是密切相关紧密关联的，其中numpy、pandas、matplotlib和jupyter的安装需求是一样一样的。

git clone下来，运行脚本，一屏一屏的信息（居然还是彩色的，看来作者是个讲究人儿）。看到编译numpy时慢慢腾腾的劲儿，我估计是稳了，因为前面直接安装时一般都是运行没有一下就出错终止了。首次运行，没有完全安装成功，但关键的pandas倒是装好了。进去脚本看看内容，做了些调整，感觉是找对地方了。于是，再次重装termux，然后运行修改后的脚本。okay！


【**成功运行并安装成功的脚本内容如下**】

```python
# %load /data/data/com.termux/files/home/gitbase/Installing-ML-In-Termux-Python/ml-install.sh
# Regular.          # Bold.             # Underline.        # High Intensity.   # BoldHigh Intens.  # Background.       # High Intensity Backgrounds
Bla='\033[0;30m';     BBla='\033[1;30m';    UBla='\033[4;30m';    IBla='\033[0;90m';    BIBla='\033[1;90m';   On_Bla='\033[40m';    On_IBla='\033[0;100m';
Red='\033[0;31m';     BRed='\033[1;31m';    URed='\033[4;31m';    IRed='\033[0;91m';    BIRed='\033[1;91m';   On_Red='\033[41m';    On_IRed='\033[0;101m';
Gre='\033[0;32m';     BGre='\033[1;32m';    UGre='\033[4;32m';    IGre='\033[0;92m';    BIGre='\033[1;92m';   On_Gre='\033[42m';    On_IGre='\033[0;102m';
Yel='\033[0;33m';     BYel='\033[1;33m';    UYel='\033[4;33m';    IYel='\033[0;93m';    BIYel='\033[1;93m';   On_Yel='\033[43m';    On_IYel='\033[0;103m';
Blu='\033[0;34m';     BBlu='\033[1;34m';    UBlu='\033[4;34m';    IBlu='\033[0;94m';    BIBlu='\033[1;94m';   On_Blu='\033[44m';    On_IBlu='\033[0;104m';
Pur='\033[0;35m';     BPur='\033[1;35m';    UPur='\033[4;35m';    IPur='\033[0;95m';    BIPur='\033[1;95m';   On_Pur='\033[45m';    On_IPur='\033[0;105m';
Cya='\033[0;36m';     BCya='\033[1;36m';    UCya='\033[4;36m';    ICya='\033[0;96m';    BICya='\033[1;96m';   On_Cya='\033[46m';    On_ICya='\033[0;106m';
Whi='\033[0;37m';     BWhi='\033[1;37m';    UWhi='\033[4;37m';    IWhi='\033[0;97m';    BIWhi='\033[1;97m';   On_Whi='\033[47m';    On_IWhi='\033[0;107m';

echo "${Pur}Hello !";
echo "${Pur}This is Sanheen Sethi(备注：脚本原作者)";
echo "${Pur}We are Installing ML-Libraries in Android.";

echo "${Blu}Updating Termux Files(更新termux安装源并自动升级所有程序，顺手解决对存储设备的访问权限)";
echo "${Red}";
apt update -y
apt upgrade -y
termux-setup-storage
echo "";

echo "${Red}Installing Libraries to install Python and  Python ML Pakages(开始安装机器学习相关库和工具)";
echo "${Gre}";
echo "";

echo "${Blu}Installing Clang";
echo "${Gre}";
apt install clang -y
echo "";

echo "${Blu}Installing Git";
echo "${Gre}";
apt install git -y
echo "";

echo "${Blu}Installing Python";
echo "${Gre}";
apt install python -y
echo "";

echo "${Blu}Installing fftw";
echo "${Gre}";
apt install fftw -y
echo "";

echo "${Blu}Installing libzmq";
echo "${Gre}";
apt install libzmq -y
echo "";

echo "${Blu}Installing freetype";
echo "${Gre}";
apt install freetype -y
echo "";

echo "${Blu}Installing libpng";
echo "${Gre}";
apt install libpng -y
echo "";

echo "${Blu}Installing pkg-config";
echo "${Gre}";
apt install pkg-config -y
echo "";

echo "${Blu}Updating PIP";
echo "${Gre}";
pip install --upgrade pip
echo "";

echo "${Blu}Installing Numpy";
echo "${Gre}";
LDFLAGS=" -lm -lcompiler_rt" pip install numpy
echo "";

echo "${Blu}Installing Zlib Zlib-dev";
echo "${Gre}";
apt install zlib zlib-dev
echo ""

echo "${Blu}Installing Matplotlib";
echo "${Gre}";
LDFLAGS=" -lm -lcompiler_rt" pip install matplotlib
echo "";

echo "${Blu}Installing Pandas";
echo "${Gre}";
LDFLAGS=" -lm -lcompiler_rt" pip install pandas
echo "";

echo "${Blu}Installing Jupyter";
echo "${Gre}";
LDFLAGS=" -lm -lcompiler_rt" pip install jupyter
echo "";

echo "${Blu}Installing Wget";
echo "${Gre}";
apt install wget -y
echo "";

echo "${Blu}Installing Scipy(这里直接借用了pointless的资源)";
echo "${Gre}";
$PREFIX/bin/wget https://its-pointless.github.io/setup-pointless-repo.sh 
bash setup-pointless-repo.sh
apt install scipy -y
echo "";

echo "${Blu}Installing OPEN-CV";
echo "${Gre}";
apt install opencv -y
echo "";

pip install jupyter
pip install numpy
pip install matplotlib
pip install pandas

echo "${Pur}Instructions to Use :";
echo "";
echo "${Red}Using Jupyter type in shell : jupyter notebook (Press-Enter)";
echo "";
echo "${Red}Using MatplotLib in jupyter type : ";
echo "${Red}import matplotlib";
echo "${Red}%matplotlib inline";
echo ""


```

```python
!vim --version | grep clipboard
```

#### 华为P8max（android版本：5.1.1）


用以上脚本安装，在pandas安装时总是出错。试试老方法。（这也就意味着有不老少库是经过ML脚本已经安装过的）


##### 更新pip源


**更改pip源为国内**

linux系统下，修改 ~/.pip/pip.conf (没有就创建一个)， 内容如下：
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```


#### 相关安装

<!-- #region -->
```bash
apt install python2 python # 安装了老版本的python2和现有版本的python3
pip install --upgrade pip # 升级pip到最新版本
pip install BeautifulSoup4 requests
apt-get --assume-yes install pkg-config clang libxml2 libxslt libcrypt
apt install openssl openssl-tool
pip install lxml Cython # 安装lxml时转了半天
pip install scrapy # 成功安装
apt --assume-yes install fftw libzmq freetype libpng
LDFLAGS=" -lm -lcompiler_rt" pip install numpy==1.12.1 # 除开itpointless安装法，在P8max上还真只有这个版本可以安装成功
LDFLAGS=" -lm -lcompiler_rt" pip install pandas jupyter
LDFLAGS=" -lm -lcompiler_rt" pip install matplotlib scipy
```
<!-- #endregion -->

### everwork相关

<!-- #region -->
```bash
pip install bs4 evernote3 py2ifttt xlrd oauth2 oauth2client openpyxl xpinyin yagmail itchat wrapt  google_auth_oauthlib odps cython
pip install pygsheets==1.1.4 # 高版本搞不好，就只能这个了
pip install jupytext==1.3.1 # ipynb适配git的插件。不知道咋地，备份系统上版本升不上去，为了避免meta变化导致没必要的签入签出，强制两边版本一样算了，就低。
pip install cython # 安装line_profiler时需要
```
<!-- #endregion -->

### line_profiler库


#### 安装

<!-- #region -->
```bash
git clone https://github.com/rkern/line_profiler.git
find line_profiler -name '*.pyx' -exec cython {} \;
cd line_profiler && pip install . --user
```
<!-- #endregion -->

#### 关于`kernprof`脚本启用

<!-- #region -->
不知道咋地，需要手动设置软连接才行。
```bash
cd ~/../usr/bin
ln -s ~/ghub/line_profiler/kernprof.py kernprof
```
<!-- #endregion -->

#### 使用

<!-- #region -->
##### 在函数上面加载装饰器
```python
@profile
def ttt():
    pass
```

然后命令行运行
```bash
kernprof -l fileincludettt.py
```

`kernprof`会把分析结果放在`fileincludettt.py.lprof`的二进制文件中

查看分析结果命令如下：
```bash
python -m line_profiler fielincludettt.py.lprof
```
<!-- #endregion -->

##### `import line_profiler`法

<!-- #region -->
1. 单个函数

```python

from line_profiler import LineProfiler
import random
 
def do_stuff(numbers):
    s = sum(numbers)
    l = [numbers[i]/43 for i in range(len(numbers))]
    m = ['hello'+str(numbers[i]) for i in range(len(numbers))]
 
numbers = [random.randint(1,100) for i in range(1000)]
lp = LineProfiler()
lp_wrapper = lp(do_stuff)
lp_wrapper(numbers)
lp.print_stats()
```

2. 嵌套函数分别输出（直接使用只能显示被调用函数的总时间）

```python
from line_profiler import LineProfiler
import random
 
def do_other_stuff(numbers):
    s = sum(numbers)
 
def do_stuff(numbers):
    do_other_stuff(numbers)
    l = [numbers[i]/43 for i in range(len(numbers))]
    m = ['hello'+str(numbers[i]) for i in range(len(numbers))]
 
numbers = [random.randint(1,100) for i in range(1000)]
lp = LineProfiler()
lp.add_function(do_other_stuff)   # add additional function to profile
lp_wrapper = lp(do_stuff)
lp_wrapper(numbers)
lp.print_stats()
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

### PIL安装

<!-- #region -->
```bash
pip install pillow
```

太大了（有38M），一次性拉下来经常出错，加参数：
```bash
pip --default-timeout=500 install -U Pillow
```
<!-- #endregion -->

## jupyter notebook配置


1. 配置文件和密码

    `jupyter notebook --generate-config`
    
    在~/.jupyter文件夹下生成一个jupyter_notebook_config.py配置文件
    
    `jupyter notebook password    # 如果4`
    
    生成远程登录需要的密码,自己填,密码会直接输出到jupyter_notebook_config.json文件

2. 编辑配置文件
    ```ini
    # Set ip to '*' to bind on all interfaces (ips) for the public server
    c.NotebookApp.ip = '*'
    c.NotebookApp.open_browser = False

    # It is a good idea to set a known, fixed port for server access
    c.NotebookApp.port = 8888

    c.Notebookapp.allow_remote_access = True
    c.NotebookApp.allow_root = True
    ```
3. 启动即可,记着搞清楚服务器的ip地址(ifconfig)

    `jupyter notebook --allow-root`

4. 访问地址，网址形如：`192.168.154.114:8888`

5. 支持jupytext
在配置文件末尾加入：
```ini
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
```


## Jupyterlab安装使用

<!-- #region -->
#### 安装指定版本的jupyter，目前已知的有1.2.6和2.0.1

```bash
pip install jupyterlab==1.2.6
```
<!-- #endregion -->

### 插件安装


##### `toc`

<!-- #region -->
```bash
jupyter labextension install @jupyterlab/toc
```
<!-- #endregion -->

#### `git`

<!-- #region -->
```bash
pip install --upgrade jupyterlab-git
jupyter lab build
```
<!-- #endregion -->

### 插件无法运作

在setting中把扩展配置修改为true后，左侧边栏出现相应按钮，点进去出错：
```
Error communicating with server extension. Consult the documentation for how to ensure that it is enabled.

Reason given:

Error: 500 (Internal Server Error)
```
对照版本，9X Max的jupyterlab版本是1.2.6，而bs2pro主系统经过一番折腾，已经是2.0.1了。不甘心降回去，上网找找吧。

<!-- #region -->
安装必要的nodejs：
```
pkg install nodejs-lts
```
然后运行：
```
jupyter labextension list
```
输出如下：
```bash
Fail to get yarn configuration. 
Fail to get yarn configuration. 
JupyterLab v2.0.1
Known labextensions:
   app dir: /data/data/com.termux/files/usr/share/jupyter/lab
        jupyterlab-jupytext v1.1.1  enabled   X

   The following extension are outdated:
        jupyterlab-jupytext
        
   Consider running "jupyter labextension update --all" to check for updates.
```
<!-- #endregion -->

```python
!jupyter labextension update --all
```

```python
!jupyter labextension list
```

```python
!jupyter lab build
```

### 解决yarn、nodejs的版本问题

```python
!node -v
```

```python
!npm -v
```

```python
!jupyter labextension list
```

```python
!jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

### 神奇的root模式


终止jupyter-lab服务重新启动，插件居然可以正常显示了。查看后台还是有`Fail to get yarn configuration. `的出错提示。~~不管那么多了，能用就好~~。我们还是要聚焦要搞的项目，对于平台工具能用就好！


实际上还是不行，这个fail犹如梦魇，导致jupyterlab在build时老是失败。网上搜了半天，最终决定还是重装nodejs（因为版本新些）。中间还尝试了解决yarn的问题，需要`termux-chroot`进入root模式。在root模式完成了yarn（不知道有没有用）、nodejs和jupyterlab的安装后退出该模式。运行：

```python
!jupyter labextension list
```

```python
!jupyter labextension update --all
```

### 关于jupyterlab的版本


这是jupyterlab版本和这个插件不兼容的问题。查询了备份机上是1.2.6，而主机上安装自动上了2.0.1

```python
!pip search jupyterlab extension
```

```python
!pkg show nodejs-lts
```

```python
!pkg show nodejs
```

<!-- #region -->
安装指定版本的jupyterlab
```bash
pip install jupyterlab==1.2.6
```
会自动删安装好的库，然后装上这个版本。
<!-- #endregion -->

### 【jupyter labextension 命令】


jupyter labextension install @jupyterlab/toc #安装指定插件

jupyter labextension uninstall @jupyterlab/toc #卸载指定插件

jupyter labextension list #列出已安装的所有插件

jupyter labextension update --all # 更新所有已安装插件到最新版本


~~**【没事不要安装新插件，不要尝试，管住手】**~~

jupyterlab-lsp就是个大坑，浪费了n多时间！！！

**【能用就是福，且用且珍惜】**


### 输出所有变量值


#### 默认情况下，Code Cell 只输出最后一个可以被 evaluate 的值，用 _ 代表之前刚刚被 evaluate 的值。

```python
_
```

为了显示最近 evaluate 的多个值，我们总是不得不使用很多的 print()……为了避免这种情况，我们用如下方式解决。


##### 在当前notebook默认输出所有变量值，可以在 Cell 最上面写上：

<!-- #region -->
```python
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
```
<!-- #endregion -->

##### 对所有新打开的notebook生效，则在配置文件增加：


```ini
c.InteractiveShell.ast_node_interactivity = "all"
```


```ini
InteractiveShell.ast_node_interactivity
```

【**关于配置文件**】
1. jupyter和jupyterlab都基于IPython。上面说的配置文件指的就是IPython的[配置文件](https://ipython.readthedocs.io/en/stable/config/intro.html "IPython配置文件官方指南")。
    
2. 生成ipython配置文件。`ipython profile create`，会在目录`~/.ipython/profile_default/`中自动生成默认的配置文件`ipython_config.py`和`ipython_kernel_config.py`
    
3. 修改完善配置文件内容。下面是官方示例配置文档。【**注意拼写检查和其他设置，IPython处理配置文件时会自动忽略错误行而不做任何提示**】
```ini
        c = get_config() # 获得root（顶级）配置对象，以便进行调整
        c.TerminalIPythonApp.display_banner = True
        c.InteractiveShellApp.log_level = 20
        c.InteractiveShellApp.extensions = [
            'myextension'
        ]
        c.InteractiveShellApp.exec_lines = [
            'import numpy',
            'import scipy'
        ]
        c.InteractiveShellApp.exec_files = [
            'mycode.py',
            'fancy.ipy'
        ]
        c.InteractiveShell.colors = 'LightBG'
        c.InteractiveShell.confirm_exit = False
        c.InteractiveShell.editor = 'vim'
        c.InteractiveShell.xmode = 'Context'

        c.PrefilterManager.multi_line_specials = True

        c.AliasManager.user_aliases = [
         ('la', 'ls -al')
        ]
```
4. [有用的相关讨论](https://stackoverflow.com/questions/36786722/how-to-display-full-output-in-jupyter-not-only-last-result "来自stackoverflow")

### 魔法函数


Jupyterlab 里较为常用的魔法函数整理如下：

魔法函数|	说明|
:---:|:--
%lsmagic	|列出所有可被使用的 Jupyter lab 魔法函数
%run	|在 Cell 中运行 .py 文件：%run file_name
%who	|列出所有当前 Global Scope 中的变量；类似的还有：%who df，%whos
%env	|列出当前的环境变量
%load	|将其他文件内容导入 Cell，%load source，source 可以是文件名，也可以是 URL。
%time	|返回 Cell 内代码执行的时间，相关的还有 %timeit
%writefile	|把 Cell 的内容写入文件，%write file_name；%write -a file_name，-a 是追加
%matplotlib inline	|行内展示 matplotlib 的结果
%%bash	|运行随后的 shell 命令，比如 %%bash ls；与之类似的还有 %%HTML，%%python2，%%python3，%%ruby，%%perl……

```python
%env
```

```python
%lsmagic
```

```python
%pip install conda
```

```python
%timeit
!ps
%timeit
```

## 其他

```python

```
