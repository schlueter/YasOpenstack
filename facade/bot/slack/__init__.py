from __future__ import print_function

import os
import re
import sys
import time

from slackclient import SlackClient

BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
BOT_ID = os.environ.get('SLACK_BOT_ID')
READ_WEBSOCKET_DELAY = float(os.environ.get('READ_WEBSOCKET_DELAY', 1))
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
BOT_NAME = 'facade'

def list_handler(target):
    return 'listing'

def launch_handler(name, branch):
    return f'launching {name} on {branch}'

def delete_handler(name):
    return f'deleting {name}'

HANDLERS = {
    re.compile('(?:list)\ ?(\w\.)'): list_handler,
    re.compile('(?:launch|start)\ ([-\w]+)(?:\ on\ )?([-\w]+:?[-\w]+)?'): launch_handler,
    re.compile('(?:delete|drop|terminate|bust a cap in|pop a cap in) ([-\ \w]+)'): delete_handler
}

def log(*msgs):
    print(*msgs, file=sys.stderr)

class Client(SlackClient):

    def __init__(self):
        super().__init__(BOT_TOKEN)
        self.bot_id = self.__retrieve_bot_user_id()
        self.at_bot = "<@" + self.bot_id + ">"

    def __retrieve_bot_user_id(self):
        log("Retrieving users list.")
        api_call = self.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            log(f"Pulling the bot's, {BOT_NAME}, ID.")
            for user in users:
                if 'name' in user and user.get('name') == BOT_NAME:
                    return user.get('id')
            else:
                raise NoBot("could not find bot user with the name " + BOT_NAME)
        else:
            raise SlackClientFailure()

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
                   "* command with numbers, delimited by spaces."

        for regex in HANDLERS.keys():
            match = regex.match(command)
            if match:
                groups = match.groups()
                return self.reply(channel, HANDLERS[regex](*groups))
        else:
            response = "Sure...write some more code then I can do that!"

    def reply(self, channel, response):
        return self.api_call(
            "chat.postMessage",
            channel=channel,
            text=response,
            as_user=True
        )

    def parse_slack_output(self, rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        if rtm_output and len(rtm_output) > 0:
            for output in [output for output in rtm_output
                              if output
                                  and 'channel' in output
                                  and 'text' in output
                                  and not output.get('user') == BOT_ID]:
                log(f"rtm_output {rtm_output}")
                channel_info = self.api_call('channels.info', channel=output.get('channel'))
                if channel_info.get('ok', False) and AT_BOT in output['text']:
                    log(f"receieved message in {output['channel']} from {output['user']}: {output['text']}")
                    return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
                group_info = self.api_call('groups.info', channel=output.get('channel'))
                if not channel_info.get('ok', False) and not group_info.get('ok', False):
                    log(f"receieved direct message from {output['user']}: {output['text']}")
                    return output['text'].strip().lower(), output['channel']
        return None, None

    def listen(self):
        if self.rtm_connect():
            log("StarterBot connected as {}<{}> and running!".format(BOT_NAME, BOT_ID))
            while True:
                command, channel = self.parse_slack_output(self.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            log("Connection failed. Invalid Slack token or bot ID?")

def main():
    client = Client()
    client.listen()

if __name__ == '__main__':
    main()
