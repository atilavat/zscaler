import time
import requests
import json
import csv
from itertools import islice
import ipaddress

dc_list = None  # global variable to hold ips json


def _chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


class zclient:
    MAX_URLS_LOOKUP_PER_REQUEST = 100

    def __init__(self, cloud, api_key, admin_user, admin_password):

        self.cloud = cloud
        self.api_key = api_key
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.base_url = "admin." + cloud + '/api/v1'
        self.obf_api_key = ''
        self.timestamp = ''
        self.JSESSIONID = ''
        
        self.login()

        self.headers = { #used across functions except during login
            'content-type': "application/json",
            'cache-control': "no-cache",
            'cookie': "JSESSIONID=" + self.JSESSIONID
        }

    def obfuscate_api_key(self):
        seed = self.api_key
        now = int(time.time() * 1000)
        n = str(now)[-6:]
        r = str(int(n) >> 1).zfill(6)
        key = ""
        for i in range(0, len(str(n)), 1):
            key += seed[int(str(n)[i])]
        for j in range(0, len(str(r)), 1):
            key += seed[int(str(r)[j]) + 2]

        self.obf_api_key = key
        self.timestamp = now

        # print("Timestamp:", now, "\tKey", key)

    def login(self):
        self.obfuscate_api_key()

        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        payload = {
            'apiKey': self.obf_api_key,
            'username': self.admin_user,
            'password': self.admin_password,
            'timestamp': self.timestamp
        }

        try:
            r = requests.post('http://' + self.base_url + "/authenticatedSession", data=json.dumps(payload),
                              headers=headers)

        except Exception as e:
            print(e)

        self.JSESSIONID = r.cookies['JSESSIONID']

    def url_lookup(self, urls):  # expects url in array
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'cookie': "JSESSIONID=" + self.JSESSIONID
        }

        urls = list(_chunk(urls, self.MAX_URLS_LOOKUP_PER_REQUEST))

        url_categories = []

        urls_array = [list(row) for row in urls]

        for array in urls_array:

            payload = array

            try:
                r = requests.post('https://' + self.base_url + "/urlLookup", data=json.dumps(payload), headers=headers)

            except Exception as e:
                print(e.args)
                exit(e.args[0])

            for item in r.json():

                url_categories.append(item)

        return (url_categories)

    def read_url_csv(self, csvfile):  # expect CSV file as input
        urls_list = []
        try:
            with open(csvfile) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0

                for row in csv_reader:
                    if line_count == 0:
                        pass  # ignore headers
                    else:
                        urls_list.append(row[0])
                    line_count += 1
        except Exception as e:
            print(e.args)
            exit(e.args[0])

        return (urls_list)


    def get_url_quota(self):

        r = requests.get('https://' + self.base_url + "/urlCategories/urlQuota", headers=self.headers)

        return r.json()

    def activate(self):

        r = requests.post('https://' + self.base_url + "/status/activate", headers=self.headers)

        return r.json()


def proxy_check():

    try:
        r = requests.get('http://ip.zscaler.com')

        if r.text.find("You are accessing this host via a Zscaler proxy") > 0:
            return True
        else:
            return False

    except Exception as e:
        return (e.message, e.args)

def access_check(url): #returns true if allowed else false
        try:
            r = requests.get(url)

            if r.status_code == 200: return True

            else:
                return False

        except Exception as e:
            print (e)
            return False


def _get_ips_json(cloud):
    # get list of DCs
    global dc_list
    dc_list = dict()
    r = requests.get("https://ips." + cloud + "/cenr/jsonip")

    for region in r.json()['Geo_regions']:
        for location in r.json()['Geo_regions'][region]:
            for item in r.json()['Geo_regions'][region][location]:
                a = dict(item)
                if 'NRU' not in a['notes'] and 'DNP' not in a['notes']:  # ignores DC which are not ready
                    dc_list.update({location: a})


def get_dc(cloud, egress_site):  # return 2 closest dc info as dictionary type
    if dc_list is None:
        _get_ips_json(cloud)

    r = requests.get("https://nominatim.openstreetmap.org/search?q=" + egress_site + "&format=json")

    vpn_endpoints = requests.get(
        "https://pac." + cloud + "/getVpnEndpoints?long=" + r.json()[0]['lon'] + "&lat=" + r.json()[0]['lat'])

    resolved_egress_site = r.json()[0]['display_name']

    vpn_primary_vip = vpn_endpoints.json()['primaryIp']
    vpn_secondary_vip = vpn_endpoints.json()['secondaryIp']

    results_dc = dict()

    results_dc.update({"resolved_location": resolved_egress_site})

    # now lookup jsonip from ips page to get rest of DC info

    for dc in dc_list:  # dc_list is global dict for ips json page

        dc_cidr = ipaddress.IPv4Network(dc_list[dc]['cidr'])

        # print(dc)
        if ipaddress.IPv4Address(vpn_primary_vip) in dc_cidr:
            # hit for primary DC

            # gre_endpoints.append(dc_list[dc]['gre_vip'])
            # print(dc, dc_list[dc])
            results_dc.update({"primary_dc": dc_list[dc]})

        if ipaddress.IPv4Address(vpn_secondary_vip) in dc_cidr:
            # hit for secondary DC
            # print(dc, dc_list[dc])
            results_dc.update({"secondary_dc": dc_list[dc]})

            # gre_endpoints.append(dc_list[dc]['gre_vip'])

    return results_dc
