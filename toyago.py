# -*- coding: utf-8 -*-
import client
import xmlCommon
import threading
from datetime import datetime, timedelta
import time
import datasource
import control

apiUrl = 'https://api-go.toya.net.pl/toyago/index.php'


class GetInstance:

    def __init__(self, devId, user, passw, token, auth):
        self.deviceId = devId
        self.user = user
        self.passw = passw
        self.token = token
        self.xmlReq = xmlCommon.Request()
        self.xmlResp = xmlCommon.Response()
        if auth:
            self.authenticate(True)

    def authenticate(self, valid):
        import control
        isvalid = self.setVersion()
        # print('Token valid: ' + str(isvalid) + ' prev: ' + str(valid))
        if not isvalid:
            authReq = self.xmlReq.auth(self.deviceId, self.user, self.passw)
            authResp = client.request(apiUrl, authReq)
            token = self.xmlResp.parseToken(authResp)
            if 'Wrong' in token:
                raise Exception('Wrong Credentials')
            self.token = token
            control.setSetting('toya_go_token', token)
            return self.authenticate(False)
        elif not isvalid and not valid:
            raise Exception('Login failed')
        else:
            return valid

    # Deprecated
    def auth(self):
        authReq = self.xmlReq.auth(self.deviceId, self.user, self.passw)
        authResp = client.request(apiUrl, authReq)
        token = self.xmlResp.parseToken(authResp)
        self.token = token
        self.setVersion()

    def setVersion(self):
        verReq = self.xmlReq.version(self.deviceId, '2.0', self.token)
        verResp = client.request(apiUrl, verReq)
        isvalid = self.xmlResp.parseVersion(verResp)
        return isvalid

    def channels(self, cids):
        channelsReq = self.xmlReq.getChannels(self.token, self.deviceId)
        channelsResp = client.request(apiUrl, channelsReq)
        channels = self.xmlResp.parseChannels(channelsResp, cids)
        return channels

    def epg(self, cids, epg):
        epgStr = self.xmlReq.getEPG(self.token, self.deviceId, cids)
        # control.logError(str(epgStr))
        epgResp = client.request(apiUrl, epgStr).decode('utf-8')
        # control.logError(str(epgResp))
        self.xmlResp.parseEPG(epgResp, epg)

    # Deprecated
    def channel(self, cid, number, parent):
        cid2 = str(cid).replace('1111', '')
        channelReq = self.xmlReq.getChannel(self.token, self.deviceId, cid2, number, parent)
        channelResp = client.request(apiUrl, channelReq)
        return channelResp


    def updatechannels(self):
        table = 'channel'
        db = datasource.Create('toyago')
        db.drop(table)
        colums = ['url text']
        db.create(table, colums)
        self.authenticate(True)
        cids = []
        channels = self.channels(cids)
        values = []
        for ch in channels:
            values.append((ch.name, ch.source))
        print(str(values.__len__()))
        db.saveall(table, values, 2)
        db.commit()
        db.close()


    def loadChannels(self):
        table = 'channel'
        db = datasource.Create('toyago')
        channels = db.findall(table)
        for channel in channels:
            print(channel[0] + ' ' + channel[1])
        db.close()


