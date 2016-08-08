#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import requests



addonID = 'plugin.program.pimatic'
addon = xbmcaddon.Addon(id=addonID)
home = addon.getAddonInfo('path').decode('utf-8')
pluginhandle = int(sys.argv[1])

host = addon.getSetting('ipaddress')
port = addon.getSetting('port')
username = addon.getSetting('username')
password = addon.getSetting('password')



def getDimmerDevice(deviceid):
    print deviceid
    print
    print deviceid
    cnt = -1
    data = requests.get('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))
    for i in data.json()['device']['attributes']:
        cnt += 1
        name = i['name']
        value = i['value']
        url = str(cnt)
        name = name +' is '+ str(value)
        addDir(name,url,6,'',deviceid)

        '''
        if i['unit'] in data.json()['device']['attributes']:
            print i['unit']
        '''

def getSwitchDevice(deviceid):
    print
    data = requests.get('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))
    cnt = 0
    for i in data.json()['device']['actions']:
        cnt += 1
    for x in range(0, cnt):
        name = data.json()['device']['actions'][x]['name']
        url = name
        addDir(name,url,4,'',deviceid)
    addDir('History','0',6,'',deviceid)

def getTempDevice(deviceid):
    data = requests.get('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))
    cnt=0
    for i in data.json()['device']['attributes']:
        cnt+=1
    for x in range(0, cnt):
        name = data.json()['device']['attributes'][x]['name']
        unit = data.json()['device']['attributes'][x]['unit']
        value = data.json()['device']['attributes'][x]['value']
        name = (name).encode('utf-8') +':   '+ repr(value) + (unit).encode('utf-8')
        url = str(x)
        addDir(name,url,6,'',deviceid)

def getButtonDevice(deviceid):
    data = getURL('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))['device']
    for i in data['config']['buttons']:
        name = i['text']
        url = 'buttonPressed?buttonId=' + i['id']
        addDir(name,url,4,'',deviceid)
    addDir('History','0',6,'',deviceid)

def getButtonDevice2(deviceid):
    print
    data = getURL('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))['device']

def getSysSenDevice(name, deviceid):
    print
    cnt = -1
    data = getURL('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))['device']
    for i in data['attributes']:
        cnt += 1
        name = i['name']
        if i['name']=='memory':
            print 'MEMORY'
            value = i['value'] / 10000
            value = value / 100.00
            value = str(value) + 'MB'
        elif i['name']=='diskusage':
            print 'DISK'
            value = str(round(i['value'], 2)) + i['unit']
        else:
            if i['label']=='Temperature':
                value = str(i['value']) + repr(i['unit'])#.encode('utf-8')
            else:
                try:
                    value = str(i['value']) + (i['unit']).encode('utf-8')
                except KeyError:
                    try:
                        value = str(i['value'])
                    except KeyError:
                        value = 'KeyError'
                xbmc.log('KEYRROR - getSysSenDevice - %s - %s' % (name, deviceid))
        url = str(cnt)
        #value = str(value)
        name = (name).encode('utf-8') +' '+ (value).encode('utf-8')
        addDir(name,url,6,'',deviceid)

def getPresence(deviceid):
    data = requests.get('http://%s:%s@%s:%s/api/devices/%s' % (username, password, host, port, deviceid))
    value = data.json()['device']['attributes'][0]['value']
    if str(value) == 'False':
        value = 'absent'
    else:
        value = 'present'
    name = deviceid +' is '+ value
    url = '0'
    addDir(name,url,6,'',deviceid)

def getURL(url):
    r=requests.get(url)
    data=r.json()
    return data
    r.close()

def addDir(name,url,mode,iconimage,deviceid):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&deviceid="+urllib.quote_plus(deviceid)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name} )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok