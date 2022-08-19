# -*- coding: utf-8 -*-
import client
import model
#import control

API_CAT = '/22-free-vod'
CAT_URL = 'https://data-go.toya.net.pl/photo/categories/free/'
ITEM_CATEGORY = 'item isotope-item category'
ITEM_FREEVOD = 'item isotope-item not-locked search-item'


class GetInstance:

    def __init__(self):
        print()

    def getFreeVodCategories(self, src):
        categories = []
        cat = API_CAT
        if src is not None:
            cat = src
        soap = client.authRequest(cat, True)
        cats = soap.findAll("li", {"class": ITEM_CATEGORY})
        for cat in cats:
            source = cat.find("a").get('href')
            img = cat.find("img").get('src')
            name = img.replace(CAT_URL, '').replace('.jpg', '').replace('.png', '').replace('2', '')\
                .capitalize().replace('_', ' ').replace('-', ' ')
            categories.append(model.Radio(name, source, img, False))
        vods = soap.findAll("li", {"class": ITEM_FREEVOD})
        for vod in vods:
            source = vod.find("a").get('href')
            entry = vod.find("img", {"class": 'poster'})
            name = entry.get('alt')
            img = entry.get('src')
            categories.append(model.Radio(name, source, img, True))
        return categories


    def getFreeVodSource(self, camsource):
        soap = client.authRequest(camsource, True)
        playUrl = soap.find("div", {"class": 'main'}).find("a").get('href')
        soap = client.authRequest(playUrl, False)
        return soap.find("div", {"id": 'player'}).get('data-stream')

