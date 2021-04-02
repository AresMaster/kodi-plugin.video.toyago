# -*- coding: utf-8 -*-


class Radio:
    name = None
    source = None
    thumbnail = None
    playable = False

    def __init__(self, name, source, thumbnail, playable):
        self.name = name
        self.source = source
        self.thumbnail = thumbnail
        self.playable = playable


class Channel:
    id = None
    name = None
    source = None
    thumbnail = None
    number = None
    genre = None
    cid = None
    lastscan = None

    def __init__(self, id, name, source, thumbnail, number, genre, cid, lastscan):
        self.id = id
        self.name = name
        self.source = source
        self.thumbnail = thumbnail
        self.number = number
        self.genre = genre
        self.cid = cid
        self.lastscan = lastscan


class EPG:
    id = None
    title = None
    descr = None
    next_title = None
    category = None
    start = None
    end = None
    duration = None
    channel = None
    longdesc = None
    detail = None

    def __init__(self, id, title, descr, next_title, category, start, end, duration, channel, longdesc, detail):
        self.id = id
        self.descr = descr
        self.title = title
        self.next_title = next_title
        self.category = category
        self.start = start
        self.end = end
        self.duration = duration
        self.channel = channel
        self.longdesc = longdesc
        self.detail = detail




