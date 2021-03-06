import os, sys
import pandas as pd
import numpy as np
import xml.etree.ElementTree
import argparse
import PIL.Image
from datetime import datetime
from datetime import timedelta
import easygui

# print("VERSION")
# print(sys.version)

num = []
images = []
whales = []

imagenames = []
whaleids = []
image_time = []
cor_time = []
dafs = []
dates = []
Laser = []
Time130 = []
Baro = []

#get photogrammetry script as input
scriptWS = easygui.diropenbox(msg = "select PhotogrammetryMatchup folder")
csvname = easygui.enterbox(msg = "enter name of Image List that is in Photogrammetry Matchup Folder")
inputcsv = os.path.join(scriptWS,csvname)
#print(scriptWS)

#f = os.path.join(scriptWS, "ImageList.csv")
dfTL = pd.read_csv(inputcsv, sep = ',')
#print(dfTL.columns)
print("image list read in")
dfTL = dfTL.drop(['Individual'],axis=1)
for dateflight in dfTL['Image']:
	dateflight = str(dateflight)
	date = dateflight[:8]
	name = str(date)
	dates += [name]
dfTL['date_ac'] = dates
dfTL = dfTL.dropna(axis = 0, how = 'any')

dfDates = dfTL.groupby(['date_ac']).first().reset_index()
#print(dfDates)
print("matching up altitudes to image list")
for i in dfDates['date_ac']:
	if i[0].isdigit():
	    for image, whale in zip(dfTL['Image'], dfTL['Whale_ID']):
                dtfl = str(dateflight)
                d = image[:8]
                csv = os.path.join(scriptWS, ("ImageMeasurements_{0}.csv".format(i)))
                dfM = pd.read_csv(csv, sep = ',')
                #print(d)
                #print(i)
                if d == i:
                    images += [image]
                for img in images:
                    for image, time, correctedtime, las, time130, baro in zip(dfM['Image'],dfM['ImgTime'], dfM['CorrectedTime'], dfM['LaserAlt'], dfM['Time130'], dfM['BaroAlt']):
                        if image == img:
                            imagenames += [img]
                            #print(image)
                            tt = time[7:15]
                            image_time += [time]
                            cor_time += [correctedtime]
                            Laser += [las]
                            #time130 = time[7:15]
                            Time130 += [time130]
                            Baro += [baro]

print("making dataframe")
dat = { 'Image' : imagenames, 'Img_Time': image_time, 'CorrectedTime': cor_time, 'LaserAlt': Laser, 'Time130': Time130, 'BaroAlt': Baro}
#print(len(whaleids), len(image_names), len(image_time), len(cor_time), len(Laser), len(Time130), len(Baro))
df_a = pd.DataFrame(data = dat)
df_all = dfTL.set_index('Image').join(df_a.set_index('Image'), lsuffix='_TL', rsuffix='_TL').reset_index()
df_all = df_all.groupby('Image').first().reset_index()
#print(df_all)

dfWhales = pd.read_csv(inputcsv, sep = ",")
#print(dfWhales)
target_cols = ['Image', 'BaroAlt', 'LaserAlt', 'Time130']
df_final = dfWhales.merge(df_all[target_cols], on = 'Image', how = 'left')
#print(df_final)
name = csvname.split(".")[0]
#print(name)
file = os.path.join(scriptWS, "{0}_imageAltitudes.csv".format(name))
df_final.to_csv(file, sep = ",")
print("file {0} created".format(file))
print("done")
                                     
