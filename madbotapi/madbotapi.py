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

from Yowsup.Registration.v2.existsrequest import WAExistsRequest as WAExistsRequestV2
from Yowsup.Registration.v2.coderequest import WACodeRequest as WACodeRequestV2
from Yowsup.Registration.v2.regrequest import WARegRequest as WARegRequestV2
from Yowsup.Contacts.contacts import WAContactsSyncRequest

import threading,time, base64
from collections import deque

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

        Debugger.enabled = False

        self.phoneNumber = phoneNumber
        self.jid = "%s@s.whatsapp.net" % phoneNumber
        self.sendReceipts = True # Auto ack flag
        self.username = login
        self.password = password
        self.keepAlive = keepAlive

        self.unreadMsges = deque()

        connectionManager = YowsupConnectionManager()
        connectionManager.setAutoPong(keepAlive)
        connectionManager.jid = self.jid
        self.methodsInterface = connectionManager.getMethodsInterface() # used
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
        status = (status,)
        self.methodsInterface.call("profile_setStatus", status)


if __name__ == "__main__":
    bot = madbotapi()
    bot.read_messages()

    readMsgs = [] # past tense
    while bot.unreadMsges:
        msgDict = bot.unreadMsges.pop()
        print msgDict["msg"], msgDict["jid"], msgDict["msgId"], msgDict["wantsReceipt"]

        if msgDict["wantsReceipt"]:
            readMsgs.append((msgDict["jid"], msgDict["msgId"]))

    #wa = WhatsappListenerClient(False)
    # with sendReceipt = True messages are sent back from server only once
    # bot.set_profile_pic(("/home/dobby/.config/variety/Downloaded/wallbase_leaves",))
    #wa.login(self.username, self.password)
    #bot.set_status("Hacking! :D")
