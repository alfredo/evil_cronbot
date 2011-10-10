Simple twitter bot
--------------

Requires a ``config.py`` file with the following details::

OAUTH_APP_SETTINGS = {
    'twitter': {
        'consumer_key': '',
        'consumer_secret': '',
        'request_token_url': 'https://api.twitter.com/oauth/request_token',
        'access_token_url': 'https://api.twitter.com/oauth/access_token',
        'user_auth_url': 'https://api.twitter.com/oauth/authorize',
        'default_api_prefix': 'http://twitter.com',
        'default_api_suffix': '.json',
    },
}
