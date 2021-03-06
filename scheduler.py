#!/usr/bin/env
# -*- coding: utf-8 -*-
from __future__ import print_function

# Lines In Space (LIS) scheduler
# Requires rclone with a configured 'remote', defined below.
# By James Gilbert (@labjg); feel free to take, use, fix, hack etc.
# Designed to be run every 24 hours as a cron job. Example crontab entry:
# 0 0 * * * python3 /home/user/lines-in-space/scheduler.py > /dev/null 2>&1

import os
import glob
import random
import streaker
import time
import pub

REMOTE_NAME = 'dropbox'
REMOTE_DIR_ROOT = 'Apps/lines_in_space/images/'
LOCAL_DIR_ROOT = '/home/pi/lines-in-space/images/'
TODO_DIR = 'in/todo/'
DONE_DIR = 'in/done/'
OUT_DIR = 'out/'

verbose = False


def filename_check(path_in):
    # If a file path exists, return a valid one with an appended number.
    path_out = path_in
    path_split = os.path.splitext(path_in)
    if os.path.isfile(path_out):
        if verbose: print("Appending number to existing filename...")
        i = 2
        while os.path.isfile(path_out):
            path_out = path_split[0] + (' %i'%i) + path_split[1]
            i += 1
    return path_out


# Check the required local directories exist
if not os.path.exists(LOCAL_DIR_ROOT+TODO_DIR+'/vertical'):
    if verbose: print("Creating non-existent 'todo' directory...")
    os.makedirs(LOCAL_DIR_ROOT+TODO_DIR+'/vertical')
if not os.path.exists(LOCAL_DIR_ROOT+TODO_DIR+'/horizontal'):
    if verbose: print("Creating non-existent 'todo' directory...")
    os.makedirs(LOCAL_DIR_ROOT+TODO_DIR+'/horizontal')

if not os.path.exists(LOCAL_DIR_ROOT+DONE_DIR+'/vertical'):
    if verbose: print("Creating non-existent 'done' directory...")
    os.makedirs(LOCAL_DIR_ROOT+DONE_DIR+'/vertical')
if not os.path.exists(LOCAL_DIR_ROOT+DONE_DIR+'/horizontal'):
    if verbose: print("Creating non-existent 'done' directory...")
    os.makedirs(LOCAL_DIR_ROOT+DONE_DIR+'/horizontal')

if not os.path.exists(LOCAL_DIR_ROOT+OUT_DIR+'/vertical'):
    if verbose: print("Creating non-existent 'out' directory...")
    os.makedirs(LOCAL_DIR_ROOT+OUT_DIR+'/vertical')
if not os.path.exists(LOCAL_DIR_ROOT+OUT_DIR+'/horizontal'):
    if verbose: print("Creating non-existent 'out' directory...")
    os.makedirs(LOCAL_DIR_ROOT+OUT_DIR+'/horizontal')

# Sync the LIS Dropbox to get any new source images.
try:
    if verbose: print("Syncing source images...")
    os.system('rclone sync'
              + ' ' + REMOTE_NAME
              + ':' + REMOTE_DIR_ROOT+TODO_DIR
              + ' ' + LOCAL_DIR_ROOT+TODO_DIR )
except Exception as e:
    if verbose: print(e)

# Everything from this point is contingent on there being new source images
# available, and whether the selected image is processed successfully.
try:
    # We see whether there are any source images available for processing. If
    # so, one is picked at random, processed, and saved.
    if verbose: print("Listing source images todo...")
    infileList = glob.glob(LOCAL_DIR_ROOT+TODO_DIR+'**/*.jpg')
    infilePath = random.choice(infileList)
    if verbose: print("Selected image is", infilePath)
    infileDir = os.path.split(infilePath)[0]
    infileName = os.path.split(infilePath)[1]
    infileSub = os.path.split(infileDir)[1]
    outfilePath = LOCAL_DIR_ROOT+OUT_DIR+infileSub+'/'+infileName
    outfilePath = filename_check(outfilePath)
    vertical = infileSub == 'vertical'
    if verbose: print("Vertical status is", vertical)
    if verbose: print("Processing image...")
    streaker.streak(
        infilePath,
        outfilePath,
        vertical,
        rMedian = 0,
        contrast=1.5,
        saturation=1.0,
        verbose=verbose )

    # If we get this far then the image has been successully processed and
    # saved. Now we move the source file to the 'done' folder, sync with the
    # cloud, then pick a random delay before publishing in the next 24 hours.
    if verbose: print("Moving image to done folder...")
    donePath = LOCAL_DIR_ROOT+DONE_DIR+infileSub+'/'+infileName
    donePath = filename_check(donePath)
    os.rename(infilePath, donePath)

    try:
        if verbose: print("Syncing 'out' directory...")
        os.system('rclone sync'
              + ' ' + LOCAL_DIR_ROOT+OUT_DIR
              + ' ' + REMOTE_NAME
              + ':' + REMOTE_DIR_ROOT+OUT_DIR )
        if verbose: print("Syncing 'todo' directory...")
        os.system('rclone sync'
              + ' ' + LOCAL_DIR_ROOT+TODO_DIR
              + ' ' + REMOTE_NAME
              + ':' + REMOTE_DIR_ROOT+TODO_DIR )
        if verbose: print("Syncing 'done' directory...")
        os.system('rclone sync'
              + ' ' + LOCAL_DIR_ROOT+DONE_DIR
              + ' ' + REMOTE_NAME
              + ':' + REMOTE_DIR_ROOT+DONE_DIR )
    except Exception as e:
        if verbose: print(e)

    randelay = random.randint(0,60*60*24)
    if verbose: print("Random delay is %i s (%f h)" % (randelay,randelay/3600))
    time.sleep(randelay)

    title = os.path.splitext(infileName)[0]

    try:
        if verbose: print("Publishing to Twitter...")
        pub.tweet_image(outfilePath, title)
    except Exception as e:
        if verbose: print(e)

except Exception as e:
    if verbose: print(e)

