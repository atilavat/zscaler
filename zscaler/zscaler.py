import time
import requests
import json
import csv
from itertools import islice
from urllib.parse import urlparse


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

    def chunk(self, it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    def url_format_check(self, url):

        result = urlparse(url)
        return all([result.scheme, result.netloc])


    def url_lookup(self, urls):  # expects url in array
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


