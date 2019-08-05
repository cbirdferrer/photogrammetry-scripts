##perday_imgdata.py
## most recently updated: 05/10/2019
## created by: Clara Bird (clara.bird@duke.edu)
##
## this script extracts laser altitude, barometer altitude, and GPS coordinates
##  from the flight logs for the alta and lemhex for the time at which each
##  image was taken
##
## to use there are two user inputs that should be written in the command line
## 1. the path to the date aircraft folder
## 2. the aircraft: current options are alta or lemhex

#import modules
import pandas as pd
import numpy as np
import os, sys
import xml.etree.ElementTree
import argparse
import PIL.Image
from datetime import datetime
from datetime import timedelta
import easygui

# # setting up the user input args
# parser = argparse.ArgumentParser(description = 'manage flight imagery and logs')
# parser.add_argument('filepath', metavar = 'fp', type = str,
#                         help = "file path to the date_aircraft folder")
# parser.add_argument('aircraft_type', metavar = 'ac', type = str,
#                         help = "aircraft type used")
#
# args = parser.parse_args()
# scriptWS = args.filepath
# aircraft = args.aircraft_type
# print("filepath:{0}".format(scriptWS))
# print("aircraft is {0}".format(aircraft))

easygui.msgbox(msg = "the next window will ask you to select the date_aircraft folder, hit the button to continue", title = "hello!", ok_button = "OK")
scriptWS = easygui.diropenbox(msg = "date_aircraft folder")

msg = "select aircraft type"
title = "Aircraft Type"
choices = ['alta', 'lemhex']
aircraft = easygui.choicebox(msg,title,choices)

#set up folders
rootWS = os.path.dirname(scriptWS)
day_aircraft = os.path.split(scriptWS)[1]

#make lists
AllImgList = []
ImgList = [] #this list will contain all the image names
ImgTime = [] #this list will contain the original image time stamp
CorrTimeList = [] #this list will contain the corrected image time stamps
LaserList = [] #this list will contain the laser altitudes
LaserImg = [] #the image that the laser was pulled for
Time130List = [] #if the laser value was pulled from a different time, which time
BaroImg = [] #the image that the barometer was pulled for
BaroList = [] #the barometer altitudes
LatList = [] #the latitudes
LonList = [] #the longitudes
DAFlist = []

#read in time correction csv
TCcsv = os.path.join(rootWS, "TimeCorrections.csv")
dfTimeCorr = pd.read_csv(TCcsv, sep = ',')
dfTimeCorr = dfTimeCorr.dropna(axis = 0, how = 'any')

#make list of date_aircraft prefixes and add as a column
day_ac  = []
for i in dfTimeCorr['Flight']:
    out = i.split("_")
    ii = out[0] + "_" + out[1]
    day_ac += [ii]
dfTimeCorr['date_aircraft'] = day_ac

#make a list of the time correction values w/o : and add as column
correction = []
for i in dfTimeCorr['TimeChange']:
    ii = str(i)
    iii = ii.replace(":","")
    correction += [iii]
dfTimeCorr['TimeCorrection'] = correction

#take the flights and convert to a format that we can use to make a list of
#flight folders to go into
day_flights = []
for d, f in zip(dfTimeCorr['date_aircraft'], dfTimeCorr['Flight']):
    if d == day_aircraft:
        ff = f.split("_")[2]
        if len(ff) == 2:
            f_num = str("0" + ff[1:])
        elif len(ff) > 2:
            f_num = str(ff[1:])
        day_flights += [f_num]

#use aircraft argument to go into the loop for either lemhex or alta
if aircraft == 'lemhex':
    for i in day_flights:
        flight = "Flight_" + i #set up name of the flight folder
        FlightFold = os.path.join(scriptWS, flight)
        n = i[-1]
        daf = day_aircraft + "_F" + n
        print("FLIGHT FOLDER IS")
        print(FlightFold)
        for dd, tc, addsub in zip(dfTimeCorr['Flight'], dfTimeCorr['TimeChange'], dfTimeCorr['AddSub']):
            if dd == daf:
                timecorr = str(tc)
                SonyFold = os.path.join(FlightFold, "Sony") #go into the image folder for that flight
                img_files = os.listdir(SonyFold)
                print("number of image files = {0}".format(len(img_files)))
                for image_name in img_files: #loop through every image in the folder
                    if image_name.endswith(".JPG") and image_name[0].isdigit():
                        print(image_name)
                        AllImgList += [image_name]
                        imgF = os.path.join(SonyFold,image_name)
                        #extract the time stamp from the metadata
                        img = PIL.Image.open(imgF)
                        exif_data = img._getexif()
                        dt = exif_data[36867]
                        imgtime = dt[11:]
                        #format the times into timedelta
                        imgT = imgtime.split(":")
                        timeC = timecorr.split(":")
                        timestamp = timedelta(hours = int(imgT[0]), minutes = int(imgT[1]), seconds = int(imgT[2]))
                        timecorrecting = timedelta(hours = int(timeC[0]), minutes = int(timeC[1]), seconds = int(timeC[2]))
                        #add or subtract the time correction
                        if addsub == "ADD":
                            correctedtime = timestamp + timecorrecting
                            correctedtime = str(correctedtime)
                        if addsub == "SUB":
                            correctedtime = timestamp - timecorrecting
                            correctedtime = str(correctedtime)
                        print("img time = {0}, corrected time = {1}".format(timestamp, correctedtime))
                        #go into the flight log folder where the GPX is stored
                        LogFold = os.path.join(FlightFold,"Flight_Logs")
                        LogFiles = os.listdir(LogFold)
                        for log in LogFiles:
                            if log.endswith(".GPX"):
                                log = os.path.join(LogFold,log)
                                root = xml.etree.ElementTree.parse(log).getroot()
                                alt_collection = root[1][1]
                                for alt_point in alt_collection.findall('trkpt'):
                                    time = alt_point.find('time').text
                                    time = time[11:19]
                                    tt = str(time).split(":")
                                    timeGPX = timedelta(hours = int(tt[0]), minutes = int(tt[1]), seconds = int(tt[2]))
                                    gpxtime = str(timeGPX)
                                    # GPXtime = []
                                    # GPXtime += [gpxtime]
                                    # print(GPXtime)
                                    # if correctedtime in GPXtime:
                                    #print(correctedtime)
                                    if gpxtime == correctedtime:
                                        ImgList += [image_name]
                                        ImgTime += [timestamp]
                                        CorrTimeList += [correctedtime]
                                        # if time in list of time from timecorrection.csv
                                        print("found it!!!")

                                        #pull lat and lon
                                        lat = alt_point.attrib['lat']
                                        LatList += [lat]
                                        lon = alt_point.attrib['lon']
                                        LonList += [lon]

                                        #pull laser
                                        extensions = alt_point.find("extensions")
                                        laser = extensions.find('Laser').text
                                        laser = float(laser)
                                        #if the laser is 130 (error) it will look 5 seconds above and below the image time
                                        #looking for a non-130 value. if it finds one it will use that value and also
                                        #show the time that the value was taken from
                                        if laser == 130:
                                            #make window that is 5 seconds before and after image time
                                            tm = timedelta(hours = int(time[:2]), minutes = int(time[3:5]), seconds = int(time[6:8]))
                                            upperbound = tm + timedelta(seconds = 5)
                                            lowerbound = tm - timedelta(seconds = 5)
                                            windowtime = []
                                            windowlaser = []
                                            windowtimediff = []
                                            for alt_point in alt_collection.findall('trkpt'):
                                                time = alt_point.find('time').text
                                                time = time[11:19]
                                                tt = str(time).split(":")
                                                timeGPX = timedelta(hours = int(tt[0]), minutes = int(tt[1]), seconds = int(tt[2]))
                                                gpxtime = str(timeGPX)
                                                if timeGPX >= lowerbound and timeGPX <= upperbound:
                                                    windowtime += [timeGPX]
                                                    windowlaser += [laser]
                                                    timediff = abs(timeGPX - tm)
                                                    windowtimediff += [timediff]
                                                d = {'time': windowtime, 'timediff': windowtimediff, 'laser': windowlaser}
                                                df_window = pd.DataFrame(data=d)
                                                df_window = df_window.drop(df_window[df_window.laser == 130.000].index)
                                                if df_window.empty == True: #if all the values were 130
                                                    laser = "130*"
                                                    time130 = gpxtime
                                                    LaserList+=[laser]
                                                    Time130List += [time130]
                                                    LaserImg +=[image_name]
                                                else: #if theres a non-130 use the closest value in time for the laser
                                                    values = df_window.loc[df_window['timediff'].idxmin()]
                                                    time130 = values['time']
                                                    laser = str(values['laser']) + "*"
                                                    LaserList += [laser]
                                                    Time130List += [time130]
                                                    LaserImg +=[image_name]
                                        elif laser != 130:
                                            time130 = np.nan
                                            LaserList += [laser]
                                            Time130List += [time130]
                                            LaserImg +=[image_name]
                                        elif laser == False:
                                            no = "noLaser"
                                            LaserList += [no]
                                            Time130List += [no]
                                            LaserImg += [image_name]

                                        #pull the barometer altitude
                                        baroalt = extensions.find('Altimeter').text
                                        b = baroalt.split(',', 1)[0]
                                        baroalt = float(b)
                                        barolem = baroalt/20
                                        BaroList += [barolem]
                                        BaroImg += [image_name]

    #making dataframes from the lists and merging them, didn't make one big one because of problems
    #with lengths not lining up
    #print(len(ImgList), len(ImgTime), len(CorrTimeList), len(BaroList), len(LatList), len(LonList))
    # print(len(AllImgList))
    df_imglist = pd.DataFrame(data ={'Image': AllImgList} )

    # print(df_imglist)
    d = {'Image': ImgList, 'ImgTime': ImgTime, 'CorrectedTime': CorrTimeList, 'BaroAlt': BaroList, 'Lat': LatList, 'Lon': LonList}
    df_most = pd.DataFrame(data=d)
    df_most = df_most.groupby('Image').first().reset_index()
    df_1 = df_imglist.merge(df_most, on = 'Image', how = 'left').replace(np.nan, 'imgmissingfromlog', regex = True)
    #print(len(LaserImg), len(LaserList), len(Time130List))
    dl = {"Image": LaserImg, "LaserAlt": LaserList, 'Time130':Time130List}
    df_las = pd.DataFrame(data = dl)
    df_las = df_las.groupby('Image').first().reset_index()
    print(df_las)
    df_measurements = df_1.merge(df_las, on = 'Image', how = 'left').replace(np.nan, 'notinlog', regex = True)

    # dd = {'Image':ImgList, 'ImgTime': ImgTime, 'CorrectedTime': CorrTimeList, 'BaroAlt': BaroList, 'LaserAlt': LaserList, 'Time130': Time130List, 'Lat':LatList, 'Lon': LonList }
    # print(len(ImgList), len(ImgTime), len(CorrTimeList), len(BaroList), len(LaserList), len(Time130List), len(LatList), len(LonList))
    # df_all = pd.DataFrame(data = dd, columns = ['Image', 'ImgTime', 'CorrectedTime', 'BaroAlt', 'LaserAlt', 'Time130', 'Lat', 'Lon'])
    # print(df_all)


    # df_measurements = df_img.set_index('Image').join(df_las.set_index('Image'), lsuffix = "_m", rsuffix = '_l').reset_index()
    # df_measurements1 = df_measurements.set_index('Image').join(df_baro.set_index('Image'), lsuffix = "_l", rsuffix = '_a').reset_index()
    # df_measurements = df_measurements1.groupby(['Image']).first().reset_index()
    #print(df_measurements)
    filename = "ImageAltitudes_{0}.csv".format(day_aircraft)
    file = os.path.join(scriptWS, filename)
    df_measurements.to_csv(file, sep = ',')
    #save in photogrammetry matchup folder
    filenm = os.path.join(rootWS, "PhotogrammetryMatchup", "ImageAltitudes_{0}.csv".format(day_aircraft))
    df_measurements.to_csv(filenm, sep=',')

elif aircraft == 'alta':
    for i in day_flights:
        flight = "Flight_" + i
        FlightFold = os.path.join(scriptWS, flight)
        n = i[-1]
        daf = day_aircraft + "_F" + n
        for dd, tc, addsub in zip(dfTimeCorr['Flight'], dfTimeCorr['TimeChange'], dfTimeCorr['AddSub']): #loops through time correction sheet which is essenially looping through by flight
            if dd == daf:
                timecorr = str(tc)
                SonyFold = os.path.join(FlightFold,"Sony") #go into the image folder for that flight
                img_files = os.listdir(SonyFold)
                for image_name in img_files: #loop through every image in the folder
                    if image_name.endswith(".JPG") and image_name[0].isdigit():
                        #add the image name and date aircraft flight to their lists
                        ImgList += [image_name]
                        print(image_name)
                        DAFlist += [daf]
                        imgF = os.path.join(SonyFold,image_name)
                        #extract the time stamp from the metadata
                        img = PIL.Image.open(imgF)
                        exif_data = img._getexif()
                        dt = exif_data[36867]
                        imgtime = dt[11:]
                        #format the timestamps into timedelta
                        imgT = imgtime.split(":")
                        timeC = timecorr.split(":")
                        timestamp = timedelta(hours = int(imgT[0]), minutes = int(imgT[1]), seconds = int(imgT[2]))
                        timecorrecting = timedelta(hours = int(timeC[0]), minutes = int(timeC[1]), seconds = int(timeC[2]))
                        #add or subtract the correction
                        if addsub == "ADD":
                            correctedtime = timestamp + timecorrecting
                            correctedtime = str(correctedtime)
                        if addsub == "SUB":
                            correctedtime = timestamp - timecorrecting
                            correctedtime = str(correctedtime)
                        correctedtime = str(datetime.time(datetime.strptime(correctedtime, '%H:%M:%S')))
                        #add original image time and corrected time to sheet
                        ts = str(datetime.time(datetime.strptime(str(timestamp), '%H:%M:%S')))
                        ImgTime += [ts]
                        CorrTimeList += [correctedtime]
                        #now go into the Flight Log folder for the flight to get the barometer data
                        LogFold = os.path.join(FlightFold,"Flight_Logs") #if the flight log folder is named differently edit that here
                        LogFiles = os.listdir(LogFold)
                        l = len(LogFiles)
                        if len == 0: #if there is no csv in the folder
                            nobaro = "nobarofile"
                            BaroList += [nobaro]
                        else:
                            for log in LogFiles:
                                if log.endswith('.csv') and ".DS_Store" not in log and log[0].isalpha():
                                    logfile = os.path.join(LogFold, log)
                                    firstrow = pd.read_csv(logfile, nrows=0)
                                    fr = str(firstrow)
                                    if len(firstrow.columns) == 1:
                                        #read in just the first row of the file to look a headers
                                        #print(logfile)
                                        df = pd.read_csv(logfile, nrows = 0, skiprows = 10, dtype = str)
                                        #something is wrong with how the baro alt column is named so
                                        ##looped through column names to pull the corresponding index values
                                        for i in df:
                                            if i == "GPS Time":
                                                gps_idx = df.columns.get_loc(i)
                                            if i.startswith("Baro A"):
                                                baro_idx = df.columns.get_loc(i)
                                        df_baro = pd.read_csv(logfile, sep = ',', usecols = [gps_idx, baro_idx], skiprows = 10, dtype = str)
                                        df_baro.columns = ['GPS_Time', 'Baro_Alt'] #rename columns
                                        df_baro = df_baro.groupby(['GPS_Time'])['Baro_Alt'].first().reset_index() #only use first instance of timestamp
                                        if correctedtime in df_baro['GPS_Time'].values:
                                            print('yay baro!')
                                            for time, baro in zip(df_baro['GPS_Time'], df_baro['Baro_Alt']):
                                                if time == correctedtime:
                                                    BaroList += [baro]
                                        elif correctedtime not in df_baro['GPS_Time'].values:
                                            print('no time in baro')
                                            baro = "ImgTimeNotInTable"
                                            BaroList += [baro]

                                    else: #if there is only one column and the file is weird
                                        bad = "badbarofile"
                                        BaroList += [bad]

                        #now go into Laser Altimeter folder to extract laser data
                        LaserFold = os.path.join(FlightFold,"Laser_Altimeter")
                        LaserFiles = os.listdir(LaserFold)
                        if len(LaserFiles) == 0: #if there are no files then make the values "nolaserfile"
                            nolaser = "nolaserfile"
                            LaserList += [nolaser]
                            ImgTime += [timestamp]
                            Time130List += [nolaser]
                            LatList += [nolaser]
                            LonList += [nolaser]
                        elif len(LaserFiles) > 0:
                            for file in LaserFiles:
                                #if there are multiple laser files and you only want one, add an idenifier heres
                                if ".DS_Store" not in file:
                                    laserfile = os.path.join(LaserFold,file)
                                    #read in csv
                                    df_laser = pd.read_csv(laserfile, sep = ",", names = ["loopCounter", "curr_buffer", "curr_length", "loopBackIntCnt", "externalTrigIntCnt","Time",
                                                                                       "ValidAok", "Latt", "NS", "Long", "EW", "Speedkts", "TrueCourse","Date","Variation", "EtWt",
                                                                                        "CheckSum", "Altimeter", "Alt1", "Alt2", "Alt3", "Alt4", "Alt5", "Alt6", "Alt7", "Alt8",
                                                                                        "Alt9", "Alt10", "Alt11", "Alt12", "Alt13", "Alt14", "Alt15", "Alt16", "Alt17", "Alt18",
                                                                                       "Alt19", "Alt20", "Alt21", "Alt22", "Alt23", "Alt24", "Alt25", "Alt26", "Alt27", "Alt28",
                                                                                       "Alt29", "Alt30","Alt31", "Alt32", "Alt33", "Alt34", "Alt35", "Alt36", "Alt37", "Alt38",
                                                                                       "Alt39", "Alt40", "Alt41", "Alt42", "Alt43", "Alt44", "Alt45", "Alt46", "Alt47", "Alt48"])
                                    df_laser = df_laser.drop([0])
                                    dfl = df_laser.filter(regex='Alt') #select for columns that include with "Alt"
                                    dfl = dfl.drop(['Altimeter'], axis = 1)

                                    df_laser['MedianAlt'] =  dfl.median(axis=1, skipna = True) #calculate the median of all the alt values
                                    df_laser['TimeT'] = df_laser['Time'].astype(str).str[:6]
                                    corrtime = correctedtime.replace(":","")
                                    tv = df_laser['TimeT'].values
                                    if len(tv) > 0:
                                        #print(len(tv))
                                        if corrtime in tv:
                                            print (corrtime)
                                            print('yay, laser!')
                                            for time, laser, lat, lon in zip(df_laser['TimeT'], df_laser['MedianAlt'], df_laser["Latt"], df_laser["Long"]):
                                                if time == corrtime:
                                                    print('hooray!')
                                                    #pull latitude and longitude
                                                    lat = lat
                                                    lon = lon
                                                    LatList += [lat]
                                                    LonList += [lon]

                                                    #if the laser is 130 (error) it will look 5 seconds above and below the image time
                                                    #looking for a non-130 value. if it finds one it will use that value and also
                                                    #show the time that the value was taken from
                                                    if laser == 130:
                                                        tm = timedelta(hours = int(time[:2]), minutes = int(time[2:4]), seconds = int(time[4:6]))
                                                        upperbound = tm + timedelta(seconds = 5)
                                                        lowerbound = tm - timedelta(seconds = 5)
                                                        windowtime = []
                                                        windowlaser = []
                                                        windowtimediff = []
                                                        #make window of 5 seconds above and below image timestamp
                                                        for t, laser in zip(df_laser['Time'],df_laser['MedianAlt']):
                                                            if "." not in t:
                                                                t = timedelta(hours = int(t[:2]), minutes = int(t[2:4]), seconds = int(t[4:6]))
                                                                if t >= lowerbound and t <= upperbound:
                                                                    windowtime += [t]
                                                                    windowlaser += [laser]
                                                                    timediff = abs(t - tm)
                                                                    windowtimediff += [timediff]
                                                                else:
                                                                    continue
                                                            else:
                                                                continue
                                                        d = {'time': windowtime, 'timediff': windowtimediff, 'laser': windowlaser}
                                                        df_window = pd.DataFrame(data=d)
                                                        #drop all rows where laser is still 130
                                                        df_window = df_window.drop(df_window[df_window.laser == 130.000].index)
                                                        if df_window.empty == True: #if all the values were 130 then laser is 130
                                                            laser = "130*"
                                                            time130 = np.nan
                                                            LaserList += [laser]
                                                            Time130List +=[time130]
                                                        else: #if there was a non 130 then pull the value closest in time to the image
                                                            values = df_window.loc[df_window['timediff'].idxmin()]
                                                            time130 = values['time']
                                                            time130 = (str(time130))[-8:]
                                                            las130 = values['laser']
                                                            las130 = str(las130)
                                                            laser = las130 + "*"
                                                            LaserList += [laser]
                                                            Time130List +=[time130]
                                                    elif laser != 130: #if the laser isn't 130 then add that value
                                                        time130 = np.nan
                                                        LaserList += [laser]
                                                        Time130List += [time130]
                                                else:
                                                    continue
                                        elif corrtime not in tv:
                                            print(corrtime)
                                            print('no laser time')
                                            nottable = "ImgTimeNotInTable"
                                            time130 = np.nan
                                            LaserList += [nottable]
                                            Time130List += [time130]
                                            LatList += [nottable]
                                            LonList += [nottable]
                                    else:
                                        continue
                                else:
                                    continue
                        else:
                            continue
    print(len(ImgList), len(BaroList), len(LaserList))
    #print(LaserList)
    dd = {'Image':ImgList, 'ImgTime': ImgTime, 'CorrectedTime': CorrTimeList, 'BaroAlt': BaroList, 'LaserAlt': LaserList, 'Time130': Time130List, 'Lat':LatList, 'Lon': LonList }
    df_all = pd.DataFrame(data = dd, columns = ['Image', 'ImgTime', 'CorrectedTime', 'BaroAlt', 'LaserAlt', 'Time130', 'Lat', 'Lon'])


    csv = os.path.join(scriptWS, "ImageAltitudes_{0}.csv".format(day_aircraft))
    df_all.to_csv(csv, sep = ',')

    file = os.path.join(rootWS, "PhotogrammetryMatchup", "ImageAltitudes_{0}.csv".format(day_aircraft))
    df_all.to_csv(file, sep=',')

else:
    print("incorrect aircraft type, current options are lemhex or alta")
