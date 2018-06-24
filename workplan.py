#
# encoding:utf-8
#
"""
处理业务计划总结

名称：业务计划总结    guid：2c8e97b5-421f-461c-8e35-0f0b1a33e91c    更新序列号：471364    默认笔记本：False
创建时间：2016-02-16 19:56:56    更新时间：2018-02-25 00:24:57    笔记本组：None

5830a2f2-7a76-4f1a-a167-1bd18818a141 业务推广日工作总结和计划——周莉
ddf1cbea-c6e4-4d74-9782-51017c798a99 业务推广日工作总结和计划——陈威
252e380f-11ff-4fe5-bb0c-fc24af74d385 业务推广日工作总结和计划—陈益
ac7088ee-c1eb-4489-b249-e22692706d15 业务推广日工作总结和计划——梅富忠
443f5b18-d0d9-436a-9f9e-5c7a070b8726 业务推广日工作总结和计划——徐志伟
b627331e-179f-4d69-a8cf-807a1d0f6862 业务推广计划和总结—王家龙
6e68b4ee-78f8-456e-bf76-71547e83ae21 业务推广日工作总结和计划——陈威
e34ae4da-4ddd-4b13-bb1c-307d39f03cc8 业务推广计划和总结—刘权
53115c1b-3623-4a0b-aecc-88f85543c549 业务工作日志提交情况汇总


名称：人事管理    guid：3d927c7e-98a6-4761-b0c6-7fba1348244f    更新序列号：47266    默认笔记本：False
创建时间：2015-07-14 13:50:09    更新时间：2015-07-14 13:50:09    笔记本组：origin
992afcfb-3afb-437b-9eb1-7164d5207564 在职业务人员名单
"""
from imp4nb import *


def gezhongzaxiang():
    # findnotebookfromevernote(token)
    findnotefromnotebook(token, '2c8e97b5-421f-461c-8e35-0f0b1a33e91c', '汇总')
    # findnotefromnotebook(token, '3d927c7e-98a6-4761-b0c6-7fba1348244f', '在职')
    # times = timestamp2str(int(1527605554000 / 1000))
    # print(times)


def chulinote_workplan(wenben):
    pattern = re.compile('(\d{4}\s*[年\\\.-]\d{1,2}\s*[月\\\.-]\d{1,2}\s*[日|号]?)(?:(?:[,， 。])?(?:周.))?', re.U)
    splititems = re.split(pattern, wenben)
    # print(len(splititems))
    splititems = splititems[1:]
    # print(len(splititems))
    # print(splititems)
    items = []
    for i in range(int(len(splititems) / 2)):
        item = []
        patternriqi = re.compile('(\d+)\s*[年\\\.-](\d+)\s*[月\\\.-](\d+)\s*[日|号]?', re.U)
        splitriqi = re.split(patternriqi, splititems[i * 2])
        # print(splitriqi)
        try:
            item.append(pd.to_datetime('%s-%s-%s' % (splitriqi[1], splitriqi[2], splitriqi[3])))
        except TypeError as te:
            log.critical('工作日志中出现日期错误：%s，跳过此记录。%s' % (splititems[i * 2], str(te)))
            continue
        except ValueError as ve:
            log.critical('工作日志中出现日期错误：%s，跳过此记录。%s' % (splititems[i * 2], str(ve)))
            continue
        item.append(splititems[i * 2 + 1].replace(" ", ""))
        items.append(item)

    # print(items)
    return items


def updatedb_workplan(note_store, persons):
    cnxp = lite.connect('data\\workplan.db')
    tablename_plan = 'personplan'
    tablename_updated = 'planupdated'
    try:
        liuxin = 5
        for person in persons:
            # print(person)
            # if person != '梅富忠':
            #     continue
            guid = cfpzysm.get('业务计划总结guid', person)
            # print(guid)
            if note_store is None:
                note = get_notestore().getNote(guid, True, True, False, False)
                log.debug(f'处理{person}日志时notestore失效，重构一个再来。')
            else:
                note = note_store.getNote(guid, True, True, False, False)
            evernoteapijiayi()
            # print(timestamp2str(int(note.updated/1000)))
            # print(note.updateSequenceNum)
            soup = BeautifulSoup(note.content, "html.parser").get_text().strip()
            planitems = chulinote_workplan(soup)
            # print(planitems[:3])
            if len(planitems) == 0:
                log.info('%s业务日志中无有效日记录，跳过。' % person)
                continue
            sqlstr = 'select max(date) from %s where name=\'%s\'' % (tablename_plan, person)
            dftmp = pd.read_sql(sqlstr, cnxp)
            datemaxdb = pd.to_datetime(dftmp.iloc[0, 0])
            if datemaxdb is None:
                datemaxdb = planitems[-1][0] + datetime.timedelta(days=-1)
            planitemsxinxiancount = 0
            for i in range(len(planitems)):
                planitemsxinxiancount += 1
                if planitems[i][0] <= datemaxdb:
                    break
            baddate = False
            for i in range(1, planitemsxinxiancount):
                baddate |= planitems[i - 1][0] < planitems[i][0]
                if baddate:
                    log.critical('%s的业务日志中存在日期错误：%s，位于第%d条。' % (person, str(planitems[i - 1][0]), i))
                    break
            if baddate:
                continue
            if len(planitems) > liuxin:  # 固化内容存储，预留5天可修改，随着记录更新追加到数据表中
                dfrizhi = pd.DataFrame(planitems, columns=['date', 'content'])
                dfrizhi['name'] = person
                dfrizhi = dfrizhi[['name', 'date', 'content']]
                dfrizhi.sort_values(['date'], inplace=True)  # 升序排列
                dfrizhichuli = dfrizhi[dfrizhi.date > datemaxdb]  # 取尾部记录
                # print(dfrizhichuli)
                if dfrizhichuli.shape[0] > liuxin:
                    dfrizhiappend = dfrizhichuli[:dfrizhichuli.shape[0] - liuxin]  # 取头部
                    dfrizhiappend.to_sql(tablename_plan, cnxp, if_exists='append')
                    log.info('%s的业务日志有%d条追加到日志内容表中，最新日期为：%s' % (person, dfrizhiappend.shape[0], str(datemaxdb)))

            # print(planitems[0])
            if cfpzysm.has_option('业务计划总结updatenum', person):
                updatable = note.updateSequenceNum > cfpzysm.getint('业务计划总结updatenum', person)
            else:
                updatable = True
            if updatable:
                log.info('业务主管%s的日志有更新。' % person)
                item = list()
                item.append(person)
                datestr = datetime.date.strftime(planitems[0][0], '%Y-%m-%d')
                item.append(datestr)
                item.append(planitems[0][0])
                item.append(planitems[0][1])
                item.append(len(planitems[0][1]))
                item.append(timestamp2str(int(note.updated / 1000)))
                itemss = list()
                itemss.append(item)
                dfupdate = pd.DataFrame(itemss, columns=['name', 'nianyueri', 'date', 'content', 'contentlength',
                                                         'updatedtime'])
                dfupdate.to_sql(tablename_updated, cnxp, if_exists='append')
                log.info('%s的业务日志有%d条追加到日志更新表中，日期为%s。' % (person, dfupdate.shape[0], datestr))
                cfpzysm.set('业务计划总结updatenum', person, '%d' % note.updateSequenceNum)
                cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        else:
            log.info('下列人员的日志笔记正常处置完毕：%s' % persons)

    except Exception as eee:
        log.critical('读取工作日志笔记更新入日志内容表和日志更新表时发生错误。%s' % str(eee))
    finally:
        cnxp.close()


def planfenxi(jiangemiao):
    cnxp = lite.connect('data\\workplan.db')
    tablename_updated = 'planupdated'
    try:
        note_store = get_notestore()
        persons = BeautifulSoup(note_store.getNoteContent('992afcfb-3afb-437b-9eb1-7164d5207564'),
                                'html.parser').get_text().strip().split()
        evernoteapijiayi()
        updatedb_workplan(note_store, persons)

        sqlstr = 'select distinct * from %s order by updatedtime desc' % tablename_updated
        dfsource = pd.read_sql(sqlstr, cnxp)
        updatablelist = []
        for person in persons:
            planitemscount = dfsource.loc[dfsource.name == person].shape[0]
            if cfpzysm.has_option('业务计划总结itemscount', person):
                updatable = planitemscount > cfpzysm.getint('业务计划总结itemscount', person)
            else:
                updatable = True
            updatablelist.append(updatable)
        print(updatablelist)

        updatableall = False
        for i in range(len(updatablelist)):
            updatableall |= updatablelist[i]
            if updatableall:
                break
        if updatableall:  # or True:
            dayscount = cfpzysm.getint('业务计划总结dayscount', 'count')
            dtgroup = dfsource[pd.to_datetime(dfsource.nianyueri) <= datetime.datetime.now()].groupby(
                ['nianyueri']).count().index
            # print(dtgroup)
            workdaylist = isworkday(dtgroup)
            workdaydf = pd.DataFrame(workdaylist, columns=['work'], index=dtgroup)
            workdaydftrue = workdaydf[workdaydf.work == True]
            workdaydftrue.sort_index(ascending=False, inplace=True)
            if workdaydftrue.shape[0] > dayscount:
                datelast = workdaydftrue.index[dayscount - 1]
            else:
                datelast = workdaydftrue.index[workdaydftrue.shape[0] - 1]
            print(datelast)
            dflast = dfsource[
                pd.to_datetime(dfsource.nianyueri) > pd.to_datetime(datelast)]
            df = dflast[['name', 'nianyueri', 'contentlength', 'updatedtime']]
            df2show = df.drop_duplicates(['name', 'nianyueri'], keep='last')
            df2show.columns = ['业务人员', '计划日期', '内容字数', '更新时间']

            def hege(a, b):
                if pd.to_datetime(a) > pd.to_datetime(b):
                    return '准时'
                else:
                    return '延迟'

            col_names = list(df2show.columns)
            col_names.append('计划提交')
            df2show = df2show.reindex(columns=col_names)
            df2show.loc[:, ['计划提交']] = df2show.apply(lambda x: hege(x.计划日期, x.更新时间), axis=1)
            stylelist = ['<span style=\"color:red\">', '</span>']
            for ix in df2show.index:
                if df2show.loc[ix]['计划提交'] == '延迟':
                    df2show.loc[ix, '业务人员'] = df2show.loc[ix, '业务人员'].join(stylelist)
                    df2show.loc[ix, '计划日期'] = df2show.loc[ix, '计划日期'].join(stylelist)
                    df2show.loc[ix, '更新时间'] = df2show.loc[ix, '更新时间'].join(stylelist)
                    df2show.loc[ix, '计划提交'] = df2show.loc[ix, '计划提交'].join(stylelist)
                    pass
            # descdb(df2show)
            neirong = tablehtml2evernote(df2show, '业务工作日志提交情况汇总（最近%d工作日）' % dayscount)
            neirong = html.unescape(neirong)
            # print(neirong)
            guid = cfpzysm.get('业务计划总结guid', '汇总')
            huizongnoteupdatedtime = datetime.datetime.now().strftime('%F %T')
            imglist2note(note_store, [], guid,
                         '业务工作日志提交情况汇总（%s）' % huizongnoteupdatedtime, neirong)

        for person in persons:
            dfperson = dfsource.loc[dfsource.name == person]
            planitemscount = dfperson.shape[0]
            if cfpzysm.has_option('业务计划总结itemscount', person):
                updatable = planitemscount > cfpzysm.getint('业务计划总结itemscount', person)
            else:
                updatable = True
            if updatable:
                log.info(
                    '%s的业务日志条目数增加至%d，日志更新表中最新日期为：%s。' % (person, planitemscount, str(dfperson.iloc[0]['nianyueri'])))
                cfpzysm.set('业务计划总结itemscount', person, '%d' % planitemscount)
                cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
    except Exception as eee:
        log.critical('更新业务日志汇总笔记时出现错误。%s' % (str(eee)))
    finally:
        cnxp.close()

    global timer_plan2note
    timer_plan2note = Timer(jiangemiao, planfenxi, [jiangemiao])
    timer_plan2note.start()


def chulioldversion():
    note_store = get_notestore()
    notes = findnotefromnotebook(token, '2c8e97b5-421f-461c-8e35-0f0b1a33e91c', '业务推广')
    for ii in range(len(notes)):
        note = notes[ii]
        guid = note[0]
        titles = note[1].split('—')
        if len(titles) >= 2:
            person = titles[-1]
            print('%s\t%s' % (person, guid))
            # if person != '梅富忠':   #开关，某人记录未读完是专项处理
            #     continue
        else:
            continue
        verlist = note_store.listNoteVersions(token, guid)
        evernoteapijiayi()
        print(len(verlist))
        print(verlist[0])
        # NoteVersionId(updateSequenceNum=472609, updated=1527677247000, saved=1527682577000,
        # title='业务推广日工作总结和计划——徐志伟')
        items = []
        note_store = get_notestore()
        for ver in verlist:
            try:
                # if ver.updateSequenceNum >= 151454:   #开关，断点续传
                #     continue
                notever = note_store.getNoteVersion(token, guid, ver.updateSequenceNum, True, True, True)
                evernoteapijiayi()
            except Exception as eeee:
                log.critical('%s业务日志读取版本%d中时出现错误，终止操作进入下一轮。%s' % (person, ver.updateSequenceNum, str(eeee)))
                break
            soup = BeautifulSoup(notever.content, "html.parser").get_text().strip()
            planitems = chulinote_workplan(soup)
            if len(planitems) == 0:
                log.info('%s业务日志版本%d中无有效日志记录，跳过此版本。' % (person, ver.updateSequenceNum))
                continue
            item = list()
            item.append(person)
            datestr = datetime.date.strftime(planitems[0][0], '%Y-%m-%d')
            item.append(datestr)
            item.append(planitems[0][0])
            item.append(planitems[0][1])
            item.append(len(planitems[0][1]))
            item.append(timestamp2str(int(notever.updated / 1000)))
            items.append(item)
        print(items)
        cnxp = lite.connect('data\\workplan.db')
        tablename_updated = 'planupdated'
        dfupdate = pd.DataFrame(items,
                                columns=['name', 'nianyueri', 'date', 'content', 'contentlength', 'updatedtime'])
        dfupdate.to_sql(tablename_updated, cnxp, if_exists='append')
        cnxp.close()


def chayanshuju():
    cnxp = lite.connect('data\\workplan.db')
    tablename_updated = 'planupdated'

    # person = '梅富忠'
    sqlstr = 'select * from %s order by updatedtime desc' % tablename_updated
    dftmp = pd.read_sql(sqlstr, cnxp)
    print(dftmp.shape[0])

    sqlstr = 'select distinct * from %s order by updatedtime desc' % tablename_updated
    dftmp = pd.read_sql(sqlstr, cnxp)
    print(dftmp.shape[0])
    dftmp.to_sql(tablename_updated, cnxp, if_exists='replace')

    sqlstr = 'select * from %s order by updatedtime desc' % tablename_updated
    dftmp = pd.read_sql(sqlstr, cnxp)
    print(dftmp.shape[0])

    dfupdated = dftmp.groupby(['name', 'nianyueri'], as_index=False)['updatedtime'].max().sort_values('updatedtime',
                                                                                                      ascending=False)
    descdb(dfupdated)

    cnxp.close()

    huizongnoteupdatedtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(huizongnoteupdatedtime)
    huizongnoteupdatedtime = datetime.datetime.now().strftime('%F %T')
    print(huizongnoteupdatedtime)


if __name__ == '__main__':
    token = cfp.get('evernote', 'token')
    # gezhongzaxiang()
    planfenxi(60 * 5)
    # chayanshuju()
    # chulioldversion()
    pass
