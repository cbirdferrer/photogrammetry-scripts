#---------------------------------------------------------------
#gui_collating_safteynet.py
#this script collates measurements from individual csv outputs of
#the morphometriX GUI
#the csvs can be saved either all in one folder or within each individual
#animals folder.
#this version includes a safety net that recalculates the measurement using
#accurate altitude and focal lengths that the user must provie in csvs.
#created by: Clara Bird (clara.birdferrer#gmail.com), July 2019
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
        self.title = 'PyQt5 input dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # self.getOption()
        # self.getSafe()
        # self.openFileNameDialog()

        self.show()

        items = ('Individual Folders', 'One Folder')
        option, okPressed = QInputDialog.getItem(self, "Option","Saved Where", items, 0, False)
        if okPressed and option:
            print(option)


        items = ('yes', 'no')
        safety, okPressed = QInputDialog.getItem(self,"Safety?", "On or Off?",items,0,False)
        if okPressed and safety:
            print(safety)

        if safety == 'yes':
            items = ('hello','goodbye')
            test, okPressed = QInputDialog.getItem(self,"Test",'if', items, 0, False)
            if okPressed and test:
                print(test)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;csv files (*.csv)", options=options)
        if fileName:
            print(fileName)

        path = QFileDialog.getExistingDirectory(None, "Select Directory")
        print(path)

        csv = pd.read_csv(fileName,sep=',')
        print(csv)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
