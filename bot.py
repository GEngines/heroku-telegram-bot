


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
import os
import time
import  threading
os.environ["TZ"] = "Asia/Calcutta"
time.tzset()

greet_bot = telepot.Bot(WelcomeBot_Token)
reply_bot = telepot.Bot(ReplyBot_Token)

now = datetime.datetime.now()


def current_time():
    return "{0}:{1}:{2}".format( now.hour, now.minute, now.second)


def greet_users():
    new_offset = None
    today = now.day
    hour = now.hour
    minute = now.minute
    seconds = now.second

    while True:

        print ("Checking for new Messages...")
        greet_bot.getUpdates()

        if len(greet_bot.getUpdates(new_offset)) == 0:
            pass
        else:
            last_update = greet_bot.getUpdates(new_offset)[0]
            last_update_id = last_update['update_id']
            if "new_chat_members" in last_update["message"].keys():
                print("Sending Greeting....")
                new_member = last_update['message']['new_chat_members']
                chat_group_id = last_update["message"]["chat"]["id"]

                for each in new_member:
                    chat_user_id = each["id"]
                    chat_user_first_name = each["first_name"]
                    _message = welcome_message.replace("<name>", "*"+chat_user_first_name+"*")
                    greet_bot.sendMessage(chat_user_id, _message, "MarkDown")
                    greet_bot.sendMessage(chat_group_id, _message, "MarkDown")

            elif "left_chat_member" in last_update["message"].keys():
                print("Sending GoodBye....")
                leaving_member = last_update['message']['left_chat_member']
                chat_id = leaving_member["id"]
                chat_name = leaving_member["first_name"]
                chat_group_id = last_update["message"]["chat"]["id"]
                greet_bot.sendMessage(chat_id, leaving_message.replace("<name>", chat_name))
                greet_bot.sendMessage(chat_group_id, leaving_message_to_the_group.replace("<name>", chat_name))
            else:
                try:
                    last_chat_text = last_update['message']['text']
                    last_chat_id = last_update['message']['chat']['id']
                    last_chat_name = last_update['message']['chat']['first_name']

                    if last_chat_text.lower() in greetings and today == now.day and 6 <= hour < 12:
                        greet_bot.sendMessage(last_chat_id, 'Good Morning {}'.format(last_chat_name))
                        today += 1
                    elif last_chat_text.lower() in greetings and today == now.day and 12 <= hour < 17:
                        greet_bot.sendMessage(last_chat_id, 'Good Afternoon {}'.format(last_chat_name))
                        today += 1
                    elif last_chat_text.lower() in greetings and today == now.day and 17 <= hour < 23:
                        greet_bot.sendMessage(last_chat_id, 'Good Evening  {}'.format(last_chat_name))
                        today += 1
                    else:
                        greet_bot.sendMessage(last_chat_id, 'Hey There {}!'.format(last_chat_name))
                        today += 1

                except:
                    greet_bot.sendMessage("607211820", "Issue Occurred!")

            new_offset = last_update_id + 1

        sleep(1)


def common_tasks():

    new_offset = None

    while True:

        print ("Task Process is Idle...")

        reply_bot.getUpdates()

        if len(reply_bot.getUpdates(new_offset)) == 0:
            pass
        else:
            last_update = reply_bot.getUpdates(new_offset)[0]
            print(last_update)
            last_update_id = last_update['update_id']

            new_offset = last_update_id + 1

        sleep(5)


MainThread = threading.Thread(target=greet_users)
#TasksThread = threading.Thread(target=common_tasks)

MainThread.start()
#TasksThread.start()
