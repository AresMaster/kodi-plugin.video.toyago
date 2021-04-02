# -*- coding: utf-8 -*-
import client
import model
import control

API_URL = 'https://go.toya.net.pl'
API_CAT = '/15'
ITEM_CATEGORY = 'item isotope-item category'
ITEM_RADIO = 'item isotope-item category'


class GetInstance:

    def __init__(self):
        print()

    def getAllRadios(self):
        radios = []
        categories = self.getRadioCategories()
        for category in categories:
            catradios = self.getRadiosByCat(category.source)
            radios.extend(catradios)
        return radios

    def getRadiosByCat(self, catsource):
        soap = client.getRequest(catsource)
        rads = soap.findAll("li", {"class": ITEM_RADIO})
        radios = []
        for rad in rads:
            source = rad.find("audio").get('src')
            img = rad.find("img").get('src')
            name = rad.find('span', {'class', 'item-small-title'}).getText().strip()
            radios.append(model.Radio(name, source, img, True))
        return radios

    def getRadioCategories(self):
        soap = client.getRequest(API_CAT)
        cats = soap.findAll("li", {"class": ITEM_CATEGORY})
        categories = []
        for cat in cats:
            source = cat.find("a").get('href')
            img = cat.find("img").get('src')
            name = img.replace(control.PHOTO_URL, '').replace('.png', '').capitalize().replace('_', ' ')
            categories.append(model.Radio(name, source, img, False))
        return categories
