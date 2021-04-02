# -*- coding: utf-8 -*-

import channelrepo
import epgrepo
import model
from datetime import datetime
import xmlCommon


if __name__ == '__main__':
    xmltv = xmlCommon.XMLTV()
    repo = channelrepo.Repository('test')
    channels = repo.findall()
    for ch in channels:
        xmltv.channel(ch.number, ch.name)

    erepo = epgrepo.Repository('test')
    epgs = erepo.findall()
    for ep in epgs:
        print(str(ep))
        xmltv.programme(str(ep.channel), ep.start, ep.end, ep.title, ep.descr, ep.category)
    epg = xmltv.gen()
    m3ufile = open(profile + "playlist.m3u8", "w+")
    m3ufile.write(m3u)
    m3ufile.close()
    # now = datetime.now()
    # format = now.strftime('%Y-%m-%d %H:%M:%S')
    # print(format)
    # repo = channelrepo.Repository('test')
    # repo.findall()
    # repo.cretetable(True)
    # channels = []
    # print(str(now.date()))
    # print(str(now.time()))

    # channel = model.Channel('a', 'b', 'c', 'd', 'e', '15', now)
    # repo.save(channel)

    #ch2 = repo.findbyid('13')
    #print('CH2: ' + ch2.cid)
    #print('ORI: ' + ch2.name)
    #ch2.name = 'T'
    #repo.update(ch2)
    #ch3 = repo.findbyid('13')
    #print('UPD: ' + ch3.name)
