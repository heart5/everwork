# encoding:utf-8
"""
模块说明
"""
import platform
import os
import zipfile
os.sys.path.append('/storage/emulated/0/.0code/everwork/everwork')
os.sys.path.append('~/ewbase/func')
print(os.sys.path)
from pathlib import Path
from threading import Timer
from func.first import dirmainpath, touchfilepath2depth
from func.logme import log


def zipdir2one():
    sourcedirpath = dirmainpath / 'data'
    sourcedir = str(sourcedirpath)
    env_dlist = os.environ
    #for key in env_dlist:
    #    print(key, env_dlist[key])
    onedrivedir = Path(env_dlist['onedrive'])
    #zipfilename = f'datauto_{platform.node()}.zip'
    zipfilename = f"datauto_{platform.uname().system}_{platform.uname().machine}_{platform.uname().node}.zip"
    print(zipfilename)
    zipfilenamenew = zipfilename.replace('.zip', '_other.zip')
    print(zipfilenamenew)
    targetzipdir = Path(onedrivedir) / '文档' / 'Program' / 'python' / 'everworkdataonly'
    targetzipfile = targetzipdir / zipfilename
    targetzipfilenew = targetzipdir / zipfilenamenew
    print(targetzipfilenew)
    print(targetzipfile)
    if not targetzipfile.is_file():
        print(f'{targetzipfile}文件不存在，需要创建。')
        touchfilepath2depth(targetzipfile)
    elif not zipfile.is_zipfile(targetzipfile):
        print(f'{targetzipfile}不是一个合格的zip文件。')
        targetzipfile =targetzipfilenew
    else:
        targetzip = zipfile.ZipFile(str(targetzipfile), 'r')
        print(targetzip.namelist())
        targetzip.close()

    log.info(f'压缩目录《{sourcedir}》到OneDrive文件夹实现自动同步')
    filelist = list()
    newzip = zipfile.ZipFile(str(targetzipfile), 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(sourcedir):
        for filename in filenames:
            filelist.append(os.path.join(dirpath, filename))
    # print(filelist)

    for tar in filelist:
        newzip.write(tar, tar[len(sourcedir):])  # tar为写入的文件，tar[len(filePath)]为保存的文件名
    newzip.close()
    log.info(f'成功压缩备份至：{targetzipfile}')


def zipdata2one_timer(jiangemiao):
    try:
        zipdir2one()
    except ValueError as wve:
        log.critical(f'自动备份至OneDrive目录时出现错误。{wve}')
    global timer_zip2one
    timer_zip2one = Timer(jiangemiao, zipdata2one_timer, [jiangemiao])
    timer_zip2one.start()


if __name__ == '__main__':
    print(f'开始测试文件\t{__file__}')
    # zipdir2one()

    zipdata2one_timer(60 * 154)

    print('Done.测试完成。')
