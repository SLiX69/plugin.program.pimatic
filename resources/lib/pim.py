import requests

'''
addonID = 'plugin.program.pimatic'
addon = xbmcaddon.Addon(id=addonID)
# pluginhandle = int(sys.argv[1])

host = addon.getSetting('ipaddress')
port = addon.getSetting('port')
username = addon.getSetting('username')
password = addon.getSetting('password')
'''


class pimatic:
    host = ''
    port = ''
    username = ''
    password = ''

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def get_device_history(self, deviceid):
        history = []
        data = self.get_requests('http://%s:%s@%s:%s/api/devices/%s' % (self.username, self.password, self.host, self.port, deviceid))
        for i in data['device']['attributes']:
            history.append(i['history'])
        return history

    def get_params(self, deviceid, action):
        params = []
        ret_param = []
        url = 'http://%s:%s@%s:%s/api/devices/%s' % (self.username, self.password, self.host, self.port, deviceid)
        data = self.get_requests(url)['device']
        for i in data['actions']:
            if i['name'] == action and 'params' in i:
                params.append(i['params'])
        for param in params:
            for k in param:
                attribute = [k][0]  #supports only one paramter?
                type = param[k]['type'] #needed? supports only one paramter?
                #xbmc.log(str(attribute) + str(type))
            for attrib in data['attributes']:
                if attrib['name'] == attribute or attrib['name'] == 'button':  # button action key is named wrong in pimatic
                    if attrib['type'] == 'number':
                        parameter = 'get_number'
                        pass
                    if attrib['type'] == 'string':
                        # check if buttonDevice
                        if data['template'] == 'buttons':
                            # get buttonIds as list for dialog
                            parameter = [d['id'] for d in data['config']['buttons'] if 'id' in d]
                        else:
                            # regular string param
                            parameter = attrib['enum']
                    if attrib['type'] == 'boolean':
                        parameter = ['true', 'false']
                    ret_param.append({'attribute': attribute, 'values': parameter})
        if ret_param == []:
            ret_param.append({'attribute': '', 'values': ''})
        return ret_param

    def execute_action(self, deviceid, action, param, value):
        url = 'http://%s:%s@%s:%s/api/device/%s/%s' % (self.username, self.password, self.host, self.port, deviceid, action)
        if param != '':
            url += '?%s=%s' % (param, value)
        self.get_requests(url)

    def get_device_values(self, deviceId):
        # url = template
        actions = False
        values = []
        data = self.get_requests('http://%s:%s@%s:%s/api/devices/%s/' % (self.username, self.password, self.host, self.port, deviceId))
        # check if device has actions
        if data['device']['actions'] != []:
            actions = True
        for i in data['device']['attributes']:
            name = i['name'].encode('utf-8')
            try:
                value = i['value']
                if isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or (value is None):
                    value = str(value)
                value = value.encode('utf-8')
            except KeyError:
                value = ''
            name += ' is ' + value
            if 'unit' in i:
                unit = i['unit'].encode('utf-8')
                name += ' ' + unit
            values.append(name)
        return values, actions

    def get_device_actions(self, deviceid):
        actions = []
        data = self.get_requests('http://%s:%s@%s:%s/api/devices/%s/' % (self.username, self.password, self.host, self.port, deviceid))
        for i in data['device']['actions']:
            actions.append(i['name'])
        return actions

    def get_device_from_devices(self, deviceid):
        values, actions = get_device_values(deviceid)
        return values

    def get_page(self, pageId):
        devices = []
        value = ''
        data = self.get_requests('http://%s:%s@%s:%s/api/pages/%s' % (self.username, self.password, self.host, self.port, pageId))['page']
        data_devices = self.get_all_devices()    # get all existing! devices
        for i in data['devices']:
            deviceId = i['deviceId'].encode('utf-8')
            if any(d.get('name', None) == deviceId for d in data_devices):  # check if device really exists
                values, actions = self.get_device_values(deviceId)
                for j in values:
                    value += ' ' + j
                name = deviceId + value
                value = ''  # clear value
                device = {'name': name, 'deviceId': deviceId}
                devices.append(device)
        return devices

    def get_all_pages(self):
        pages = []
        data = self.get_requests('http://%s:%s@%s:%s/api/pages' % (self.username, self.password, self.host, self.port))['pages']
        for i in data:
            name = (i['name']).encode('utf-8')
            pageId = i['id']
            #addDir(name, url, 'getPage', '', '', )
            page = {'name': name, 'url': pageId}
            pages.append(page)
        return pages

    def get_all_devices(self):
        devices = []
        data = self.get_requests('http://%s:%s@%s:%s/api/devices' % (self.username, self.password, self.host, self.port))['devices']
        for i in data:
            deviceId = (i['id']).encode('utf-8')
            #template = get_device_template(deviceId)
            device = {'name': deviceId}
            devices.append(device)
        return devices

    def get_all_vars(self):
        variables = []
        data = self.get_requests('http://%s:%s@%s:%s/api/variables' % (self.username, self.password, self.host, self.port))['variables']
        for i in data:
            name = i['name'].encode('utf-8')
            value = i['value']
            unit = i['unit']
            if isinstance(value, float) or isinstance(value, int) or isinstance(value, long) or (value is None):
                value = str(value)
            value = ' ' + value.encode('utf-8') + unit.encode('utf-8')
            name += value
            variable = {'name': name}
            variables.append(variable)
        return variables

    def get_all_groups(self):
        groups = []
        data = self.get_requests('http://%s:%s@%s:%s/api/groups' % (self.username, self.password, self.host, self.port))['groups']
        cnt = -1
        for i in data:
            cnt += 1
            name = (i['name']).encode('utf-8')
            id = i['id']
            url = str(cnt)
            group = {'name': name, 'url': url, 'id': id}
            groups.append(group)
        return groups

    def get_group(self, groupid):
        ret_grp = []
        data = self.get_requests('http://%s:%s@%s:%s/api/groups' % (self.username, self.password, self.host, self.port))
        for group in data['groups']:
            if group['id'] == groupid:
                ret_grp = group['devices']
        return ret_grp

    def get_all_rules(self):
        rules = []
        data = self.get_requests('http://%s:%s@%s:%s/api/rules' % (self.username, self.password, self.host, self.port))['rules']
        for i in data:
            name = (i['name']).encode('utf-8')
            deviceId = i['id']
            rule = {'name': name, 'deviceId': deviceId}
            rules.append(rule)
        return rules

    def get_rule(self, rule_id):
        data = self.get_requests('http://%s:%s@%s:%s/api/rules/%s' % (self.username, self.password, self.host, self.port, rule_id))['rule']
        id = data['id']
        name = data['name']
        cond_token = data['conditionToken']
        acti_token =  data['actionsToken']
        logging = data['logging']
        active = data['active']
        rule = {'id': id, 'name': name, 'cond': cond_token, 'acti': acti_token, 'active': active, 'logging': logging}
        return rule

    def get_requests(self, url):
        r = requests.get(url)
        data = r.json()
        return data
