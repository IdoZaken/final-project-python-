#!/usr/bin/python
# -*- coding: utf-8 -*-
# interface

import datetime
import glob
from abc import ABC, abstractmethod
import pickle  # saving object for other sessions
from time import sleep
import dill as pickle
import socket
import os
import time
import zlib



class device(ABC):

    # device constructor
    def __init__(self, interval, ID, description, IP):
        self.interval = interval
        self.ID = ID
        self.description = description
        self.dataType = self.dataType
        self.mode = "standBy"  #device state: standby= regular mode (waiting for something to happen)
        self.masterIP = IP
        print("device: init device:", description)

    def save(self, path):
        with open(path, 'wb') as f:
            return pickle.dump(self, f)

    def load(self, path):
        with open(path, 'rb') as f:
            self.__dict__.update(pickle.load(f).__dict__)

    def printDetails(self):
        print("ID:", self.ID)
        print("Interval:", self.interval)
        print("Description:", self.description)
        print("Data Type:", self.dataType)

    # path to folder fo files to get
    def getDataFromInputFolder(self, path):
        # print("Searching for files in input directory...")
        files = glob.glob(path + "/*.*")  # create list of files in directory
        try:
            while not files:
                sleep(10)
                files = glob.glob(path + "/*.*")
            else:  # then list (actually the directory) isn't empty
                # print("File detected!") #todo Filedetected message is duplicate because its also says it in the standby mode.
                return (files)
        except KeyboardInterrupt:
            print("Exit Stand By mode")
            pass

    # 'files': what files[0] to compress. 'path': to file goes after compress
    def compress(self, files, path, deviceID, date):  #   compress data with some known compress method
        #compress the data
        print("device: compressing data")
        original_data = open(files[0], 'rb').read()
        compressed_data = zlib.compress(original_data, zlib.Z_BEST_COMPRESSION)

        # compress_ratio = (float(len(original_data)) - float(len(compressed_data))) / float(len(original_data))
        # print('Compressed: %d%%' % (100.0 * compress_ratio))

        #save the compressed data to file
        f = open(path + '/' + deviceID + '-' + date + '-' +'.zlib' + '-' + self.description, 'wb') # ---------> save file here after compress
        f.write(compressed_data)
        f.close()

    def sendData(self, path): # send data from device to Master

        total_size =0

        host = self.masterIP                                #get the IP of the master
        port = 5000        

        dirs = os.listdir(path)

        while True:                                          #check whether the connection succeed
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((host, port))
                break
            except:                                         #if not, probably server on load situation, wait and try again
                print("Falied to connect, auto try again after 10sec")
                time.sleep(10)
                continue

        print("CONNECTED TO MASTER ON" , self.masterIP)
        for files in dirs:
            filename = files
            size = len(filename)                        #the lines on the file
            size = bin(size)[2:].zfill(16)              # change to bin and fill to not lose zeros
            sock.sendall(size.encode('utf8'))            # encode so we could send it
            sock.sendall(filename.encode('utf8'))

            filename = os.path.join(path, filename)     #full file name
            filesize = os.path.getsize(filename)        #actual size after comression and reduction
            total_size +=filesize
            filesize = bin(filesize)[2:].zfill(32)       # change to bin and fill to not lose zeros
            sock.sendall(filesize.encode('utf8'))

            file_to_send = open(filename, 'rb')

            l = file_to_send.read()
            sock.sendall(l)
            file_to_send.close()

            conf = sock.recv(4096)                                  #recvied confirmation from server


            if str(total_size) != conf.decode('utf8'):              #in case connection lost during sendig
                print("Falied to send all files, auto try again after 5sec")
                time.sleep(5)
                self.sendData('readyFiles')

        sock.close()
        print("ALL FILES RECEIVED SUCCESSFULLY")

        filelist = [f for f in os.listdir(path)]                       #clear the storage of client
        for f in filelist:
            os.remove(os.path.join(path, f))

        print("File sent!")


    def noChange(self):
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = self.masterIP
            port  = 5000
            try:
                sock.connect((host, port))
                break
            except:
                print("Falied to connect, auto try again after 10sec")
                time.sleep(10)
                continue

        print("CONNECTED TO MASTER ON" , self.masterIP)
        print("no change")
        sock.sendall(("No Change").encode('utf8'))
        sock.close()


    #--------------------------------- Currently not in use --------------------------------
    # override from device
    def setInterval(self, interval):  # interval for heart beat send
        pass

    #override from device
    def doesNeedAnalyzing(self):   # is the data need to be analyzed (example: if only 1 second past from last time there is no need)
        # print("device: check if need analyze")
        return True

    def isTheDataHasChanged(self):  # boolean
        print("device: Check for change in data...")
        return self.compareData()  # compare the new data from the sensor to the data captured last time. (return true if data has changed)

    def sendPulse(self):  # pulse heart beat to the server
        print("device: sending pulse")
        pass

    def isReady(self, false):  # is the device ready to send data and etc?
        pass




    #-----------------------------------------------------------------------------------------
