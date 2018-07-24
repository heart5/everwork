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
ED569A94-28F0-4C61-B81A-D38D6CB52A92 业务推广日工作总结和计划——梅富忠 为什么guid变了？！
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


def chulinote_workplan(wenben: str):
    """
    处理输入的文本，输出整理后的以日期为单位的工作日志列表
    :param wenben: 原始字符串文本，一般是从笔记中提取的纯文本
    :return: 日期工作日志列表
    """
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
            itemdate = pd.to_datetime('%s-%s-%s' % (splitriqi[1], splitriqi[2], splitriqi[3]))
            qixianzuixindate = pd.to_datetime(datetime.datetime.now()) + datetime.timedelta(days=1)
            if itemdate <= qixianzuixindate:
                item.append(itemdate)
            else:
                log.critical(f'工作日志中出现日期超限错误，跳过此记录。{splititems[i * 2]}，超过允许的计划日期范围。')
                continue
        except TypeError as te:
            log.critical(f'工作日志中出现日期类型错误，跳过此记录。{splititems[i * 2]}，{te}')
            continue
        except ValueError as ve:
            log.critical(f'工作日志中出现日期限值错误，跳过此记录。{splititems[i * 2]}，{ve}')
            continue
        item.append(splititems[i * 2 + 1].replace(" ", ""))
        items.append(item)

    # print(items)
    return items


def updatedb_workplan(note_store, persons):
    cnxp = lite.connect(dbpathworkplan)
    tablename_plan = 'personplan'
    tablename_updated = 'planupdated'
    token = cfp.get('evernote', 'token')
    try:
        liuxin = 5
        for person in persons:
            # print(person)
            # if person != '梅富忠':
            #     continue
            guid = cfpworkplan.get('业务计划总结guid', person).lower()
            # print(guid)
            if note_store is None:
                note = get_notestore().getNote(guid, True, True, False, False)
                log.debug(f'处理{person}日志时notestore失效，重构一个再来。')
            else:
                note = note_store.getNote(guid, True, True, False, False)
            evernoteapijiayi()
            # print(timestamp2str(int(note.updated/1000)))
            # print(note.updateSequenceNum)
            if cfpworkplan.has_option('业务计划总结updatenum', person):
                usnini = cfpworkplan.getint('业务计划总结updatenum', person)
                updatable = note.updateSequenceNum > usnini
            else:
                usnini = 0
                updatable = True
            if updatable is False:
                log.info(f'{person}的工作日志本轮查询中无更新，跳过。')
                continue

            verlist = note_store.listNoteVersions(token, guid)  # 历史版本，不含当前最新版本
            evernoteapijiayi()
            #  当前版本和历史版本组成轮训池
            usnlist = [note.updateSequenceNum] + [x.updateSequenceNum for x in verlist if x.updateSequenceNum > usnini]
            # print(f'{note.updateSequenceNum}\t{usnini}\t{usnlist}')
            log.info(f'业务主管{person}的日志有更新，版本号列表为：{usnlist}')
            for verusn in usnlist[::-1]:  # 倒过来，从最早的笔记版本开始处理
                if verusn == note.updateSequenceNum:
                    vernote = note
                else:
                    vernote = note_store.getNoteVersion(token, guid, verusn, True, True, True)
                evernoteapijiayi()
                soup = BeautifulSoup(vernote.content, "html.parser").get_text().strip()
                planitems = chulinote_workplan(soup)
                # print(planitems[:3])
                if len(planitems) == 0:
                    log.info('%s业务日志中无有效日志记录，跳过。' % person)
                    continue
                # 通过已存储项目的日期（如果没有就默认是当前项目列表最早日期的前一天）截取需要处理的项目并追加到相应数据表中
                sqlstr = 'select max(date) from %s where name=\'%s\'' % (tablename_plan, person)
                dftmp = pd.read_sql(sqlstr, cnxp)
                datemaxdb = pd.to_datetime(dftmp.iloc[0, 0])
                print(f'{person}的日志数据表中最新条目日期为{datemaxdb}')
                if datemaxdb is None:
                    datemaxdb = planitems[-1][0] + datetime.timedelta(days=-1)
                planitemsxinxiancount = 0
                for i in range(len(planitems)):
                    planitemsxinxiancount += 1
                    if planitems[i][0] <= datemaxdb:
                        break
                baddate = False
                for i in range(1, planitemsxinxiancount):  # 逐项检查，看是否有时间倒序问题存在
                    baddate |= planitems[i - 1][0] < planitems[i][0]
                    if baddate:
                        log.critical(f'{person}业务日志（版本号：{verusn}）中存在日期倒置：{planitems[i - 1][0]}，位于第{i}条。跳过。')
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
                        dfrizhiappend.to_sql(tablename_plan, cnxp, index=False, if_exists='append')
                        log.info(f'{person}的业务日志有{dfrizhiappend.shape[0]}条追加到日志内容表中，最新日期为：{datemaxdb}')

                sqlstr = 'select max(date) from %s where name=\'%s\'' % (tablename_updated, person)
                dftmp = pd.read_sql(sqlstr, cnxp)
                datemaxdb = pd.to_datetime(dftmp.iloc[0, 0])
                if datemaxdb is None:
                    datemaxdb = planitems[-1][0] + datetime.timedelta(days=-1)
                print(f'{person}的日志更新数据表中最近有效日期为{datemaxdb}')
                dfitems = pd.DataFrame(planitems, columns=['date', 'content'])
                dfadd = dfitems[dfitems.date > datemaxdb]
                if dfadd.shape[0] > 0:
                    print(dfadd)
                else:
                    log.info(f'{person}业务日志（版本号：{verusn}）暂无有效新内容，最新有效日期为{planitems[0][0]}')
                    continue
                itemss = list()
                for ix in dfadd.index:
                    item = list()
                    item.append(person)
                    datestr = datetime.date.strftime(dfadd.loc[ix, 'date'], '%Y-%m-%d')
                    item.append(datestr)
                    item.append(dfadd.loc[ix, 'date'])
                    item.append(dfadd.loc[ix, 'content'])
                    item.append(len(dfadd.loc[ix, 'content']))
                    item.append(timestamp2str(int(vernote.updated / 1000)))
                    itemss.append(item)
                dfupdate = pd.DataFrame(itemss, columns=['name', 'nianyueri', 'date', 'content', 'contentlength',
                                                         'updatedtime'])
                print(dfupdate)
                dfupdate.to_sql(tablename_updated, cnxp, index=False, if_exists='append')
                log.info(f'{person}的业务日志有{dfupdate.shape[0]}条追加到日志内容表中')
                cfpworkplan.set('业务计划总结updatenum', person, '%d' % verusn)
                cfpworkplan.write(open(iniworkplanpath, 'w', encoding='utf-8'))
        else:
            log.info('下列人员的日志笔记正常处置完毕：%s' % persons)

    except Exception as eee:
        log.critical('读取工作日志笔记更新入日志内容表和日志更新表时发生错误。%s' % str(eee))
    finally:
        cnxp.close()


def planfenxi(jiangemiao):
    cnxp = lite.connect(dbpathworkplan)
    tablename_updated = 'planupdated'
    try:
        note_store = get_notestore()
        persons = BeautifulSoup(note_store.getNoteContent('992afcfb-3afb-437b-9eb1-7164d5207564'),
                                'html.parser').get_text().strip().split()
        evernoteapijiayi()
        updatedb_workplan(note_store, persons)

        sqlstr = f'select distinct * from {tablename_updated} order by date desc, name, updatedtime desc'
        dfsource = pd.read_sql(sqlstr, cnxp, parse_dates=['date', 'updatedtime'])
        updatablelist = []
        for person in persons:
            planitemscount = dfsource.loc[dfsource.name == person].shape[0]
            print(f'{person}日志更新记录有{planitemscount}条')
            if cfpworkplan.has_option('业务计划总结itemscount', person):
                updatable = planitemscount > cfpworkplan.getint('业务计划总结itemscount', person)
            else:
                updatable = True
            updatablelist.append(updatable)
        print(f'{persons}，{updatablelist}')

        updatableall = False
        for i in range(len(updatablelist)):
            updatableall |= updatablelist[i]
            if updatableall:
                break
        if updatableall:  # or True:
            dayscount = cfpworkplan.getint('业务计划总结dayscount', 'count')
            today = pd.to_datetime(datetime.datetime.today().strftime('%F'))
            workdays = isworkday([today - datetime.timedelta(days=60)], '全体', fromthen=True)
            dtqishi = workdays[workdays.work == True].groupby('date').count().sort_index(ascending=False).index[
                dayscount - 1]
            print(f'最近{dayscount}个工作日（公司）的起始日期：{dtqishi}')
            # dtqishi = today - datetime.timedelta(days=dayscount)
            dtqujian = pd.date_range(dtqishi, today, freq='D').values
            dfqujian = pd.DataFrame()
            for person in persons:
                resultlist = isworkday(dtqujian, person)
                dftmp = pd.DataFrame(resultlist, columns=['date', 'name', 'work', 'xingzhi', 'tianshu'])
                if dfqujian.shape[0] == 0:
                    dfqujian = dftmp
                else:
                    dfqujian = dfqujian.append(dftmp)
            dfsourcequjian = dfsource[dfsource.date >= dtqishi]
            # print(dfqujian)
            # print(dfsourcequjian)
            dfresult = pd.merge(dfqujian, dfsourcequjian, on=['date', 'name'], how='outer')
            dflast = dfresult[dfresult.work == True].sort_values(['date', 'name'], ascending=[False, True])
            df = dflast.loc[:, ['name', 'date', 'contentlength', 'updatedtime']]
            df2show = df.drop_duplicates(['name', 'date'], keep='last')
            print(f'去重前记录数为：{df.shape[0]}，去重后记录是：{df2show.shape[0]}')
            df2show.columns = ['业务人员', '计划日期', '内容字数', '更新时间']

            # print(df2show)

            def hege(a, b):
                if pd.isnull(b):
                    # print(f'{a}\t{b}')
                    return '未提交'
                if pd.to_datetime(a) > pd.to_datetime(b):
                    return '准时'
                else:
                    return '延迟'

            col_names = list(df2show.columns)
            col_names.append('计划提交')
            df2show = df2show.reindex(columns=col_names)
            df2show.loc[:, ['计划提交']] = df2show.apply(lambda x: hege(x.计划日期, x.更新时间), axis=1)
            print(df2show[pd.isnull(df2show.更新时间)])
            stylelist = ['<span style=\"color:red\">', '</span>']
            df2show['计划日期'] = df2show['计划日期'].apply(lambda x: x.strftime('%F'))
            df2show['更新时间'] = df2show['更新时间'].apply(lambda x: x.strftime('%m-%d %T') if pd.notnull(x) else '')
            df2show['内容字数'] = df2show['内容字数'].apply(lambda x: int(x) if pd.notnull(x) else '')
            for ix in df2show.index:
                if (df2show.loc[ix]['计划提交'] == '延迟') or (df2show.loc[ix]['计划提交'] == '未提交'):
                    df2show.loc[ix, '业务人员'] = df2show.loc[ix, '业务人员'].join(stylelist)
                    df2show.loc[ix, '计划日期'] = df2show.loc[ix, '计划日期'].join(stylelist)
                    df2show.loc[ix, '更新时间'] = df2show.loc[ix, '更新时间'].join(stylelist)
                    df2show.loc[ix, '计划提交'] = df2show.loc[ix, '计划提交'].join(stylelist)
                    pass
            # descdb(df2show)
            neirong = tablehtml2evernote(df2show, '业务工作日志提交情况汇总（最近%d工作日）' % dayscount)
            neirong = html.unescape(neirong)
            # print(neirong)
            guid = cfpworkplan.get('业务计划总结guid', '汇总')
            huizongnoteupdatedtime = datetime.datetime.now().strftime('%F %T')
            imglist2note(note_store, [], guid,
                         '业务工作日志提交情况汇总（%s）' % huizongnoteupdatedtime, neirong)

        for person in persons:
            dfperson = dfsource.loc[dfsource.name == person]
            planitemscount = dfperson.shape[0]
            if cfpworkplan.has_option('业务计划总结itemscount', person):
                updatable = planitemscount > cfpworkplan.getint('业务计划总结itemscount', person)
            else:
                updatable = True
            if updatable:
                log.info(
                    '%s的业务日志条目数增加至%d，日志更新表中最新日期为：%s。' % (person, planitemscount, str(dfperson.iloc[0]['nianyueri'])))
                cfpworkplan.set('业务计划总结itemscount', person, '%d' % planitemscount)
                cfpworkplan.write(open(iniworkplanpath, 'w', encoding='utf-8'))
    except Exception as eee:
        log.critical('更新业务日志汇总笔记时出现错误。%s' % (str(eee)))
        # raise eee
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
            # if person != '黄壮':   #开关，某人记录未读完是专项处理
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
            print(
                f'{ver.updateSequenceNum}\t{timestamp2str(int(ver.updated / 1000))}\t{timestamp2str(int(ver.saved / 1000))}')
            try:
                # if ver.updateSequenceNum >= 349273:   #开关，断点续传
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
        cnxp = lite.connect(dbpathworkplan)
        tablename_updated = 'planupdated'
        dfupdate = pd.DataFrame(items,
                                columns=['name', 'nianyueri', 'date', 'content', 'contentlength', 'updatedtime'])
        dfupdate.to_sql(tablename_updated, cnxp, index=False, if_exists='append')
        cnxp.close()


def chayanshuju():
    cnxp = lite.connect(dbpathworkplan)
    tablename_updated = 'planupdated'

    # person = '梅富忠'
    sqlstr = 'select * from %s order by updatedtime desc' % tablename_updated
    dftmp = pd.read_sql(sqlstr, cnxp, parse_dates=['date', 'updatedtime'])
    print(dftmp.shape[0])

    sqlstr = 'select distinct * from %s order by updatedtime desc' % tablename_updated
    dftmp = pd.read_sql(sqlstr, cnxp, parse_dates=['date', 'updatedtime'])
    print(dftmp.shape[0])
    dftmp.to_sql(tablename_updated, cnxp, index=False, if_exists='replace')

    sqlstr = 'select * from %s order by updatedtime desc' % tablename_updated
    dftmp = pd.read_sql(sqlstr, cnxp, parse_dates=['date', 'updatedtime'])
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
