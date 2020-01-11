#!/usr/bin/env python3
"""A standalone Slack client implementation
see https://slack.dev/python-slackclient/
"""
import os
import re
import logging
import asyncio
from datetime import datetime as dt

from dotenv import load_dotenv
from slack import RTMClient, WebClient

load_dotenv()
logger = logging.getLogger(__name__)
sc = None


class SlackBotClient:
    """
    Creates a slackbot object capable of logging into slack
    and monitoring messages
    """

    def __init__(self, token):
        self.rtm_client = RTMClient(token=token, run_async=True)
        self.id = WebClient(token).api_call('auth.test')['user_id']
        self.start_time = None
        self.tweets = []
        self.twitter_keywords = []
        self.future = self.rtm_client.start()
        self.commands = {
            "help": {
                "help": "Shows this helpful command reference",
                "func": lambda cmd, chan, wc: self.send_help_message(chan, wc)
            },
            "ping": {
                "help": "Show uptime of the bot",
                "func": lambda cmd, chan, wc: self.send_ping_message(chan, wc)
            },
            "exit": {
                "help": "Shutdown the bot",
                "func": lambda cmd, chan, wc: self.exit_bot(chan, wc)
            },
            "quit": {
                "help": "Shutdown the bot",
                "func": lambda cmd, chan, wc: self.exit_bot(chan, wc)
            },
            "list": {
                "help": "List current Twitter filters and counts",
                "func": lambda cmd, chan, wc: self.list_tweet_filters(chan, wc)
            },
            "add": {
                "help": "Add some twitter keyword filter",
                "func": lambda cmd, chan, wc: self.add_tweet_filter(
                    cmd, chan, wc)
            }
        }

        RTMClient.run_on(event="message")(self.read_message)

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        logger.debug('exiting')

    def connect_to_stream(self):
        """
        Returns the future to start the client loop outside of the class
        that way we can interject another coroutine to allow us to do other
        things inside the slack event loop
        """
        self.start_time = dt.now()
        return self.future

    def read_message(self, **kwargs):
        """
        Called when RTMClient receieves a message type event makes sure the
        message is directed at our bot then sends the command off to the
        command handler
        """
        data = kwargs['data']
        web_client = kwargs['web_client']
        message = data['text']
        channel = data['channel']

        matches = re.search(r"^<@(|[WU].+?)>(.*)", message)

        if matches and matches.group(1) == self.id:
            self.handle_command(matches.group(2).strip(), channel, web_client)

    def handle_command(self, command, channel, web_client):
        """
        this is where our command is actually executed, we first look to see
        if a command is in self.commands, this will be true if its a command
        that requires no input. (@BestSlackBot list)

        If its not then we are checking to see if it is a command that requires
        input (@BestSlackBot add <keyword>) and if so send that command off with
        its correct input
        """
        cmd = command.split(' ')
        if command in self.commands:
            self.commands[command]['func']("", channel, web_client)
        elif cmd[0] in self.commands:
            self.commands[cmd[0]]['func'](cmd[1], channel, web_client)

    def send_help_message(self, channel, web_client):
        """
        Construct a help message from available commands, then send them as a
        message to the channel where it was requested from
        """
        help_s = '```\n'
        for cmd in self.commands:
            help_s += f"{cmd}: {self.commands[cmd]['help']}\n"
        help_s += '```'

        web_client.chat_postMessage(
            channel=channel,
            text=help_s
        )

    def send_ping_message(self, channel, web_client):
        """
        Send a message about current uptime of the bot
        """
        up_time = dt.now() - self.start_time
        web_client.chat_postMessage(
            channel=channel,
            text=f"Bot has been active for: {up_time}"
        )

    def exit_bot(self, channel, web_client):
        """
        Disconnects the RTMClient from the slack server
        """
        web_client.chat_postMessage(
            channel=channel,
            text=":( Bot powering down"
        )
        self.rtm_client.stop()

    def list_tweet_filters(self, channel, web_client):
        """
        Gathers a list of current twitter keyword filters and sends them
        to a given channel
        """
        keywords = ""
        for keyword in self.twitter_keywords:
            keywords += f"{keyword}\n"

        keywords = "Keywords:\n" + keywords if keywords else ""

        web_client.chat_postMessage(
            channel=channel,
            text=keywords if keywords else "No keywords added yet"
        )

    def add_tweet_filter(self, command, channel, web_client):
        """
        adds a given filter word to search tweets by
        """
        self.twitter_keywords.append(command)

        web_client.chat_postMessage(
            channel=channel,
            text=f"Added keyword: {command}"
        )

    def add_tweets(self, tweets):
        self.tweets = tweets

    def print_tweets(self):
        if self.tweets:
            print(self.tweets)


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

    loop = asyncio.get_event_loop()

    with SlackBotClient(os.environ['SLACK_BOT_TOKEN']) as client:
        loop.run_until_complete(asyncio.gather(
            client.connect_to_stream(),
            add_tweet_to_bot(client),
            print_tweets(client)
        ))

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


# We will need a way to check if the bot is still connected,
# Handle this case with a signal handler in the integration
async def add_tweet_to_bot(client):
    tweets = []
    while True:
        tweets.append(1)
        client.add_tweets(tweets)
        await asyncio.sleep(5)


async def print_tweets(client):
    while True:
        client.print_tweets()
        await asyncio.sleep(5)

if __name__ == '__main__':
    main()
