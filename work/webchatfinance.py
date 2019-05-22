import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.splitwebchatmsgs import showjinzhang, showshoukuan


def showfinance():
    showjinzhang()
    showshoukuan()


if __name__ == '__main__':
    log.info(f'开始测试文件\t{__file__}')
    showfinance()
    log.info(f'对\t{__file__}\t的测试结束。')

