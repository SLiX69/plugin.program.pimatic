#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import requests


from getDeviceStuff import getDeviceTemplate,getDeviceValue



addonID = 'plugin.video.pimatic'
addon = xbmcaddon.Addon(id=addonID)
home = addon.getAddonInfo('path').decode('utf-8')
pluginhandle = int(sys.argv[1])


host = addon.getSetting('ipaddress')
port = addon.getSetting('port')
username = addon.getSetting('username')
password = addon.getSetting('password')



def getPages():
    data = getURL('http://%s:%s@%s:%s/api/pages' % (username, password, host, port))['pages']
    for i in data:
        name = (i['name']).encode('utf-8')
        url = i['id']
        print
        print url
        addDir(name,url,2,'','',)
    addDir('add Page','',29,'','')
    addDir('rem Page','',31,'','')
    xbmcplugin.endOfDirectory(pluginhandle)

def getGroup(url):
    url = int(url)
    data=getURL('http://%s:%s@%s:%s/api/groups' % (username, password, host, port))['groups']
    for i in data[url]['devices']:
        name = i
        deviceid = i
        url = getDeviceTemplate(name)
        addDir(name,url,3,'',deviceid,)
    xbmcplugin.endOfDirectory(pluginhandle,succeeded=True,updateListing=False,cacheToDisc=True)

def getRule(deviceid):
    data = getURL('http://%s:%s@%s:%s/api/rules/%s' % (username, password, host, port, deviceid))['rule']['conditionToken']
    name = data
    addDir('IF: '+name,'',90,'','',)
    url = getURL('http://%s:%s@%s:%s/api/rules/%s' % (username, password, host, port, deviceid))['rule']['actionsToken']
    addDir('THEN: '+url,url,13,'','',)

    xbmcplugin.endOfDirectory(pluginhandle,succeeded=True,updateListing=False,cacheToDisc=True)

def getPage(url):
    data = getURL('http://%s:%s@%s:%s/api/pages/%s' % (username, password, host, port, url))['page']
    pageid = url
    xbmc.log(pageid)
    try:                                # if page is empty
        print data['devices'][0]['deviceId']
    except:
        addDir('add Device', url, 14, '', '')
    for i in data['devices']:
        name = i['deviceId']
        deviceid = name
        try:
            url = getDeviceTemplate(name)
            value = getDeviceValue(name, url)
        except KeyError:
            url = 'KeyError'
            value = 'KeyError'
        print
        print value
        name = name + value
        u = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/addDeviceToPage2.py,').decode('utf-8')
        xbmc.log(u)
        cm = []
        cm.append( ('Add device', "XBMC.RunScript(%s%s,add,devices)" % (u, pageid)) )
        cm.append( ('Remove device', "XBMC.RunScript(%s%s,rem,%s)" % (u, pageid, deviceid)) )
        addDir(name,url,3,'',deviceid,cm)
        xbmc.log(str(cm))
    xbmcplugin.endOfDirectory(pluginhandle,succeeded=True,updateListing=False,cacheToDisc=True)

def getAllDevices():
    data = getURL('http://%s:%s@%s:%s/api/devices' % (username, password, host, port))['devices']
    for i in data:
        name = (i['id']).encode('utf-8')
        deviceid = name
        url = getDeviceTemplate(deviceid)
        u = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/addDeviceToPage.py,'+ name +',').decode('utf-8')
        cm = []
        cm.append( ('Add to page', "XBMC.RunScript(%s add,pages)" % u) )
        cm.append( ('Remove from page', "XBMC.RunScript(%s rem,pages)" % u) )
        addDir(name,url,3,'',deviceid,cm)
        xbmc.log(str(cm))
    xbmcplugin.endOfDirectory(pluginhandle,succeeded=True,updateListing=False,cacheToDisc=True)

def getAllRules():
    data = getURL('http://%s:%s@%s:%s/api/rules' % (username, password, host, port))['rules']
    for i in data:
        name=(i['name']).encode('utf-8')
        deviceid=i['id']
        addDir(name,'',8,'',deviceid,)
    xbmcplugin.endOfDirectory(pluginhandle,succeeded=True,updateListing=False,cacheToDisc=True)

def getAllVars():
    data = getURL('http://%s:%s@%s:%s/api/variables' % (username, password, host, port))['variables']
    for i in data:
        name=i['name']
        xbmc.log(name)
        try:
            value=i['value']
            unit=i['unit']
            name = name.encode('utf-8') +' is '+ (str(value)).encode('utf-8') + unit.encode('utf-8')
        except KeyError:
            try:
                value=i['value']
                name = name.encode('utf-8') +' is '+ (str(value)).encode('utf-8')
            except KeyError:
                name = name.encode('utf-8') + 'KeyError'
        addDir(name,'',90,'','',)
    xbmcplugin.endOfDirectory(pluginhandle,succeeded=True,updateListing=False,cacheToDisc=True)

def getAllGroups():
    data = getURL('http://%s:%s@%s:%s/api/groups' % (username, password, host, port))['groups']
    cnt = -1
    for i in data:
        cnt += 1
        name=(i['name']).encode('utf-8')
        id=i['id']
        url = str(cnt)
        addDir(name,url,11,'','',)
    addDir('add Group','',33,'','')
    addDir('rem Group','',35,'','')
    xbmcplugin.endOfDirectory(pluginhandle,succeeded=True,updateListing=False,cacheToDisc=True)


def addDir(name,url,mode,iconimage,deviceid,cm=False):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&deviceid="+urllib.quote_plus(deviceid)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name} )
        if cm:
            u2=sys.argv[0]+"?mode="+urllib.quote_plus('update')
            cm.append( ('Bibliothek aktualisieren', "XBMC.RunPlugin(%s)" % u2) )
            liz.addContextMenuItems( cm )
        else:
            cm=[]
            u2=sys.argv[0]+"?mode="+urllib.quote_plus('test')
            cm.append( ('Bibliothek aktualisieren', "XBMC.RunPlugin(%s)" % u2) )
            cm.append( ('Refresh', 'Container.Refresh') )
            cm.append( ('Go up', 'Action(ParentDir)'))
            liz.addContextMenuItems( cm )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok


def getURL(url):
    r = requests.get(url)
    data=r.json()
    return data
    r.close()

