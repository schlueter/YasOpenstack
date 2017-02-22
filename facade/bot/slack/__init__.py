from __future__ import print_function

import os
import time

from slackclient import SlackClient

BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
BOT_ID = os.environ.get('SLACK_BOT_ID')
READ_WEBSOCKET_DELAY = float(os.environ.get('READ_WEBSOCKET_DELAY', 1))
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
BOT_NAME = 'facade'

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    if slack_rtm_output and len(slack_rtm_output) > 0:
        for output in slack_rtm_output:
            if output and 'text' in output and AT_BOT in output['text']:
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

class Client(object):

    def __init__(self):
        self.slack_client = SlackClient(BOT_TOKEN)


    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
                   "* command with numbers, delimited by spaces."
        if command.startswith(EXAMPLE_COMMAND):
            response = "Sure...write some more code then I can do that!"
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response,
            as_user=True
        )

    def listen(self):
        if self.slack_client.rtm_connect():
            print("StarterBot connected as {}<{}> and running!".format(BOT_NAME, BOT_ID))
            while True:
                command, channel = parse_slack_output(self.slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")

def main():
    client = Client()
    client.listen()

if __name__ == '__main__':
    main()
