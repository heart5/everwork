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


def gezhongzaxiang(token):
    # findnotebookfromevernote(token)
    findnotefromnotebook(token, '2c8e97b5-421f-461c-8e35-0f0b1a33e91c', '汇总')
    # findnotefromnotebook(token, '3d927c7e-98a6-4761-b0c6-7fba1348244f', '在职')
    # times = timestamp2str(int(1527605554000 / 1000))
    # print(times)


def chuliwenben(wenben):
    # wenben = "2018年5月26日，周六一，计划拜访25区、26区，38家，订单20单二，重点工作1，产品推广1元小帅虎   15家         1元渔米之乡10家2，重点客户湖北特产、阿里之门赛达国际、2018年5月25日，周五一，计划拜访，25区，40家，订单20单，回款5千实际拜访，25区，28家，订单15单1，跟进新点，天猫小店天顺园，今天在城市广场4期碰头，已经确认了，可以开货，后面他们采购通过我们的供货清单报单2，新点一家，可多保利香槟国际2店，保利香槟国际1店介绍的3，三商佳兴园转让，5月9日，欠款单，今天跟老板娘打了电话，这两天她在那边过去结账4，最舒服的店，福乐平价     最不舒服的店，芙蓉兴盛丰华路二，重点工作1，产品推广1元小帅虎  15家        1元渔米之乡10家实际，8家                                 8家今天线路，主要是补上周没拜访的线路，整体质量不是很高2，重点客户阿里之门赛达国际、天顺园、未拜访完，明天补三，其他乐惠结欠款1，乐惠明天去，今天还没拜访到他家2.今天为了拜访天猫小店天顺园，耽搁时间，后面下雨就没拜访完，明天补3，自我评分，努力70分，结果55分"
    pattern = re.compile('(\d{4}\s*[年\\\.-]{1}\d{1,2}\s*[月\\\.-]{1}\d{1,2}\s*[日|号]?)(?:(?:[,， 。])?(?:周.))?', re.U)
    splititems = re.split(pattern, wenben)
    # print(len(splititems))
    splititems = splititems[1:]
    # print(len(splititems))
    # print(splititems)
    items = []
    for i in range(int(len(splititems) / 2)):
        item = []
        patternriqi = re.compile('(\d+)\s*[年\\\.-]{1}(\d+)\s*[月\\\.-]{1}(\d+)\s*[日|号]?', re.U)
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


def planfenxi(token, jiangemiao):
    try:
        note_store = get_notestore(token)
        persons = BeautifulSoup(note_store.getNoteContent('992afcfb-3afb-437b-9eb1-7164d5207564'),
                                'html.parser').get_text().strip().split()
        # print(persons)
        cnxp = lite.connect('data\\workplan.db')
        tablename_plan = 'personplan'
        tablename_updated = 'planupdated'
        liuxin = 5
        updatablelist = []
        for person in persons:
            # print(person)
            # if person != '梅富忠':
            #     continue
            guid = cfpzysm.get('业务计划总结guid', person)
            # print(guid)
            note = note_store.getNote(guid, True, True, False, False)
            evernoteapijiayi()
            # print(timestamp2str(int(note.updated/1000)))
            # print(note.updateSequenceNum)
            soup = BeautifulSoup(note.content, "html.parser").get_text().strip()
            planitems = chuliwenben(soup)
            # print(planitems[:3])
            if (len(planitems) == 0):
                log.info('%s业务日志中无有效日记录，跳过。' % (person))
                continue
            sqlstr = 'select max(date) from %s where name=\'%s\'' % (tablename_plan, person)
            dftmp = pd.read_sql(sqlstr, cnxp)
            datemaxdb = pd.to_datetime(dftmp.iloc[0, 0])
            log.info('%s的日志内容表中最新日期为%s' % (person, str(datemaxdb)))
            if datemaxdb == None:
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
                    log.info('%s的业务日志有%d条追加到日志内容表中。' % (person, dfrizhiappend.shape[0]))

            # print(planitems[0])
            if cfpzysm.has_option('业务计划总结updatenum', person):
                updatable = note.updateSequenceNum > cfpzysm.getint('业务计划总结updatenum', person)
            else:
                updatable = True
            updatablelist.append(updatable)
            if updatable:
                log.info('业务主管%s的日志有更新。' % person)
                item = []
                item.append(person)
                datestr = datetime.date.strftime(planitems[0][0], '%Y-%m-%d')
                item.append(datestr)
                item.append(planitems[0][0])
                item.append(planitems[0][1])
                item.append(len(planitems[0][1]))
                item.append(timestamp2str(int(note.updated / 1000)))
                itemss = []
                itemss.append(item)
                dfupdate = pd.DataFrame(itemss, columns=['name', 'nianyueri', 'date', 'content', 'contentlength',
                                                         'updatedtime'])
                dfupdate.to_sql(tablename_updated, cnxp, if_exists='append')
                log.info('%s的业务日志有%d条追加到日志更新表中，日期为%s。' % (person, dfupdate.shape[0], datestr))
                cfpzysm.set('业务计划总结updatenum', person, '%d' % note.updateSequenceNum)
                cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

        updatableall = False
        for i in range(len(updatablelist)):
            updatableall |= updatablelist[i]
            if updatableall:
                break
        if updatableall:  # or True:
            sqlstr = 'select distinct * from %s order by updatedtime desc' % tablename_updated
            dftmp = pd.read_sql(sqlstr, cnxp,
                                columns=['name', 'nianyueri', 'date', 'content', 'contentlength', 'updatedtime'])
            dftmp.columns = ['index', 'name', 'nianyueri', 'date', 'content', 'contentlength', 'updatedtime']
            dayscount = cfpzysm.getint('业务计划总结dayscount', 'count')
            dflast = dftmp[pd.to_datetime(dftmp.date) > (datetime.datetime.now() + pd.DateOffset(days=-1 * dayscount))]
            df = dflast[['name', 'nianyueri', 'contentlength', 'updatedtime']]
            df2show = df.drop_duplicates(['name', 'nianyueri'], keep='last')
            df2show.columns = ['业务人员', '计划日期', '内容字数', '更新时间']

            def hege(a, b):
                if pd.to_datetime(a) > pd.to_datetime(b):
                    return '准时'
                else:
                    return '延迟'

            col_names = df2show.columns.tolist()
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
            note = note_store.getNote(guid, True, True, False, False)
            huizongnoteupdatedtime = timestamp2str(int(note.updated / 1000))
            imglist2note(note_store, [], '53115c1b-3623-4a0b-aecc-88f85543c549',
                         '业务工作日志提交情况汇总（自动更新时间：%s）' % huizongnoteupdatedtime, neirong)
        else:
            log.info('本次查阅业务人员日志无更新。')
        cnxp.close()

    except Exception as e:
        log.critical('更新业务日志汇总笔记时出现错误。%s' % (str(e)))

    global timer_plan2note
    timer_plan2note = Timer(jiangemiao, planfenxi, (token, jiangemiao))
    timer_plan2note.start()


def chulioldversion(token):
    note_store = get_notestore(token)
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
        print(verlist[
                  0])  # NoteVersionId(updateSequenceNum=472609, updated=1527677247000, saved=1527682577000, title='业务推广日工作总结和计划——徐志伟')
        items = []
        note_store = get_notestore(token)
        for ver in verlist:
            try:
                # if ver.updateSequenceNum >= 151454:   #开关，断点续传
                #     continue
                notever = note_store.getNoteVersion(token, guid, ver.updateSequenceNum, True, True, True)
                evernoteapijiayi()
            except Exception as e:
                log.critical('%s业务日志读取版本%d中时出现错误，终止操作进入下一轮。%s' % (person, ver.updateSequenceNum, str(e)))
                break
            soup = BeautifulSoup(notever.content, "html.parser").get_text().strip()
            planitems = chuliwenben(soup)
            if (len(planitems) == 0):
                log.info('%s业务日志版本%d中无有效日志记录，跳过此版本。' % (person, ver.updateSequenceNum))
                continue
            item = []
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
    sqlstr = 'select distinct * from %s order by updatedtime desc' % tablename_updated
    dftmp = pd.read_sql(sqlstr, cnxp, columns=['name', 'nianyueri', 'date', 'content', 'contentlength', 'updatedtime'])
    dftmp.columns = ['index', 'name', 'nianyueri', 'date', 'content', 'contentlength', 'updatedtime']
    dflasttwenty = dftmp[pd.to_datetime(dftmp.date) > datetime.datetime.now() + pd.DateOffset(days=-20)]
    df = dflasttwenty[['name', 'nianyueri', 'contentlength', 'updatedtime']]
    # dfupdated = df.drop_duplicates(['name', 'nianyueri'],keep='last')
    dfupdated = df

    def hege(a, b):
        if pd.to_datetime(a) > pd.to_datetime(b):
            return '准时'
        else:
            return '<font color=\'red\'>延迟</font>'

    col_names = dfupdated.columns.tolist()
    col_names.append('timed')
    dfupdated = dfupdated.reindex(columns=col_names)
    dfupdated.loc[:, ['timed']] = dfupdated.apply(lambda x: hege(x.nianyueri, x.updatedtime), axis=1)
    print(dfupdated[dfupdated.name == '陈威'])

    cnxp.close()

if __name__ == '__main__':
    token = cfp.get('evernote', 'token')
    # gezhongzaxiang(token)
    # planfenxi(token, 60 * 60 * 3)
    chayanshuju()
    # chulioldversion(token)
    pass
