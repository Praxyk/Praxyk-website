#!/usr/bin/python
import sys 
import os

user = os.path.expanduser("~")
sys.path.insert(0, user+'/praxyk-website-live/')
sys.path.insert(0, user+'/praxyk-website-live/praxyk-dot-com')
sys.path.insert(0, user+'/praxyk-api-live/api/praxyk-dot-com/app')

from app import *
from app import app as application

