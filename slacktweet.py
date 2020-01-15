#!/usr/bin/env python3
"""
A Slackbot implementation that integrates Slack and Twitter clients
together
"""
import asyncio
import logging
import argparse
from datetime import datetime as dt

from slack_client import SlackClient
from twitter_client import TwitterClient

logger = logging.getLogger(__name__)

commands = {
    "help": "Prints a helpful message",
    "ping": "Show uptime of this bot",
    "exit": "Shutdown this bot",
    "quit": "Shutdown this bot",
    "list": "list current twitter filters and counters",
    "add": "add some twitter keyword filters",
    "del": "Remove some twitter keyword filters",
    "clear": "Remove all twitter filters",
    "raise": "Manually test exception handler"
}


class ClientInjector(object):
    """Injects a given client into a function"""
    def __init__(self, client):
        self.client = client

    def __call__(self, function):
        def wrapped(*args):
            function(*args, self.client)
        return wrapped


def slackbot_callback(client, command, data, channel, web_client):
    """Callback method to handle commands emitted by the slackbot client"""
    if command == 'help':
        help_s = '```\n'
        for cmd in client.commands:
            help_s += f"{cmd}: {client.commands[cmd]}\n"
        help_s += '```'

        web_client.chat_postMessage(
            channel=channel,
            text=help_s
        )


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

    with TwitterClient(['test']) as tc:
        slack_client = SlackClient()
        for cmd in commands:
            slack_client.add_command(cmd, commands[cmd])

        slack_client.add_callback(slackbot_callback)
        tc.add_callback(slack_client.private_message_jt)

        slack_client.start_stream()

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
