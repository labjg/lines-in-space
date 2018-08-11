#!/usr/bin/env
# -*- coding: utf-8 -*-
from __future__ import print_function

# Lines In Space (LIS) scheduler
# Designed to be run every 24 hours with cron.
# Requires rclone with a configured remote, defined below.
# By James Gilbert (@labjg) 2018-08; feel free to take, use, fix, hack etc.

import os
import glob

REMOTE_NAME = 'dropbox'
REMOTE_DIR = 'Apps/lines_in_space/images/'
LOCAL_DIR = '/home/pi/lines_in_space/images/'
TODO_DIR = 'in/todo/'
DONE_DIR = 'in/done/'
OUT_DIR = 'out/'

# The first thing to do is sync the LIS Dropbox to get any new source images.
try:
    os.system('rclone -v sync'
              + ' ' + REMOTE_NAME
              + ':' + REMOTE_DIR + TODO_DIR
              + ' ' + LOCAL_DIR + TODO_DIR )
except:
    pass

# Next, we see whether there are any source images available for processing.
# If so, one is picked at random, processed, and saved.
try:
    infileList = glob.glob(LOCAL_DIR + TODO_DIR + '*.jpg')
except:
    pass

# Next, a random hour of day is generated:
