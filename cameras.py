# -*- coding: utf-8 -*-

import client
import model
#import control

WEATHER = '/weather'
API_CAT = '/25'
ITEM_CATEGORY = 'item isotope-item category'
ITEM_CAMERA = 'item isotope-item --locked search-item'
PHOTO_URL = 'https://data-go.toya.net.pl/photo/'


class GetInstance:

    def __init__(self):
        print()

    def getCamSource(self, camsource):
        soap = client.getRequest(camsource)
        # detailId = camsource.split('/')[2]
        # detailJson = client.requestJson(API_URL + WEATHER + '/' + detailId)
        # detailData = json.loads(detailJson)
        # print('WEATHER: ' + str(detailData['wind']))
        return soap.find("div", {"id": 'player'}).get('data-stream')

    def getCamsByCat(self, catsource):
        soap = client.getRequest(catsource)
        rads = soap.findAll("li", {"class": ITEM_CAMERA})
        radios = []
        for rad in rads:
            source = rad.find("a").get('href')
            img = rad.find("img").get('src')
            name = rad.get('data-search')
            radios.append(model.Radio(name, source, img, True))
        return radios

    def getCameraCategories(self):
        soap = client.getRequest(API_CAT)
        cats = soap.findAll("li", {"class": ITEM_CATEGORY})
        categories = []
        for cat in cats:
            source = cat.find("a").get('href')
            img = cat.find("img").get('src')
            # name = 'Pokaż kamery >>'
            name = cat.find("a", {"class": 'pure-button pure-button-success'}).get('href')
            name = name.replace('/25-kamery/', '').split('-')[1].capitalize()
            categories.append(model.Radio(name, source, img, False))
        return categories
