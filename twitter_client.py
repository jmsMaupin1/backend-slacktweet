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
        self.api = self.create_api()
        self.tweets = []
        self.processed_tweets_count = 0
        self.start_time = None
        self.callback = None
        self.stream = tweepy.Stream(
            auth=self.api.auth,
            listener=self,
            daemon=True,
        )

    def __enter__(self):
        self.start_time = dt.now()
        self.start_stream()
        return self

    def __exit__(self, err_type, value, traceback):
        self.stream.disconnect()

    def create_api(self):
        """Logs into the twitter api"""
        try:
            auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
            auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
            logger.info("Logging into Twitter API")
            return tweepy.API(auth)
        except Exception as e:
            logger.error(f"Failed to login to twitter: {e}")

    def start_stream(self):
        """Starts monitering twitter stream for filtered tweets"""

        if not self.filters:
            return

        try:
            logger.info("Starting Twitter Stream")
            self.stream.filter(track=list(self.filters.keys()), is_async=True)
        except Exception as e:
            logger.error(f"Failed to start stream: {e}")

    def close_stream(self):
        """Disconnects from the twitter stream"""
        logger.info('Disoconnecting Stream')
        self.stream.disconnect()

    def restart_stream(self):
        """Restarts the twitter stream"""
        logger.info('Restarting the twitter stream')
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

    def add_callback(self, callback):
        self.callback = callback

    def on_status(self, status):
        """
        Takes events from twitter, filters out retweets then adds
        the text to our tweets list
        """
        if 'retweeted_status' in status.__dict__:
            return

        for keyword in self.filters:
            if keyword in status.text:
                self.processed_tweets_count += 1
                self.filters[keyword] += 1
                if self.callback:
                    self.callback(self, status.text)
                return

    def get_tweet_stats(self):
        up_time = (dt.now() - self.start_time).total_seconds() / 60
        tweets_per_minute = self.processed_tweets_count / up_time
        return {
            "tweets_per_minute": tweets_per_minute,
            "filter_count": self.filters,
            "total_tweets_processed": self.processed_tweets_count
        }

    def on_error(self, error):
        """Exit stream if we are rate limited, otherwise continue"""
        if error == 420:
            logger.error('Rate limited, try again later')
            return False

        logger.error(f"Unhandled Error: {error}")
