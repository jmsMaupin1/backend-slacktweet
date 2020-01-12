#!/usr/bin/env python3
"""
A standalone twitter client implementation
see https://tweepy.readthedocs.io/en/latest/
"""
import os
import time

from dotenv import load_dotenv
import tweepy
from datetime import datetime as dt
load_dotenv()

TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET = os.environ['TWITTER_API_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']


class TwitterClient(tweepy.StreamListener):
    """
    Creates a Twitter bot that looks for tweets with a given filter
    """
    def __init__(self, filters):
        self.filters = filters
        self.tweets = []
        self.api = self.create_api()
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self)
        self.start_time = dt.now()

    def create_api(self):
        """Logs into the twitter api"""
        try:
            auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
            auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
            return tweepy.API(auth)
        except Exception as e:
            print(f"Failed to login to twitter: {e}")

    def start_stream(self):
        """Starts monitering twitter stream for filtered tweets"""
        try:
            self.stream.filter(track=self.filters, is_async=True)
        except Exception as e:
            print(f"Failed to start stream: {e}")

    def close_stream(self):
        """Disconnects from the twitter stream"""
        self.stream.disconnect()
        pass

    def restart_stream(self):
        """Restarts the twitter stream"""
        pass

    def update_filters(self):
        """Updates filters for the twitter stream, then restarts the stream"""
        pass

    def on_status(self, status):
        """
        Takes events from twitter, filters out retweets then adds
        the text to our tweets list
        """
        if 'retweeted_status' in status.__dict__:
            return
        print(status.text)


def main():
    client = TwitterClient(['python', 'trump', 'republicans'])
    client.start_stream()
    time.sleep(5)
    client.close_stream()


if __name__ == '__main__':
    main()
