# -*- coding: utf-8 -*-
import client
import model
import control

API_CAT = '/23'
CAT_URL = 'https://data-go.toya.net.pl/photo/categories/free/'
ITEM_CATEGORY = 'item isotope-item category'
ITEM_KARAOKE = 'item isotope-item not-locked search-item'


class GetInstance:

    def __init__(self):
        print()

    def getKaraokeCategories(self, src):
        categories = []
        source = API_CAT
        if src is not None:
            source = src
        soap = client.authRequest(source, True)
        cats = soap.findAll("li", {"class": ITEM_CATEGORY})
        for cat in cats:
            source = cat.find("a").get('href')
            img = cat.find("img").get('src')
            name = img.replace(control.PHOTO_URL, '').replace('.png', '').replace('.jpg', '')\
                .capitalize().replace('_', ' ')
            categories.append(model.Radio(name, source, img, False))
        vods = soap.findAll("li", {"class": ITEM_KARAOKE})
        for vod in vods:
            source = vod.find("a").get('href')
            entry = vod.find("img", {"class": 'poster'})
            name = entry.get('alt')
            img = entry.get('src')
            categories.append(model.Radio(name, source, img, True))
        return categories


    def getKaraokeSource(self, camsource):
        soap = client.authRequest(camsource, True)
        playUrl = soap.find("div", {"class": 'main'}).find("a").get('href')
        player = client.authRequest(playUrl, False)
        return player.find("div", {'id': 'player'}).get('data-stream')



