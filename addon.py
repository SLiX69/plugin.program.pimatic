#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import sys
import requests
import os
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon


from resources.lib.getDevices import getTempDevice, getPresence, getButtonDevice, getSysSenDevice, getDimmerDevice, getSwitchDevice
from resources.lib.getIndex import getAllDevices,getAllVars,getAllRules,getAllGroups,getGroup,getPage,getPages,getRule
from resources.lib.getDeviceStuff import getActionsList,getDeviceHistory


addonID = 'plugin.video.pimatic'
addon = xbmcaddon.Addon(id=addonID)
home = addon.getAddonInfo('path').decode('utf-8')
icon = xbmc.translatePath(os.path.join(home, 'icon.png'))
fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
#addDeviceToPage = xbmc.translatePath(os.path.join(home, 'addDeviceToPage2.py'))
pluginhandle = int(sys.argv[1])

translation = addon.getLocalizedString


host = addon.getSetting('ipaddress')
port = addon.getSetting('port')
username = addon.getSetting('username')
password = addon.getSetting('password')



def main():
    xbmc.log(home)
    addDir('Pages','pages',1,'','')
    addDir('Devices','',5,'','')
    addDir('Variables','',9,'','')
    addDir('Groups','',10,'','')
    addDir('Rules','',7,'','')
    xbmcplugin.endOfDirectory(pluginhandle)


def executeRule(url):
    xbmc.log('EXECUTE-RULE')
    actionsToken = url
    line1 = "Do you really want to execute the rule?"
    retval_rule = xbmcgui.Dialog().yesno("Pimatic Addon", line1)
    if retval_rule == 1:
        url = ('http://%s:%s@%s:%s/api/execute-action' % (username, password, host, port))
        payload = {'actionString': actionsToken}
        r = requests.post(url, json=payload)
        status = (str(r.status_code))
        out = str(r.json())
        xbmc.log(status + ' - ' + out + ' - actionsToken: ' + actionsToken)


def getDevice(name,url,deviceid):
    template = url
    if template == 'switch':
        addDir('Actions','0',12,'',deviceid)
        addDir('History','0',6,'',deviceid)
    elif template == 'temperature':
        getTempDevice(deviceid)
    elif template == 'presence':
        getPresence(deviceid)
    elif template == 'buttons':
        getButtonDevice(deviceid)
    elif template == 'device':
        getSysSenDevice('',deviceid)
    elif template == 'dimmer':
        getDimmerDevice(deviceid)
        addDir('Actions','0',12,'',deviceid)
    elif template == 'shutter':
        addDir('Actions','0',12,'',deviceid)
        addDir('History','0',6,'',deviceid)
    elif template == 'contact':
        addDir('Actions','0',12,'',deviceid)
        addDir('History','0',6,'',deviceid)
    elif template == 'thermostat':
        addDir('Actions','0',12,'',deviceid)
        addDir('History','0',6,'',deviceid)
    elif template == 'KeyError':
        addDir('KeyError','',99,'',deviceid)

    xbmcplugin.endOfDirectory(pluginhandle,succeeded=True,updateListing=False,cacheToDisc=True)

def getActionsAsPopup(deviceid):
    actions=getActionsList(deviceid)
    dialog=xbmcgui.Dialog()
    call=dialog.select("Choose an action",actions)
    print actions[call]
    url = actions[call]
    executeAction('', url, deviceid)

def executeAction(name,url,deviceid):
    if url == 'getState':
        switchlog = requests.get('http://%s:%s@%s:%s/api/device/%s/%s' % (username, password, host, port, deviceid, url))
        state = str(switchlog.json()['result'])
        xbmc.executebuiltin("Notification(pimatic addon,state of %s is %s,4000,%s)" % (deviceid, state, icon))
        url = ''
        xbmc.log(state)
    if url == 'changeStateTo':
        print
        states = ['true', 'false']
        dialog=xbmcgui.Dialog()
        call=dialog.select("Choose an action",states)
        url = 'changeStateTo?state=' + states[call]
        switchlog = requests.get('http://%s:%s@%s:%s/api/device/%s/%s' % (username, password, host, port, deviceid, url))
    if url == 'changeDimlevelTo':
        level = ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
        dialog=xbmcgui.Dialog()
        call=dialog.select("Choose an action",level)
        url = 'changeDimlevelTo?dimlevel=' + level[call]
        switchlog = requests.get('http://%s:%s@%s:%s/api/device/%s/%s' % (username, password, host, port, deviceid, url))
    if url == 'changeContactTo':
        contact = ['true', 'false']
        dialog=xbmcgui.Dialog()
        call=dialog.select("Choose an action",contact)
        url = 'changeContactTo?contact=' + contact[call]
        switchlog = requests.get('http://%s:%s@%s:%s/api/device/%s/%s' % (username, password, host, port, deviceid, url))
    if url == 'moveToPosition':
        position = ['up', 'down']
        dialog=xbmcgui.Dialog()
        call=dialog.select("Choose an action",position)
        url = 'moveToPosition?state=' + position[call]
        switchlog = requests.get('http://%s:%s@%s:%s/api/device/%s/%s' % (username, password, host, port, deviceid, url))
    if url == 'changeModeTo':
        mode = ['auto', 'manu', 'boost']
        dialog=xbmcgui.Dialog()
        call=dialog.select("Choose an action",mode)
        url = 'changeModeTo?mode=' + mode[call]
        switchlog = requests.get('http://%s:%s@%s:%s/api/device/%s/%s' % (username, password, host, port, deviceid, url))
    if url == 'changeTemperatureTo':
        temp = ['15', '16', '17', '18', '18.5', '19', '19.5', '20', '20.5', '21', '21.5', '22', '22.5', '23', '23.5',
                '24', '24.5', '25', '26', '27', '28']
        dialog=xbmcgui.Dialog()
        call=dialog.select("Choose an action",temp)
        url = 'changeTemperatureTo?temperatureSetpoint=' + temp[call]
        switchlog = requests.get('http://%s:%s@%s:%s/api/device/%s/%s' % (username, password, host, port, deviceid, url))

    else:
        switchlog = requests.get('http://%s:%s@%s:%s/api/device/%s/%s' % (username, password, host, port, deviceid, url))

def getURL(url):
    r=requests.get(url)
    data=r.json()
    return data
    r.close()

def addDevice(url):
    xbmc.log(url)
    if url:
        u = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/addDeviceToPage2.py,'+ url +',').decode('utf-8')
        xbmc.executebuiltin('XBMC.RunScript(%s add,devices)' % u)
    else:
        u = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/addDeviceToPage2.py,,').decode('utf-8')
        xbmc.executebuiltin('XBMC.RunScript(%s add,both)' % u)

def setRule(url, iconimage, deviceid):
    ruleid = iconimage
    if url == 'True':
        line1 = "%s is %s. Set it to 'False'?" % (deviceid, url)
        choice = False
    else:
        line1 = "%s is %s. Set it to 'True'?" % (deviceid, url)
        choice = True
    retval_rule = xbmcgui.Dialog().yesno("Pimatic Addon", line1)
    if retval_rule == 1:
        url = ('http://%s:%s@%s:%s/api/rules/%s' % (username, password, host, port, ruleid))
        payload = {'ruleId': ruleid, 'rule':{deviceid: choice}}
        r = requests.patch(url, json=payload)
        #status = (str(r.status_code))
        #out = str(r.json())


def addItem(item):
    keyboard = xbmc.Keyboard('', 'add '+item+'')
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        uinput = keyboard.getText()
        try:
            url = 'http://%s:%s@%s:%s/api/%ss/%s' % (username, password, host, port, item, uinput)
            payload = {item+'Id': uinput, item:{'name': uinput}}
            r = requests.post(url, json=payload)
            status = (str(r.status_code))
            out = str(r.json())
            xbmc.log(status + ' - ' + out + ' - User-Input: ' + uinput)
        except KeyError:
            xbmc.log('Pimatic Addon: Add '+item+' - KeyError while Input add'+item+'')


def remItem(item):
    item = item + 's'
    xbmc.log(item)
    id = getPopup(item)
    line1 = "Do you really want to remove the "+item+" '"+id+"'?"
    retval_rule = xbmcgui.Dialog().yesno("Pimatic Addon", line1)
    if retval_rule == 1:
        url = ('http://%s:%s@%s:%s/api/%s/%s' % (username, password, host, port, item, id))
        payload = {''+item+'Id': id}
        r = requests.delete(url, json=payload)
        status = (str(r.status_code))
        out = str(r.json())
        xbmc.log('Pimatic Addon: Rem '+item+' ' +status+ ' - ' +out+ ' - User-Input: ' +id)


def kodilog(string):
    xbmc.log('Pimatic Addon - ' + string)


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
    call=dialog.select("Pimatic Addon",list)
    print list[call]
    url = list[call]
    return url


def addDir(name,url,mode,iconimage,deviceid):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&deviceid="+urllib.quote_plus(deviceid)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name} )
        liz.addContextMenuItems([ ('Refresh', 'Container.Refresh'),
                                ('Go up', 'Action(ParentDir)') ])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
        return param        
params=get_params()

name=None
url=None
mode=None
iconimage=None
deviceid=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        desc=urllib.unquote_plus(params["desc"])
except:
        pass
try:
        fanart=urllib.unquote_plus(params["fanart"])
except:
        pass
try:
        deviceid=urllib.unquote_plus(params["deviceid"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

if mode == None:
     main()
elif mode == 'test':
    getTest()
elif mode == 1:
    getPages()
elif mode == 2:
    getPage(url)
elif mode == 3:
    getDevice(name,url,deviceid)
elif mode == 4:
    executeAction(name,url,deviceid)
elif mode == 5:
    getAllDevices()
elif mode == 6:
    getDeviceHistory(deviceid, url)
elif mode == 7:
    getAllRules()
elif mode == 8:
    getRule(deviceid)
elif mode == 9:
    getAllVars()
elif mode == 10:
    getAllGroups()
elif mode == 11:
    getGroup(url)
elif mode == 12:
    getActionsAsPopup(deviceid)
elif mode == 13:
    executeRule(url)
elif mode == 14:
    addDevice(url)
elif mode == 15:
    setRule(url, iconimage, deviceid)
elif mode == 29:
    addItem('page')
elif mode == 31:
    remItem('page')
elif mode == 33:
    addItem('group')
elif mode == 35:
    remItem('group')



