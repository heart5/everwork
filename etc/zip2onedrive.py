# encoding:utf-8
"""
模块说明
"""
import os
import zipfile
from pathlib import Path
from threading import Timer
from func.first import dirmainpath
from func.logme import log


def zipdir2one():
    sourcedirpath = dirmainpath / 'data'
    sourcedir = str(sourcedirpath)
    env_dlist = os.environ
    # for key in env_dlist:
    #     print(key, env_dlist[key])
    onedrivedir = Path(env_dlist['onedrive'])
    computername = env_dlist['COMPUTERNAME']
    username = env_dlist['USERNAME']
    targetzipfile = onedrivedir / '文档' / 'Program' / 'python' / 'everworkdataonly' \
                    / f'datauto_{computername}_{username}.zip'
    print(targetzipfile)
    log.info(f'压缩目录《{sourcedir}》到OneDrive文件夹实现自动同步')

    filelist = list()
    newzip = zipfile.ZipFile(str(targetzipfile), 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(sourcedir):
        for filename in filenames:
            filelist.append(os.path.join(dirpath, filename))
    print(filelist)
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
    timer_zip2one = Timer(jiangemiao, zipdir2one, [jiangemiao])
    timer_zip2one.start()


if __name__ == '__main__':
    print(f'开始测试文件\t{__file__}')
    # zipdir2one()

    zipdata2one_timer(60*100)

    print('Done.测试完成。')
