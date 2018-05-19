

'''
 Bot Wrapper for Telegram API v2


This script is written for Telegram API's bot tasks and commands.

This script will help the Bot send greeting messages when a User(not a bot) joins the group where the bot is deployed.
Also, a Message to the user and the group will be sent when the He/She leaves the group.
Upon request by the Admin of the group, the Bot will provide the list of users who joined the group recently.



Next Update:
 - Update the Bot's help command, which will help the user see the list of commands one can ask the bot.
 - Update the commands, provide additional commands if the user is the admin of the group.
 - Update to provide the list of user who joined or left the group to the requested user only if he/she is an admin
    of that specified group.




# Author - Bharath Metpally
# Email - bharathgdk@gmail.com

'''

###############################################################
#                   MODIFY THESE VALUES                       #
###############################################################


# This is the Welcome Message, Which will be sent to the User when he/she joins the Group.
# <name>  - This is required to be present in the message where User's name is to be replaced.

welcome_message = """Hey There <name>,
Welcome to our profound community. Glad you have considered to be part of this community.

These are few rules, we would like you to adhere to, when interacting with anyone in this group.

1.No Foul Language.


Many Thanks!
Bot"""


# This message will be sent when a User leaves the group.
# <name>  - This is required to be present in the message where User's name is to be replaced.
leaving_message = "Sorry to see you leave our community! <name>, Please share your feedback."

# This message will be sent to the group once a user leaves the group.
leaving_message_to_the_group = "Oops! We just lost <name>"


# If you are unaware on how to Create a Bot, The following Links might be of help.
#  BotFather (https://telegram.me/botfather) -  Use it to create new bot accounts and manage your existing bots.

# Please update the Token for the Bot you wish to use for Welcoming Users to the Group.

WelcomeBot_Token = "570531436:AAGhlmqiyehM7hS_GzmvS9_pdnhUN96VFV8"

# Please update the Token for the bots you wish to be reply Bots.
ReplyBot_Token = "600394117:AAFWzJN8ybJTo5IKhEyYtPKxNjkGBvxVugA"


# Basic Greetings to which Bot will reply back with a basic greeting.
greetings = ('hello', 'hi', 'greetings', 'sup', "greet me")


######################### DO NOT MODIFY ANYTHING BEYOND THIS POINT ######################################


import requests
import datetime
from time import sleep
import telepot
import os,sys
import time
import  threading

from collections import defaultdict

if hasattr(time, 'tzset'):
    os.environ["TZ"] = "Asia/Calcutta"
    time.tzset()



def current_time():
    '''
    Get Current Time
    :return: string
    '''

    now = datetime.datetime.now()
    return "{0}:{1}:{2}".format( now.hour, now.minute, now.second)


class Message(object):
    '''
    Wrapper for the Messages dictionary from Telegram Messages.
    '''
    def __init__(self, update):
        self._update = update
        self.ID = self._update["message_id"]
        self.Date = self._update["date"]
        self.Chat = Chat(self._update["chat"])
        if "text" in self._update:
            self.Text = self._update["text"]
        else:
            self.Text = ""
        self.From = FromObj(self._update["from"])
        self.IncomingMembers = ""
        self.OutgoingMembers = ""
        self.classify_members()

    def classify_members(self):

        local_list_in = []
        if "new_chat_members" in self._update:
            for e in self._update["new_chat_members"]:
                local_list_in.append(Members(e))

            self.IncomingMembers = local_list_in

        if "left_chat_member" in self._update:
            self.OutgoingMembers = Members(self._update['left_chat_member'])


class Chat(object):
    '''
    Wrapper for the 'Chat' Dictionary from the Messages.
    '''
    def __init__(self, chat):
        self._chat = chat
        self.ID = ""
        self.FirstName = ""
        self.LastName = ""
        self.Type = ""
        self.isBot = False
        self.Title = ""
        self.AllMembersAdmins = False
        self.update_values()

    def update_values(self):
        self.ID = self._chat["id"]
        self.Type = self._chat["type"]

        if "first_name" in self._chat:
            self.FirstName = self._chat["first_name"]
            self.LastName = self._chat["last_name"]
        else:
            self.AllMembersAdmins = self._chat["all_members_are_administrators"]
            self.Title = self._chat["title"]


class FromObj(object):
    '''
    Wrapper for the 'From' Dictionary from the Messages.
    '''
    def __init__(self, f):
        self._from_values = f
        self.ID = ""
        self.IsBot = ""
        self.FirstName = ""
        self.LastName = ""
        self.Language = ""
        self.update_values()

    def update_values(self):
        self.ID = self._from_values["id"]
        self.FirstName = self._from_values["first_name"]
        self.LastName = self._from_values["last_name"]
        self.IsBot = self._from_values["is_bot"]
        self.Language = self._from_values["language_code"]


class Members(object):
    '''
        Wrapper for the 'New Members' and 'Departing Members' Dictionary from the Messages.
    '''
    def __init__(self, cm):
        self._cm = cm
        self.ID = ""
        self.IsBot = ""
        self.FirstName = ""
        self.UserName = ""
        self.update_values()

    def update_values(self):
        self.ID = self._cm["id"]
        self.IsBot = self._cm["is_bot"]
        self.FirstName = self._cm["first_name"]
        self.UserName = self._cm["username"]


class HostResponse(telepot.Bot):
    '''
    Host Control. Main Class for all the responses.
    '''
    def __init__(self, token, delay):
        self._token = token
        self.delay = delay
        self.new_offset = None
        self.Now = datetime.datetime.now()
        telepot.Bot.__init__(self, token)
        self.members_joined = defaultdict(list)
        self.members_left = defaultdict(list)
        self.latest_update = ""

    def fetch_updates(self):
        '''
        Get updates for each new Message from the server.
        :return: dictionary
        '''
        return self.getUpdates(self.new_offset)

    def parse_update(self):
        '''
        Function that runs in a Loop, controlling all the aspects of the Bot.
        :return: None
        '''
        while True:
            print("Checking for new Messages...")
            if len(self.fetch_updates()) == 0:
                pass
            else:
                self.latest_update = self.fetch_updates()[0]
                self.objectify_latest_update()
                self.greet_users()
                self.custom_commands()

                self.new_offset = self.latest_update["update_id"] + 1
            sleep(self.delay)

    def objectify_latest_update(self):
        '''
        Function to convert the Message from the server to an Object.
        :return: None
        '''
        self.Message = Message(self.latest_update["message"])

    def custom_commands(self):
        '''
        Additional Commands, For Users and Admins, to get certain tasks done.
        :return: None
        '''
        last_chat_text = self.Message.Text.lower()
        last_chat_id = self.Message.From.ID

        if last_chat_text == "/getnewmemberslist" and not self.Message.From.IsBot:
            self.sendMessage(last_chat_id, "You will get the list shortly.")

    def greet_users(self):
        '''
        This Function will send out Greeting Messages to New and Departing Users. Also sends out basic greetings.
        :return: None
        '''
        if self.Message.IncomingMembers != "":
            print("Sending Greeting....")
            for eachMember in self.Message.IncomingMembers:
                _message = welcome_message.replace("<name>", "*"+eachMember.FirstName+"*")
                if not eachMember.IsBot:
                    self.sendMessage(eachMember.ID, _message, "MarkDown")
                    self.sendMessage(self.Message.Chat.ID, _message, "MarkDown")
                    _temp_list = []
                    _temp_list.append(eachMember.ID)
                    _temp_list.append(eachMember.FirstName)
                    self.members_joined[self.Message.Chat.ID].append(_temp_list)
                else:
                    print ("Oops! Looks like the member is a Bot!")

        if self.Message.OutgoingMembers != "":
            print("Sending GoodBye....")
            if not self.Message.OutgoingMembers.IsBot:
                self.sendMessage(self.Message.OutgoingMembers.ID, leaving_message.replace("<name>", self.Message.OutgoingMembers.FirstName))
                self.sendMessage(self.Message.Chat.ID, leaving_message_to_the_group.replace("<name>", self.Message.OutgoingMembers.FirstName))
                _temp_list = []
                _temp_list.append(self.Message.OutgoingMembers.ID)
                _temp_list.append(self.Message.OutgoingMembers.FirstName)
                _temp_list.append()
                self.members_left[self.Message.Chat.ID].append(_temp_list)
            else:
                print("Oops! Looks like the member is a Bot!")

        else:
            if not self.Message.From.IsBot and self.Message.Text != "":
                last_chat_text = self.Message.Text.lower()
                if last_chat_text in greetings and 6 <= self.Now.hour < 12:
                    self.sendMessage(self.Message.Chat.ID, 'Good Morning {}'.format(self.Message.Chat.FirstName))
                elif last_chat_text in greetings and 12 <= self.Now.hour < 17:
                    self.sendMessage(self.Message.Chat.ID, 'Good Afternoon {}'.format(self.Message.Chat.FirstName))
                elif last_chat_text in greetings and 17 <= self.Now.hour < 23:
                    self.sendMessage(self.Message.Chat.ID, 'Good Evening  {}'.format(self.Message.Chat.FirstName))
                elif last_chat_text in greetings and 0 <= self.Now.hour <= 5:
                    self.sendMessage(self.Message.Chat.ID, 'Hey There {}!'.format(self.Message.Chat.FirstName))

    def run(self):
        self.parse_update()


GreetingBot = HostResponse(WelcomeBot_Token, 1)
GreetingBot.run()
