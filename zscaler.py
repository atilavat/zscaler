import time
import requests
import json
from itertools import islice


class client:
    version = '1.0'         # class variable shared by all instances
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


    def obfuscateApiKey(self):
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

    def login(self):
        self.obfuscateApiKey()

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
            r = requests.post('http://'+ self.base_url + "/authenticatedSession", data=json.dumps(payload), headers = headers)

        except Exception as e:
            print(e)

        self.JSESSIONID = r.cookies['JSESSIONID']


    def chunk(self, it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())


    def urllookup(self, urls): #expects url in array
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'cookie': "JSESSIONID=" + self.JSESSIONID
        }

        urls = list(self.chunk(urls, self.MAX_URLS_LOOKUP_PER_REQUEST))

        url_categories = []

        urls_array = [list(row) for row in urls]

        for array in urls_array:


            payload = array
            r = requests.post('https://' + self.base_url + "/urlLookup", data=json.dumps(payload), headers=headers)

            for item in r.json():
                url_categories.append(item)

        return(url_categories)