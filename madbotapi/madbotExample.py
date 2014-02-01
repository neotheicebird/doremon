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
"""
if __name__ == "__main__":
    username = '919790744316'
    password = 'dCyse6Ukq54kL6t88FjurE0F380='
    cl = cmdclient.WhatsappCmdClient(username)
    cl.login(username, password)
"""




