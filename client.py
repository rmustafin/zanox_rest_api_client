from hashlib import sha1
import hmac
import random
import string
from time import gmtime, strftime
import datetime
import binascii
import urllib.request
import json
import pdb


class ZanoxClient(object):

    api_url = 'http://api.zanox.com'
    api_version = '2011-03-01'


    def __init__(self, connect_id = None, secret_key = None, api_format = 'json'):
        self.connect_id = connect_id
        self.secret_key = secret_key
        self.api_format = api_format


    def signature(self, http_verb, uri, timestamp, nonce):
        string_to_sign = http_verb + uri + timestamp + nonce
        encoded_string_to_sign = str.encode(string_to_sign, 'utf-8')
        encoded_secret_key = str.encode(self.secret_key, 'utf-8')
        hashed = hmac.new(encoded_secret_key, encoded_string_to_sign, sha1)
        signature = binascii.b2a_base64(hashed.digest())[:-1].decode('utf-8')
        return signature


    def _nonce(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(20))


    def _timestamp(self):
        return strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime())


    def call_api(self, http_method, url_template, **args):
        url =  url_template.format(**args)
        timestamp = self._timestamp()
        nonce = self._nonce()
        signature = self.signature(http_method, url, timestamp, nonce)

        url = self.api_url + '/' + self.api_format + '/' + self.api_version + url
        headers = {
            'Authorization': 'ZXWS ' + self.connect_id + ':' + signature,
            'Date': timestamp,
            'nonce': nonce
        }
        u = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
        response = json.loads(u.read().decode('utf-8'))
        return response


    def get_sales_report(self, date):
        return self.call_api('GET', '/reports/sales/date/{date}', date=date)

