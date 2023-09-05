# encoding:utf-8
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
#
"""
进程和线程学习

"""

# %%
from multiprocessing import Process, Pool, Queue
import os, sys, locale, time, random, subprocess


# %%
# 子进程要执行的代码
def run_proc(name):
    print('Run child process %s (%s)...' % (name, os.getpid()))


# %%
def test1():
    print('Parent process %s.' % os.getpid())
    p = Process(target=run_proc, args=('test',))
    print('Child process will start.')
    p.start()
    p.join()
    print('Child process end.')


# %%
def long_time_task(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))


# %%
def test2():
    print('Parent process %s.' % os.getpid())
    p = Pool()  # 默认大小是运行计算机的CPU内核数量，也可以手动指定
    for i in range(12):
        p.apply_async(long_time_task, args=(i,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')


# %%
def test_subprocess1():
    print('$ nslookup www.python.org')
    r = subprocess.call(['nslookup', 'heart5.com'])
    print('Exit code:', r)


# %%
def test_subporcess2():
    print('$ nslookup')
    p = subprocess.Popen(['nslookup'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate(b'set q=mx\nbyf.com\nexit\n')
    print(sys.getdefaultencoding())  # 系统的缺省编码
    print(locale.getdefaultlocale())  # 系统当前的编码
    tp, encoding_local = locale.getdefaultlocale()
    print(locale.getlocale())  # 系统代码中临时被更改的编码
    print(sys.getfilesystemencoding())  # 文件系统的编码
    print(sys.stdin.encoding)  # 终端的输入编码
    print(sys.stdout.encoding)  # 终端的输出编码
    print(output.decode(encoding_local))
    print('Exit code:', p.returncode)


# %%
# 写数据进程执行的代码:
def write(q):
    print('Process to write: %s' % os.getpid())
    for value in range(10):
        print('Put %s to queue...' % value)
        q.put(value)
        time.sleep(random.random())


# %%
# 读数据进程执行的代码:
def read(q):
    print('Process to read: %s' % os.getpid())
    while True:
        time.sleep(random.random())
        value = q.get(True)
        print('Get %s from queue.' % value)


# %%
if __name__ == '__main__':
    # 父进程创建Queue，并传给各个子进程：
    q = Queue()
    pw = Process(target=write, args=(q,))
    pr = Process(target=read, args=(q,))
    # 启动子进程pw，写入:
    pw.start()
    # 启动子进程pr，读取:
    pr.start()
    # 等待pw结束:
    pw.join()
    # pr进程里是死循环，无法等待其结束，只能强行终止:
    pr.terminate()

# %% [markdown]
# if __name__=='__main__':
# test1()
# test2()
# test_subprocess1()
# test_subporcess2()
# test_processqueue()
