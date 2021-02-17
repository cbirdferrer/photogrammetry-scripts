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
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox, QLabel, QVBoxLayout
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

        #add message box with link to github documentation
        msgBox = QMessageBox()
        msgBox.setWindowTitle("For detailed input info click link below")
        msgBox.setTextFormat(QtCore.Qt.RichText)
        msgBox.setText('<a href = "https://github.com/cbirdferrer/collatrix#inputs">CLICK HERE</a> for detailed input instructions, \n then click on OK button to continue')
        x = msgBox.exec_()

        #do you want the Animal ID to be assigned based on the name of the folder
        items = ('yes', 'no')
        anFold, okPressed = QInputDialog.getItem(self,"Input #1", "Do you want the Animal ID to be assigned based on the name of the folder? \n yes or no",items,0,False)
        if okPressed and anFold:
            print("{0} Animal ID in folder name".format(anFold))

        #ask if they want safey net
        items = ('yes', 'no')
        safety, okPressed = QInputDialog.getItem(self,"Input #2", "Do you want to use the safety? \n Yes or No?",items,0,False)
        if okPressed and safety:
            print("{0} safety".format(safety))
        #if safety yes, ask for file
        if safety == 'yes':
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            safe_csv, _ = QFileDialog.getOpenFileName(self,"2.1 Safety File: Image list with altitudes and other information.", "","All Files (*);;csv files (*.csv)", options=options)
            print("safety csv = {0}".format(safe_csv))
        elif safety == 'no':
            pass

        #animal id list?
        items = ('no','yes')
        idchoice, okPressed = QInputDialog.getItem(self, "Input #3", "Do you want output to only contain certain individuals? \n Yes or No?",items,0,False)
        if idchoice and okPressed:
            print("{0} subset list".format(idchoice))
        if idchoice == 'yes':
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            idsCSV, _ = QFileDialog.getOpenFileName(self,"3.1 File containing ID list", "","All Files (*);;csv files (*.csv)", options=options)
            if idsCSV:
                print("ID list file = {0}".format(idsCSV))
        elif idchoice == 'no':
            pass

        #ask for name of output
        outname, okPressed = QInputDialog.getText(self, "Input #4", "Prefix for output file",QLineEdit.Normal,"")

        #import safety csv if safety selected
        if safety == 'yes':
            dfList = pd.read_csv(safe_csv, sep = ",")
            dfList = dfList.dropna(how="all",axis='rows').reset_index()
            df_L = dfList.groupby('Image').first().reset_index()
            df_L['Image'] = [x.strip() for x in df_L['Image']]
        elif safety == 'no':
            df_L = "no safety"

        #get folders
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        GUIfold = QFileDialog.getExistingDirectory(None, "Input 5. Folder containing MorphoMetriX outputs",options=options)
        saveFold = QFileDialog.getExistingDirectory(None,"Input 6. Folder where output should be saved",options = options)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog


        #make lists
        #for csvs
        csvs_all = []
        csvs = []
        not_mmx = []
        #for measurements
        measurements = []
        nonPercMeas = []

        #walk through all folders in GUI folder and collect all csvs
        for root,dirs,files in os.walk(GUIfold):
            csvs_all += [os.path.join(root,f) for f in files if f.endswith('.csv')]
        #make sure the csvs are morphometrix outputs by checking first row
        csvs += [c for c in csvs_all if 'Image ID' in pd.read_csv(c,nrows=1,header=None)[0].tolist()]
        #make list of all csvs that were not morphometrix csvs to tell user
        not_mmx += [x for x in csvs if x not in csvs_all]
        print("these csvs were not morphometrix outputs: {0}".format(not_mmx))

        #check for csvs that (for whatever reason) hit an error when being read in.
        #makes a list of those csvs for users to examine
        badcsvs = []
        for f in csvs:
            try:
                temp=pd.read_csv(f,sep='^',header=None,prefix='X',engine = 'python',quoting=3, na_values = ['""','"']) #read in csv as one column
            except:
                print(f)
                badcsvs += [f]
                pass
        badcsvs = set(badcsvs)
        csvs = [x for x in csvs if x not in badcsvs]

        #put together dataframe of inputs and error csvs to output
        if safety == 'yes':
            message = "Animal ID from folder name?: {0} \n\nThe safety file was: {1}\n\n\nThese csvs were not morphometrix outputs:{2}\n\nThese csvs could not be read in: {3}".format(anFold, safe_csv, not_mmx, badcsvs)
        elif safety == 'no':
            message = "Animal ID from folder name?: {0} \n\nSafety not used\n\n\nThese csvs were not morphometrix outputs:{1}\n\nThese csvs could not be read in: {2}".format(anFold, not_mmx, badcsvs)

        mess = pd.DataFrame(data={'Processing Notes':message},index=[1])
        mess_out = os.path.join(saveFold,"{0}_processing_notes.txt".format(outname))
        mess.to_csv(mess_out)

        #set up list of constants

        constants = ['Image ID', 'Image Path', 'Focal Length', 'Altitude', 'Pixel Dimension', 'Notes']

        def anydup(l): #we'll use this function later to check for duplicates
            seen = set()
            for x in l:
                if x in seen: return True
                seen.add(x)
            return False

        def readfile(f):
            temp=pd.read_csv(f,sep='^',header=None,prefix='X',engine = 'python',quoting=3, na_values = ['""','"']) #read in csv as one column
            df00=temp.X0.str.split(',',expand=True) #split rows into columns by delimeter
            df00 = df00.replace("",np.nan)
            df0 = df00.dropna(how='all',axis = 'rows').reset_index(drop=True)
            return df0

        for ff in csvs:
            df0 = readfile(ff)
            idx = df0.loc[df0[0] == 'Object Name'].index #find index (row) values of 'Object'
            df = df0.truncate(before=idx[0]) #take subset of df starting at first row containing Object
            head = df.iloc[0]
            df = df[1:]
            df.columns = head

            widths = df.columns.values.tolist()

            l = df['Object Name'].tolist()
            l = [x for x in l if pd.isna(x) == False] #eliminate all empty cells
            l = [x for x in l if x not in constants]
            if 'Object Name' in l: l.remove('Object Name') #get rid of second instance of object name

            measurements = measurements + l #add the measurement names to the master list
            nonPercMeas = nonPercMeas + l #copy of the master list that does not include widths

            df = df.set_index('Object Name')
            df = df.replace('nan', np.nan, regex=True)

            if anydup(l) == True: #check for any duplicate measurement names, if exists, exit code, print error msg
                print("please check file {0} for duplicate Object Names and remove duplicates".format(f))
                sys.exit("remove duplicate and run script again")
            elif anydup(l) == False:
                print(f)
                for i in l: #loop through list of measurement types
                    for w in (w for w in widths if w[0].isdigit()): #loop through the widths
                        x = df.loc[i,w] #extract cell value of width of measurement type
                        if pd.isna(x) == False: #if the cell isn't empty
                            ww = i + "_" + w #combine the names
                            measurements += [ww] #add this combined name to the master list
                        else: pass

        #now we're going to set up a dictionary to fill in with all the measurements
        #that we will eventually turn into a dataframe where the keys are the columns
        rawM = measurements
        measurements += ['Image','Animal_ID','Altitude','Focal Length','PixD']
        names = ['Image','Animal_ID','Altitude','Focal Length','PixD']
        mDict = dict.fromkeys(measurements)
        keys = list(mDict.keys())

        #now make list and dictionary for pixel count dataframe
        measurements_pixc = ["{0}.PixCount".format(x) if x not in names else x for x in measurements]
        mDict_pixc = dict.fromkeys(measurements_pixc)
        keys_pixc = list(mDict_pixc.keys())

        #make an empty dataframe with the headers being the measurement types/info to pull
        df_all = pd.DataFrame(columns = keys)
        df_all_pixc = pd.DataFrame(columns = keys_pixc)

        rawMM = set(rawM)

        for f in csvs:
            print(f)
            #pull the initial values i.e image, ID, alt, focal length
            df0 = readfile(f)
            idx = df0.loc[df0[0]=='Object Name'].index #set object column to index
            df = df0.truncate(after=idx[0]) #subset df to be only top info section

            if anFold == 'yes':
                aID = os.path.split(os.path.split(f)[0])[1] #extract animal ID
            elif anFold == 'no':
                aID = df[df[0] == 'Image ID'].loc[:,[1]].values[0] #pull animal id
                aID = aID[0]
            mDict['Animal_ID'] = aID; mDict_pixc['Animal_ID'] = aID

            image = os.path.split(df[df[0] == 'Image Path'].loc[:,1].values[0])[1] #extract image
            print(image)
            mDict['Image'] = image; mDict_pixc['Image'] = image

            alt = float((df[df[0] == 'Altitude'].loc[:,[1]].values[0])[0]) #extract entered altitude
            mDict['Altitude'] = alt; mDict_pixc['Altitude'] = alt

            focl = float((df[df[0] == 'Focal Length'].loc[:,[1]].values[0])[0]) #extract entered focal length
            mDict['Focal Length'] = focl; mDict_pixc['Focal Length'] = focl

            pixd = float((df[df[0] == 'Pixel Dimension'].loc[:,[1]].values[0])[0]) #extract entered pixel dimension
            mDict['PixD'] = pixd; mDict_pixc['PixD'] = pixd

            notes = df[df[0] == 'Notes'].loc[:,[1]].values[0] #extract entered notes
            mDict['Notes'] = notes[0]; mDict_pixc['Notes'] = notes

            if safety == 'yes': #pull the altitude, focal length, and pix d from the safety csv by image name
                #get the true values of focal length and altitude to use when recalculating
                alt_act = float(df_L[df_L.Image == image].loc[:,'Altitude'].values[0]) #this says: find row where image = image and pull altitude
                foc_act = float(df_L[df_L.Image == image].loc[:,'Focal_Length'].values[0])
                pixd_act = float(df_L[df_L.Image == image].loc[:,'Pixel_Dimension'].values[0])
            else:
                pass

            #go into the cvs to look for the values
            dfGUI = df0.truncate(before=idx[0]) #take subset of df starting at first row containing Object
            headG = dfGUI.iloc[0]
            dfGUI = dfGUI[1:]
            dfGUI.columns = headG
            dfGUI = dfGUI.set_index('Object Name')

            for key in keys: #loop through the keys aka future column headers
                if key in nonPercMeas: #if that key is in the list of measurement types (not widths)
                    if key in dfGUI.index: #if that key (measurement) is in this csv
                        x = float(dfGUI.loc[key,'Length']) #extract the measurement value using location
                        #print(key,x)
                        # now is the time to do the back calculations
                        pixc = (x/pixd)*(focl/alt) #back calculate the pixel count
                        #print(pixc)
                        if safety == 'yes':
                            xx = ((alt_act/foc_act)*pixd_act)*pixc #recalculate using the accurate focal length and altitude
                        elif safety == 'no':
                            xx = x
                        #print(xx)
                        #just the thing for the time we had to divide by 2 for a few images
                        #print(div)
                    else: #if this key is not in the csv
                        xx = np.nan
                    mDict[key] = xx #add the value to the respective key
                    mDict_pixc["{0}.PixCount".format(key)] = pixc #add pixel count to respecitive key in pixel count dataframe

                elif "%" in key and key.split("_")[0] in dfGUI.index: #if the key is a width
                    row = key.split("_")[0] #split the name of the measurement
                    col = key.split("_")[1] #to get the row and column indices
                    y = float(dfGUI.loc[row,col]) #to extract the measurement value
                    #recalculate using accurate focal length and altitude
                    pixc = (y/pixd)*(focl/alt) #back calculate the pixel count
                    if safety == 'yes':
                        yy = ((alt_act/foc_act)*pixd_act)*pixc #recalculate using the accurate focal length and altitude
                    elif safety == 'no':
                        yy = y
                    mDict[key] = yy
                elif key not in dfGUI.index and key not in names:
                    mDict[key] = np.nan
                    mDict_pixc["{0}.PixCount".format(key)] = pixc #add pixel count to respecitive key in pixel count dataframe

            df_dict = pd.DataFrame(data = mDict,index=[1]) #make dictionary into dataframe
            df_dict_pixc = pd.DataFrame(data = mDict_pixc,index=[1]) #make dictionary filled with pixel counts of measurements into dataframe

            df_all = pd.concat([df_all,df_dict],sort = True)
            df_all_pixc = pd.concat([df_all_pixc,df_dict_pixc],sort = True) #add this dataframe to the empty one with all the measurements as headers

        df_allx = df_all.drop(columns = ['Altitude','Focal Length','PixD']).replace(np.nan,0)
        df_allx_pixc = df_all_pixc.drop(columns = ['Altitude','Focal Length','PixD']).replace(np.nan,0) #replace nans with 0 for grouping in final formatting)

        def df_formatting(df_allx):
            df_all_cols = df_allx.columns.tolist() #make list of column names
            gby = ['Animal_ID','Image','Notes'] #list of non-numeric columns
            togroup = [x for x in df_all_cols if x not in gby] #setting up list of columns to be grouped

            df_all = df_allx.groupby(['Animal_ID','Image'])[togroup].apply(lambda x: x.astype(float).sum()).reset_index()
            df_notes = df_allx.groupby(['Animal_ID','Image'])['Notes'].first().reset_index()
            df_all =df_all.merge(df_notes,on=['Animal_ID','Image'])

            #sort cols
            cols = list(df_all)
            a = "AaIiTtEeJjRrBbFfWwCcDdGgHhKkLlMmNnOoPpQqSsUuVvXxYyZz" #make your own ordered alphabet
            col = sorted(cols, key=lambda word:[a.index(c) for c in word[0]]) #sort headers based on this alphabet
            df_all1 = df_all.loc[:,col] #sort columns based on sorted list of column header
            df_all1 = df_all1.replace(0,np.nan) #replace the 0s with nans
            return df_all1

        #now we group by ID and image just incase multiple images were measured for the same animal
        #this would combine those measurements (it's why I replaced nans with 0)
        df_all1 = df_formatting(df_allx)
        df_all1_pc = df_formatting(df_allx_pixc)

        print(df_all1)
        print(df_all1_pc)

        #output to csvs
        outcsv = os.path.join(saveFold,"{0}_allIDs.csv".format(outname))
        df_all1.to_csv(outcsv,sep = ',',index_label = 'IX')

        outcsv_pc = os.path.join(saveFold,"{0}_PixelCount.csv".format(outname))
        df_all1_pc.to_csv(outcsv_pc,sep = ',',index_label = 'IX')

        if idchoice == 'yes':
            df_ids = pd.read_csv(idsCSV,sep = ',')
            idList = df_ids['Animal_ID'].tolist()
            df_allx = df_all1[df_all1['Animal_ID'].isin(idList)]

            outidcsv = os.path.join(saveFold,"{0}_IDS.csv".format(outname))
            df_allx.to_csv(outidcsv,sep = ',')
        elif idchoice == 'no':
            pass
        print("done")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
