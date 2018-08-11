#!/usr/bin/env
# -*- coding: utf-8 -*-
from __future__ import print_function

# Streaker
# By James Gilbert (@labjg) 2017-10; feel free to take, use, fix, hack etc.

import sys, getopt
from PIL import Image, ImageEnhance
from scipy import ndimage
import numpy as np


def imStreak(im, vertStreak=False, rMedian=0):
    
    imArr = np.array(im)

    if not vertStreak:
        #A single column of pixel values - will be 'wiped' sideways later:
        pxVals = np.zeros((imArr.shape[0],imArr.shape[2]))
        #Calculate the average pixel value of every row:
        for y in range(pxVals.shape[0]):
            pxVals[y,:] = np.mean(imArr[y,:], axis=0)
    else:
        #A single row of pixel values - will be 'wiped' downwards later:
        pxVals = np.zeros((imArr.shape[1],imArr.shape[2]))
        #Calculate the average pixel value of every column:
        for x in range(pxVals.shape[0]):
            pxVals[x,:] = np.mean(imArr[:,x], axis=0)

    #Apply a median filter if specified:
    if rMedian > 0:
        #Check the median mask isn't too big for the image:
        if rMedian > (pxVals.shape[0]-1):
            print("Median mask size reduced from %i to %i due to image size" % (rMedian, pxVals.shape[0]-1))
            rMedian = pxVals.shape[0] - 1
        #Create a padded array, mirroring the px values:
        size_padded = (pxVals.shape[0]+(2*rMedian), pxVals.shape[1])
        pxVals_padded = np.zeros(size_padded)
        pxVals_padded[rMedian:size_padded[0]-rMedian] = pxVals
        for r in range(rMedian):
            pxVals_padded[r] = pxVals[rMedian-r]
            pxVals_padded[size_padded[0]-1-r] = pxVals[pxVals.shape[0]-1-rMedian+r]
        #Calculate the median values:
        for i in range(pxVals.shape[0]):
            pxVals[i,:] = np.median(pxVals_padded[i:i+(2*rMedian)+1,:], axis=0)
        
    #'Wipe' the pixel values across the whole image:
    if not vertStreak:
        for y in range(pxVals.shape[0]):
            imArr[y,:] = pxVals[y]
    else:
        for x in range(pxVals.shape[0]):
            imArr[:,x] = pxVals[x]

    return Image.fromarray(imArr)

def imSetContrast(im, val=1.0):
    if val > 1.0:
        enh = ImageEnhance.Contrast(im)
        return enh.enhance(val)
    else:
        return im

def imSetSaturation(im, val=1.0):
    if val > 1.0:
        enh = ImageEnhance.Color(im)
        return enh.enhance(val)
    else:
        return im


argv = sys.argv[1:]

infile = "photo.jpg"    #Default input filename
outfile = "out.jpg"     #Default output filename
imRotateAngle = None         #Default image rotation (can be 90, 180, 270)
rMedian = 30            #Default radius for median filter mask
imContrast = 1.5        #Default contrast (1.0 is no change)
imSaturation = 1.0      #Default saturation (1.0 is no change)
vertStreak = False      #Streak is horizontal by default

print('0')

try:
    opts, args = getopt.getopt(argv,"hi:o:r:m:c:s:v",["help","infile=","outfile=","rotate=","median=","contrast=","saturation=","vertical"])
except getopt.GetoptError:
    print("streaker.py -i <infile> -o <outfile> [-r <imRotateAngle> -m <rMedian> -c <contrast> -s <saturation> -v]")
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print("streaker.py -i <infile> -o <outfile> [-v]")
        sys.exit()
    elif opt in ("-i", "--infile"):
        infile = arg
    elif opt in ("-o", "--outfile"):
        outfile = arg
    elif opt in ("-r", "--rotate"):
        if arg == '0':
            imRotateAngle = None
        elif arg == '90':
            imRotateAngle = Image.ROTATE_90
        elif arg == '180':
            imRotateAngle = Image.ROTATE_180
        elif arg == '270':
            imRotateAngle = Image.ROTATE_270
        else:
            print("Warning: invalid image rotation")
    elif opt in ("-m", "--median"):
        rMedian = int(arg)
    elif opt in ("-c", "--contrast"):
        imContrast = float(arg)
    elif opt in ("-s", "--saturation"):
        imSaturation = float(arg)
    elif opt in ("-v", "--vertical"):
        vertStreak = True

print('1')

im_in = Image.open(infile)

print('2')

if imRotateAngle != None:
    im_in = im_in.transpose(imRotateAngle)

print('3')
im_out = imStreak(im_in, vertStreak, rMedian)
print('4')
im_out = imSetContrast(im_out, imContrast)
print('5')
im_out = imSetSaturation(im_out, imSaturation)
print('6')

im_out.save(outfile)
