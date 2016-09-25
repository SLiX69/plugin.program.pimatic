#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import sys
import requests
import os
import datetime
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
from urllib import unquote_plus, unquote, quote_plus
from resources.lib.pim import pimatic

addonID = 'plugin.program.pimatic'
addon = xbmcaddon.Addon(id=addonID)
home = addon.getAddonInfo('path').decode('utf-8')
icon = xbmc.translatePath(os.path.join(home, 'icon.png'))
fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
# addDeviceToPage = xbmc.translatePath(os.path.join(home, 'addDeviceToPage2.py'))
pluginhandle = int(sys.argv[1])


host = addon.getSetting('ipaddress')
port = addon.getSetting('port')
username = addon.getSetting('username')
password = addon.getSetting('password')

pim = pimatic(host, port, username, password)

def main():
    addDir(get_translation(30010), '', 'getAllPages', '', '')
    addDir(get_translation(30011), '', 'getAllDevices', '', '')
    addDir(get_translation(30012), '', 'getAllVars', '', '')
    addDir(get_translation(30013), '', 'getAllGroups', '', '')
    addDir(get_translation(30014), '', 'getAllRules', '', '')
    xbmcplugin.endOfDirectory(pluginhandle)

def get_page(pageId):
    devices = pim.get_page(pageId)
    #xbmc.log(str(devices))
    for device in devices:
        name = device['name']
        #url = device['url']    #old template
        #mode = device['mode']
        deviceId = device['deviceId']
        addDir(name, '', 'getDevice', '', deviceId)
    xbmcplugin.endOfDirectory(pluginhandle)


"""INDEX"""
def get_all_pages():
    pages = pim.get_all_pages()
    for page in pages:
        name = page['name']
        url = page['url']
        #mode = page['mode']
        addDir(name, url, 'getPage', '', '', )
    #addDir(get_translation(30031), '', 'addPage', '', '')
    #addDir(get_translation(30032), '', 'remPage', '', '')
    xbmcplugin.endOfDirectory(pluginhandle)


def get_all_devices():
    devices = pim.get_all_devices()
    for device in devices:
        deviceId = device['name']
        #url = device['url']    #old template
        # FIX CM
        '''
        u = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path') + '/addDeviceToPage2.py,' + deviceId + ',').decode(
            'utf-8')
        cm = []
        cm.append((get_translation(30033), "XBMC.RunScript(%s add,pages)" % u))
        cm.append((get_translation(30034), "XBMC.RunScript(%s rem,pages)" % u))
        '''
        addDir(deviceId, '', 'getDevice', '', deviceId)
    xbmcplugin.endOfDirectory(pluginhandle)


def get_rule(rule_id):
    data = pim.get_rule(rule_id)
    id = data['id']
    name = data['name']
    cond = 'IF: %s' % data['cond']
    acti = 'THEN: %s' % data['acti']
    logg = 'logging: %s' % data['logging']
    active = 'active: %s' % data['active']
    addDir(name, '', 'end', '', '')
    addDir(cond, '', 'end', '', '')
    addDir(acti, '', 'exeRule', '', id)
    addDir(active, 'active', 'set_rule', '', id)
    addDir(logg, 'logging', 'set_rule', '', id)
    xbmcplugin.endOfDirectory(pluginhandle)


def execute_rule(rule_id):
    data = pim.get_rule(rule_id)
    actionToken = data['acti']
    line = "Do you really want to execute the rule?"
    retval_rule = xbmcgui.Dialog().yesno("Pimatic Addon", line)
    if retval_rule == 1:
        url = ('http://%s:%s@%s:%s/api/execute-action' % (username, password, host, port))
        payload = {'actionString': actionToken}
        r = requests.post(url, json=payload)
        status = (str(r.status_code))
        out = str(r.json())
        xbmc.log(status + ' - ' + out + ' - actionsToken: ' + actionToken)


def set_rule(rule_id, name):
    data = pim.get_rule(rule_id)
    state = data[name]
    if not state:
        change_to = True
    else:
        change_to = False
    line = "%s is %s. Set it to %s?" % (name, state, str(change_to))
    retval_rule = xbmcgui.Dialog().yesno("Pimatic Addon", line)
    if retval_rule == 1:
        url = ('http://%s:%s@%s:%s/api/rules/%s' % (username, password, host, port, rule_id))
        payload = {'ruleId': rule_id, 'rule':{name: change_to}}
        r = requests.patch(url, json=payload)
        #status = (str(r.status_code))
        #out = str(r.json())


def get_all_rules():
    rules = pim.get_all_rules()
    for rule in rules:
        name = rule['name']
        deviceid = rule['deviceId']
        addDir(name, '', 'getRule', '', deviceid)
    xbmcplugin.endOfDirectory(pluginhandle)


def get_all_vars():
    variables = pim.get_all_vars()
    for variable in variables:
        name = variable['name']
        addDir(name, '', 'end', '', '', )
    xbmcplugin.endOfDirectory(pluginhandle)


def get_all_groups():
    groups = pim.get_all_groups()
    for group in groups:
        name = group['name']
        url = group['url']
        groupid = group['id']
        addDir(name, url, 'getGroup', '', groupid)
    #addDir(get_translation(30041), '', 'addGroup', '', '')
    #addDir(get_translation(30042), '', 'remGroup', '', '')
    xbmcplugin.endOfDirectory(pluginhandle)


def get_group(groupid):
    devices = pim.get_group(groupid)
    for device in devices:
        name = device
        addDir(name, '', 'getDevice', '', name)
    xbmcplugin.endOfDirectory(pluginhandle)


"""GET DEIVCE STUFF"""


def get_device(deviceid):
    cnt = 0
    values, actions = pim.get_device_values(deviceid)
    if actions:
        addDir('Actions', '', 'getDeviceActions', '', deviceid)
    for value in values:
        addDir(value, str(cnt), 'getDevHistory', '', deviceid)
        cnt += 1
    xbmcplugin.endOfDirectory(pluginhandle)


def get_attribute_history(deviceid, url):
    data = pim.get_device_history(deviceid)
    for i in reversed(data[int(url)]):
        time = i['t']
        state = str(i['v'])
        time = time / 1000
        time2 = datetime.datetime.fromtimestamp(time)
        time = (time2.strftime('%Y-%m-%d %H:%M:%S'))
        name = (time).encode('utf-8') + ' was ' + (state).encode('utf-8')
        addDir(name, '', '', '', '')
    xbmcplugin.endOfDirectory(pluginhandle)


def get_device_actions(deviceid):
    actions_select(deviceid)


def actions_select(deviceid):
    value = ''
    attribute = ''
    actions = pim.get_device_actions(deviceid)
    dialog = xbmcgui.Dialog()
    call = dialog.select("Choose an action", actions)
    if call != -1:
        action = actions[call]
        param = pim.get_params(deviceid, action)    # get params
        values = param[0]['values']     # get values of param
        xbmc.log('values')
        xbmc.log(str(values))
        if values == '':
            # action without params
            d = 0
        elif values == 'get_number':
            # choose number
            d = dialog.input(heading='Choose Value', type=xbmcgui.INPUT_NUMERIC)
            xbmc.log(str(d))
        else:
            # choose string
            d = dialog.select(heading='Choose Value', list=values)
            if d != -1:
                value = values[d]
                attribute = param[0]['attribute']
        if d != -1:
            pim.execute_action(deviceid, action, attribute, value)


"""KODI STUFF"""

def get_translation(string_id):
    return addon.getLocalizedString(string_id)


def addDir(name, url, mode, iconimage, deviceId):
    u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode) + "&name=" + quote_plus(name) + "&deviceId=" + str(deviceId)
    ok = True
    item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    item.setInfo(type="Video", infoLabels={"Title": name})
    #item.setProperty('fanart_image', fanart)
    xbmcplugin.addDirectoryItem(handle=pluginhandle, url=u, listitem=item, isFolder=True)


def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params = parameters_string_to_dict(sys.argv[2])
mode = params.get('mode')
url = params.get('url')
name = params.get('name')
deviceId = params.get('deviceId')
if type(url) == type(str()):
    url = unquote_plus(url)

if mode == None:
    main()
#######################
elif mode == 'getAllPages':
    get_all_pages()
elif mode == 'getAllVars':
    get_all_vars()
elif mode == 'getAllGroups':
    get_all_groups()
elif mode == 'getAllDevices':
    get_all_devices()
elif mode == 'getAllRules':
    get_all_rules()
#######################
elif mode == 'getPage':
    get_page(url)
elif mode == 'getDevice':
    get_device(deviceId)
elif mode == 'getRule':
    get_rule(deviceId)
elif mode == 'getGroup':
    get_group(deviceId)
#######################
elif mode == 'getDeviceActions':
    get_device_actions(deviceId)
elif mode == 'exeActi':
    executeAction(name, url, deviceid)
elif mode == 'getDevHistory':
    get_attribute_history(deviceId, url)
elif mode == 'exeRule':
    execute_rule(deviceId)
elif mode == 'set_rule':
    set_rule(deviceId, url)
#elif mode == 'addDevice':
#    addDevice(url)
#elif mode == 'addPage':
#    addItem('page')
#elif mode == 'remPage':
#    remItem('page')
#elif mode == 'addGroup':
#    addItem('group')
#elif mode == 'remGroup':
#    remItem('group')

