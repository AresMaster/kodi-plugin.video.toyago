# -*- coding: utf-8 -*-

import sys
# from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmc
import toyago
import service
import time
import kodiservice
import control
import urllib
import requests

# import urlparse

IMG_URL = 'https://data-go.toya.net.pl/logo/iconxmb'
IMG_RADIO = '/internetradio_icon_big.png'
IMG_CAMERA = '/camera_active.png'
IMG_TV = '/tv_icon_big.png'
IMG_FREEVOD = '/Movies_VOD_focus.png'
IMG_TV = '/tv_icon_big.png'
IMG_KARAOKE = '/KaraokeTv_focus.png'
IMG_SETTINGS = '/settings_icon_big.png'

_url = sys.argv[0]
_handle = int(sys.argv[1])


def getRadios(source):
    import radio
    radapi = radio.GetInstance()
    radios = radapi.getRadiosByCat(source)
    listing = []
    for rad in radios:
        list_item = xbmcgui.ListItem(rad.name)
        list_item.setProperty('fanart_image', rad.thumbnail)
        list_item.setArt({'thumb': control.icon})
        list_item.setArt({'landscape': rad.thumbnail})
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('music', {'title': rad.name})
        url = rad.source
        is_folder = False
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle, cacheToDisc=True)


def playCam(source):
    import cameras
    camapi = cameras.GetInstance()
    url = camapi.getCamSource(source).split('?')[0]
    play_item = xbmcgui.ListItem('CAM')
    play_item.setProperty('IsPlayable', 'true')
    xbmc.Player().play(item=url, listitem=play_item)


def playFreeVod(source):
    import freevod
    control.setbusy(True)
    freevodapi = freevod.GetInstance()
    url = freevodapi.getFreeVodSource(source)
    play_item = xbmcgui.ListItem('FreeVOD')
    play_item.setProperty('IsPlayable', 'true')
    control.setbusy(False)
    xbmc.Player().play(item=url, listitem=play_item)  # , windowed=False, startpos=3


def playTv(source):
    import tv
    control.setbusy(True)
    tvapi = tv.GetInstance()
    url = tvapi.getTvSource(source)
    format = tvapi.getTvFormat(source)
    manifest = tvapi.getTvManifesttUrl(source)
    license = tvapi.getTvLicenseServer(source)
    control.logInfo("URL TV: " + url)
    control.logInfo("FORMAT TV: " + format)
    control.logInfo("LICENSE TV: " + license)
    control.logInfo("MANIFEST TV: " + manifest)
    if manifest != "":
        url = manifest
    play_item = playTvApi(url, format, license, manifest)
    control.setbusy(False)
    xbmc.Player().play(item=url, listitem=play_item)


def playTvApi(path, format, license, manifest):
    control.logInfo("!!! RUN playTvApi !!!")
    #ch = kodiservice.getchannel(control.profile, path, control.db)
    play_item = xbmcgui.ListItem('TV', path=path)

    play_item.setProperty('IsPlayable', 'true')
    play_item.setMimeType('application/xml+dash')
    play_item.setContentLookup(False)

    play_item.setProperty('inputstream', 'inputstream.adaptive')

    play_item.setProperty(
        'inputstream.adaptive.manifest_type', format)
    if manifest != '':
        import inputstreamhelper
        ia_helper = inputstreamhelper.Helper(format, drm='com.widevine.alpha')
        if ia_helper.check_inputstream():
            # headers = {
            #     'Host': 'api-go.toya.net.pl',
            #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0',
            #     'Accept': '*/*',
            #     'Referer': 'https://go.toya.net.pl/',
            #     'Origin':'https://go.toya.net.pl',
            #     'Sec-Fetch-Dest': 'empty',
            #     'Sec-Fetch-Mode': 'cors',
            #     'Sec-Fetch-Site': 'same-site',
            #     'Sec-GPC': '1',
            # }
            # response = requests.get("https://api-go.toya.net.pl/toyago/drm/token/?cid=1167&dev=TOYA_GO_WEB", headers=headers, timeout=15, verify=False).json()
            # control.logInfo("HEADER VALUE: "+response['headerValue'])

            play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            play_item.setProperty(
            'inputstream.adaptive.manifest_update_parameter', 'full')
            #play_item.setProperty(
            #    'inputstream.adaptive.license_key', license + '|Content-Type=application/octet-stream&preauthorization='+response['headerValue']+'|b{SSM}R{KID}|B')
            play_item.setProperty(
                'inputstream.adaptive.license_key', license+'|||B')
            play_item.setProperty('inputstream.adaptive.license_flags', "persistent_storage")

            xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
    return play_item


def playKaraoke(source):
    import karaoke
    control.setbusy(True)
    karaokeapi = karaoke.GetInstance()
    url = karaokeapi.getKaraokeSource(source)
    play_item = xbmcgui.ListItem('Karaoke')
    play_item.setProperty('IsPlayable', 'true')
    control.setbusy(False)
    xbmc.Player().play(item=url, listitem=play_item)  # , windowed=False, startpos=3


def getCams(source):
    import cameras
    camapi = cameras.GetInstance()
    cams = camapi.getCamsByCat(source)
    listing = []
    for cam in cams:
        list_item = xbmcgui.ListItem(cam.name)
        list_item.setArt({'thumb': cam.thumbnail})
        list_item.setProperty('fanart_image', cam.thumbnail)
        list_item.setArt({'landscape': cam.thumbnail})
        list_item.setProperty('IsPlayable', 'false')
        list_item.setInfo('music', {'title': cam.name})
        url = '{0}?action=playCam&source={1}'.format(_url, cam.source)
        is_folder = False
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def categories(type, source):
    api = None
    src = None
    subsrc = None
    epg = {}
    if type == 'radio':
        import radio
        api = radio.GetInstance()
        cats = api.getRadioCategories()
        src = 'radios'
    elif type == 'cam':
        import cameras
        api = cameras.GetInstance()
        cats = api.getCameraCategories()
        src = 'cams'
    elif type == 'karaoke':
        import karaoke
        api = karaoke.GetInstance()
        cats = api.getKaraokeCategories(source)
        src = 'karaokeCats'
        subsrc = 'playKaraoke'
    elif type == 'freevod':
        import freevod
        api = freevod.GetInstance()
        cats = api.getFreeVodCategories(source)
        src = 'freevodCats'
        subsrc = 'playFreeVod'
    elif type == 'tv':
        import tv
        api = tv.GetInstance()
        cats = api.getChannels()
        src = 'tvs'
        subsrc = 'playTv'
    listing = []
    for cat in cats:
        is_folder = True
        name = '[B]' + cat.name + '[/B]'
        list_item = xbmcgui.ListItem(name)
        list_item.setArt({'thumb': cat.thumbnail})
        list_item.setProperty('fanart_image', cat.thumbnail)
        list_item.setArt({'landscape': cat.thumbnail})
        list_item.setProperty('IsPlayable', 'false')
        list_item.setInfo('video', {'plot': name})
        if cat.playable == True:
            url = '{0}?action={1}&source={2}'.format(_url, subsrc, cat.source)
            is_folder = False
        else:
            url = '{0}?action={1}&source={2}'.format(_url, src, cat.source)
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    addsort(type)
    xbmcplugin.endOfDirectory(_handle)


def channelsTv():
    listing = []
    addChannelsTv(listing)
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    if control.tv_sort == '1':
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc=False)


def addChannelsTv(listing):
    import tv
    counter = 0
    cids = []
    epg = {}
    API = toyago.GetInstance(control.deviceid, control.user, control.password, control.token, True)
    BROWS_API = tv.GetInstance()
    channels = BROWS_API.getTvChannels(cids)
    # channels = API.channels(cids)
    if control.epg == 'true':
        API.epg(cids, epg)
    for channel in channels:
        if channel.source != None:
            counter += 1
            channelThumb = channel.thumbnail
            title = ''
            if control.toya_go_tv_num == 'true':
                title += str(counter) + '. '
            title += '[B]' + channel.name + '[/B]'
            descr = ''
            epgTitle = ''
            next_title = ''
            if str(channel.cid) in epg:
                epgObj = epg[str(channel.cid)]
                if epgObj != None:
                    title += '[I]' + ' - " ' + epgObj.title + ' "' + '[/I]'
                    descr = epgObj.descr
                    epgTitle = epgObj.title
                    next_title = ''
                    if epgObj.next_title != None:
                        next_title = 'Nastepnie: ' + '[B]' + epgObj.next_title + '[/B]\n'
                    next_title += 'Teraz: ' + '[B]' + epgObj.title + '[/B]'
            list_item = xbmcgui.ListItem(title)
            list_item.setArt({'thumb': channelThumb})
            list_item.setProperty('fanart_image', channelThumb)
            list_item.setInfo('video', {'title': title, 'genre': channel.genre, 'plot': next_title + '\n' + descr,
                                        'plotoutline': epgTitle, 'originaltitle': epgTitle})
            list_item.setArt({'landscape': channelThumb})
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=playTv&source={1}'.format(_url, channel.source)
            is_folder = False
            listing.append((url, list_item, is_folder))


def addsort(type):
    if type == 'tv':
        if control.tv_sort == '1':
            xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)


def createm3u():
    import control
    control.logInfo('createm3u')
    m3u = getm3u()
    # control.logInfo(m3u)
    m3ufile = __openfile(control.profile, control.m3u_dir, 'toyago.m3u8', 'w+')
    m3ufile.write(str(m3u))
    m3ufile.close()
    control.sendInfo('Playlista wygenerowana')


def getm3u():
    import tv
    import playlist
    import control
    control.logInfo('getm3u')
    api = tv.GetInstance()
    channels = api.getChannels()
    count = 0
    m3u = playlist.Playlist("ToyaGo")
    for channel in channels:
        count += 1
        url = ''
        if control.playlist_type == '1':
            url = '{0}?action={1}&source={2}'.format(_url, 'playTv', channel.source)
        elif control.playlist_type == '0':
            url = 'http://localhost:' + str(control.server_port) + '/channel?id=' + channel.source.split('/')[2]
        m3u.addM3UChannel(count, channel.name, channel.thumbnail, 'All', channel.name, url)
    return m3u.getM3UList()


def __openfile(profile, path, name, mode):
    location = profile
    if path not in '':
        location = path
    import os
    file = open(os.path.join(location,name), mode)
    return file


def mainscreen():
    listing = []
    services(listing)
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle, cacheToDisc=False)

def oldchannels():
    listing = []
    if control.toya_go_tv == 'test':
        cids = []
        channels = kodiservice.getchannels(control.profile, True, control.db)
        epg = {}
        if 'true' in control.epg:
            for ch in channels:
                cids.append(ch.cid)
            try:
                API = toyago.GetInstance(control.deviceid, control.user, control.password, control.token, True)
                API.epg(cids, epg)
            except Exception as e:
                control.reauthCreator()

        for channel in channels:
            if channel.source != None:
                channelThumb = channel.thumbnail
                title = '[B]' + channel.name + '[/B]'
                descr = ''
                epgTitle = ''
                next_title = ''
                if str(channel.cid) in epg:
                    epgObj = epg[str(channel.cid)]
                    if epgObj != None:
                        title += '[I]' + ' - " ' + epgObj.title + ' "' + '[/I]'
                        descr = epgObj.descr
                        epgTitle = epgObj.title
                        next_title = ''
                        if epgObj.next_title != None:
                            next_title = 'Nastepnie: ' + '[B]' + epgObj.next_title + '[/B]\n'
                        next_title += 'Teraz: ' + '[B]' + epgObj.title + '[/B]'
                list_item = xbmcgui.ListItem(title)
                list_item.setArt({'thumb': channelThumb})
                list_item.setProperty('fanart_image', channelThumb)
                list_item.setInfo('video', {'title': title, 'genre': channel.genre, 'plot': next_title + '\n' + descr,
                                            'plotoutline': epgTitle, 'originaltitle': epgTitle})
                list_item.setArt({'landscape': channelThumb})
                list_item.setProperty('IsPlayable', 'true')
                url = '{0}?action=play&video={1}'.format(_url, channel.id)
                is_folder = False
                listing.append((url, list_item, is_folder))


def toyaGoFolder():
    listing = []
    addToyaGoElements(listing)
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle, cacheToDisc=False)


def addEntry(listing, label, img, url, isFolder):
    # list_item = xbmcgui.ListItem(label=label, thumbnailImage=IMG_URL + img)
    list_item = xbmcgui.ListItem(label)
    list_item.setArt({'thumb': IMG_URL + img})
    url = url.format(_url)
    list_item.setInfo('video', {'plot': '[B]' + label + '[/B]'})
    listing.append((url, list_item, isFolder))


def addToyaGoElements(listing):
    if not (control.user == '' and control.password == '') and control.has_account == 'true':
        if control.main_screen_tv == 'false':
            addEntry(listing, 'Telewizja', IMG_TV, '{0}?action=channelsTv', True)
    if control.toya_go_radio == 'true':
        addEntry(listing, 'Radio', IMG_RADIO, '{0}?action=radioCats', True)
    if control.toya_go_camera == 'true':
        addEntry(listing, 'Kamery', IMG_CAMERA, '{0}?action=camCats', True)
    if control.has_account == 'true':
        if control.toya_go_camera == 'true':
            addEntry(listing, 'FreeVOD', IMG_RADIO, '{0}?action=freevodCats', True)
        if control.toya_go_karaoke == 'true':
            addEntry(listing, 'Karaoke', IMG_KARAOKE, '{0}?action=karaokeCats', True)
    addEntry(listing, 'Ustawienia', IMG_SETTINGS, '{0}?action=settings', False)
    addEntry(listing, 'Wygeneruj Playlist M3U', IMG_SETTINGS, '{0}?action=generatePlaylist', False)


def services(listing):
    if control.toya_go_tv == 'true' and control.main_screen_tv == 'true' and control.has_account == 'true':
        list_item = xbmcgui.ListItem('ToyaGO')
        list_item.setArt({'thumb': control.icon})
        is_folder = True
        url = '{0}?action=toyaGoFolder'.format(_url)
        list_item.setInfo('video', {'plot': 'ToyaGo - Kategorie, Ustawienia'})
        listing.append((url, list_item, is_folder))
        addChannelsTv(listing)
    else:
        addToyaGoElements(listing)


def play_video(path):
    ch = kodiservice.getchannel(control.profile, path, control.db)
    play_item = xbmcgui.ListItem(path=ch.source)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    # control.sendInfo(paramstring)
    params = dict(urllib.parse.parse_qsl(paramstring))
    if params:
        if params['action'] == 'listing':
            print('listing')
        elif params['action'] == 'play':
            play_video(params['video'])
        elif params['action'] == 'stopServer':
            stopServer()
        elif params['action'] == 'startServer':
            startServer()
        elif params['action'] == 'iptvSettings':
            control.openIPTVsettings(params['target'])
        elif params['action'] == 'setIptvSettings':
            control.setIptvSettings(params['target'])
        elif params['action'] == 'setIptvCustomSettings':
            control.setIptvCustomSettings()
        elif params['action'] == 'refreshtoken':
            kodiservice.refreshsession()
        elif params['action'] == 'cleardb':
            kodiservice.cleardb()
        elif params['action'] == 'freevodCats':
            source = None
            if 'source' in params:
                source = params['source']
            categories('freevod', source)
        elif params['action'] == 'radioCats':
            categories('radio', None)
        elif params['action'] == 'karaokeCats':
            source = None
            if 'source' in params:
                source = params['source']
            categories('karaoke', source)
        elif params['action'] == 'tvChannels':
            categories('tv', None)
        elif params['action'] == 'radios':
            getRadios(params['source'])
        elif params['action'] == 'camCats':
            categories('cam', None)
        elif params['action'] == 'cams':
            getCams(params['source'])
        elif params['action'] == 'playCam':
            playCam(params['source'])
        elif params['action'] == 'playFreeVod':
            playFreeVod(params['source'])
        elif params['action'] == 'playKaraoke':
            playKaraoke(params['source'])
        elif params['action'] == 'playTv':
            playTv(params['source'])
        elif params['action'] == 'settings':
            control.openSettings()
        elif params['action'] == 'generatePlaylist':
            createm3u()
        elif params['action'] == 'channelsTv':
            channelsTv()
        elif params['action'] == 'toyaGoFolder':
            toyaGoFolder()
    else:
        mainscreen()


def startServer():
    port = control.addon.getSetting('server_port');
    if service.serverOnline():
        xbmcgui.Dialog().notification(control.addonname, 'Serwer obecnie działa - Port: ' + str(port),
                                      xbmcgui.NOTIFICATION_INFO);
    else:
        service.startServer();
        time.sleep(5);
        if service.serverOnline():
            control.sendInfo('Server został uruchomiony.')
        else:
            control.sendInfo('Server nie może zostać uruchominy, spróbuj ponownie.')


def stopServer():
    import control
    if service.serverOnline():
        service.stopServer()
        time.sleep(5);
        control.sendInfo('Server został wyłączony.')
    else:
        control.sendInfo('Server obecnie jest wyłączony.')


if __name__ == '__main__':
    router(sys.argv[2][1:])
