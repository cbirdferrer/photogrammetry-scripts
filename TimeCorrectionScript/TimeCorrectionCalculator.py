##----------------------------------------
##TimeCorrectionCalculator.py
##tool built to calculate the correction factor needed to correct image time
## stamp time to GPS time
##
##Description: this script will pull the timestamp fromm the images where
##              a picture of the GPS time was taken. then using the GPS time
##              entered in a table by the user the script will calculate
##              the correction factor for matchups.
##
##Created January 2019
##Author: Clara Bird (clara.birdferrer@gmail.com), Duke MarineUAS
##---------------------------------------

import pandas as pd
import numpy as np
import os, sys
import PIL.Image
from datetime import datetime
from datetime import timedelta
import easygui

print(sys.version)
print(sys.path)
#import .csv with IMG and GPStime
scriptWS = easygui.diropenbox(msg = "select Time Corrections folder")
imageFold = os.path.join(scriptWS, "images")

csv = os.path.join(scriptWS, "GPStime_images.csv")
df1 = pd.read_csv(csv, sep = ',')

imgnames = []
imgtimes = []
addsub = []
img_files = os.listdir(imageFold)
for img in img_files:
    #print(img)
    if img.endswith('.JPG'):
        imgnames += [img]
        imgF = os.path.join(imageFold,img)
        image = PIL.Image.open(imgF)
        exif_data = image._getexif()
        dt = exif_data[36867]
        print(dt)
        imgtime = dt[11:]
        imgtimes += [imgtime]

d = {'ImageName':imgnames, 'ImageTime': imgtimes}
dfI = pd.DataFrame(data = d)

df = df1.set_index('ImageName').join(dfI.set_index('ImageName')).reset_index()
df = df.dropna()
timecorrs = []
for time, gpst in zip (df['ImageTime'], df['GPStime']):
    time = str(time)
    print(time)
    time = time.split(":")
    imagetime = timedelta(hours = int(time[0]), minutes = int(time[1]), seconds = int(time[2]))
    gpst = str(gpst).split(":")
    gpstime = timedelta(hours = int(gpst[0]), minutes = int(gpst[1]), seconds = int(gpst[2]))
    if gpstime >= imagetime:
        corr = gpstime - imagetime
        corr = str(corr)
        cr = corr
        timecorrs += [cr]
        AS = "ADD"
        addsub += [AS]
    if gpstime < imagetime:
        corr = imagetime - gpstime
        corr = str(corr)
        cr = corr
        timecorrs += [cr]
        AS = "SUB"
        addsub += [AS]


df['TimeChange'] = timecorrs
df['AddSub'] = addsub
print(df)
file = os.path.join(scriptWS, "TimeCorrections.csv")
df.to_csv(file, sep=',')
