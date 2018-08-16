# encoding:utf-8
"""
模块说明
"""
import datetime
import platform
import os
import time
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
    # for key in env_dlist:
    #    print(key, env_dlist[key])
    onedrivedir = Path(env_dlist['onedrive'])
    # zipfilename = f'datauto_{platform.node()}.zip'
    zipfilename = f"datauto_{platform.uname().system}_{platform.uname().machine}_{platform.uname().node}.zip"
    # print(zipfilename)
    zipfilenamenew = zipfilename.replace('.zip', '_other.zip')
    # print(zipfilenamenew)
    targetzipdir = Path(onedrivedir) / '文档' / 'Program' / 'python' / 'everworkdataonly'
    targetzipfile = targetzipdir / zipfilename
    addextstr = datetime.datetime.now().strftime("_%Y%m%d%H%M%S")
    zipfilename = f"datauto_{platform.uname().system}_{platform.uname().machine}_{platform.uname().node}{addextstr}.zip"
    targetzipfileadd = targetzipdir / zipfilename
    # print(targetzipfileadd)
    targetzipfilenew = targetzipdir / zipfilenamenew
    # print(targetzipfilenew)
    # print(targetzipfile)
    flnamesinzip = dict()
    if not targetzipfile.is_file():
        print(f'{targetzipfile}文件不存在，需要创建。')
        touchfilepath2depth(targetzipfile)
    elif not zipfile.is_zipfile(targetzipfile):
        print(f'{targetzipfile}不是一个合格的zip文件。')
        targetzipfile = targetzipfilenew
    elif zipfile.is_zipfile(targetzipfile):
        print(f'合格的zip文件{targetzipfile}已经存在。')
        targetzip = zipfile.ZipFile(str(targetzipfile), 'r')
        # print(targetzip)
        filesinzip = targetzip.namelist()
        for filein in filesinzip:
            fileinfo = targetzip.getinfo(filein)
            fileinname = fileinfo.filename
            filestructtime = fileinfo.date_time[0:6]
            fileinmtime = datetime.datetime(*filestructtime).strftime('%F %T')
            flnamesinzip[fileinname] = fileinmtime
            # print(flnamesinzip)
            # print(f'{fileinname}\t{fileinmtime}')
        # print(targetzip.filelist())
        # print(flnamesinzip)
        # print(targetzip.infolist())
        targetzip.close()

    log.info(f'压缩目录《{sourcedir}》到OneDrive文件夹实现自动同步')
    # print(flnamesinzip.keys())
    filelist = list()
    for dirpath, dirnames, filenames in os.walk(sourcedir):
        for filename in filenames:
            filelist.append(os.path.join(dirpath, filename))
    # print(filelist)

    updateoradd = list()
    for tar in filelist:
        flmtime = time.strftime('%F %T', time.localtime(os.path.getmtime(tar)))
        # print(f'{tar[len(sourcedir) + 1:]}')
        if tar[len(sourcedir) + 1:].replace('\\', '/') in flnamesinzip.keys():
            flmtimeinzip = flnamesinzip[tar[len(sourcedir) + 1:].replace('\\', '/')]
            dtzip = datetime.datetime.strptime(flmtimeinzip, '%Y-%m-%d %H:%M:%S')
            dtnow = datetime.datetime.strptime(flmtime, '%Y-%m-%d %H:%M:%S')
            if dtnow > dtzip:
                timespan = dtnow - dtzip
            else:
                timespan = dtzip - dtnow
            # print(timespan.total_seconds())
            if timespan.total_seconds() > 1:
                print(f'{tar}文件已存在，且有更新。{flmtime}\t{flmtimeinzip}')
                updateoradd.append(tar)
            # else:
            #     print(f'{tar}文件已存在，暂无更新。')
        else:
            print(f'{tar}\t文件需要添加')
            updateoradd.append(tar)
    if len(updateoradd) == 0:
        log.info(f'没有发现需要更新的文件。')
        return
    else:
        newzip = zipfile.ZipFile(str(targetzipfileadd), 'w', zipfile.ZIP_DEFLATED)
        for tar in updateoradd:
            # print(f'{tar[len(sourcedir):]}\t{time.strftime("%F %T", flmtime)}')
            # newzip.write(tar, tar[len(sourcedir):])  # tar为写入的文件，tar[len(filePath)]为保存的文件名
            try:
                newzip.write(tar, tar[len(sourcedir):])
            except FileNotFoundError as fnfe:
                log.critical(f'文件找不到，可能是临时文件。{tar}\t{fnfe}')
            except OSError as ose:
                log.critical(f'出现系统错误。{ose}')
        newzip.close()
        log.info(f'成功压缩{updateoradd}备份至：{targetzipfileadd}')


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

    zipdata2one_timer(60 * 60 * 12 + 60 * 35)

    print('Done.测试完成。')
