#!/usr/bin/python
import sys
import requests
import xbmc
import xbmcgui
import xbmcaddon

name = sys.argv[1]  #id
xbmc.log(name)
mode = sys.argv[2]  #option: rem, add
xbmc.log(mode)
url  = sys.argv[3]  #pages or devices list
xbmc.log(url)

addonID = 'plugin.video.pimatic'
addon = xbmcaddon.Addon(id=addonID)
home = addon.getAddonInfo('path').decode('utf-8')


host = addon.getSetting('ipaddress')
port = addon.getSetting('port')
username = addon.getSetting('username')
password = addon.getSetting('password')


def getList(url):
    data = requests.get('http://%s:%s@%s:%s/api/%s' % (username, password, host, port, url))
    cnt = 0
    list = []
    for i in data.json()[url]:
        #print i['id']
    #for x in range(0, cnt):
        list.append(i['id'])
    return list


def getPopup(url):
    list=getList(url)
    dialog=xbmcgui.Dialog()
    call=dialog.select("Choose",list)
    print list[call]
    url = list[call]
    return url



def addDeviceToPage(deviceid, option, url):
    if url == 'pages':
        id = getPopup(url)
        url = 'http://%s:%s@%s:%s/api/pages/%s/devices/%s' % (username, password, host, port, id, deviceid)
        xbmc.log(url)
    elif url == 'devices':
        id = getPopup(url)
        url = 'http://%s:%s@%s:%s/api/pages/%s/devices/%s' % (username, password, host, port, deviceid, id)
        xbmc.log(url)
    elif url == 'both':
        pageid = getPopup('pages')
        id = getPopup('devices')
        url = 'http://%s:%s@%s:%s/api/pages/%s/devices/%s' % (username, password, host, port, pageid, id)
    else:
        id = url
        url = 'http://%s:%s@%s:%s/api/pages/%s/devices/%s' % (username, password, host, port, deviceid, id)
        xbmc.log(url)
    if option == 'add':
        r = requests.post(url)
    elif option == 'rem':
        line1 = "Do you really want to delete the item?"
        retval_rule = xbmcgui.Dialog().yesno("Pimatic Addon", line1)
        if retval_rule == 1:
            r = requests.delete(url)
    elif option == 'ask':
        dialog=xbmcgui.Dialog()
        list = ['add', 'rem']
        call=dialog.select("Choose",list)
        option = list[call]
        if option == 'add':
            r = requests.post(url)
        elif option == 'rem':
            line1 = "Do you really want to delete the item?"
            retval_rule = xbmcgui.Dialog().yesno("Pimatic Addon", line1)
            if retval_rule == 1:
                r = requests.delete(url)
    else:
        xbmc.executebuiltin('XBMC.Notification(Pimatic Addon,unsupported action (add or rem),2000)')
        xbmc.log('Pimatic Addon - Wrong Option - %s %s %s' % (id, deviceid, option))
    #print r.status_code
    #print r.json()
    xbmc.executebuiltin('Container.Refresh')


addDeviceToPage(name, mode, url)










