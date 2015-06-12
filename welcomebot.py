#!/usr/bin/env python
import getpass
import logging
import logging.handlers
import os
import random
import sys
import time

import ChatExchange.chatexchange.client
import ChatExchange.chatexchange.events
import ChatExchange.chatexchange.browser
import who_to_welcome
import image_search

logger = logging.getLogger(__name__)

def main():
    setup_logging()
    # Run `. setp.sh` to set the below testing environment variables

    def welcome_bot_host_options():
        print "Welcome Bot Host Site Options (select 1, 2, or 3)"
        print "  1. chat.stackexchange.com"
        print "  2. chat.meta.stackexchange.com"
        print "  3. chat.stackoverflow.com"
        print "What will be your Welcome Bot's host site?"
    welcome_bot_host_options()
    host_id_choice = raw_input()
    while host_id_choice not in ['1','2','3']:
        print "Invalid Choice"
        welcome_bot_host_options()
        host_id_choice = raw_input()
    if host_id_choice == '1':
        print "You have chosen chat.stackexchange.com as your Welcome Bot's host site."
        host_id = 'stackexchange.com'
    elif host_id_choice == '2':
        print "You have chosen meta.chat.stackexchange.com as your Welcome Bot's host site."
        host_id = 'meta.stackexchange.com'
    elif host_id_choice == '3':
        print "You have chosen chat.stackoverflow.com as your Welcome Bot's host site."
        host_id = 'stackoverflow.com'

    print "What is the room's ID?"
    room_id_choice = raw_input()
    while room_id_choice.isdigit() == False:
        print "Invalid Input, must be a number"
        room_id_choice = raw_input()
    global room_id
    room_id = room_id_choice  # Charcoal Chatbot Sandbox

    print "What would you like the welcome message to be?"
    global welcome_message
    welcome_message = raw_input()

    if 'ChatExchangeU' in os.environ:
        email = os.environ['ChatExchangeU']
    else:
        email = raw_input("Email: ")
    if 'ChatExchangeP' in os.environ:
        password = os.environ['ChatExchangeP']
    else:
        password = getpass.getpass("Password: ")

    client = ChatExchange.chatexchange.client.Client(host_id)
    client.login(email, password)

    global bot
    bot = client.get_me()

    global room
    room = client.get_room(room_id)
    room.join()
    room.watch(on_enter)
    room.watch(on_command)

    print "(You are now in room #%s on %s.)" % (room_id, host_id)
    room.send_message("I'm alive :)")

    while True:
        message = raw_input("<< ")
        if message == "die":
            room.send_message("I'm dead :(")
            time.sleep(0.4)
            break
        else:
            room.send_message(message)

    client.logout()


def on_enter(event, client):
    if isinstance(event, ChatExchange.chatexchange.events.UserEntered):
        if event.user.id == bot.id:
            pass
        else:
            if who_to_welcome.check_user(event.user.id, room_id, 'enter'):
                room.send_message("@"+event.user.name.replace(" ","")+" "+welcome_message)

def on_command(message, client):
    if isinstance(message, ChatExchange.chatexchange.events.MessagePosted):
        print "Message Posted"
        if message.content.startswith("!!_image"):
            print "Is image request"
            search_term = "".join(message.content.split()[1:])
            image = image_search.search_image(search_term)
            print image
            if image is False:
                print "No Image"
                room.send_message("@"+message.user.name.replace(" ","")+" No image was found for "+search_term)
            else:
                print message.content
                print search_term
                room.send_message(image)
                print ""

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.DEBUG)

    # In addition to the basic stderr logging configured globally
    # above, we'll use a log file for chatexchange.client.
    wrapper_logger = logging.getLogger('ChatExchange.chatexchange.client')
    wrapper_handler = logging.handlers.TimedRotatingFileHandler(
        filename='client.log',
        when='midnight', delay=True, utc=True, backupCount=7,
    )
    wrapper_handler.setFormatter(logging.Formatter(
        "%(asctime)s: %(levelname)s: %(threadName)s: %(message)s"
    ))
    wrapper_logger.addHandler(wrapper_handler)

if __name__ == '__main__':
    main(*sys.argv[1:])
