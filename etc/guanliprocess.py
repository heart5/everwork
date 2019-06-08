import psutil

import pathmagic
with pathmagic.context():
    from func.logme import log


def judgeprocess(processcmdline):
    inputlst = processcmdline.strip().split()
    processcmdline = ' '.join(inputlst)
    try:
        pl = psutil.pids()

        for pid in pl:
            pidname = psutil.Process(pid).name() 
            pidcmdline = ' '.join(psutil.Process(pid).cmdline())
            # print(f"{pid}\t{pidname}\t{pidcmdline}")
            if pidcmdline == processcmdline:
                print(f"\"{processcmdline}\" is found!")
                return True
    except Exception as e:
        pass


def test_judgepro():
    if judgeprocess('python life/webchat.py '):
        print('success')
        exit(0)
    else:
        print(f"没有找到")
        exit(1)


def getproall():
    """
    返回带有详细信息的进程列表
    """
    proclst, all_processes = [], psutil.process_iter()
    for items in all_processes:
        print(f"{items}")
        try:
            procinfo = items.as_dict(attrs=['pid', 'name'])
            try:
                # 进程启动路径
                # p_path_cwd = items.cwd().decode('gbk')
                p_path_cwd = items.cwd()
                # print(f"{p_path_cwd}")
                # 内存占用百分比
                p_mem_percent = items.memory_percent()
                # 命令行内容
                # cmdlines = str(items.cmdline())
                cmdlines = ' '.join(items.cmdline())
                # print(f"{cmdlines}")
                # CPU占用百分比
                p_cpu_percent = items.cpu_percent(interval=1)
            except Exception as e:
                try:
                    p_path_cwd = items.exe()
                except Exception as e:
                    p_path_cwd = e.name

            procinfo.update({
                "path": p_path_cwd,
                "cmdline": cmdlines,
                "MemPercent": p_mem_percent,
                "cpu_percent": p_cpu_percent
            })

            p_status, p_create_time, proc_user, proc_io_info = items.status(), items.create_time(), items.username(), {}
            try:
                pro_io = items.io_counters()
                proc_io_info['ReadCount'] = pro_io.read_count
                proc_io_info['WriteCount'] = pro_io.write_count
                proc_io_info['ReadBytes'] = pro_io.read_bytes
                proc_io_info['WriteBytes'] = pro_io.write_bytes
            except Exception as e:
                print(f"内轮try io:\t{e}")

            procinfo.update({
                "status": p_status,
                "Createtime": p_create_time,
                "user": proc_user,
                "DiskIO": proc_io_info
            })
        except Exception as e:
            print(f"外轮try：\t{e}")

        finally:
            proclst.append(procinfo)

    return proclst


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    test_judgepro()
    # allp = getproall()
    # print(f"{allp}")
    log.info(f"文件\t{__file__}\t运行结束。")
