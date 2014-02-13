from django.shortcuts import render
from django.http import HttpResponse, Http404

from django.template import Template, Context, loader
#from website.templates import

import os
import json

# Create your views here.
"""
MSG_FILEPATH = os.path.join(
               os.path.dirname(
               os.path.dirname(
               os.path.dirname(os.path.abspath(__file__)))),
               "messages.json")
"""
MSG_FILEPATH = "/home/dobby/Projects/madbot/messages.json" # Hardcoded for testing

def home(request):
    t = loader.get_template('home.html')
#    t = Template('website/templates/home.html')
    c = Context()
    r = t.render(c)
    return HttpResponse(r)

def tags(request):
    """draws a page where all known tags are displayed as links"""
    tags = extract_tags()
    tags = [tag[1:] for tag in tags] # Removing the # from a '#tag'

    t = loader.get_template('tags.html')
    c = Context({
        'tags': tags,
        })
    r = t.render(c)
    return HttpResponse(r)

def filter_tags(request, tag):
    messages = extract_msgs(tags = [tag,])

    if not messages:
        raise Http404

    # edit jids
    for msg in messages:
        msg["jid"] = msg["jid"].split("@")[0] # wonder if this is the best way to do this??

    t = loader.get_template('filteredMsgs.html')
    c = Context({
        'ideas': messages,
        })
    r = t.render(c)
    return HttpResponse(r)

def extract_msgs(tags = [], filepath = MSG_FILEPATH):
    """Reads the messages.json file and retreives all messages containing the
       given set of tags, tags = [] is a special case, it retreives all the
       messages in the dataset
    """
    with open(filepath, 'r') as fp:
        messages = json.load(fp)

    if tags == []:
        return messages

    extract = [msg for msg in messages
                   if any( '#' + req_tag == msg_tag
                   for req_tag in tags
                   for msg_tag in msg["tags"] ) ]

    return extract

# TODO extract_msgs is made keeping in mind a multi-tag search for ideas
# Try to implement a view for that and way to add that to the UI

def extract_tags(filepath = MSG_FILEPATH):
    """extract tags from messages.json"""

    with open(filepath, 'r') as fp:
        messages = json.load(fp)

    seen = set() # finding unique tags
    seen_add = seen.add
    extract = [tag for msg in messages
                   for tag in msg["tags"]
                   if tag not in seen and not seen_add(tag)]

    return extract
