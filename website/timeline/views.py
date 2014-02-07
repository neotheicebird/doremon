from django.shortcuts import render
from django.http import HttpResponse, Http404

# Create your views here.

def home(request):
    return HttpResponse("Hello world")

def tags(request):
    """draws a page where all known tags are displayed as links"""
    return HttpResponse("tags page")

def filter_tags(request, tag):
    return HttpResponse("tag: %s's page" % tag)

