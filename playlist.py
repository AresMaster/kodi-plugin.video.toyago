# -*- coding: utf-8 -*-


class Playlist:
    EXTM3U = "#EXTM3U\n";
    service = None

    def __init__(self, service):
        self.service = service

    def addM3URadio(self, count, name, source):
        nameStr = str(name)
        self.EXTM3U += '#EXTINF:-1 radio="true"'
        self.EXTM3U += ' group-title="radio"'
        self.EXTM3U += ', ' + nameStr + '\n'
        self.EXTM3U += str(source) + '\n\n'

    def addM3UChannel(self, count, name, thumb, group, id, source):
        nameStr = str(name)
        genreStr = str(group)
        self.EXTM3U += '#EXTINF:0, tvg-id="' + str(count)
        self.EXTM3U += '" tvg-name="' + nameStr
        self.EXTM3U += '" tvg-logo="' + str(thumb)
        self.EXTM3U += '" group-title="' + genreStr
        self.EXTM3U += '", ' + nameStr + '\n'
        self.EXTM3U += str(source) + '\n\n'

    def getM3UList(self):
        return self.EXTM3U


class Media:
    def __init__(self, name, thumb, group, id, epg):
        self.name = name
        self.id = id
        self.thumb = thumb
        self.group = group
        self.epg = epg
