# -*- coding: utf-8 -*-
import datasource
import model


class Repository:
    def __init__(self, db):
        self.table = 'epg'
        self.datasrc = datasource.Create(db)
        # self.cretetable(True)

    def __mapObject(self, tup):
        return model.EPG(tup[0], tup[1], tup[2], tup[5], tup[7], tup[3], tup[4], tup[6], tup[8], tup[9], tup[10])

    def __mapObjects(self, tups):
        epgs = []
        for tup in tups:
            epgs.append(self.__mapObject(tup))
        return epgs

    def saveall(self, epgs):
        dbepgs = []
        for epg in epgs:
            dbepgs.append((epg.id, epg.title, epg.descr, epg.start, epg.end, epg.next_title, epg.duration, epg.category, epg.channel, epg.longdesc, epg.detail))
        self.datasrc.saveall(self.table, dbepgs, 11)
        self.datasrc.commit()

    def findall(self):
        dbepgs = self.datasrc.findall(self.table)
        return self.__mapObjects(dbepgs)

    def findallOrderByChannelStart(self):
        dbepgs = self.datasrc.findallOrderBy(self.table, 'channel ASC, start ASC')
        return self.__mapObjects(dbepgs)

    def findByNoDetailFromNow(self):
        now = "datetime('now', 'localtime')"
        sql = 'SELECT * FROM ' + self.table + ' WHERE ' + 'start >= ' + now + ' AND detail == 0'
        # print('findByNoDetailFromNow: ' + sql)
        epgs = self.datasrc.custom(sql)
        return self.__mapObjects(epgs)

    def cretetable(self, ifNotExist):
        columns = ['title', 'descr', 'start DATETIME', 'end DATETIME', 'next', 'duration INT', 'category', 'channel INT', 'longdesc', 'detail BOOLEAN']
        self.datasrc.create(self.table, columns, ifNotExist)
        self.datasrc.commit()

    def close(self):
        self.datasrc.close()

    def findAfterStartBeforeEnd(self):
        now = "datetime('now', 'localtime')"
        sql = 'SELECT * FROM ' + self.table + ' WHERE ' + 'start <= ' + now + ' AND ' + 'end >= ' + now
        dbepgs = self.datasrc.custom(sql)
        return self.__mapObjects(dbepgs)

    def delteStartBefore(self, date):
        sql = 'DELETE from epg WHERE start <= ' + "'" + str(date) + "'"
        # print(sql)
        self.datasrc.customdel(sql)

    def update(self, e):
        fields = ['title', 'descr', 'start', 'end', 'next', 'duration', 'category','channel', 'longdesc', 'detail']
        update = (e.title, e.descr, e.start, e.end, e.next_title, e.duration, e.category, e.channel, e.longdesc, e.detail)
        self.datasrc.update(self.table, update, fields, 'id', e.id)

    def deleteall(self):
        self.datasrc.deleteall(self.table)

    def commit(self):
        self.datasrc.commit()
