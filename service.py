# -*- coding: utf-8 -*-
import socketserver
# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
# from urlparse import parse_qsl
import threading
import http.server
import urllib
server = None

Handler = http.server.BaseHTTPRequestHandler


class MyHandler(Handler):
    global server
    API = None

    def do_GET(self):
        import control
        control.setbusy(True)
        import tv
        try:
            if 'channel' in self.path:
                req = self.path.replace('/channel?', '')
                params = dict(urllib.parse.parse_qsl(req))
                api = tv.GetInstance()
                url = api.getTvSource('/tv/' + str(params['id']))
                self.send_response(301)
                self.send_header('Location', url)
                self.end_headers()
                self.finish()
        except Exception as e:
            control.sendError('Błąd inicjalizacji kanału TV')
            control.logError(str(e))
        control.setbusy(False)


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
            server = socketserver.TCPServer(('', port), MyHandler);
            server.serve_forever();
        except KeyboardInterrupt:
            if server != None:
                server.socket.close();


def stopServer():
    import control
    try:
        url = urllib.urlopen('http://localhost:' + str(control.server_port) + '/stop')
        code = url.getcode()
    except Exception as e:
        control.sendError(str(e))
    return True


def serverOnline():
    import control
    try:
        url = urllib.urlopen('http://localhost:' + str(control.server_port) + '/online')
        code = url.getcode()
        if code == 200:
            return True
    except Exception as e:
        return False
    return False


def initSession():
    import client
    client.authRequest('', True)


if __name__ == '__main__':
    import control
    if control.server_enable:
        initSession()
        startServer()
