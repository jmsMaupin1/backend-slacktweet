#!/usr/bin/env python3
"""A standalone Slack client implementation
see https://slack.dev/python-slackclient/
"""
import time
import os
import re
import logging
from datetime import datetime as dt

from dotenv import load_dotenv
from slackclient import SlackClient

load_dotenv()
logger = logging.getLogger(__name__)


class SlackBotClient:

    def __init__(self, token, delay=1, logger=None):
        self.client = SlackClient(token)
        self.id = None
        self.logger = logger
        self.exit_flag = False
        self.delay = delay
        self.mention_regex = r"^<@(|[WU].+?)>(.*)"

    def __enter__(self):
        if self.client.rtm_connect(with_team_state=False):
            self.id = self.client.api_call('auth.test')['user_id']

            self.logger.debug('Bot connected to slack, id: {}'.format(self.id))

            while self.client.server.connected:
                command, channel = self.parse_bot_commands(
                    self.client.rtm_read())
                if command:
                    self.handle_command(command, channel)

                time.sleep(self.delay)

    def __exit__(self):
        self.logger.debug('Bot disconnected')

    def parse_bot_commands(self, slack_events):
        for event in slack_events:
            if ('type' in event
                    and event['type'] == 'message'
                    and 'subtype' not in event):

                user_id, message = self.parse_direct_mention(event['text'])
                self.logger.info(
                    'parse_direct_mention():\n'
                    'user_id: {}\n'
                    'message: {}\n'
                    .format(user_id, message)
                )
                if user_id == self.id:
                    return message, event['channel']

        return None, None

    def handle_command(self, command, channel):
        if command.startswith('echo'):
            self.logger.info(
                'handle_command(command, channel)\n'
                'command: {}\n'
                'channel: {}\n'
                .format(command, channel)
            )
            self.client.rtm_send_message(
                channel,
                command[5:]
            )

    def parse_direct_mention(self, message_text):
        matches = re.search(self.mention_regex, message_text)
        if matches:
            return (matches.group(1), matches.group(2).strip())
        return (None, None)


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

    with SlackBotClient(os.environ['BOT_TOKEN'], 1, logger):
        pass

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
