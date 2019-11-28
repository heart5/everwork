import pathmagic

with pathmagic.context():
    from func.logme import log
    from work.fetchdata import fetchworkfile_from_gmail

if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    fetchworkfile_from_gmail('')
    log.info(f'文件{__file__}运行结束！')

