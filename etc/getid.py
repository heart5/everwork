# encoding:utf-8
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       jupytext_version: 1.10.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
"""
获取主机的唯一id
"""

# %%
# import os
# import sys
import platform
import uuid
# import wmi_client_wrapper as wmi

import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue, is_log_details
#     from func.wrapfuncs import timethis, ift2phone
    from func.evernttest import getinivaluefromnote
    from func.termuxtools import termux_telephony_deviceinfo
    from func.sysfunc import execcmd, not_IPython
    try:
        import wmi
    except ImportError:
        # log.warning('wmi库未安装或者是在linux系统下无法成功import而已。')
        # print('wmi库未安装或者是在linux系统下无法成功import而已。')
        pass


# %%
def set_devicename2ini(id, sysstr):
    if (device_name := getcfpoptionvalue('everhard', id, 'device_name')) is None:
        if (device_name_fromnote := getinivaluefromnote('device', id)):
            setcfpoptionvalue('everhard', id, 'device_name', device_name_fromnote)
        else:
            log.critical(f"当前主机（id：{id}）尚未在网络端配置笔记中设定名称或者是还没完成本地化设定！！！")
            if sysstr == 'Linux':
                log.critical(f"主机信息：{execcmd('uname -a')}")


# %%
def get_devicenamefromini(id):
    return getcfpoptionvalue('everhard', id, 'device_name')


# %%
# @timethis
def getdeviceid():
    # printCPU()
    # printMain_board()
    # printBIOS()
    # printDisk()
    # printMacAddress()
    # print(printBattery())
    if (d_id_from_ini := getcfpoptionvalue('everhard', 'everhard', 'device_id')):
        return str(d_id_from_ini)
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
        try:
            outputdict = termux_telephony_deviceinfo()
            id = outputdict["device_id"].strip()
        except Exception as e:
            print(f"运行termux专用库出错{e}\n下面尝试用主机名代替")
            try:
                idstr = execcmd("uname -n")
                print(idstr)
                uid = uuid.uuid3(uuid.NAMESPACE_URL, idstr)
                # print(uid)
                print(hex(hash(uid)))
                id = hex(hash(uid))
            except Exception as e:
                print("天啊，命令行都不成！只好强行赋值了")
                id = 123456789
                type(e)
#                 raise
    else:
        log.critical('既不是Windows也不是Linux，那是啥啊。只好强行赋值了！！！')
        id = 123456789
#         exit(1)

    id = str(id)
    setcfpoptionvalue('everhard', 'everhard', 'device_id', id)
    set_devicename2ini(id, sysstr)

    return id


# %%
if __name__ == '__main__':
    if not_IPython() and is_log_details:
        log.info(f'运行文件\t{__file__}')
    id = getdeviceid()
    set_devicename2ini(id, 'Linux')
    devicename = get_devicenamefromini(id)
    print(f"{devicename}")
    if not_IPython() and is_log_details:
        log.info(f'文件\t{__file__}\t运行完毕。')
