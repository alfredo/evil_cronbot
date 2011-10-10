import os

from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from random import choice

from twitter_oauth_handler import OAuthHandler, OAuthClient

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
here = lambda *x: os.path.join(PROJECT_ROOT, *x)

REPLY_TEMPLATES = [
    "Croooooooon!",
    "Cool story bro",
    "O Rly? Muahaha",
    "Problem? Muahahah",
    "Not a chance.. Muahah",
    "Stop those shenanigans",
    "Bite my shinny metal arse!",
    "And not a single Cron was given",
    "Bow before me, your twin evil clone",
    "Pixel counting, that is what you need",
    "Imma let you finish, but... I am the best Cron",
    "You always end up nerdjacking any conversation",
    "That's something a youtube commenter would say!",
    "You need some evil ghost pixels, that's what you need",
    "If in doubt ask your self What Would Evil Cron Do? WWECD",
    "I think you are a bit of a ponce, what's with the monocle?",
]

QUESTION_TEMPLATES = [
    "Let me google that for you, muahah",
    "Confused? Maybe I can help, NOT!",
]

STANDALONE_TEMPLATES = [
    "Crooooooooon!",
    "I am alive! Muahah...",
    "Bite my shinny metal arse.",
]

class Tweet(db.Model):
    """Stores tweets created and responses"""
    tweet_id = db.StringProperty()
    tweet = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

def get_random_text(text_list, threshold):
    """From a given threshold and a list of text returns a
    valid option"""
    return choice([i for i in text_list if len(i) < threshold])

def generate_tweet(text, username):
    """Generates a new witty tweet from the original text"""
    # we use 130 because we need to add a response
    new_username = '@%s' %  username
    threshold = 140 - len(new_username)
    if '?' in text:
        new_text = get_random_text(QUESTION_TEMPLATES, threshold)
    else:
        new_text = get_random_text(REPLY_TEMPLATES, threshold)
    new_text = '%s %s' % (new_username, new_text)
    return new_text

def do_tweet(request, text, extra_data=None):
    """Performs the tweet"""
    client = OAuthClient('twitter', request)
    data = {'status': text}
    if extra_data:
        data.update(extra_data)
    status = client.post('/statuses/update', **data)
    return status

class MainPage(webapp.RequestHandler):
    def get(self):
        """Shows a welcome page"""
        extra_context = {}
        template_path = here('templates', 'base.html')
        self.response.out.write(template.render(template_path, extra_context))

class EvilCronbotTweet(webapp.RequestHandler):
    def get(self):
        """Uses twitter api to search and respond for certain tweets
        Sample response:
        {u'favorited': False,
        u'in_reply_to_user_id': None,
        u'contributors': None,
        u'truncated': False,
        u'text': u'Achoo - CRON ! Excuse me.',
        u'created_at': u'Thu Jun 02 13:33:47 +0000 2011',
        u'retweeted': False,
        u'in_reply_to_status_id': None,
        u'coordinates': None,
        u'id': 76280352674549760,
        u'source': u'',
        u'in_reply_to_status_id_str': None, 
        u'in_reply_to_screen_name': None, 
        u'place': None, 
        u'retweet_count': 0, 
        u'geo': None, 
        u'in_reply_to_user_id_str': None, 
        u'id_str': u'76280352674549760'}
        """
        client = OAuthClient('twitter', self)
        # get the latest tweets from cronbot
        username = 'cronbot_001'
        # TODO: get last tweet
        extra_data = {'screen_name': username,
                      #'since_id': '76280352674549760'
        }
        tweet_list = client.get('/statuses/user_timeline', **extra_data)
        final_tweets = []
        try:
            tweet = tweet_list[0]
            final_tweets.append(tweet)
        except IndexError:
            tweet = None
        # mention data
        mention_data = {'count': 1}
        mention_list = client.get('/statuses/mentions', **mention_data)
        try:
            mention = mention_list[0]
            final_tweets.append(mention)
        except IndexError:
            mention = None
        for tweet in final_tweets:
            text = generate_tweet(tweet.get('text'), tweet['user']['screen_name'])
            tweet_id = tweet.get('id_str')
            # We havent answered to this one
            if not Tweet.get_by_key_name(tweet_id):
                # Store at the first try
                data = {'tweet_id': tweet_id,
                        'tweet': text,}
                stored_tweet = Tweet(key_name=tweet_id, **data)
                stored_tweet.put()
                do_tweet(self, text)
        self.response.out.write('ok')

application = webapp.WSGIApplication([
    ('/', MainPage),
    ('/evilcronbot/search-and-tweet/', EvilCronbotTweet),
    ('/oauth/(.*)/(.*)', OAuthHandler),
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
