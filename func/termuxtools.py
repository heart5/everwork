# ---
# termux工具集，API
# ---

import subprocess

import pathmagic
with pathmagic.context():
    from func.common import utils
    from func.logme import log


"""
    implementation of all the termux-api commands
    via subprocesses,
"""

# print(f"{__file__} is loading now...")

def evaloutput(output):
    if (output is None) or (output == 'null') or (len(output) == 0):
        # print(f"output\'s content:\n{output}")
        return False
    # 转换成字典输出
    out = output.replace('false', 'False').replace('true',
                                                   'True').replace('null', 'None')
    # print(out)
    return eval(out)


def battery_status():
    out, rc, err = utils.execute('termux-battery-status')
    if rc:
        raise Exception(err)
    return evaloutput(out)


def camera_info():
    out, rc, err = utils.execute('termux-camera-info')
    if rc:
        raise Exception(err)
    return evaloutput(out)


def termux_camera_photo():
    out, rc, err = utils.execute('termux-camera-photo')
    if rc:
        raise Exception(err)
    return out


def termux_clipboard_get():
    out, rc, err = utils.execute('termux-clipboard-get')
    if rc:
        raise Exception(err)
    return out


def termux_clipboard_set():
    out, rc, err = utils.execute('termux-clipboard-set')
    if rc:
        raise Exception(err)
    return out


def termux_contact_list():
    out, rc, err = utils.execute('termux-contact-list')
    if rc:
        raise Exception(err)
    return out


def termux_dialog():
    out, rc, err = utils.execute('termux-dialog')
    if rc:
        raise Exception(err)
    return out


def termux_download():
    out, rc, err = utils.execute('termux-download')
    if rc:
        raise Exception(err)
    return out


def termux_fix_shebang():
    out, rc, err = utils.execute('termux-fix-shebang')
    if rc:
        raise Exception(err)
    return out


def termux_info():
    out, rc, err = utils.execute('termux-info')
    if rc:
        raise Exception(err)
    return out


def termux_infrared_frequencies():
    out, rc, err = utils.execute('termux-infrared-frequencies')
    if rc:
        raise Exception(err)
    return out


def termux_infrared_transmit():
    out, rc, err = utils.execute('termux-infrared-transmit')
    if rc:
        raise Exception(err)
    return out


def termux_location():
    out, rc, err = utils.execute('termux-location')
    if rc:
        raise Exception(err)
    if len(out) == 0:
        out, rc, err = utils.execute(['termux-location', '-p', 'network'])
        if rc:
            raise Exception(err)
    if len(out) == 0:
        out, rc, err = utils.execute(['termux-location', '-p', 'passive'])
        if rc:
            raise Exception(err)
    return evaloutput(out)


def termux_notification():
    out, rc, err = utils.execute('termux-notification')
    if rc:
        raise Exception(err)
    return out


def termux_notification_remove():
    out, rc, err = utils.execute('termux-notification-remote')
    if rc:
        raise Exception(err)
    return out


def termux_open():
    out, rc, err = utils.execute('termux-open')
    if rc:
        raise Exception(err)
    return out


def termux_open_url():
    out, rc, err = utils.execute('termux-open-url')
    if rc:
        raise Exception(err)
    return out


def termux_reload_settings():
    out, rc, err = utils.execute('termux-reload-settings')
    if rc:
        raise Exception(err)
    return out


def termux_setup_storage():
    out, rc, err = utils.execute('termux-setup-storage')
    if rc:
        raise Exception(err)
    return out


def termux_share():
    out, rc, err = utils.execute('termux-share')
    if rc:
        raise Exception(err)
    return out


def termux_sms_list():
    out, rc, err = utils.execute('termux-sms-list')
    if rc:
        raise Exception(err)
    return out


def termux_sms_send(msg='hi'):
    cmdlist = ['termux-sms-send', '-n', '15387182166', f'{msg}']
    out, rc, err = utils.execute(cmdlist)
    if rc:
        log.Warning(f"发送短信时出现错误：{msg}")
        raise Exception(err)
    else:
        log.info(f"成功发送短信。")
    return out


def termux_storage_get():
    out, rc, err = utils.execute('termux-storage-get')
    if rc:
        raise Exception(err)
    return out


def termux_telephony_call():
    out, rc, err = utils.execute('termux-telephony-call')
    if rc:
        raise Exception(err)
    return out


def termux_telephony_cellinfo():
    out, rc, err = utils.execute('termux-telephony-cellinfo')
    if rc:
        raise Exception(err)
    return evaloutput(out)


def termux_telephony_deviceinfo():
    out, rc, err = utils.execute('termux-telephony-deviceinfo')
    if rc:
        raise Exception(err)
    return evaloutput(out)


def termux_toast():
    out, rc, err = utils.execute('termux-toast')
    if rc:
        raise Exception(err)
    return out


def termux_tts_engines():
    out, rc, err = utils.execute('termux-tts-engines')
    if rc:
        raise Exception(err)
    return out


def termux_tts_speak():
    out, rc, err = utils.execute('termux-tts-speak')
    if rc:
        raise Exception(err)
    return out


def termux_vibrate():
    out, rc, err = utils.execute('termux-vibrate')
    if rc:
        raise Exception(err)
    return out


def termux_wake_lock():
    out, rc, err = utils.execute('termux-wake-lock')
    if rc:
        raise Exception(err)
    return out


def termux_wake_unlock():
    out, rc, err = utils.execute('termux-wake-unlock')
    if rc:
        raise Exception(err)
    return out


def termux_wifi_connectioninfo():
    out, rc, err = utils.execute('termux-wifi-connectioninfo')
    if rc:
        raise Exception(err)
    return evaloutput(out)


def termux_wifi_scaninfo():
    out, rc, err = utils.execute('termux-wifi-scaninfo')
    if rc:
        raise Exception(err)
    return evaloutput(out)


if __name__ == '__main__':
    log.info(f'测试文件\t{__file__}')
    print(termux_info())
    print(termux_location())
    print('Done.测试完毕。')
