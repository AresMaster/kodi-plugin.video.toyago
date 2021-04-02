# -*- coding: utf-8 -*-

import client
import json
import epgrepo
import channelrepo
import model
from datetime import datetime, timedelta
import control

apiUrl = 'https://webapi.toya.net.pl/v1/tv/guide/'
programUrl = apiUrl + 'program/'
detailUrl = apiUrl + 'programInfo/'
date_pattern = '%Y-%m-%d %H:%M:%S'


class GetInstance:

    def __init__(self):
        epglist = []
        #repo = epgrepo.Repository(control.profile + control.db)
        # dt = datetime.now()
        #epgs = repo.findAfterStartBeforeEnd()
        #for e in epgs:
        #    print(e)
        # repo.cretetable(True)
        # repo.close()
        # dt = datetime.now()
        # next = dt + timedelta(days=1)
        # self.epg('57', dt)

    def epg(self, num, dt):
        epgs = []
        dateStr = str(dt.date())
        resp = client.requestJson(programUrl + num + '?date=' + dateStr)
        epgData = json.loads(resp)['data'][num]
        for epg in epgData:
            if 'empty' not in epg['title']:
                duration = int(epg['duration'])
                start = epg['on_air_at']
                descr = epg['short_description']
                catgory = epg['category']
                end = datetime.strptime(start, date_pattern) + timedelta(minutes=duration)
                single = model.EPG(epg['id'], epg['title'], descr, None, catgory, start, end, duration, num, None, False)
                epgs.append(single)
        repo = epgrepo.Repository(control.profile + control.db)
        repo.saveall(epgs)
        repo.close()

    def detail(self, epg):
        try:
            resp = client.requestJson(detailUrl + epg.id)
            epgDetail = json.loads(resp)['data']
            country = epgDetail['country']
            long_description = epgDetail['long_description']
            data = epgDetail['data']
            epgData = json.loads(data)
            if 'directedBy' in epgData:
                directedBy = epgData['directedBy']
            if 'cast' in epgData:
                allCats = ''
                first = True
                for cast in epgData['cast']:
                    if first:
                        allCats += cast
                        first = False
                    else:
                        allCats += ', ' + cast
            original_title = epgDetail['original_title']
            epg.longdesc = long_description
        except Exception as e:
            print('EPG Detail Exception: ' + str(e))
        epg.detail = True
        return epg






if __name__ == '__main__':
    EPG = GetInstance()
    # EPG.epg()




