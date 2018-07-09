import os
import socket
from datetime import datetime
from threading import Thread
import time
import firebase_admin
import pyrebase
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage



#handle the clinets connection
def client_thread(clientsocket, ip, port,serverID , MAX_BUFFER = 4096):       # MAX_BUFFER_SIZE is how big the message can be
    global thread_check_for_internet_exist
    global sombodySendToCloud
    while True:

        total_size = 0
        #recv file size from client
        size = clientsocket.recv(16)

        if size.decode('utf8') == "No Change":          #check if there is no change detected by client and print it
            print("No Change detected")
            break


        if not size:                                    #if client done sending
            break

        size = int(size, 2)
        filename = clientsocket.recv(size)              #gets the filename from client
        filesize = clientsocket.recv(32)                #gets the file size from cleint
        filesize = int(filesize, 2)
        file_to_write = open(filename, 'wb')            #creating the received file on server side with the original name

        chunksize = 4096
        while filesize > 0:                             #when filesize = 0, we received the entire file
            if filesize < chunksize:                    #if server get large file
                chunksize = filesize
            data = clientsocket.recv(chunksize)
            file_to_write.write(data)
            total_size += filesize
            filesize -= len(data)                        #subtrack what we received from the actual size

        file_to_write.close()
        clientsocket.sendall(((str(total_size)).encode(('utf8'))))
        print('File received successfully from Device')

        sendFileToCloud('', serverID, filename)



def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
	# doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def startserver():


    serverID = "0001"

    os.chdir('Recvied')
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = get_ip()
    port = 5000;
    print('Listen on: ' + host + ':' + str(port))
    serversock.bind((host,port));
    filename = ""
    serversock.listen(10);
    print ("Waiting for a connection.....")

    try:
        thread = Thread(target = fileSyncHandlerThread, args=(serverID,))
        thread.start()
    except:
        print("Error trying to create Thread")

    #Infinte loop - so the server wont reset after each connetion
    while True:


        clientsocket,addr = serversock.accept()
        ip, port = str(addr[0]), str(addr[1])
        print("\nGot a connection from "+ ip + ":" + port)

        try:
           Thread(target = client_thread , args=(clientsocket, ip, port, serverID)).start()

        except:
            print("Error trying to create Thread")



def files_db(self, serverID):
    internetOn = have_internet() # for checking internet connection only once

    server_id = serverID
    dirs = os.listdir()



    for files in dirs:  #scanning the whole folder given- 'files' is a single file inside a folder

        device_id = files.rsplit('-')[0]  # export id
        temp_date = files.rsplit('-')[
            1]  # export date                                                     #split the time so it would be readable
        date = str(datetime(int(temp_date[4:]), int(temp_date[2:4]),
                            int(temp_date[:2])))  # contain the relvant date but in full format
        # temp_time = files.rsplit('-')[2].rsplit('.')[0] # export time
        temp_time = files.rsplit('-')[2]  # export time
        mtime = str(temp_time[0:2]) + ':' + str(temp_time[2:4]) + ':' + temp_time[4:]
        fileExtension = files.rsplit('-')[3]  # export file extension
        description = files.rsplit('-')[4]  # export description

        print("\nFile name:" + files)




def sendData():





startserver()
