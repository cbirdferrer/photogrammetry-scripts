##-----------------------------------------------------
##dji_altitude.py
## tool built to pull altitude data from image metadata
##
##Created February 2019
##Author: Clara Bird (clara.birdferrer@gmail.com), Duke MarineUAS
##----------------------------------------------------

import pandas as pd
import numpy as np
import os, sys
import PIL.Image

#set paths
scriptPath = sys.argv[0]
scriptWS = os.path.dirname(scriptPath) #gives you the script folder
rootWS = os.path.dirname(scriptWS) #goes up one folder into project folder
imageFold = os.path.join(scriptWS, "images")

imgnames = []
imgalts = []

imageFiles = os.listdir(imageFold)
for img in imageFiles:
        if img.startswith("1"):
                print(img)
                imgnames += [img]
                imgF = os.path.join(imageFold,img)
                print(imgF)
                image = '"' + imgF + '"'
                output = os.system("exiftool.exe exiftool -T -filename -xmp:RelativeAltitude "+ image + " > dji.txt")
                table = open("dji.txt","r")
                row = table.readline()
                r = row.split("\t")
                print(r)
                rr = r[1]
                print(rr)
                r1 = float(rr)
                imgalts += [r1]
print(imgalts)
d = {'Image':imgnames, 'Meta_Alt':imgalts}
df = pd.DataFrame(data = d)
outfile = os.path.join(scriptWS,"metadata_altitudes.csv")
df.to_csv(outfile, sep = ',')
