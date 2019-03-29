import tweepy
import config

from tweepy.utils import import_simplejson
json = import_simplejson()

def has_config():
    return config.twitter_consumer_key != '' and config.twitter_screen_name != '' and \
        config.twitter_access_token != '' and config.twitter_consumer_secret != '' and \
        config.twitter_access_token_secret != ''

if has_config():
    auth = tweepy.OAuthHandler(config.twitter_consumer_key, config.twitter_consumer_secret)
    auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)

    api = tweepy.API(auth)

class RoboStreamListener(tweepy.StreamListener):
    def __init__(self, bot, channel):
        super().__init__()
        self.bot = bot
        self.channel = channel
        print('init twitter module, channel: ' + channel)
        self.bot.add_privmsg_listener(self.handle_privmsg)
        stream = tweepy.Stream(auth = api.auth, listener=self)

        stream.filter(track[config.twitter_screen_name])

    def handle_privmsg(self, sender, channel, message):
        if message.startswith('.tweet '):
            message_to_tweet = message[7:]
            status = api.update_status(message_to_tweet)
            self.on_status(status)

    def on_status(self, status):
        text = status.text
        text = text.replace('\n', '  ')
        user = status.user.name
        screen_name = status.user.screen_name
        tweet_id = status.id_str

        url = 'https://twitter.com/' + screen_name + '/statuses/' + tweet_id
        full_text = (user + ' (@' + screen_name + '): ' + text + ' - ' + url)
        self.bot.queue_message(self.channel, full_text)


