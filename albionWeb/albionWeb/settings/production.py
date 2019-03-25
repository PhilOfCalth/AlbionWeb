from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*'] #["ec2-*.eu-west-1.compute.amazonaws.com"] # or ['*']

STATIC_URL = 'https://s3-eu-west-1.amazonaws.com/albionstatic/'