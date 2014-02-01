import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print parentdir

sys.path.insert(0, os.path.join(os.path.join(os.path.join(parentdir, "yowsup"), "src"), ""))
#print os.path.join(os.path.join(os.path.join(parentdir, "yowsup"), "src"), "Yowsup")
import Yowsup
sys.path.remove( os.path.join(os.path.join(os.path.join(parentdir, "yowsup"), "src"), ""))
Yowsup.
