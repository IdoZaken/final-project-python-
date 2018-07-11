# this is a device.
# import here the interface "device" to make it able to act as device who can work with the compressing protocol
#impot tensiometer to make this device be able to connect to a tensiometer sensor

import datetime
import device
from switch import switch #import class switch from file switch
import pickle #saving object for other sessions
import dill as pickle
import os.path
import time
import glob
import shutil
import os
import ntpath
from pathlib import Path



# The code below is generic. it works with all type of devices depends on the device type we imported



option = None # :-)

while(True):
    if option == None:
        print("\nInsert case NUM:\n"
              " 1: first start"
              " 2:  Upload File"
              " 3: Download File")
        option = input("insert NUM: ")
        if option == "1":
            option = "first start"
        if option == "2":
            option = "Upload File"
        if option == "3":
            option == "Download File"

    for case in switch(option):

        if case('first start'):
            print("\ncase: Upload File")
            # todo description cant include dots
            myDevice = Device("0011",  "10.0.2.15") #(self, id,  masterIP)create device instance to actually run in background and gather data
            option == "standBy"
            break


        if case ('standBy'):
            print("\nChoose an action:\n"
                  " 2: Upload File"
                  " 3: Download File" )
            option = input("insert NUM: ")
            if option == "1":
                option = "Upload File"
            if option == "2":
                option == "Download File"
            break



        if case('Download File'):  # need to load the object created in the case of "first start"
            pass



        if case('Upload File'):
            print("Please upload file to sending folder.")
            if os.listdir('sendFiles'):
                myDevice.sendData("sendFiles")

            while (True):
                print("Searching for files in input directory...") #todo: implements other trigers then new file
                filesExist = glob.glob("sendFiles/*.*")  # create list of files in directory
                try:
                    while not filesExist:
                        print("No file detected")
                        time.sleep(4)
                        filesExist = glob.glob("filesPool/*.*")
                    else:  # then list (actually the directory) isn't empty
                        print("File detected!")
                        myDevice.change_name()
                        myDevice.sendData("sendFiles")
                        option = "standBy"
                        break


                except KeyboardInterrupt:
                    print("Exit Stand By mode")
                    pass


        if case(): # default, could also just omit condition or 'if True'
            pass
            # No need to break here, it'll stop anyway
