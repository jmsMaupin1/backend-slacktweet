#!/usr/bin/env python3
"""
A standalone twitter client implementation
see https://tweepy.readthedocs.io/en/latest/
"""
import os
from dotenv import load_dotenv
import tweepy
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

    def create_api(self):
        """Logs into the twitter api"""
        pass

    def start_stream(self):
        """Starts monitering twitter stream for filtered tweets"""
        pass

    def close_stream(self):
        """Disconnects from the twitter stream"""
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
        self.tweets.append(status.text)


def main():
    pass


if __name__ == '__main__':
    main()
