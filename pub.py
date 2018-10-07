#!/usr/bin/env
# -*- coding: utf-8 -*-
from __future__ import print_function

# Lines In Space (LIS) publisher
# Publish processed images on the web.
# By James Gilbert (@labjg); feel free to take, use, fix, hack etc.

import tweepy
from credentials import *

def twitter_auth():
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    return tweepy.API(auth)

def tweet_image(imPath, imTitle):
    api = twitter_auth()
    api.update_with_media(
        filename=imPath,
        status=imTitle )
