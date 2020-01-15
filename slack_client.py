#!/usr/bin/env python3
"""A standalone Slack client implementation
see https://slack.dev/python-slackclient/
"""
import os
import re
import logging
import time
from datetime import datetime as dt

from dotenv import load_dotenv
from slack import RTMClient

load_dotenv()
logger = logging.getLogger(__name__)


class SlackClient:
    """
    Creates a slackbot object capable of logging into slack
    and monitoring messages
    """

    def __init__(self):
        token = os.environ['SLACK_BOT_TOKEN']
        self.rtm_client = RTMClient(token=token, run_async=True)
        self.future = self.rtm_client.start()
        self.vomit_channel = "#bestslackbot-room"
        self.web_client = None
        self.id = None
        self.start_time = None
        self.command_callback = None
        self.commands = {}
        RTMClient.run_on(event="message")(self.read_message)
        RTMClient.run_on(event="channel_joined")(self.channel_joined)
        RTMClient.run_on(event="hello")(self.bot_connected)

    def start_stream(self):
        """
        Starts the stream to listen for commands to the bot
        """
        self.start_time = dt.now()
        loop = self.future.get_loop()
        loop.run_until_complete(self.future)

    def bot_connected(self, **kwargs):
        """Upon connecting to the slack client grab the bot id"""
        self.web_client = kwargs['web_client']
        self.id = self.web_client.api_call('auth.test')['user_id']

    def channel_joined(self, **kwargs):
        """When joining a channel emit a hello message"""
        web_client = kwargs['web_client']
        channel = kwargs['data']['channel']

        web_client.chat_postMessage(
            channel=channel['id'],
            text="Whats up party people!"
        )

    def get_channel_list(self):
        chan_list = self.web_client.channels_list()

    def add_command(self, command, help_str):
        """Adds commands to listen for and a help message"""
        self.commands[command] = help_str

    def add_callback(self, callback):
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
                logger.info(channel)
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
        message = data['text'] if 'text' in data else ''
        channel = data['channel']

        matches = re.search(r"^<@(|[WU].+?)>(.*)", message)

        if matches and matches.group(1) == self.id:
            self.handle_command(matches.group(2).strip(), channel, web_client)

    def private_message_jt(self, text):
        try:
            self.web_client.chat_postMessage(
                channel='DSD690213',
                text=text
            )
            time.sleep(1)
        except Exception as e:
            logger.exception(f" Slack - Unhandled Exception: {e}")
