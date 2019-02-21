# encoding:utf-8
"""
功能描述
"""

import os, sys, platform
# import wmi_client_wrapper as wmi

import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.termuxtools import termux_location, termux_telephony_deviceinfo
    try:
        import wmi
    except ImportError:
        log.warn('wmi库未安装或者是在linux系统下无法成功import而已。')

# c = wmi.WMI()
#
#
# # 处理器
# def printCPU():
#     tmpdict = {}
#
#     tmpdict["CpuCores"] = 0
#     for cpu in c.Win32_Processor():
#         tmpdict["cpuid"] = cpu.ProcessorId.strip()
#         tmpdict["CpuType"] = cpu.Name
#         tmpdict['systemName'] = cpu.SystemName
#         try:
#             tmpdict["CpuCores"] = cpu.NumberOfCores
#         except:
#             tmpdict["CpuCores"] += 1
#             tmpdict["CpuClock"] = cpu.MaxClockSpeed
#             tmpdict['DataWidth'] = cpu.DataWidth
#     print(tmpdict)
#     return tmpdict
#
#
# # 主板
# def printMain_board():
#     boards = []
#     print(len(c.Win32_BaseBoard()))
#     for board_id in c.Win32_BaseBoard():
#         tmpmsg = {}
#         tmpmsg['UUID'] = board_id.qualifiers['UUID'][1:-1]  # 主板UUID,有的主板这部分信息取到为空值，ffffff-ffffff这样的
#         tmpmsg['SerialNumber'] = board_id.SerialNumber  # 主板序列号
#         tmpmsg['Manufacturer'] = board_id.Manufacturer  # 主板生产品牌厂家
#         tmpmsg['Product'] = board_id.Product    # 主板型号
#         boards.append(tmpmsg)
#     print(boards)
#     return boards
#
#
# # BIOS
# def printBIOS():
#     bioss = []
#
#     for bios_id in c.Win32_BIOS():
#         tmpmsg = {}
#         tmpmsg['BiosCharacteristics'] = bios_id.BiosCharacteristics # BIOS特征码
#         tmpmsg['version'] = bios_id.Version # BIOS版本
#         tmpmsg['Manufacturer'] = bios_id.Manufacturer.strip()   # BIOS固件生产厂家
#         tmpmsg['ReleaseDate'] = bios_id.ReleaseDate # BIOS释放日期
#         tmpmsg['SMBIOSBIOSVersion'] = bios_id.SMBIOSBIOSVersion # 系统管理规范版本
#         bioss.append(tmpmsg)
#     print(bioss)
#
#     return bioss
#
#
# # 硬盘
# def printDisk():
#     disks = []
#
#     for disk in c.Win32_DiskDrive():
#         # print disk.__dict__
#         tmpmsg = {}
#         tmpmsg['SerialNumber'] = disk.SerialNumber.strip()
#         tmpmsg['DeviceID'] = disk.DeviceID
#         tmpmsg['Caption'] = disk.Caption
#         tmpmsg['Size'] = disk.Size
#         tmpmsg['UUID'] = disk.qualifiers['UUID'][1:-1]
#         disks.append(tmpmsg)
#     for d in disks:
#         print(d)
#
#     return disks
#
#
# # 内存
# def getPhysicalMemory():
#     memorys = []
#
#     for mem in c.Win32_PhysicalMemory():
#         tmpmsg = {}
#         tmpmsg['UUID'] = mem.qualifiers['UUID'][1:-1]
#         tmpmsg['BankLabel'] = mem.BankLabel
#         tmpmsg['SerialNumber'] = mem.SerialNumber.strip()
#         tmpmsg['ConfiguredClockSpeed'] = mem.ConfiguredClockSpeed
#         tmpmsg['Capacity'] = mem.Capacity
#         tmpmsg['ConfiguredVoltage'] = mem.ConfiguredVoltage
#         memorys.append(tmpmsg)
#     # for m in memorys:
#     #     print(m)
#
#     return memorys
#
#
# # 电池信息，只有笔记本才会有电池选项
# def printBattery():
#     isBatterys = False
#
#     for b in c.Win32_Battery():
#         isBatterys = True
#
#     return isBatterys
#
#
# # 网卡mac地址：
# def printMacAddress():
#     macs = []
#
#     for n in c.Win32_NetworkAdapter():
#         mactmp = n.MACAddress
#         if mactmp and len(mactmp.strip()) > 5:
#             tmpmsg = {}
#             tmpmsg['MACAddress'] = n.MACAddress
#             tmpmsg['Name'] = n.Name
#             tmpmsg['DeviceID'] = n.DeviceID
#             tmpmsg['AdapterType'] = n.AdapterType
#             tmpmsg['Speed'] = n.Speed
#             macs.append(tmpmsg)
#     print(macs)
#
#     return macs


@timethis
def getdeviceid():
    # printCPU()
    # printMain_board()
    # printBIOS()
    # printDisk()
    # printMacAddress()
    # print(printBattery())
    id = None
    sysstr = platform.system()
    print(sysstr)
    if sysstr == "Windows":
        c = wmi.WMI()
        memorys = []
        for mem in c.Win32_PhysicalMemory():
            tmpmsg = {}
            tmpmsg['UUID'] = mem.qualifiers['UUID'][1:-1]
            tmpmsg['BankLabel'] = mem.BankLabel
            tmpmsg['SerialNumber'] = mem.SerialNumber.strip()
            tmpmsg['ConfiguredClockSpeed'] = mem.ConfiguredClockSpeed
            tmpmsg['Capacity'] = mem.Capacity
            tmpmsg['ConfiguredVoltage'] = mem.ConfiguredVoltage
            memorys.append(tmpmsg)
        id = memorys[0]['UUID']
    elif sysstr == 'Linux':
        outputdict = termux_telephony_deviceinfo()
        id = outputdict["device_id"].strip()
    else:
        log.critical('既不是Windows也不是Linux，那是啥啊。不搞了，闪退！！！')
        exit(1)
    return id


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    id = getdeviceid()
    print(id)
    log.info(f'文件\t{__file__}\t测试完毕。')
