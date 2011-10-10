import random
from time import time
from hashlib import sha1
from hmac import new as hmac
from urllib import urlencode

from google.appengine.api.urlfetch import fetch as urlfetch
from twitter_oauth_handler import OAUTH_APP_SETTINGS, encode, get_service_key

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'


class Twitter(object):
    """Simple thin wrapper to access Twitter from
    the mighty app engine
    """
    base_url = 'http://api.twitter.com'
    service = OAUTH_APP_SETTINGS['twitter']

    def __init__(self, token):
        self.token = token

    def get_signed_body(self, url, method, **extra_data):
        service_info = OAUTH_APP_SETTINGS['twitter']
        kwargs = {
            'oauth_consumer_key': service_info['consumer_key'],
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_version': '1.0',
            'oauth_timestamp': int(time()),
            'oauth_nonce': random.getrandbits(64),
            'oauth_token': self.token
            }
        kwargs.update(extra_data)
        message = '&'.join(map(encode,
                               [method.upper(), url,
                                '&'.join('%s=%s' % (
                                    encode(k),
                                    encode(kwargs[k])) for k in sorted(kwargs))]))
        key = get_service_key('twitter')
        kwargs['oauth_signature'] = hmac(
            key, message, sha1).digest().encode('base64')[:-1]
        return urlencode(kwargs)

    def get_signed_url(self, url, method, **extra_data):
        return '%s?%s' % (url, self.get_signed_body(url, method,
                                                    **extra_data))

    def do_request(self, path, **extra_data):
        """Generates the request"""
        url = '%s/%s' % (self.base_url, path)
        signed_url = self.get_signed_url(url, 'POST', **extra_data)
        fetch = urlfetch(url=url, payload=signed_url, method='POST')
        assert False, fetch.content

    def tweet(self, text):
        data = {'status': text}
        self.do_request('statuses/update.json', **data)