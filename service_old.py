# -*- coding: utf-8 -*-

# import xbmcgui
from urlparse import parse_qsl
import threading
import urllib
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import kodiservice
server = None


class MyHandler(BaseHTTPRequestHandler):
    global server
    API = None
    def do_GET(self):
        import control
        try:
            if 'channel' in self.path:
                req = self.path.replace('/channel?', '')
                params = dict(parse_qsl(req))
                print(params)
                ch = kodiservice.getchannel(control.profile, params['id'], control.db)
                self.send_response(301)
                self.send_header('Location', ch.source)
                self.end_headers()
                self.finish()

            elif 'playlist' in self.path:
                m3u = kodiservice.getm3u(control.profile, control.db)
                self.send_response(200)
                self.send_header('Content-type', 'application/x-mpegURL')
                self.send_header('Connection', 'close')
                self.send_header('Content-Length', len(m3u))
                self.end_headers()
                self.wfile.write(m3u)
                self.finish()

            elif 'epg' in self.path:
                self.send_response(301)
                self.send_header('Location', control.epg_url)
                self.end_headers()
                self.finish()

            elif 'stop' in self.path:
                msg = 'Stopping ...'
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Connection', 'close')
                self.send_header('Content-Length', len(msg))
                self.end_headers()
                self.wfile.write(msg.encode('utf-8'))
                server.socket.close()

            elif 'online' in self.path:
                msg = 'Yes. I am.'
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Connection', 'close')
                self.send_header('Content-Length', len(msg))
                self.end_headers()
                self.wfile.write(msg.encode('utf-8'))
        except Exception as e:
            control.sendError(str(e))
            print('ToyaGO PVR: ' + str(e))
            # xbmcgui.Dialog().notification("ToyaGO PVR", str(e), xbmcgui.NOTIFICATION_ERROR);


class AsyncCall(object):
    def __init__(self, fnc, callback=None):
        self.Callable = fnc
        self.Callback = callback

    def __call__(self, *args, **kwargs):
        self.Thread = threading.Thread(target=self.run, name=self.Callable.__name__, args=args, kwargs=kwargs)
        self.Thread.start()
        return self

    def wait(self, timeout=None):
        self.Thread.join(timeout)
        if self.Thread.isAlive():
            raise TimeoutError()
        else:
            return self.Result

    def run(self, *args, **kwargs):
        self.Result = self.Callable(*args, **kwargs)
        if self.Callback:
            self.Callback(self.Result)


class AsyncMethod(object):
    def __init__(self, fnc, callback=None):
        self.Callable = fnc
        self.Callback = callback

    def __call__(self, *args, **kwargs):
        return AsyncCall(self.Callable, self.Callback)(*args, **kwargs)


def Async(fnc=None, callback=None):
    if fnc == None:
        def AddAsyncCallback(fnc):
            return AsyncMethod(fnc, callback)

        return AddAsyncCallback
    else:
        return AsyncMethod(fnc, callback)


@Async
def startServer():
    global server;
    import control
    server_enable = control.server_enable;
    if server_enable == 'true':
        port = int(control.server_port);
        try:
            server = SocketServer.TCPServer(('', port), MyHandler);
            server.serve_forever();
        except KeyboardInterrupt:
            if server != None:
                server.socket.close();


def stopServer():
    import control
    port = control.server_port;
    try:
        url = urllib.urlopen('http://localhost:' + str(port) + '/stop');
        code = url.getcode();
    except Exception as e:
        control.sendError(str(e))
        print('ToyaGO PVR: ' + str(e))
        # xbmcgui.Dialog().notification("ToyaGO PVR", str(e), xbmcgui.NOTIFICATION_ERROR);
    return;


def serverOnline():
    import control
    port = control.server_port;
    try:
        url = urllib.urlopen('http://localhost:' + str(port) + '/online');
        code = url.getcode();
        if code == 200:
            return True;
    except Exception as e:
        return False;
    return False;


def keepSession():
    sessionThread = threading.Thread(target=kodiservice.keepSession)  # , args=(10,)
    sessionThread.daemon = True
    sessionThread.start()


def getepg(profile, xmltv_dir, db, intepg):
    if 'true' in intepg:
        kodiservice.updateepg(profile, db)
        kodiservice.createxmltv(profile, xmltv_dir, db)
        kodiservice.updateepgdetails(profile, db)
        kodiservice.createxmltv(profile, xmltv_dir, db)
    else:
        kodiservice.internetepg(profile, xmltv_dir)


if __name__ == '__main__':
    import control
    # control.runCreator()
    kodiservice.initdb(control.profile, control.db)
    kodiservice.updatechannels(control.deviceid, control.user, control.password, control.token, control.profile, control.db)
    # kodiservice.createm3u(control.profile, control.m3u_dir, control.db)
    if control.server_enable:
        startServer()
    kodiservice.createm3u(control.profile, control.m3u_dir, control.db)
    try:
        kodiservice.internetepg(control.profile, control.xmltv_dir)
        # kodiservice.updateepg(control.profile, control.db)
        # kodiservice.createxmltv(control.profile, control.xmltv_dir, control.db)
        # kodiservice.updateepgdetails(control.profile, control.db)
        # kodiservice.createxmltv(control.profile, control.xmltv_dir, control.db)
    except Exception as e:
        print('EPG Process Error: ' + str(e))
        control.sendError('EPG Process Error')
    # control.sendInfo('Before Keep Session Process')
    keepSession()
    # control.sendInfo('After Keep Session Process')
