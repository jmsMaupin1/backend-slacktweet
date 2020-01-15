#!/usr/bin/env python3
"""
A Slackbot implementation that integrates Slack and Twitter clients
together
"""
import logging
import logging.handlers
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

log_levels = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG
}


class ClientInjector(object):
    """Injects a given client into a function"""
    def __init__(self, client):
        self.client = client

    def __call__(self, function):
        def wrapped(*args):
            function(*args, self.client)
        return wrapped


def slackbot_callback(client, command, data, channel, web_client, *args):
    """Callback method to handle commands emitted by the slackbot client"""
    if command == 'help':
        """Prints a list of commands"""
        help_s = '```\n'
        for cmd in client.commands:
            help_s += f"{cmd}: {client.commands[cmd]}\n"
        help_s += '```'

        web_client.chat_postMessage(
            channel=channel,
            text=help_s
        )

    if command == 'ping':
        """returns the uptime of the bot"""
        uptime = dt.now() - client.start_time

        web_client.chat_postMessage(
            channel=channel,
            text=f"The bot has been active for: {uptime}"
        )

    if command == 'exit' or command == 'quit':
        """Shuts the bot down"""
        client.rtm_client.stop()

    if command == 'list':
        """List current filter keywords"""
        twitter_client = args[0]
        web_client.chat_postMessage(
            channel=channel,
            text=twitter_client.filters
        )

    if command == 'add':
        """Add a keyword filter to twitter client"""
        twitter_client = args[0]
        filters = twitter_client.filters
        filters.append(data)
        twitter_client.update_filters(filters)

    if command == 'del':
        """Remove a keyword filter from twitter client"""
        twitter_client = args[0]
        filters = twitter_client.filters
        filter_index = filters.index(data)
        if filter_index >= 0:
            filters.pop(filter_index)

        twitter_client.update_filters(filters)

    if command == 'clear':
        """Remove all keyword filters from twitter client"""
        twitter_client = args[0]
        twitter_client.update_filters([])

    if command == 'raise':
        client.raise_exception(data, channel)


def create_parser():
    logger_levels = " ".join([key for key in log_levels])
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l', '--loglevel',
        help=f"Logging level can be: {logger_levels}"
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.loglevel:
        parser.print_help()
        exit(1)

    logging.basicConfig(
        level=log_levels[args.loglevel],
        format='%(process)d - %(asctime)s - %(levelname)s - %(message)s',
        datefmt='%y-%m-%d %H:%M:%S',
        handlers=[
            logging.handlers.RotatingFileHandler(
                'slacktweet-log.log',
                maxBytes=50000,
                backupCount=5
            ),
            logging.StreamHandler()
        ]
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

    with TwitterClient([]) as tc:
        slack_client = SlackClient()
        for cmd in commands:
            slack_client.add_command(cmd, commands[cmd])

        slack_client.add_callback(
            ClientInjector(tc)(slackbot_callback)
        )
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
