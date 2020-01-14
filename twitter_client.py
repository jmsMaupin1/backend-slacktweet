#!/usr/bin/env python3
"""
A standalone twitter client implementation
see https://tweepy.readthedocs.io/en/latest/
"""
import os
import time
import logging

from dotenv import load_dotenv
import tweepy
from datetime import datetime as dt
load_dotenv()

TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET = os.environ['TWITTER_API_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']

logger = logging.getLogger(__name__)


class TwitterClient(tweepy.StreamListener):
    """
    Creates a Twitter bot that looks for tweets with a given filter
    """
    def __init__(self, filters):
        self.filters = filters
        self.tweets = []
        self.api = self.create_api()
        self.stream = tweepy.Stream(
            auth=self.api.auth,
            listener=self,
            daemon=True
        )
        self.start_time = dt.now()

    def __enter__(self):
        self.start_stream()
        return self

    def __exit__(self, err_type, value, traceback):
        self.stream.disconnect()

    def create_api(self):
        """Logs into the twitter api"""
        try:
            auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
            auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
            logger.debug("Logging into Twitter API")
            return tweepy.API(auth)
        except Exception as e:
            logger.error(f"Failed to login to twitter: {e}")

    def start_stream(self):
        """Starts monitering twitter stream for filtered tweets"""
        try:
            logger.debug("Starting Twitter Stream")
            self.stream.filter(track=self.filters, is_async=True)
        except Exception as e:
            logger.error(f"Failed to start stream: {e}")

    def close_stream(self):
        """Disconnects from the twitter stream"""
        logger.debug('Disoconnecting Stream')
        self.stream.disconnect()

    def restart_stream(self):
        """Restarts the twitter stream"""
        logger.debug('Restarting the twitter stream')
        self.close_stream()
        self.start_stream()

    def update_filters(self, filters):
        """Updates filters for the twitter stream, then restarts the stream"""
        logger.debug('Updating twitter filter keywords')
        self.filters = filters
        self.restart_stream()

    def get_tweets(self):
        """Returns a list of tweets and emptys tweets list"""
        return_tweets = self.tweets
        self.tweets = []
        return return_tweets

    def on_status(self, status):
        """
        Takes events from twitter, filters out retweets then adds
        the text to our tweets list
        """
        if 'retweeted_status' in status.__dict__:
            return
        logger.info(status.text)
        self.tweets.append(status.text)

    def on_error(self, error):
        """Exit stream if we are rate limited, otherwise continue"""
        if error == 420:
            logger.error('Rate limited, try again later')
            return False

        logger.error(f"Unhandled Error: {error}")


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(process)d - %(asctime)s - %(levelname)s - %(message)s',
        datefmt='%y-%m-%d %H:%M:%S'
    )

    app_start_time = dt.now()

    logging.info(
        '\n'
        '--------------------------------------------------\n'
        '      Running: {}\n'
        '      started on: {}\n'
        '--------------------------------------------------\n'
        .format(__file__, app_start_time.isoformat())
    )

    with TwitterClient(['trump']) as tclient:
        time.sleep(5)
        tclient.update_filters(['iran'])
        time.sleep(5)
        print(tclient.get_tweets())
        print(tclient.tweets)
        tclient.close_stream()

    uptime = dt.now() - app_start_time
    logging.info(
        '\n'
        '--------------------------------------------------\n'
        '      Running: {}\n'
        '      stopped on: {}\n'
        '--------------------------------------------------\n'
        .format(__file__, str(uptime))
    )
    logging.shutdown()


if __name__ == '__main__':
    main()
