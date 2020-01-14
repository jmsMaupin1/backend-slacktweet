#!/usr/bin/env python3
"""A standalone Slack client implementation
see https://slack.dev/python-slackclient/
"""
import os
import re
import logging
import signal
from datetime import datetime as dt

from dotenv import load_dotenv
from slack import RTMClient, WebClient

load_dotenv()
logger = logging.getLogger(__name__)

sig_dict = dict(
    (k, v) for v, k in reversed(sorted(signal.__dict__.items()))
    if v.startswith('SIG') and not v.startswith('SIG_')
)


class SlackBotClient:
    """
    Creates a slackbot object capable of logging into slack
    and monitoring messages
    """

    def __init__(self, token):
        self.rtm_client = RTMClient(token=token)
        self.id = WebClient(token).api_call('auth.test')['user_id']
        self.start_time = None
        self.up_time = None
        self.command_callback = None
        self.commands = {}
        RTMClient.run_on(event="message")(self.read_message)
        RTMClient.run_on(event="channel_joined")(self.channel_joined)

    def __enter__(self):
        return self

    def __exit__(self, err_type, value, traceback):
        self.rtm_client.stop()

    def start_stream(self):
        """
        Starts the stream to listen for commands to the bot
        """
        self.start_time = dt.now()
        self.rtm_client.start()

    def channel_joined(self, **kwargs):
        """When joining a channel emit a hello message"""
        web_client = kwargs['web_client']
        channel = kwargs['data']['channel']

        web_client.chat_postMessage(
            channel=channel['id'],
            text="Whats up party people!"
        )

    def add_command(self, command, help_str):
        """Adds commands to listen for and a help message"""
        self.commands[command] = help_str

    def add_command_callback(self, callback):
        """
        Registers a callback to be called when a known command is received
        """
        self.command_callback = callback

    def handle_command(self, command, channel, web_client):
        """Takes a command and calls the callback funcion appropriately"""
        cmd = command.split(' ')
        if self.command_callback:
            if command in self.commands:
                self.command_callback(self, command, '', channel, web_client)
            elif cmd[0] in self.commands:
                self.command_callback(
                    self,
                    cmd[0],
                    cmd[1],
                    channel,
                    web_client
                )

    def read_message(self, **kwargs):
        """
        Reads and parses the message for a direct mention,
        Then if it finds a direct mention passes it to the command handler
        """
        data = kwargs['data']
        web_client = kwargs['web_client']
        message = data['text']
        channel = data['channel']

        matches = re.search(r"^<@(|[WU].+?)>(.*)", message)

        if matches and matches.group(1) == self.id:
            self.handle_command(matches.group(2).strip(), channel, web_client)

    def signal_handler(self, sig_num, frame):
        logger.warn(
            'Received OS process signal: {}'
            .format(sig_dict[sig_num])
        )

        self.close_stream()

    def close_stream(self):
        self.__exit__(None, None, None)


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

    with SlackBotClient(os.environ['SLACK_BOT_TOKEN']) as sc:
        for cmd in commands:
            sc.add_command(cmd, commands[cmd])

        sc.add_command_callback(slackbot_callback)
        sc.start_stream()

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
