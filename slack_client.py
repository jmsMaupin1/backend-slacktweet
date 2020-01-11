#!/usr/bin/env python3
"""A standalone Slack client implementation
see https://slack.dev/python-slackclient/
"""
import os
import re
import logging
from datetime import datetime as dt

from dotenv import load_dotenv
from slack import RTMClient, WebClient

load_dotenv()
logger = logging.getLogger(__name__)


class SlackBotClient:
    """"""

    def __init__(self, token):
        self.rtm_client = RTMClient(token=token, run_async=True)
        self.id = WebClient(token).api_call('auth.test')['user_id']
        self.start_time = None
        RTMClient.run_on(event="message")(self.read_message)
        self.future = self.rtm_client.start()
        self.commands = {
            "help": {
                "help": "Shows this helpful command reference",
                "func": lambda cmd, chan, wc: self.send_help_message(chan, wc)
            },
            "ping": {
                "help": "Show uptime of the bot",
                "func": lambda cmd, chan, wc: self.send_ping_message(chan, wc)
            }
        }
        self.commands_old = [
            {
                "command": "help",
                "help": "Shows this helpful command reference"
            },
            {
                "command": "ping",
                "help": "Show uptime of the bot"
            },
            {
                "command": "exit",
                "help": "Shutdown the bot"
            },
            {
                "command": "quit",
                "help": "Shutdown the bot"
            },
            {
                "command": "list",
                "help": "List current Twitter filters and counts"
            },
            {
                "command": "add",
                "help": "Add some twitter keyword filter"
            },
            {
                "command": "del",
                "help": "Remove some twitter keyword filter"
            },
            {
                "command": "clear",
                "help": "Remove all twitter keyword filters"
            },
            {
                "command": "raise",
                "help": "Manually raise an exception"
            }
        ]

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        logger.debug('exiting')

    def connect_to_stream(self):
        loop = self.future.get_loop()
        self.start_time = dt.now()
        loop.run_until_complete(self.future)

    def read_message(self, **kwargs):
        data = kwargs['data']
        web_client = kwargs['web_client']
        message = data['text']
        channel = data['channel']

        matches = re.search(r"^<@(|[WU].+?)>(.*)", message)

        if matches and matches.group(1) == self.id:
            self.handle_command(matches.group(2).strip(), channel, web_client)

    def handle_command(self, command, channel, web_client):
        if command in self.commands:
            self.commands[command]['func'](command, channel, web_client)

    def send_help_message(self, channel, web_client):
        help_s = '```\n'
        for cmd in self.commands:
            print(cmd)
            help_s += f"{cmd}: {self.commands[cmd]['help']}\n"
        help_s += '```'

        web_client.chat_postMessage(
            channel=channel,
            text=help_s
        )

    def send_ping_message(self, channel, web_client):
        up_time = dt.now() - self.start_time
        web_client.chat_postMessage(
            channel=channel,
            text=f"Bot has been active for: {up_time}"
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

    with SlackBotClient(os.environ['SLACK_BOT_TOKEN']) as client:
        client.connect_to_stream()

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
