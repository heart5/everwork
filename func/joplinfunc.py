# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %% [markdown]
# # Joplin 工具库

# %% [markdown]
# ## 引入库

# %%
import pathmagic
import subprocess
import joppy
from joppy.api import Api

# %%
with pathmagic.context():
    # from func.first import getdirmain
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    # from func.evernttest import get_notestore, imglist2note, readinifromnote, evernoteapijiayi, makenote, getinivaluefromnote
    # from func.logme import log
    # from func.wrapfuncs import timethis, ift2phone
    # from func.termuxtools import termux_location, termux_telephony_deviceinfo
    # from func.nettools import ifttt_notify
    from etc.getid import getdeviceid
    from func.sysfunc import not_IPython, set_timeout, after_timeout


# %% [markdown]
# ## 功能函数集

# %% [markdown]
# ### def joplincmd(cmd)

# %%
def joplincmd(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, shell=True)
    return result


# %% [markdown]
# ### def getallnotes()

# %%
def getallnotes():
    """
    获取所有笔记；默认仅输出id、parent_id和title三项有效信息
    """
    api = Api(token = getcfpoptionvalue("everwork", "joplin", "token"))

    return api.get_all_notes()


# %% [markdown]
# ### def getnote(id)

# %%
def getnote(id):
    api = Api(token = getcfpoptionvalue("everwork", "joplin", "token"))
    # note = api.get_note(id, fields="id, parent_id, title, body, created_time, updated_time, is_conflict, latitude, longitude, altitude, author, source_url, is_todo, todo_due, todo_completed, source, source_application, application_data, order, user_created_time, user_updated_time, encryption_cipher_text, encryption_applied, markup_language, is_shared, share_id, conflict_original_id, master_key_id, body_html, base_url, image_data_url, crop_rect")
    # 经过测试，fields中不能携带的属性值有：latitude, longitude, altitude, master_key_id, body_html,  image_data_url, crop_rect
    note = api.get_note(id, fields="id, parent_id, title, body, created_time, updated_time, is_conflict, author, source_url, is_todo, todo_due, todo_completed, source, source_application, application_data, order, user_created_time, user_updated_time, encryption_cipher_text, encryption_applied, markup_language, is_shared, share_id, conflict_original_id")
    # note = api.get_note(id, fields="id, latitude, longitude, altitude")
    
    return note


# %% [markdown]
# ## 主函数main（）

# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'开始运行文件\t{__file__}')
    allnotes = getallnotes()
    print(allnotes)
    
    api = Api(token = getcfpoptionvalue("everwork", "joplin", "token"))
    location_keys = ["longitude", "latitude", "altitude"]
    fields=",".join(["id,title"] + location_keys)
    fields_ls = fields.split(",")
    print(fields, fields_ls)
    # for note in api.get_all_notes(fields = fields):
    #     print(note)


    cmd = "joplin ls notebook"
    cmd = "joplin status"
    cmd = "joplin ls -l"
    # result = joplincmd(cmd)
    # print(result.stdout)
    if not_IPython():
        log.info(f'Done.结束执行文件\t{__file__}')


# %%
def getnoteswithfields(fields):
    api = Api(token = getcfpoptionvalue("everwork", "joplin", "token"))
    fields_ls = fields.split(",")
    allnotes = [note for note in api.get_all_notes(fields = fields)]
    geonotes = [note for note in allnotes if note.altitude != 0 and note.longitude != 0]
    print(len(allnotes),len(geonotes))
    for note in geonotes:
        # print(getattr(note, "id"))
        neededfls = [getattr(note, key) for key in fields_ls]
        print(neededfls)
        # if any(getattr(note, location_key) != 0 for location_key in location_keys):
        #     # api.modify_note(
        #     #     id_=note.id, **{location_key: 0 for location_key in location_keys}
        #     # )
        #     print(note)
    # geonotes = [[note.fl for fl in fields_ls] for note in geonotes]
    # print(geonotes)

location_keys = ["longitude", "latitude", "altitude"]
fields=",".join(["id,title,body,parent_id"] + location_keys)
getnoteswithfields(fields)


# %%
def justtest():
    myid = allnotes[-9].id
    print(getnote(myid))

justtest()
