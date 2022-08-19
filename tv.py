# -*- coding: utf-8 -*-
import client
import model
import control

API_CAT = '/11-ogladaj-tv'
ITEM_CHANNEL = 'box with-border search-item'
IMG_PATERN = 'https://toya.net.pl/telewizja/kanaly/logo/sid/'


class GetInstance:

    def __init__(self):
        print()

    def getChannels(self):
        soap = client.authRequest(API_CAT, True)
        categories = []
        channels = soap.findAll("div", {"class": ITEM_CHANNEL})
        if control.debugAddon:
            control.logInfo(str(channels))
        for channel in channels:
            source = channel.find("a").get('href')
            entry = channel.find("img", {"class": 'logo'})
            name = entry.get('alt')
            img = entry.get('src')
            categories.append(model.Radio(name, source, img, True))
        return categories

    def getTvChannels(self, cids):
        soap = client.authRequest(API_CAT, True)
        chList = []
        counter = 0
        channels = soap.findAll("div", {"class": ITEM_CHANNEL})
        if control.debugAddon:
            control.logInfo(str(channels))
        for channel in channels:
            counter += 1
            source = channel.find("a").get('href')
            entry = channel.find("img", {"class": 'logo'})
            name = entry.get('alt')
            img = entry.get('src')
            sid = img.replace(IMG_PATERN, '').split('?')[0]
            cid = '1111' + sid
            cids.append(cid)
            chList.append(model.Channel(counter, name, source, img, counter, 'All', cid, None))
        return chList

    def getTvSource(self, source):
        soap = client.authRequest(source, False)
        return soap.find("div", {"id": 'player'}).get('data-stream')
    
    def getTvFormat(self, source):
        soap = client.authRequest(source, False)
        format = soap.find("div", {"id": 'player'}).get('data-format')
        if format == 'dash':
            format = 'mpd'
        else:
            format = 'hls'
        return format
    
    def getTvLicenseServer(self, source):
        soap = client.authRequest(source, False)
        return soap.find("div", {"id": 'player'}).get('data-license-server')
    
    def getTvManifesttUrl(self, source):
        soap = client.authRequest(source, False)
        return soap.find("div", {"id": 'player'}).get('data-manifest-uri')
