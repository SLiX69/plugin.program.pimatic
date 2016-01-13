#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import requests
import datetime



addonID = 'plugin.video.pimatic'
addon = xbmcaddon.Addon(id=addonID)
home = addon.getAddonInfo('path').decode('utf-8')
pluginhandle = int(sys.argv[1])

host = addon.getSetting('ipaddress')
port = addon.getSetting('port')
username = addon.getSetting('username')
password = addon.getSetting('password')



def getDeviceTemplate(deviceid):
    print 'GETDEViCETEMPLATE'
    print deviceid
    try:
        data = getURL('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))['device']
        template = data['template']
    except KeyError:
        xbmc.log('GET DEVICE TEMPLATE KEY ERROR')
        template = 'KeyError'
    return template

def getDeviceActions(deviceid):
    data = requests.get('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))
    cnt = 0
    for i in data.json()['device']['actions']:
        cnt += 1
    for x in range(0, cnt):
        name = data.json()['device']['actions'][x]['name']
        url = name
        addDir(name,url,4,'',deviceid)

def getDeviceValue(deviceid, url):
    data = requests.get('http://%s:%s@%s:%s/api/devices/%s/' % (username, password, host, port, deviceid))
    cnt=0
    value = ''
    try:                                # big 'try and except' (global) for all templates and else
        if url == 'temperature':
            for i in data.json()['device']['attributes']:
                cnt+=1
            for x in range(0, cnt):
                #name = data.json()['device']['attributes'][x]['name']
                unit = (data.json()['device']['attributes'][x]['unit']).encode('utf-8')
                valuet = data.json()['device']['attributes'][x]['value']
                value = value + ' ' + repr(valuet) + repr(unit)
                #name = (name).encode('utf-8') +':   '+ repr(value) + repr(unit).encode('utf-8')
                #value = (value).encode('utf-8')
        elif url == 'presence':
            value = data.json()['device']['attributes'][0]['value']
            if str(value) == 'False':
                value = ' is absent'
            else:
                value = ' is present'
        elif url == 'switch':
            value = data.json()['device']['attributes'][0]['value']
            value = ' is ' + str(value)
        elif url == 'device':
            print

        elif url == 'device1':
            print
            for i in data.json()['device']['attributes']:
                cnt += 1
            for x in range(0, cnt):
                unit = data.json()['device']['attributes'][x]['unit']
                valuet = data.json()['device']['attributes'][x]['value']
                valuet = str(valuet)
                unit = repr(unit)
                value = valuet + ' ' + value + unit
        elif url == 'dimmer':
            print
            value = ' is ' + str(data.json()['device']['attributes'][0]['value']) + str(data.json()['device']['attributes'][0]['unit'])
        else:
            value = ' is ' + str(data.json()['device']['attributes'][0]['value'])
    except KeyError:
        value = 'KeyError'
        #kodilog('KeyError - getDeviceValue')
    #value = value.encode('utf-8')
    return value

def getDeviceHistory(deviceid, url):
    data = requests.get('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))
    cnt = 0
    url = int(url)
    for i in data.json()['device']['attributes'][url]['history']:
        cnt += 1
    for x in range(0, cnt):
        time = data.json()['device']['attributes'][url]['history'][x]['t']
        state = str(data.json()['device']['attributes'][url]['history'][x]['v'])
        time = time / 1000
        time2 = datetime.datetime.fromtimestamp(time)
        time = (time2.strftime('%Y-%m-%d %H:%M:%S'))
        name = (time).encode('utf-8') +' was '+ (state).encode('utf-8')
        addDir(name,'',90,'','')

    xbmcplugin.endOfDirectory(pluginhandle,succeeded=True,updateListing=False,cacheToDisc=True)

def getActionsList(deviceid):
    data = requests.get('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))
    cnt = 0
    list = []
    for i in data.json()['device']['actions']:
        cnt += 1
    for x in range(0, cnt):
        list.append(data.json()['device']['actions'][x]['name'])
    return list

def getButtonsList(deviceid):
    data = getURL('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))
    cnt = 0
    actions = []
    for i in data.json()['config']['buttons']:
        cnt += 1
    for x in range(0, cnt):
        actions.append(data.json()['config']['buttons'][x]['id'])
    return list

def addDir(name,url,mode,iconimage,deviceid):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&deviceid="+urllib.quote_plus(deviceid)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name} )
        liz.addContextMenuItems([ ('Refresh', 'Container.Refresh'),
                                ('Go up', 'Action(ParentDir)') ])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def getURL(url):
    r=requests.get(url)
    data=r.json()
    return data
    r.close()
