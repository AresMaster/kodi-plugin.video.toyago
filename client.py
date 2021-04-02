# -*- coding: utf-8 -*-
import requests
import control
import pickle
from bs4 import BeautifulSoup
import os.path

API_URL = 'https://api-go.toya.net.pl/toyago/index.php'
BROWS_URL = 'https://go.toya.net.pl'
BROWS_AUTH_URL = 'https://auth.toya.net.pl'
nextUrl = 'aHR0cHM6Ly9nby50b3lhLm5ldC5wbC8'


def request(url, data):
    headers = {'Content-type': 'application/xml', 'Content-Length': str(len(data))}
    r = requests.post(url, headers=headers, data=data)
    r.encoding = 'utf-8'
    return r.content


def requestJson(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
    return r.text


def authRequest(url, check):
    url = BROWS_URL + url
    session = getsession()
    soap = get(session, url)
    if check:
        if isAuthorized(soap):
            return soap
        else:
            authenticate()
            session = getsession()
            soap = get(session, url)
            if not isAuthorized(soap):
                control.sendError('Problem z logowaniem')
    return soap


def isAuthorized(soap):
    check = soap.find("header", {"id": 'main_header'}).find("a", {"href": '/logout'})
    if check is not None:
        return True
    else:
        return False


def get(session, url):
    headers = {'Referer': BROWS_URL}  # 'Content-type': 'application/x-www-form-urlencoded',
    r = session.get(url, headers=headers, allow_redirects=False)
    if r.status_code != 200:
        authenticate()
        session = getsession()
        r = session.get(url, headers=headers, allow_redirects=False)
    r.encoding = 'utf-8'
    return BeautifulSoup(r.text, 'html.parser')


def getRequest(url):
    headers = {'Referer': BROWS_URL}
    r = requests.get(BROWS_URL + url, headers=headers)
    r.encoding = 'utf-8'
    return BeautifulSoup(r.text, 'html.parser')


def getsession():
    sessionfile = control.profile + 'session.dat'
    session = requests.Session()
    if os.path.isfile(sessionfile):
        reloadSession(session, sessionfile)
    else:
        authenticate()
        reloadSession(session, sessionfile)
    return session


def reloadSession(session, sessionfile):
    with open(sessionfile, 'rb') as f:
        session.cookies.update(pickle.load(f))


def authenticate():
    control.logInfo('Authentication')
    s = requests.Session()
    s.get(BROWS_URL)
    headers = {'Content-type': 'application/x-www-form-urlencoded', 'Referer': BROWS_URL}
    payload = {'f_user': control.user, 'f_pass': control.password, 'remeber_me': 'on', 'f_city': 'lodz',
               'from': 'toyago-beta', 'nextURL': nextUrl, 'referrerURL': nextUrl, 'submit': 'Zaloguj'}
    r = s.post(BROWS_AUTH_URL, headers=headers, data=payload, allow_redirects=False)
    location = r.headers['Location']
    # requests.utils.add_dict_to_cookiejar(s.cookies, {'ua_resolution': '1920x1080', 'toyago.config': control.deviceid})
    r = s.get('https:' + location)
    # for cookie in s.cookies:
    #     control.logInfo(str(cookie))
    # control.logInfo(str(r.headers))
    with open(control.profile + 'session.dat', 'wb') as f:
        pickle.dump(s.cookies, f)
    return s





