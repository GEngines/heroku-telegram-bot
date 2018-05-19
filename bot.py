


# Author - Bharath Metpally


welcome_message = """Hey There <name>,
Welcome to our profound community. Glad you have considered to be part of this community.

These are few rules, we would like you to adhere to, when interacting with anyone in this group.

1.No Foul Language.


Many Thanks!
Bot"""


leaving_message = "Sorry to see you leave our community! <name>, Please share your feedback."
leaving_message_to_the_group = "Oops! We just lost <name>"

WelcomeBot_Token = "570531436:AAGhlmqiyehM7hS_GzmvS9_pdnhUN96VFV8"
ReplyBot_Token = "600394117:AAFWzJN8ybJTo5IKhEyYtPKxNjkGBvxVugA"

greetings = ('hello', 'hi', 'greetings', 'sup', "greet me")


############### Do NOT modify anything beyond this point ######################################


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

now = datetime.datetime.now()


def current_time():
    return "{0}:{1}:{2}".format( now.hour, now.minute, now.second)


class Message(object):
    def __init__(self, update):
        self._update = update
        self.ID = self._update["message_id"]
        self.Date = self._update["date"]
        self.Chat = Chat(self._update["chat"])
        if "text" in self._update.keys():
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
    def __init__(self,chat):
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

        if "first_name" in self._chat.keys():
            self.FirstName = self._chat["first_name"]
            self.LastName = self._chat["last_name"]
        else:
            self.AllMembersAdmins = self._chat["all_members_are_administrators"]
            self.Title = self._chat["title"]


class FromObj(object):
    def __init__(self,fromValues):
        self._fromvalues = fromValues
        self.ID = ""
        self.IsBot = ""
        self.FirstName = ""
        self.LastName = ""
        self.Language = ""
        self.update_values()

    def update_values(self):
        self.ID = self._fromvalues["id"]
        self.FirstName = self._fromvalues["first_name"]
        self.LastName = self._fromvalues["last_name"]
        self.IsBot = self._fromvalues["is_bot"]
        self.Language = self._fromvalues["language_code"]


class Members(object):
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
    def __init__(self, token):
        self._token = token
        self.new_offset = None
        self.Now = datetime.datetime.now()
        telepot.Bot.__init__(self, token)
        self.members_joined = defaultdict(list)
        self.members_left = defaultdict(list)
        self.latest_update = ""

    def fetch_updates(self):
        return self.getUpdates(self.new_offset)

    def parse_update(self):
        while True:
            print("Checking for new Messages...")
            if len(self.fetch_updates()) == 0:
                pass
            else:
                self.latest_update = self.fetch_updates()[0]
                print(self.latest_update)
                self.objectify_latest_update()
                self.greet_users()
                self.custom_commands()

                self.new_offset = self.latest_update["update_id"] + 1
            sleep(1)

    def objectify_latest_update(self):
        self.Message = Message(self.latest_update["message"])


    def custom_commands(self):
        last_chat_text = self.Message.Text.lower()
        last_chat_id = self.Message.From.ID

        if last_chat_text == "/getnewmemberslist" and not self.Message.From.IsBot:
            self.sendMessage(last_chat_id, "You will get the list shortly.")

    def greet_users(self):

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


GreetingBot = HostResponse(WelcomeBot_Token)
GreetingBot.run()
