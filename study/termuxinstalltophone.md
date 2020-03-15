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

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true -->
## termux和termux-api安装
termux在谷歌商店的最新版本是0.92。之前一直用的是0.65（2018年），后来升级到0.66（2019年）。因为termux-api不再支持短信读取等涉及个人隐私的功能（谷歌商店限制），担心termux主版本会自动关联这个阉割，就一直没有升级。这次黑鲨升级系统，到论坛看了下貌似整体搬迁到小米（哦，不对，应该是官宣的“将JOYUI的游戏特性与MIUI完美结合”），坛友抱怨甚多，问题反馈集中在易耗电、发热甚至不稳定，所以一直没动。昨天手痒，想着termux大版本都升级那么多，应该有不少好东东，一激动就把termux和termux-api都升级了。麻烦就此来了！
<!-- #endregion -->

先安装`pkg install openssh`（这中间还犯了个输入错误，误输入成openssl，还奇怪怎么没有生成`.ssh`目录呢），添加电脑生成的公匙，然后用putty登录在电脑上操作。按照原来的笔记步骤，要更新成清华源并追加pointless源，速度快些还方便装难以搞定的numpy。但奇怪的是`apt update`并`apt upgrade`后总是莫名出错，不是系统自带命令不见了（连ls都操作不了），就是各种库报错，连apt都用不了了。把termux重装了几次都不行，恨不得怀疑人生。实在耗不过了，突然想就用官方源试试再说（其实速度也还可以，还是在vpn科学上网的状态下），结果一路绿灯，基本系统和工具安装顺利。后面就是各种对装不上pandas的折腾，下文再讲。jupyterlab也装起来，虽然插件因为nodejs的问题一直无法使用，但基本的程序还是可以跑起来的，然后一狠心，就把手机的操作系统也一起升级到JOYUI11，华丽丽的的变化很大，也放到后面讲。试车的时候发现获取位置和ip的脚本老是挂在那里跑不动。python一切正常，那问题就在termux-api上了。


在终端中运行`termux-location`等命令，挂起无反应，怀疑是版本不匹配的问题。termux-api最新的版本是0.41，手里还有0.31（还支持短信等敏感操作）和0.32（从这个版本其就不支持敏感操作了）。把三个版本逐次试了下，按照之前的经验，先要在终端中卸载`pkg uninstall termux-api`，每次更改termux-api版本安装后再次`pkg install termux-api`，状况依旧，还是挂起没商量。然后在新版本系统的手机上对termux和termux-api授予各种权限，没有任何反应。静下来仔细想了下，决定从头来过，用轮换的方法把各个组合都试一下。


出于对新版本的艳羡，先从谷歌商店的最新版开始。手机上安装termux（0.92）和termux-api（0.41），然后直接在termux窗口命令行中`pkg install termux-api`，安装成功后试运行`termux-location`，弹出提示无权限。可把我给激动坏了，终于有动静了啊。进入手机设置对termux-pai各种授权，然后回到termux窗口再次运行，哎，输出结果了。然后测试`termux-sms-list`，调试信息显示“谷歌已经不允许读取短信”。心里明白了问题所在（这个硬件相关和系统api接口需要在手机上运行并授权），卸载0.41的api，大胆的安装了termux-api（0.31），再次在手机上运行`termux-sms-list`，okay，显示正确结果。问题彻解于此！

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true -->
### termux-api安装成功操作步骤
<!-- #endregion -->

1.**手机上**安装termux和termux-api的App程序

2.在手机系统“设置”中对termux-api进行各种授权（存储空间、位置、短信等）

3.在**手机上进入termux终端命令行**：`pkg install termux-api`

4.运行测试命令：`termux-location`，okay

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true -->
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


### vim设置和插件


这个玩意儿配置好了可以上天，所以在此专条讲述


#### 【打包备份】

<!-- #region -->
全部安装设置好后，进入home目录：
```bash
7z a vim.zip .vim/ .vimrc
```

然后把打包好的vim.zip备份到云盘之类的好地儿，以后需要的时候下载下来解压`7z x vim.zip`即可。
<!-- #endregion -->

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

#### leader，是所谓前导键。
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

##### lae是异步化运行的代码静态检查插件

<!-- #region -->
1. 需要python工具包pylint，手动安装
```bash
pip install pylint
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
<!-- #endregion -->

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true toc-hr-collapsed=true toc-nb-collapsed=true -->
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

<!-- #region toc-hr-collapsed=true toc-nb-collapsed=true -->
## python必要工作库
<!-- #endregion -->

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

## Jupyterlab安装使用


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


### 输出所有变量值


#### 默认情况下，Code Cell 只输出最后一个可以被 evaluate 的值，用 _ 代表之前刚刚被 evaluate 的值。

```python
_
```

#### 为了显示最近 evaluate 的多个值，我们总是不得不使用很多的 print()……


##### 在当前notebook默认输出所有变量值，可以在 Cell 最上面写上：

```python
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
```

##### 对所有新打开的notebook生效，则在配置文件增加：


```ini
c.InteractiveShell.ast_node_interactivity = "all"
```


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

```python

```
