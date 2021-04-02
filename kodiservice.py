# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


def getcurrentepg(profile, db):
    import epgrepo
    erepo = epgrepo.Repository(profile + db)
    epgs = erepo.findAfterStartBeforeEnd()
    epgmap = {}
    for epg in epgs:
        epgmap[str(epg.channel)] = epg
    return epgmap


def updatechannels(devId, user, passw, token, profile, db):
    import toyago
    import channelrepo
    dummydate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    try:
        API = toyago.GetInstance(devId, user, passw, token, True)
        cids = []
        lastscan = {}
        channels = API.channels(cids)
        repo = channelrepo.Repository(profile + db)
        oldchs = repo.findall()
        for oldch in oldchs:
            lastscan[oldch.id] = oldch.lastscan
        repo.deleteall()
        for newch in channels:
            if newch.id in lastscan:
                newch.lastscan = lastscan[newch.id]
            else:
                newch.lastscan = dummydate
        repo.saveall(channels)
        repo.close()
    except Exception as e:
        print('updatechannels exception' + str(e))
        # import control
        # control.sendError(str(e))

def updateepgdetails(profile, db):
    import epgrepo
    import epg
    epgcore = epg.GetInstance()
    erepo = epgrepo.Repository(profile + db)
    epgs = erepo.findByNoDetailFromNow()
    for epg in epgs:
        e = epgcore.detail(epg)
        erepo.update(e)
    erepo.commit()
    erepo.close()


def updateepg(profile, db):
    import channelrepo
    import epgrepo
    import epg
    dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    epgcore = epg.GetInstance()
    chrepo = channelrepo.Repository(profile + db)
    erepo = epgrepo.Repository(profile + db)
    channels = chrepo.findall()
    for ch in channels:
        id = ch.cid.replace('1111', '')
        for i in range(0, 2):
            scandate = dt + timedelta(days=i)
            chdate = getdatetime(ch.lastscan)
            # print('Compare: ' + str(scandate) + ' ' + str(ch.lastscan))
            if scandate > chdate:
                # print('Scaner: ' + str(ch.name) + ' lower')
                epgcore.epg(id, scandate)
                ch.lastscan = scandate
                chrepo.update(ch)
            # else:
            #     print('EPG Scaner: ' + str(scandate) + ' already in DB')
    erepo.delteStartBefore(dt)
    chrepo.close()

def getdatetime(source):
    chdate = None
    try:
        chdate = datetime.strptime(source, '%Y-%m-%d %H:%M:%S')
    except Exception:
        chdate = source
    return chdate

def internetepg(profile, xmltv_dir):
    import client
    import control
    epg = client.requestJson(control.epg_url)
    xmltvfile = __openfile(profile, xmltv_dir, 'epg_ext.xml', 'w+')
    xmltvfile.write(epg)
    xmltvfile.close()


def createm3u(profile, m3u_dir, db):
    # import control
    m3u = getm3u(profile, db)
    m3ufile = __openfile(profile, m3u_dir, 'playlist.m3u8', 'w+')
    # m3ufile = open(profile + "playlist.m3u8", "w+")
    m3ufile.write(m3u)
    m3ufile.close()

def createxmltv(profile, xmltv_dir, db):
    import xmlCommon
    import channelrepo
    import epgrepo
    import control
    xmltv = xmlCommon.XMLTV()
    repo = channelrepo.Repository(control.profile + control.db)
    channels = repo.findallOrderByNumber()
    chamap = {}
    for ch in channels:
        # xmltv.channel(ch.id, ch.name)
        xmltv.channel(ch.name, ch.name)
        chamap[str(ch.id)] = ch.name

    erepo = epgrepo.Repository(profile + db)
    epgs = erepo.findallOrderByChannelStart()
    for ep in epgs:
        description = ep.descr
        if ep.longdesc is not None:
            description = ep.longdesc
        xmltv.programme(chamap[str(ep.channel)], ep.start, ep.end, ep.title, description, ep.category)
    epg = xmltv.gen()
    xmltvfile = __openfile(profile, xmltv_dir, 'epg.xml', 'w+')
    # xmltvfile = open(profile + "epg.xml", "w+")
    xmltvfile.write(epg)
    xmltvfile.close()

def getm3u(profile, db):
    # import channelrepo
    import playlist
    import control
    port = control.getSetting('server_port')
    playlistmanager = playlist.Playlist("ToyaGo")
    # repo = channelrepo.Repository(profile + db)
    # channels = repo.findall()
    channels = getchannels(profile, True, db)
    count = 0
    for channel in channels:
        if channel.source is not None:
            count += 1
            url = 'http://127.0.0.1:' + port + '/channel?id=' + channel.id
            playlistmanager.addM3UChannel(count, channel.name, channel.thumbnail, channel.genre,
                                          channel.name, url)
    if control.server_radio == 'true':
        for rad in getradions():
            count += 1
            playlistmanager.addM3URadio(count, rad.name, rad.source)
    # repo.close()
    # m3u = '#EXTM3U' + '\n'
    # m3u += '#EXTINF:-1, tvg-id="1" tvg-name="TVP1 HD" group-title="TVP", TVP1 HD' + '\n'
    # m3u += 'https://video-go.toya.net.pl:8081/index.m3u8'
    return playlistmanager.getM3UList().encode('utf-8')


def getradions():
    # TODO Get radios only from selected categories
    import radio
    radions = radio.GetInstance()
    return radions.getAllRadios()

def getchannels(profile, first, db):
    import channelrepo
    repo = channelrepo.Repository(profile + db)
    channels = repo.findall()
    repo.close()
    if channels.__len__() == 0 and first:
        import control
        updatechannels(control.deviceid, control.user, control.password, control.token, control.profile, control.db)
        createm3u(control.profile, control.m3u_dir, control.db)
        return getchannels(profile, False, db)
    return channels


def getchannel(profile, id, db):
    import channelrepo
    repo = channelrepo.Repository(profile + db)
    channel = repo.findbyid(id)
    repo.close()
    return channel


def keepSession():
    import control
    import xbmc
    monitor = xbmc.Monitor()
    now = datetime.now()
    nextRefresh = now + timedelta(minutes=30)
    control.logInfo('Keep Session Process Started')
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            # control.logInfo('waitForAbort')
            return
        now = datetime.now()
        deltaSeconds = (nextRefresh - now).seconds
        if deltaSeconds in range(0, 10):
            reload(control)
            # control.logInfo('Token Refreshed: ' + str(control.token))
            try:
                updatechannels(control.deviceid, control.user, control.password, control.token, control.profile, control.db)
            except Exception as e:
                control.logError('KeepSession Exception: ' + str(e))
            nextRefresh = now + timedelta(minutes=30)


def initdb(profile, db):
    # import control
    # db = control.profile + control.db
    import channelrepo
    ch = channelrepo.Repository(profile + db)
    ch.cretetable(True)
    import epgrepo
    epg = epgrepo.Repository(profile + db)
    epg.cretetable(True)

def cleardb():
    import control
    import channelrepo
    ch = channelrepo.Repository(control.profile + control.db)
    ch.deleteall()
    ch.commit()
    import epgrepo
    epg = epgrepo.Repository(control.profile + control.db)
    epg.deleteall()
    epg.commit()
    control.sendInfo('DB Cleaned')

def __openfile(profile, path, name, mode):
    location = profile
    if path not in '':
        location = path
    file = open(location + name, mode)
    return file




