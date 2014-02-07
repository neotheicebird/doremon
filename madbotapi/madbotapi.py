#!/usr/bin/env python
"""API of madbot which is used to read and parse specific conversations going
on in the MAD group (GLeague). Also it can be used to update a online repo or a
GIT page of the information parsed."""

import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(1, os.path.join(os.path.join(parentdir, "yowsup"), "src"))
from Yowsup.Common.utilities import Utilities
from Yowsup.Common.debugger import Debugger
from Yowsup.Common.constants import Constants
from Examples.CmdClient import WhatsappCmdClient
from Examples.EchoClient import WhatsappEchoClient
from Examples.ListenerClient import WhatsappListenerClient
#
from Examples.MediaClient import WhatsappMediaClient
from Examples.GroupClient import WhatsappGroupClient
#

from Yowsup.Registration.v2.existsrequest import WAExistsRequest as WAExistsRequestV2
from Yowsup.Registration.v2.coderequest import WACodeRequest as WACodeRequestV2
from Yowsup.Registration.v2.regrequest import WARegRequest as WARegRequestV2
from Yowsup.Contacts.contacts import WAContactsSyncRequest

import threading,time, base64
from collections import deque

import re
import json

from Yowsup.connectionmanager import YowsupConnectionManager

DEFAULT_CONFIG = os.path.join(parentdir, "config.madbot")

def getCredentials(config = DEFAULT_CONFIG):
    if os.path.isfile(config):
        f = open(config)

        phone = ""
        idx = ""
        pw = ""
        cc = ""

        try:
            for l in f:
                line = l.strip()
                if len(line) and line[0] not in ('#',';'):

                    prep = line.split('#', 1)[0].split(';', 1)[0].split('=', 1)

                    varname = prep[0].strip()
                    val = prep[1].strip()

                    if varname == "phone":
                        phone = val
                    elif varname == "id":
                        idx = val
                    elif varname =="password":
                        pw =val
                    elif varname == "cc":
                        cc = val

            return (cc, phone, idx, pw);
        except:
            pass

    return 0


class madbotapi:

    def __init__(self, config = DEFAULT_CONFIG, keepAlive = False):
        credentials = getCredentials(config)

        if credentials:
            countryCode, login, identity, password = credentials

            identity = Utilities.processIdentity(identity)
            password = base64.b64decode(bytes(password.encode('utf-8')))

            if countryCode:
                phoneNumber = login[len(countryCode):]
            else:
                sys.exit("ERROR. Check cc in config")
        else:
            raise IOError("Couldn't find the config file")

        Debugger.enabled = True

        self.phoneNumber = phoneNumber
        self.jid = "%s@s.whatsapp.net" % phoneNumber
        self.sendReceipts = False # Auto ack flag, keep False while developing
        self.username = login
        self.password = password
        self.keepAlive = keepAlive

        self.unreadMsges = deque()

        #connectionManager = YowsupConnectionManager()
        #connectionManager.setAutoPong(keepAlive)
        #connectionManager.jid = self.jid
        #self.methodsInterface = connectionManager.getMethodsInterface() # used
        # to call methods like set_status, set_profile_pic etc

    def send_message(self, targetPhone, message):
        wa = WhatsappEchoClient(targetPhone, message)
        wa.login(self.username, self.password)

    def read_messages(self):
        """ Reads both personal and group messages
        """
        wa = WhatsappListenerClient(self.keepAlive, self.sendReceipts)
        # with sendReceipt = True messages are sent back from server only once
        wa.login(self.username, self.password)
        while wa.msgQueue:
            self.unreadMsges.append(wa.msgQueue.pop())

    def set_profile_pic(self, filePath): #ERROR
        """ Uploads a profile pic to the users' whatsapp account
        """
        filePath = (filePath,)
        self.methodsInterface.call("profile_setPicture", filePath)

    def set_status(self, status): #ERROR
        """ Sets a status message for the users' whatsapp account
        """
        #wa = WhatsappMediaClient(self.sendReceipts, timeout = float('Inf') )
        wa = WhatsappMediaClient(self.sendReceipts, timeout = 5 )
        wa.login(self.username, self.password)
        wa.setStatus(status)


    def send_presence_available(self):
        """docstring for presence_send_availbale"""
        #wa = WhatsappMediaClient(self.sendReceipts, timeout = float('Inf'))
        wa = WhatsappMediaClient(self.sendReceipts, timeout = 5)

        wa.presenceSendAvailable()
        wa.login(self.username, self.password)

    def send_presence_unavailable(self):
        """docstring for presence_send_unavailable"""
        #wa = WhatsappMediaClient(self.sendReceipts, timeout = float('Inf'))
        wa = WhatsappMediaClient(self.sendReceipts, timeout = 5)

        wa.presenceSendUnavailable()
        wa.login(self.username, self.password)

    def get_group_info(self):
        """Gets information about a whatsapp group"""
        wa = WhatsappGroupClient(keepAlive = True, sendReceipts = True)

        wa.getGroupInfo((jid,))
        wa.login(self.username, self.password)

    def upload_media(self, mediaPath):

        wa = WhatsappMediaClient(sendReceipts = True)

        wa.login(self.username, self.password)
        wa.uploadMedia(mediaPath)



if __name__ == "__main__":
    
    bot = madbotapi()
#    bot.read_messages() # Read unread messages sent to madbot, think of making this a generator
#    bot.send_message("919790744316", "Checking if send works")
    mediaPath = "/home/dobby/.config/variety/Downloaded/Desktoppr/10164.jpg"
    bot.upload_media(mediaPath)

    usersFile = os.path.join(parentdir, 'users.json') # contains all registered users/grps

    # trying to create a users.json
    bot.get_group_info("919790744316-1391169216")
    #
    try:
        with open(usersFile, 'r') as userInfo:
            users = json.load(userInfo)
    except IOError:
        #        raise IOError("Couldn't find users.json")
        pass

    readMsgs = [] # holds msgs with #tags
    while bot.unreadMsges: # process messages
        msgDict = bot.unreadMsges.pop()
        #if msgDict["jid"] in users:
        print msgDict["msg"], msgDict["jid"], msgDict["msgId"], msgDict["wantsReceipt"]
        tags = re.findall('#[a-zA-Z0-9]+', msgDict["msg"])
        if tags:
            readMsgs.append({"tags": tags, "jid" : msgDict["jid"], "msg" : msgDict["msg"]})
        else:
            tags = re.findall('#', msgDict['msg']) # finds a # with no tag e.g. msg = "Hello # how are you?"
            if tags:
                readMsgs.append({"tags": ["#"], "jid" : msgDict["jid"], "msg" : msgDict["msg"]})

    dbFile = os.path.join(parentdir, 'messages.json')\

    if os.path.isfile(dbFile):
        try: # Read all data
            with open(dbFile, 'r') as feed:
                data = json.load(feed)
        except IOError:
            print "Unable to open JSON file"

        try: # append new data and write all to file
            with open(dbFile, 'w') as feed:
                data.extend(readMsgs)
                json.dump(data, feed)
        except IOError:
            print "unable to append to JSON file"
    else: # initialize and feed data
        try:
            with open(dbFile, 'w') as feed:
                json.dump(readMsgs, feed)
        except IOError:
            print "unable to create new file"

#    bot.send_presence_available()
#    bot.set_status("Hello World")
#    bot.send_presence_unavailable()

    #wa = WhatsappListenerClient(False)
    # with sendReceipt = True messages are sent back from server only once
    # bot.set_profile_pic(("/home/dobby/.config/variety/Downloaded/wallbase_leaves",))
    #wa.login(self.username, self.password)
    #bot.set_status("Hacking! :D")
