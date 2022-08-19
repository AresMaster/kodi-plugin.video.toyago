# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import uuid

debugAddon = True

addon = xbmcaddon.Addon()
user = addon.getSetting('toya_go_user');
password = addon.getSetting('toya_go_pass');
tv_sort = addon.getSetting('toya_go_tv_sort');
deviceid = addon.getSetting('toya_go_device')
token = addon.getSetting('toya_go_token')
firststart = addon.getSetting('toya_go_init')
addonname = addon.getAddonInfo('name')
server_enable = addon.getSetting('server_enable')
server_port = addon.getSetting('server_port')
epg = addon.getSetting('toya_go_epg')
m3u_dir = xbmcvfs.translatePath(addon.getSetting('m3u_dir'))
xmltv_dir = addon.getSetting('xmltv_dir')
toya_go_radio = addon.getSetting('toya_go_radio')
toya_go_camera = addon.getSetting('toya_go_camera')
toya_go_freevod = addon.getSetting('toya_go_freevod')
toya_go_karaoke = addon.getSetting('toya_go_karaoke')
toya_go_tv = addon.getSetting('toya_go_tv')
server_radio = addon.getSetting('server_radio')
developr_mode = addon.getSetting('developr_mode')
has_account = addon.getSetting('has_account')
main_screen_tv = addon.getSetting('toya_go_tv_main_screen')
# server_epg = addon.getSetting('server_epg')
pvr_epg_source = addon.getSetting('pvr_epg_source')
playlist_type = addon.getSetting('playlist_type')
toya_go_tv_num = addon.getSetting('toya_go_tv_num')
# epg_url = 'https://github.com/piotrekcrash/kodi/raw/master/epg/epg_toya.xml'
ekg_kwp_url = 'https://epg.ovh/pl.gz'
PHOTO_URL = 'https://data-go.toya.net.pl/photo/categories/'
profile = dataPath = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
icon = addon.getAddonInfo('icon')


if deviceid == '':
    randomdev = str(uuid.uuid4().hex.upper()[0:10])
    addon.setSetting('toya_go_device', randomdev)
    deviceid = randomdev
# if user == '' or password == '':
#     addon.openSettings()
db = 'toyago'
monitor = xbmc.Monitor()
dialog = xbmcgui.Dialog()


def getSetting(name):
    return addon.getSetting(name)


def setSetting(name, value):
    addon.setSetting(name, value)


def openSettings():
    addon.openSettings()


def openIPTVsettings(addonName):
    xbmcaddon.Addon(id=addonName).openSettings()


def setIptvSettings(addonName):
    iptvAddon = xbmcaddon.Addon(id=addonName)
    if pvr_epg_source != '0':
        epgurl = epgSourceUrl(pvr_epg_source)
        if iptvAddon.getSetting('epgUrl') != epgurl:
            iptvAddon.setSetting('epgUrl', epgurl)
        if iptvAddon.getSetting('epgPathType') != '1':
            iptvAddon.setSetting('epgPathType', '1')
    location = profile
    if m3u_dir not in '':
        location = m3u_dir
    m3uPath = location + 'toyago.m3u8'
    if iptvAddon.getSetting('m3uPath') != m3uPath:
        iptvAddon.setSetting('m3uPath', m3uPath)
    if iptvAddon.getSetting('m3uPathType') != '0':
        iptvAddon.setSetting('m3uPathType', '0')


def epgSourceUrl(epgtype):
    # if epgtype == '1':
    #     return epg_url
    # elif epgtype == '2':
    #     return ekg_kwp_url
    # return ''
    return ekg_kwp_url

def setIptvCustomSettings():
    custom_pvraddon_name = addon.getSetting('custom_pvraddon_name')
    if custom_pvraddon_name == '':
        sendInfo('Nazwa dadatku nie została zdefiniowana')
    else:
        exist = xbmc.getCondVisibility('System.HasAddon(%s)' % custom_pvraddon_name)
        if exist == 1:
            sendInfo('Dodatek: ' + custom_pvraddon_name + ' jest zainstalowany')
        else:
            sendInfo('Brak dodatku: ' + custom_pvraddon_name)



def sendError(error):
    xbmcgui.Dialog().notification(addonname, error, xbmcgui.NOTIFICATION_ERROR)


def sendInfo(info):
    xbmcgui.Dialog().notification(addonname, info, icon=icon)


def logInfo(info):
    xbmc.log(msg=addonname + ' - ' + info, level=xbmc.LOGINFO)


def logError(error):
        xbmc.log(msg=addonname + ' - ' + error, level=xbmc.LOGERROR)

def runCreator():
    run = dialog.yesno(addonname, 'Chcesz skonfigurować dodatek?')
    if run == 1:
        confCreator()

def reauthCreator():
    again = dialog.yesno(addonname, 'Niepoprawy login lub hasło. Chcesz wprowadzić poprawne dane?')
    sendInfo(str(again))
    if again == 1:
        confCreator()

def confCreator():
    login = dialog.input('Podaj email (user@toya.net.pl)', defaultt=user, type=xbmcgui.INPUT_ALPHANUM)
    passw = dialog.input('Podaj hasło', type=xbmcgui.INPUT_ALPHANUM)
    import toyago
    API = toyago.GetInstance(deviceid, login, passw, '', False)
    try:
        API.authenticate(True)
        setSetting('toya_go_user', login)
        setSetting('toya_go_pass', passw)
        import kodiservice
        kodiservice.initdb(profile, db)
        kodiservice.updatechannels(deviceid, user, password, token, profile, db)
    except Exception as e:
        reauthCreator()
    confIptv = dialog.yesno(addonname, 'Chcesz skonfigurować automatycznie wtyczke IPTV? \nZostaniesz kilkakrotnie ' +
                                       'poproszony o restart. \nPotwierdż klikając OK')
    if confIptv == 1:
        try:
            # iptvsimple = xbmcaddon.Addon(id='pvr.iptvsimple')
            setIptvSettings()
        except RuntimeError as e:
            dialog.ok(addonname, 'Wygląda na to, że nie masz zainstalowanego dodatku IPTV Simple. Zinstaluj z ' +
                                 'Repozytorium (Klienty telewizji) i ponownie uruchom kreator w ustawieniach ToyaGO')


def setbusy(isBusy):
    if isBusy is True:
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    else:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')



