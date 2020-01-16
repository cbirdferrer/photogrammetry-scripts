#---------------------------------------------------------------
#gui_collating_alloptions_v3.0.py
#this script collates measurements from individual csv outputs of
#the morphometriX GUI
#the csvs can be saved either all in one folder or within each individual
#animals folder.
#this version includes a safety net that recalculates the measurement using
#accurate altitude and focal lengths that the user must provie in csvs.
# this version uses PyQt5 instead of easygui (used in v2.0)
#created by: Clara Bird (clara.birdferrer#gmail.com), August 2019
#----------------------------------------------------------------

#import modules
import pandas as pd
import numpy as np
import os, sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'close box to end script'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

        #ask how csvs are saved
        items = ('Individual Folders', 'One Folder')
        option, okPressed = QInputDialog.getItem(self, "Option","Saved Where", items, 0, False)
        if okPressed and option:
            print(option)

        #ask if they want safey net
        items = ('yes', 'no')
        safety, okPressed = QInputDialog.getItem(self,"Safety?", "On or Off?",items,0,False)
        if okPressed and safety:
            print(safety)


        #ask if they want body Volume
        items = ('yes','no')
        volchoice, okPressed = QInputDialog.getItem(self, 'Do you want body volume to be calculated? (you have to have measured Total_Length widths)','',items,0,False)
        if okPressed and volchoice:
            print(volchoice)

        if volchoice == 'yes':
            l, okPressed = QInputDialog.getText(self, "Lower Bound","Lower Bound:", QLineEdit.Normal, "")
            if okPressed and l != '':
                lower= int(l)
                print(lower)
            u, okPressed = QInputDialog.getText(self, "Upper Bound","Upper Bound:", QLineEdit.Normal, "")
            if okPressed and u != '':
               upper = int(u)
               print(upper)
            i, okPressed = QInputDialog.getText(self, "Interval","Interval:", QLineEdit.Normal, "")
            if okPressed and i != '':
                interval = int(i)
                print(interval)
        elif volchoice == 'no':
            pass

        #animal id list?
        items = ('yes','no')
        idchoice, okPressed = QInputDialog.getItem(self, "do you want output to only contain certain individuals?",'use animal id list?',items,0,False)
        if idchoice and okPressed:
            print(idchoice)
        if idchoice == 'yes':
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            idsCSV, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;csv files (*.csv)", options=options)
            if idsCSV:
                print(idsCSV)
        elif idchoice == 'no':
            pass

        #ask for name of output
        outname, okPressed = QInputDialog.getText(self, "output name",'name',QLineEdit.Normal,"")

        constants = ['Image ID', 'Image Path', 'Focal Length', 'Altitude', 'Pixel Dimension', 'Notes']

        if safety == 'yes':
            if option == 'Individual Folders':
                INDfold = QFileDialog.getExistingDirectory(None, "folder containing individual folders")
                saveFold = QFileDialog.getExistingDirectory(None,"folder where output should be saved")
                options = QFileDialog.Options()
                options |= QFileDialog.DontUseNativeDialog
                safe_csv, _ = QFileDialog.getOpenFileName(self,"img list w/ altitudes and focal lengths", "","All Files (*);;csv files (*.csv)", options=options)

                dfList = pd.read_csv(safe_csv,sep = ",")
                #print(dfList)

                #make lists
                measurements = []
                nonPercMeas = []
                csvs = []

                #loop through individual folders and make list of GUI output csvs
                files = os.listdir(INDfold)
                for i in files:
                    fii = os.path.join(INDfold,i)
                    f = os.path.isdir(fii)
                    if f == True:
                        clist = os.listdir(fii)
                        for ii in clist:
                            if ii.endswith('.csv'):
                                iii = os.path.join(fii,ii)
                                csvs += [iii]

                def anydup(l): #we'll use this function later to check for duplicates
                    seen = set()
                    for x in l:
                        if x in seen: return True
                        seen.add(x)
                    return False

                #here we loop through all csvs to extract all the possible measurement names
                for f in csvs:
                    temp = pd.read_csv(f, sep = '^', header = None, prefix = 'X')
                    df0 = temp.X0.str.split(',',expand = True)
                    idx = df0.loc[df0[0]=='Object'].index #find the row number of 'Object'
                    df = pd.read_csv(f,sep= ',', header = idx[0]) #use row num to skip the right number of rows
                    #print(df)
                    widths = df.columns.values.tolist()

                    l = df['Object'].tolist() #make a list of all measurement names in this column
                    l = [x for x in l if pd.isna(x) == False] #eliminate all empty cells
                    l = [x for x in l if x not in constants and x != 'Object'] #get rid of second Object

                    measurements = measurements + l #add the measurement names to the master list
                    nonPercMeas = nonPercMeas + l #copy of the master list that does not include widths

                    df = df.set_index('Object')

                    if anydup(l) == True: #check for any duplicate measurement names, if exists, exit code, print error msg
                        print("please check file {0} for duplicate Objects and remove duplicates".format(f))
                        sys.exit("remove duplicate and run script again")
                    elif anydup(l) == False:
                        print(f)
                        for i in l: #loop through list of measurement types
                            for w in (w for w in widths if w[0].isdigit()): #loop through the widths
                                x = df.loc[i,w] #extract cell value of width of measurement type
                                if pd.isna(x) == False: #if the cell isn't empty
                                    ww = i + "-" + w #combine the names
                                    measurements += [ww] #add this combined name to the master list

                #now we're going to set up a dictionary to fill in with all the measurements
                #that we will eventually turn into a dataframe where the keys are the columns
                rawM = measurements
                measurements += ['Image','Animal_ID','Altitude','Focal Length','PixD']
                names = ['Image','Animal_ID','Altitude','Focal Length','PixD']
                mDict = dict.fromkeys(measurements)
                keys = list(mDict.keys())

                df_all = pd.DataFrame(columns = keys)

                rawMM = set(rawM)


                for f in csvs:
                    print(f)
                    #pull the initial values i.e image, ID, alt, focal length
                    temp = pd.read_csv(f, sep = '^',header = None,prefix = 'X')
                    df0 = temp.X0.str.split(',',expand = True)
                    idx = df0.loc[df0[0]=='Object'].index #find the row number of 'Object'

                    df = pd.read_csv(f,sep = ",", header = None, nrows = idx[0])

                    aID = os.path.split(os.path.split(f)[0])[1]
                    mDict['Animal_ID'] = aID
                    #df = df.set_index([0])
                    image = os.path.split(df[df[0] == 'Image Path'].loc[:,1].values[0])[1]
                    print(image)
                    #print(image)
                    mDict['Image'] = image
                    #print(df)
                    alt = float((df[df[0] == 'Altitude'].loc[:,[1]].values[0])[0])
                    mDict['Altitude'] = alt

                    focl = float((df[df[0] == 'Focal Length'].loc[:,[1]].values[0])[0])
                    mDict['Focal Length'] = focl

                    pixd = float((df[df[0] == 'Pixel Dimension'].loc[:,[1]].values[0])[0])
                    mDict['PixD'] = pixd

                    #get the true values of focal length and altitude to use when recalculating
                    df_L = dfList.groupby('Image').first().reset_index()
                    alt_act = df_L[df_L.Image == image].loc[:,'Altitude'].values[0]
                    foc_act = float(df_L[df_L.Image == image].loc[:,'Focal_Length'].values[0])

                    #go into the cvs to look for the values
                    dfGUI = pd.read_csv(f, sep = ",", header = idx[0])
                    dfGUI = dfGUI.set_index('Object')

                    for key in keys: #loop through the keys aka future column headers
                        if key in nonPercMeas: #if that key is in the list of measurement types (not widths)
                            if key in dfGUI.index: #if that key (measurement) is in this csv
                                x = float(dfGUI.loc[key,'Length (m)']) #extract the measurement value using location
                                #print(key,x)
                                # now is the time to do the back calculations
                                pixc = (x/pixd)*(focl/alt) #back calculate the pixel count
                                #print(pixc)
                                xx = ((alt_act/foc_act)*pixd)*pixc #recalculate using the accurate focal length and altitude
                                #print(xx)
                            else: #if this key is not in the csv
                                xx = np.nan
                            mDict[key] = xx #add the value to the respective key
                        elif "%" in key and key.split("-")[0] in dfGUI.index: #if the key is a width
                            row = key.split("-")[0] #split the name of the measurement
                            col = key.split("-")[1] #to get the row and column indices
                            y = dfGUI.loc[row,col] #to extract the measurement value
                            #recalculate using accurate focal length and altitude
                            pixc = (y/pixd)*(focl/alt) #back calculate the pixel count
                            yy = ((alt_act/foc_act)*pixd)*pixc #recalculate using the accurate focal length and altitude
                            mDict[key] = yy
                        elif key not in dfGUI.index and key not in names:
                            mDict[key] = np.nan


                    df_op = pd.DataFrame(data = mDict,index=[1]) #make dictionary into dataframe
                    #df_all = pd.merge(df_all,df_op,on=['Image'])
                    df_all = pd.concat([df_all,df_op],sort = True)

                df_all = df_all.drop(columns = ['Altitude','Focal Length','PixD']).replace(np.nan,0)
                df_all = df_all.groupby(['Animal_ID','Image']).sum().reset_index()
                print(df_all)
                #calculate body volume
                df_all.columns = df_all.columns.str.replace(".00%", ".0%")
                #10% and 5%
                #10% first
                if volchoice == 'yes':
                    body_name = "Body_Vol_{0}%".format(interval)
                    volm = []
                    for x in range(lower,(upper + interval), interval):
                        xx = "Total_Length-{0}.0%".format(str(x))
                        volm += [xx]
                    print(volm)
                    vlist = []
                    for i in volm:
                        #print(i)
                        for ii in df_all.columns:
                            #print(ii)
                            if i in ii:
                                vlist += [ii]
                    #print(vlist)
                    ids = []
                    vs = []
                    imgs = []
                    for i,j in enumerate(vlist[:-1]):
                        jj = vlist[i+1]
                        #print(df_all[j])
                        for rr, RR, hh,anid,img in zip(df_all[j],df_all[jj], df_all['Total_Length'],df_all['Animal_ID'],df_all['Image']):
                            ph = float(interval)/float(100)
                            h = float(hh)*ph
                            #print(r)
                            r = float(rr)/float(2)
                            R = float(RR)/float(2)
                            v1 = (float(1)/float(3))*(math.pi)*h*((r**2)+(r*R)+(R**2))
                            #print(v1)
                            ids += [anid]
                            vs += [v1]
                            imgs += [img]

                    d = {'Animal_ID':ids, body_name:vs, 'Image':imgs}
                    df = pd.DataFrame(data = d)
                    #print(df)
                    df1 = df.groupby(['Animal_ID','Image']).sum().reset_index()

                    df_all1 = pd.merge(df_all,df1,on = ['Animal_ID','Image'])
                elif volchoice == 'no':
                    df_all1 = df_all
                print(df_all1)
                #sort cols
                cols = list(df_all1)
                a = "AaIiTtEeJjRrBbFfWwCcDdGgHhKkLlMmNnOoPpQqSsUuVvXxYyZz" #make your own ordered alphabet
                col = sorted(cols, key=lambda word:[a.index(c) for c in word[0]]) #sort headers based on this alphabet
                df_all1 = df_all1.ix[:,col] #sort columns based on sorted list of column header

                outcsv = os.path.join(saveFold,"{0}_allIDs.csv".format(outname))
                df_all1.to_csv(outcsv,sep = ',')

                if idchoice == 'yes':
                    df_ids = pd.read_csv(idsCSV,sep = ',')
                    idList = df_ids['Animal_ID'].tolist()
                    df_allx = df_all1[df_all1['Animal_ID'].isin(idList)]

                    outidcsv = os.path.join(saveFold,"{0}_IDS.csv".format(outname))
                    df_allx.to_csv(outidcsv,sep = ',')
                elif idchoice == 'no':
                    pass

                print("done, close GUI window to end script")
            elif option == 'One Folder':
                GUIfold = QFileDialog.getExistingDirectory(None, "folder containing GUI outputs")
                saveFold = QFileDialog.getExistingDirectory(None,"folder where output should be saved")
                options = QFileDialog.Options()
                options |= QFileDialog.DontUseNativeDialog
                safe_csv, _ = QFileDialog.getOpenFileName(self,"img list w/ altitudes and focal lengths", "","All Files (*);;csv files (*.csv)", options=options)

                dfList = pd.read_csv(safe_csv, sep = ",")
                #print(dfList)

                files = os.listdir(GUIfold)
                measurements= []
                nonPercMeas = []

                def anydup(l): #we'll use this function later to check for duplicates
                    seen = set()
                    for x in l:
                        if x in seen: return True
                        seen.add(x)
                    return False

                for f in (f for f in files if f.endswith('.csv')):
                    ff = os.path.join(GUIfold,f)
                    temp=pd.read_csv(ff,sep='^',header=None,prefix='X')
                    df0=temp.X0.str.split(',',expand=True)
                    idx = df0.loc[df0[0] == 'Object'].index
                    df = pd.read_csv(ff, sep = ',', header = idx[0])

                    widths = df.columns.values.tolist()

                    l = df['Object'].tolist()
                    l = [x for x in l if pd.isna(x) == False] #eliminate all empty cells
                    l = [x for x in l if x not in constants and x != 'Object'] #get rid of extra instances of Object


                    measurements = measurements + l #add the measurement names to the master list
                    nonPercMeas = nonPercMeas + l #copy of the master list that does not include widths

                    df = df.set_index('Object')

                    if anydup(l) == True: #check for any duplicate measurement names, if exists, exit code, print error msg
                        print("please check file {0} for duplicate Objects and remove duplicates".format(f))
                        sys.exit("remove duplicate and run script again")
                    elif anydup(l) == False:
                        print(f)
                        for i in l: #loop through list of measurement types
                            for w in (w for w in widths if w[0].isdigit()): #loop through the widths
                                x = df.loc[i,w] #extract cell value of width of measurement type
                                if pd.isna(x) == False: #if the cell isn't empty
                                    ww = i + "-" + w #combine the names
                                    measurements += [ww] #add this combined name to the master list

                #now we're going to set up a dictionary to fill in with all the measurements
                #that we will eventually turn into a dataframe where the keys are the columns
                rawM = measurements
                measurements += ['Image','Animal_ID','Altitude','Focal Length','PixD']
                names = ['Image','Animal_ID','Altitude','Focal Length','PixD']
                mDict = dict.fromkeys(measurements)
                keys = list(mDict.keys())

                df_all = pd.DataFrame(columns = keys)

                rawMM = set(rawM)


                for f in (f for f in files if f.endswith('.csv')):
                    print(f)
                    fil = os.path.join(GUIfold,f)
                    #pull the initial values i.e image, ID, alt, focal length
                    temp=pd.read_csv(fil,sep='^',header=None,prefix='X')
                    df0=temp.X0.str.split(',',expand=True)
                    idx = df0.loc[df0[0]=='Object'].index
                    df = pd.read_csv(fil,sep = ',', header = None, nrows = idx[0])

                    image = os.path.split((df[df[0] == 'Image Path'].loc[:,[1]].values[0])[0])[1]
                    print(image)
                    mDict['Image'] = image
                    #print(df)
                    aID = (df[df[0] == 'Image ID'].loc[:,[1]].values[0])[0]
                    mDict['Animal_ID'] = aID

                    alt =  float((df[df[0] == 'Altitude'].loc[:,[1]].values[0])[0])
                    mDict['Altitude'] = alt

                    focl = float((df[df[0] == 'Focal Length'].loc[:,[1]].values[0])[0])
                    mDict['Focal Length'] = focl

                    pixd =  float((df[df[0] == 'Pixel Dimension'].loc[:,[1]].values[0])[0])
                    mDict['PixD'] = pixd

                    #get the true values of focal length and altitude to use when recalculating
                    df_L = dfList.groupby('Image').first().reset_index()
                    # df_L = df_L.set_index('Image')
                    alt_act = df_L[df_L.Image == image].loc[:,'Altitude'].values[0]
                    foc_act = float(df_L[df_L.Image == image].loc[:,'Focal_Length'].values[0])


                    #print(foc_act)
                    #print(alt_act)
                    #print(pixd)

                    #go into the cvs to look for the values

                    dfGUI = pd.read_csv(fil, sep = ',', header = idx[0])
                    dfGUI = dfGUI.set_index('Object')

                    for key in keys: #loop through the keys aka future column headers
                        if key in nonPercMeas: #if that key is in the list of measurement types (not widths)
                            if key in dfGUI.index: #if that key (measurement) is in this csv
                                x = float(dfGUI.loc[key,'Length (m)']) #extract the measurement value using location
                                #print(key,x)
                                # now is the time to do the back calculations
                                pixc = (x/pixd)*(focl/alt) #back calculate the pixel count
                                #print(pixc)
                                xx = ((alt_act/foc_act)*pixd)*pixc #recalculate using the accurate focal length and altitude
                                #print(xx)
                                #just the thing for the time we had to divide by 2 for a few images
                                #print(div)
                            else: #if this key is not in the csv
                                xx = np.nan
                            mDict[key] = xx #add the value to the respective key
                        elif "%" in key and key.split("-")[0] in dfGUI.index: #if the key is a width
                            print(key)
                            row = key.split("-")[0] #split the name of the measurement
                            col = key.split("-")[1] #to get the row and column indices
                            y = dfGUI.loc[row,col] #to extract the measurement value
                            print(y)
                            #recalculate using accurate focal length and altitude
                            pixc = (y/pixd)*(focl/alt) #back calculate the pixel count
                            yy = ((alt_act/foc_act)*pixd)*pixc #recalculate using the accurate focal length and altitude
                            mDict[key] = yy
                        elif key not in dfGUI.index and key not in names:
                            mDict[key] = np.nan
                    df_op = pd.DataFrame(data = mDict,index=[1]) #make dictionary into dataframe
                    #df_all = pd.merge(df_all,df_op,on=['Image'])
                    df_all = pd.concat([df_all,df_op],sort = True)
                df_all = df_all.drop(columns = ['Altitude','Focal Length','PixD']).replace(np.nan,0)
                df_all = df_all.groupby(['Animal_ID','Image']).sum().reset_index()
                #calculate body volume
                df_all.columns = df_all.columns.str.replace(".00%", ".0%")
                print(df_all)
                #10% and 5%
                #10% first

                if volchoice == 'yes':
                    body_name = "Body_Vol_{0}%".format(interval)
                    volm = []
                    for x in range(lower,(upper + interval), interval):
                        xx = "Total_Length-{0}.0%".format(str(x))
                        volm += [xx]

                    vlist = []
                    for i in volm:
                        #print(i)
                        for ii in df_all.columns:
                            #print(ii)
                            if i in ii:
                                vlist += [ii]
                    #print(vlist)
                    ids = []
                    vs = []
                    imgs = []
                    for i,j in enumerate(vlist[:-1]):
                        jj = vlist[i+1]
                        #print(df_all[j])
                        for rr, RR, hh,anid,img in zip(df_all[j],df_all[jj], df_all['Total_Length'],df_all['Animal_ID'],df_all['Image']):
                            ph = float(interval)/float(100)
                            h = float(hh)*ph
                            #print(r)
                            r = float(rr)/float(2)
                            R = float(RR)/float(2)
                            v1 = (float(1)/float(3))*(math.pi)*h*((r**2)+(r*R)+(R**2))
                            #print(v1)
                            ids += [anid]
                            vs += [v1]
                            imgs += [img]

                    d = {'Animal_ID':ids, body_name:vs, 'Image':imgs}
                    df = pd.DataFrame(data = d)
                    #print(df)
                    df1 = df.groupby(['Animal_ID','Image']).sum().reset_index()

                    df_all1 = pd.merge(df_all,df1,on = ['Animal_ID','Image'])
                elif volchoice == 'no':
                    df_all1 = df_all
                print(df_all1)
                #sort cols
                cols = list(df_all1)
                a = "AaIiTtEeJjRrBbFfWwCcDdGgHhKkLlMmNnOoPpQqSsUuVvXxYyZz" #make your own ordered alphabet
                col = sorted(cols, key=lambda word:[a.index(c) for c in word[0]]) #sort headers based on this alphabet
                df_all1 = df_all1.ix[:,col] #sort columns based on sorted list of column header



                outcsv = os.path.join(saveFold,"{0}_allIDs.csv".format(outname))
                df_all1.to_csv(outcsv,sep = ',')

                if idchoice == 'yes':
                    df_ids = pd.read_csv(idsCSV,sep = ',')
                    idList = df_ids['Animal_ID'].tolist()
                    df_allx = df_all1[df_all1['Animal_ID'].isin(idList)]

                    outidcsv = os.path.join(saveFold,"{0}_IDS.csv".format(outname))
                    df_allx.to_csv(outidcsv,sep = ',')
                elif idchoice == 'no':
                    pass
                print("done, close GUI window to end script")

        elif safety == 'no':
            if option == 'Individual Folders':
                INDfold = QFileDialog.getExistingDirectory(None, "folder containing individual folders")
                saveFold = QFileDialog.getExistingDirectory(None,"folder where output should be saved")
                #make lists
                measurements = []
                nonPercMeas = []
                csvs = []

                #loop through individual folders and make list of GUI output csvs
                files = os.listdir(INDfold)
                for i in files:
                    fii = os.path.join(INDfold,i)
                    f = os.path.isdir(fii)
                    if f == True:
                        clist = os.listdir(fii)
                        for ii in clist:
                            if ii.endswith('.csv'):
                                iii = os.path.join(fii,ii)
                                csvs += [iii]

                def anydup(l): #we'll use this function later to check for duplicates
                    seen = set()
                    for x in l:
                        if x in seen: return True
                        seen.add(x)
                    return False

                #here we loop through all csvs to extract all the possible measurement names
                for f in csvs:
                    temp = pd.read_csv(f, sep = '^', header = None, prefix = 'X')
                    df0 = temp.X0.str.split(',',expand = True)
                    idx = df0.loc[df0[0]=='Object'].index #find the row number of 'Object'
                    df = pd.read_csv(f,sep= ',', header = idx[0]) #use row num to skip the right number of rows
                    #print(df)
                    widths = df.columns.values.tolist()

                    l = df['Object'].tolist()
                    l = [x for x in l if pd.isna(x) == False and x != 'Object'] #eliminate all empty cells and extra occurences of Object

                    measurements = measurements + l #add the measurement names to the master list
                    nonPercMeas = nonPercMeas + l #copy of the master list that does not include widths

                    df = df.set_index('Object')

                    if anydup(l) == True: #check for any duplicate measurement names, if exists, exit code, print error msg
                        print("please check file {0} for duplicate Objects and remove duplicates".format(f))
                        sys.exit("remove duplicate and run script again")
                    elif anydup(l) == False:
                        print(f)
                        for i in l: #loop through list of measurement types
                            for w in (w for w in widths if w[0].isdigit()): #loop through the widths
                                x = df.loc[i,w] #extract cell value of width of measurement type
                                if pd.isna(x) == False: #if the cell isn't empty
                                    ww = i + "-" + w #combine the names
                                    measurements += [ww] #add this combined name to the master list

                #now we're going to set up a dictionary to fill in with all the measurements
                #that we will eventually turn into a dataframe where the keys are the columns
                rawM = measurements
                measurements += ['Image','Animal_ID']
                names = ['Image','Animal_ID']
                mDict = dict.fromkeys(measurements)
                keys = list(mDict.keys())

                df_all = pd.DataFrame(columns = keys)

                rawMM = set(rawM)

                for f in csvs:
                    print(f)
                    #pull the initial values i.e image, ID, alt, focal length
                    temp = pd.read_csv(f, sep = '^',header = None,prefix = 'X')
                    df0 = temp.X0.str.split(',',expand = True)
                    idx = df0.loc[df0[0]=='Object'].index #find the row number of 'Object'
                    df = pd.read_csv(f,sep = ",", header = None, nrows = idx[0])

                    aID = os.path.split(os.path.split(f)[0])[1]
                    mDict['Animal_ID'] = aID
                    image = os.path.split((df[df[0] == 'Image Path'].loc[:,[1]].values[0])[0])[1]
                    print(image)
                    mDict['Image'] = image
                    #go into the cvs to look for the values

                    dfGUI = pd.read_csv(f, sep = ",", header = idx[0])
                    dfGUI = dfGUI.set_index('Object')
                    for key in keys: #loop through the keys aka future column headers
                        if key in nonPercMeas: #if that key is in the list of measurement types (not widths)
                            if key in dfGUI.index: #if that key (measurement) is in this csv
                                x = float(dfGUI.loc[key,'Length (m)']) #extract the measurement value using location
                            else: #if this key is not in the csv
                                x = np.nan
                            mDict[key] = x#add the value to the respective key
                        elif "%" in key and key.split("-")[0] in dfGUI.index: #if the key is a width
                            row = key.split("-")[0] #split the name of the measurement
                            col = key.split("-")[1] #to get the row and column indices
                            y = dfGUI.loc[row,col] #to extract the measurement value
                            mDict[key] = y
                        elif key not in dfGUI.index and key not in names:
                            mDict[key] = np.nan


                    df_op = pd.DataFrame(data = mDict,index=[1]) #make dictionary into dataframe
                    #df_all = pd.merge(df_all,df_op,on=['Image'])
                    df_all = pd.concat([df_all,df_op],sort = True)
                print(df_all)
                df_all = df_all.replace(np.nan,0)
                df_all = df_all.groupby(['Animal_ID','Image']).sum().reset_index()
                print(df_all)
                #calculate body volume
                df_all.columns = df_all.columns.str.replace(".00%", ".0%")
                #10% and 5%
                #10% first
                if volchoice == 'yes':
                    body_name = "Body_Vol_{0}%".format(interval)
                    volm = []
                    for x in range(lower,(upper + interval), interval):
                        xx = "Total_Length-{0}.0%".format(str(x))
                        volm += [xx]
                    print(volm)
                    vlist = []
                    for i in volm:
                        #print(i)
                        for ii in df_all.columns:
                            #print(ii)
                            if i in ii:
                                vlist += [ii]
                    #print(vlist)
                    ids = []
                    vs = []
                    imgs = []
                    for i,j in enumerate(vlist[:-1]):
                        jj = vlist[i+1]
                        #print(df_all[j])
                        for rr, RR, hh,anid,img in zip(df_all[j],df_all[jj], df_all['Total_Length'],df_all['Animal_ID'],df_all['Image']):
                            ph = float(interval)/float(100)
                            h = float(hh)*ph
                            #print(r)
                            r = float(rr)/float(2)
                            R = float(RR)/float(2)
                            v1 = (float(1)/float(3))*(math.pi)*h*((r**2)+(r*R)+(R**2))
                            #print(v1)
                            ids += [anid]
                            vs += [v1]
                            imgs += [img]

                    d = {'Animal_ID':ids, body_name:vs, 'Image':imgs}
                    df = pd.DataFrame(data = d)
                    #print(df)
                    df1 = df.groupby(['Animal_ID','Image']).sum().reset_index()

                    df_all1 = pd.merge(df_all,df1,on = ['Animal_ID','Image'])
                elif volchoice == 'no':
                    df_all1 = df_all
                print(df_all1)
                #sort cols
                cols = list(df_all1)
                a = "AaIiTtEeJjRrBbFfWwCcDdGgHhKkLlMmNnOoPpQqSsUuVvXxYyZz" #make your own ordered alphabet
                col = sorted(cols, key=lambda word:[a.index(c) for c in word[0]]) #sort headers based on this alphabet
                df_all1 = df_all1.ix[:,col] #sort columns based on sorted list of column header

                outcsv = os.path.join(saveFold,"{0}_allIDs.csv".format(outname))
                df_all1.to_csv(outcsv,sep = ',')

                if idchoice == 'yes':
                    df_ids = pd.read_csv(idsCSV,sep = ',')
                    idList = df_ids['Animal_ID'].tolist()
                    df_allx = df_all1[df_all1['Animal_ID'].isin(idList)]

                    outidcsv = os.path.join(saveFold,"{0}_IDS.csv".format(outname))
                    df_allx.to_csv(outidcsv,sep = ',')
                elif idchoice == 'no':
                    pass

                print("done, close GUI window to end script")
            elif option == 'One Folder':
                GUIfold = QFileDialog.getExistingDirectory(None, "folder containing GUI outputs")
                saveFold = QFileDialog.getExistingDirectory(None,"folder where output should be saved")
                files = os.listdir(GUIfold)
                measurements= []
                nonPercMeas = []

                def anydup(l): #we'll use this function later to check for duplicates
                    seen = set()
                    for x in l:
                        if x in seen: return True
                        seen.add(x)
                    return False

                for f in (f for f in files if f.endswith('.csv')):
                    ff = os.path.join(GUIfold,f)
                    temp=pd.read_csv(ff,sep='^',header=None,prefix='X')
                    df0=temp.X0.str.split(',',expand=True)
                    idx = df0.loc[df0[0] == 'Object'].index
                    df = pd.read_csv(ff, sep = ',', header = idx[0])
                    #print("initial df")
                    #print(df)

                    widths = df.columns.values.tolist()

                    l = df['Object'].tolist()
                    l = [x for x in l if pd.isna(x) == False] #eliminate all empty cells
                    l = [x for x in l if x not in constants and x != 'Object']

                    measurements = measurements + l #add the measurement names to the master list
                    nonPercMeas = nonPercMeas + l #copy of the master list that does not include widths

                    df = df.set_index('Object')
                    #print(df)
                    if anydup(l) == True: #check for any duplicate measurement names, if exists, exit code, print error msg
                        print("please check file {0} for duplicate Objects and remove duplicates".format(f))
                        sys.exit("remove duplicate and run script again")
                    elif anydup(l) == False:
                        print(f)
                        for i in l: #loop through list of measurement types
                            for w in (w for w in widths if w[0].isdigit()): #loop through the widths
                                x = df.loc[i,w] #extract cell value of width of measurement type
                                if pd.isna(x) == False: #if the cell isn't empty
                                    ww = i + "-" + w #combine the names
                                    measurements += [ww] #add this combined name to the master list

                #now we're going to set up a dictionary to fill in with all the measurements
                #that we will eventually turn into a dataframe where the keys are the columns
                rawM = measurements
                measurements += ['Image','Animal_ID']
                names = ['Image','Animal_ID']
                mDict = dict.fromkeys(measurements)
                keys = list(mDict.keys())

                df_all = pd.DataFrame(columns = keys)

                rawMM = set(rawM)

                for f in (f for f in files if f.endswith('.csv')):
                    print(f)
                    fil = os.path.join(GUIfold,f)
                    #pull the initial values i.e image, ID, alt, focal length
                    temp=pd.read_csv(fil,sep='^',header=None,prefix='X')
                    df0=temp.X0.str.split(',',expand=True)
                    idx = df0.loc[df0[0]=='Object'].index
                    df = pd.read_csv(fil,sep = ',', header = None, nrows = idx[0])

                    image = os.path.split((df[df[0] == 'Image Path'].loc[:,[1]].values[0])[0])[1]
                    print(image)
                    mDict['Image'] = image
                    #print(df)
                    aID = df[df[0] == 'Image ID'].loc[:,[1]].values[0]
                    mDict['Animal_ID'] = aID[0]
                    #go into the cvs to look for the values
                    dfGUI = pd.read_csv(fil, sep = ',', header = idx[0])
                    dfGUI = dfGUI.set_index('Object')
                    for key in keys: #loop through the keys aka future column headers
                        if key in nonPercMeas: #if that key is in the list of measurement types (not widths)
                            if key in dfGUI.index.tolist(): #if that key (measurement) is in this csv
                                x = float(dfGUI.loc[key,'Length (m)']) #extract the measurement value using location
                            else: #if this key is not in the csv
                                x = np.nan
                            mDict[key] = x #add the value to the respective key
                        elif "%" in key and key.split("-")[0] in dfGUI.index: #if the key is a width
                            row = key.split("-")[0] #split the name of the measurement
                            col = key.split("-")[1] #to get the row and column indices
                            y = dfGUI.loc[row,col] #to extract the measurement value
                            mDict[key] = y
                        elif key not in dfGUI.index and key not in names:
                            mDict[key] = np.nan

                    df_op = pd.DataFrame(data = mDict,index=[1]) #make dictionary into dataframe
                    df_all = pd.concat([df_all,df_op],sort = True)
                df_all = df_all.replace(np.nan,0)
                df_all = df_all.groupby(['Animal_ID','Image']).sum().reset_index()
                print(df_all)
                #calculate body volume
                df_all.columns = df_all.columns.str.replace(".00%", ".0%")
                #10% and 5%
                #10% first

                if volchoice == 'yes':
                    body_name = "Body_Vol_{0}%".format(interval)
                    volm = []
                    for x in range(lower,(upper + interval), interval):
                        xx = "Total_Length-{0}.0%".format(str(x))
                        volm += [xx]

                    vlist = []
                    for i in volm:
                        #print(i)
                        for ii in df_all.columns:
                            #print(ii)
                            if i in ii:
                                vlist += [ii]
                                #print(vlist)
                    ids = []
                    vs = []
                    imgs = []
                    for i,j in enumerate(vlist[:-1]):
                        jj = vlist[i+1]
                        #print(df_all[j])
                        for rr, RR, hh,anid,img in zip(df_all[j],df_all[jj], df_all['Total_Length'],df_all['Animal_ID'],df_all['Image']):
                            ph = float(interval)/float(100)
                            h = float(hh)*ph
                            #print(r)
                            r = float(rr)/float(2)
                            print(rr,r)
                            R = float(RR)/float(2)
                            print(RR,R)
                            v1 = (float(1)/float(3))*(math.pi)*h*((r**2)+(r*R)+(R**2))
                            #print(v1)
                            ids += [anid]
                            vs += [v1]
                            imgs += [img]

                    d = {'Animal_ID':ids, body_name:vs, 'Image':imgs}
                    df = pd.DataFrame(data = d)
                    print(df)
                    df1 = df.groupby(['Animal_ID','Image']).sum().reset_index()

                    df_all1 = pd.merge(df_all,df1,on = ['Animal_ID','Image'])
                elif volchoice == 'no':
                    df_all1 = df_all
                print(df_all1)
                #sort cols
                cols = list(df_all1)
                a = "AaIiTtEeJjRrBbFfWwCcDdGgHhKkLlMmNnOoPpQqSsUuVvXxYyZz" #make your own ordered alphabet
                col = sorted(cols, key=lambda word:[a.index(c) for c in word[0]]) #sort headers based on this alphabet
                df_all1 = df_all1.ix[:,col] #sort columns based on sorted list of column header
                print(df_all1)

                outcsv = os.path.join(saveFold,"{0}_allIDs.csv".format(outname))
                df_all1.to_csv(outcsv,sep = ',')

                if idchoice == 'yes':
                    df_ids = pd.read_csv(idsCSV,sep = ',')
                    idList = df_ids['Animal_ID'].tolist()
                    df_allx = df_all1[df_all1['Animal_ID'].isin(idList)]

                    outidcsv = os.path.join(saveFold,"{0}_IDS.csv".format(outname))
                    df_allx.to_csv(outidcsv,sep = ',')
                elif idchoice == 'no':
                    pass

                print("done, close GUI window to end script")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
