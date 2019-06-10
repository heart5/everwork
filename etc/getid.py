# encoding:utf-8
"""
功能描述
"""

import os
import sys
import platform
import uuid
# import wmi_client_wrapper as wmi

import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.configpr import getcfp, getcfpoptionvalue, setcfpoptionvalue
    from func.wrapfuncs import timethis, ift2phone
    from func.evernttest import getinivaluefromnote
    from func.termuxtools import termux_location, termux_telephony_deviceinfo
    try:
        import wmi
    except ImportError:
        # log.warning('wmi库未安装或者是在linux系统下无法成功import而已。')
        # print('wmi库未安装或者是在linux系统下无法成功import而已。')
        pass


# @timethis
def getdeviceid():
    # printCPU()
    # printMain_board()
    # printBIOS()
    # printDisk()
    # printMacAddress()
    # print(printBattery())
    d_id_from_ini = getcfpoptionvalue('everhard', 'everhard', 'device_id')
    if d_id_from_ini:
        return d_id_from_ini
    id = None
    sysstr = platform.system()
    # print(sysstr)
    if sysstr == "Windows":
        c = wmi.WMI()
        bios_id = c.Win32_BIOS()
        # biosidc = bios_id.BiosCharacteristics  # BIOS特征码
        bioss = bios_id[0].SerialNumber.strip()
        # for bios in bios_id:
        #     print(bios)
        cpu_id = c.Win32_Processor()
        cpus = cpu_id[0].SerialNumber.strip()
        cpus = cpu_id[0].ProcessorId.strip()
        # for cpu in cpu_id:
        #     print(cpu)
        board_id = c.Win32_BaseBoard()
        boards = board_id[0].SerialNumber.strip()
        # boards = board_id[0].Product.strip()
        # for board in board_id:
        #     print(board)
        disk_id = c.Win32_DiskDrive()
        disks = disk_id[0].SerialNumber.strip()
        # for disk in disk_id:
        #     print(disk)
        idstr = f'{bioss}\t{cpus}\t{boards}\t{disks}'
        uid = uuid.uuid3(uuid.NAMESPACE_URL, idstr)
        # print(uid)
        print(hex(hash(uid)))
        id = hex(hash(uid))
    elif sysstr == 'Linux':
        outputdict = termux_telephony_deviceinfo()
        id = outputdict["device_id"].strip()
    else:
        log.critical('既不是Windows也不是Linux，那是啥啊。不搞了，闪退！！！')
        exit(1)

    setcfpoptionvalue('everhard', 'everhard', 'device_id', id)

    return id


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    id = getdeviceid()
    print(id)
    devicename = getinivaluefromnote('device', id)
    print(f"{devicename}")
    log.info(f'文件\t{__file__}\t测试完毕。')
