# -*- coding: utf-8 -*-
import datasource
import model


class Repository:
    def __init__(self, db):
        self.table = 'channel'
        self.datasrc = datasource.Create(db)
        # self.cretetable(True)

    def __mapObject(self, tup):
        return model.Channel(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6], tup[7])

    def __mapObjects(self, tups):
        channels = []
        for tup in tups:
            channels.append(self.__mapObject(tup))
        return channels

    def findbyname(self, name):
        ch = self.datasrc.findone(self.table, 'name', name)
        return self.__mapObject(ch)

    def findbyid(self, id):
        ch = self.datasrc.findone(self.table, 'id', id)
        return self.__mapObject(ch)

    def findall(self):
        dbchannels = self.datasrc.findall(self.table)
        return self.__mapObjects(dbchannels)

    def findallOrderByNumber(self):
        dbchannels = self.datasrc.findallOrderBy(self.table, 'number ASC')
        return self.__mapObjects(dbchannels)

    def findByLastScanBeforeNow(self):
        now = "datetime('now', 'localtime')"
        sql = 'SELECT * FROM ' + self.table + ' WHERE ' + 'lastscan <= ' + now + ' OR lastscan is null'
        dbchannels = self.datasrc.custom(sql)
        return self.__mapObjects(dbchannels)


    def deleteall(self):
        self.datasrc.deleteall(self.table)

    def saveall(self, channels):
        dbchannels = []
        for ch in channels:
            dbchannels.append((ch.id, ch.name, ch.source, ch.thumbnail, ch.number, ch.genre, ch.cid, ch.lastscan))
        self.datasrc.saveall(self.table, dbchannels, 8)
        self.datasrc.commit()

    def save(self, ch):
        channel = (ch.id, ch.name, ch.source, ch.thumbnail, ch.number, ch.genre, ch.cid, ch.lastscan)
        self.datasrc.save(self.table, channel, 8)
        self.datasrc.commit()

    def update(self, ch):
        fields = ['name', 'source', 'thumbnail', 'number', 'genre', 'cid', 'lastscan']
        update = (ch.name, ch.source, ch.thumbnail, ch.number, ch.genre, ch.cid, ch.lastscan)
        self.datasrc.update(self.table, update, fields, 'id', ch.id)
        self.datasrc.commit()


    def cretetable(self, ifNotExist):
        columns = ['name', 'source', 'thumbnail', 'number', 'genre', 'cid', 'lastscan DATETIME']
        self.datasrc.create(self.table, columns, ifNotExist)
        self.datasrc.commit()

    def close(self):
        self.datasrc.close()

    def commit(self):
        self.datasrc.commit()


