#!/usr/bin/env python3
"""
A Slackbot implementation that integrates Slack and Twitter clients
together
"""
import signal
import asyncio
import logging
from datetime import datetime as dt

import nest_asyncio
from slack_client import SlackClient
from twitter_client import TwitterClient

sig_dict = dict(
    (k, v) for v, k in reversed(sorted(signal.__dict__.items()))
    if v.startswith('SIG') and not v.startswith('SIG_')
)

nest_asyncio.apply()
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


async def shutdown(sig_num, loop):
    """Shut down service and clean up"""
    logging.warn('Received force exit signal')
    tasks = [
        t for t in asyncio.all_tasks() if t is not asyncio.current_task()
    ]

    [task.cancel() for task in tasks]

    logging.info(f"cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    logging.info('finished shuttding down')
    loop.stop()


def signal_handler(sig_num, loop):
    print('\n\nsignal handling and stuff\n\n')
    return asyncio.create_task(sig_num, loop)


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

    with SlackClient() as sc:
        with TwitterClient(['test']) as tc:
            for cmd in commands:
                sc.add_command(cmd, commands[cmd])

            sc.add_command_callback(slackbot_callback)
            tc.add_callback(
               sc.private_message_jt
            )

            loop.create_task(sc.start_stream())
            loop.create_task(tc.start_stream())

            # Not being called
            signal.signal(signal.SIGINT, lambda s, l: print('\n\n\n\nSIGINT\n\n\n\n'))

            # Signal handler not being called
            for s in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(
                    s,
                    signal_handler
                )

            # Twitter client shuts down slack doesnt seem to
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                logger.warn('Keyboard interrupt')
            finally:
                loop.close()

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
