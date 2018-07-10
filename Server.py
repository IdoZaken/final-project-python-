import os
import socket
from datetime import datetime
from threading import Thread
import time
import pprint



#handle the clinets connection
def client_thread(clientsocket, ip, port,serverID , MAX_BUFFER = 4096):       # MAX_BUFFER_SIZE is how big the message can be
    global thread_check_for_internet_exist
    global sombodySendToCloud
    while True:

        #recv file size from client
        size = clientsocket.recv(16)



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
            filesize -= len(data)                        #subtrack what we received from the actual size

        file_to_write.close()
        print('File received successfully from Device')




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



    #Infinte loop - so the server wont reset after each connetion
    while True:


        clientsocket,addr = serversock.accept()
        ip, port = str(addr[0]), str(addr[1])
        print("\nGot a connection from "+ ip + ":" + port)

        try:
           Thread(target = client_thread , args=(clientsocket, ip, port, serverID)).start()

        except:
            print("Error trying to create Thread")



#creating Server DB
def files_db(self, path):
    files_dict ={}
    dirs = os.listdir(path)

    for files in dirs:                                                                          #scanning the whole flder given
        if files == 'db.txt':
            continue
        if files.rsplit('-')[0] not in files_dict:                                               #check if we still did not recvied file from that ID
            files_dict[files.rsplit('-')[0]] = {}
        device_id = files.rsplit('-')[0]
        temp_date = files.rsplit('-')[1]                                                        #split the time so it would be readable
        date =str( datetime(int(temp_date[4:]), int(temp_date[2:4]), int(temp_date[:2])))       #contain the relvant date but in full format
        temp_time = files.rsplit('-')[2].rsplit('.')[0]
        time = str(temp_time[0:2]) + ':' + str(temp_time[2:4]) + ':' + temp_time[4:]

        files_dict[files.rsplit('-')[0]][files] = {'date: ': date[0:10] , 'time: ': time}

    with open(path +'/db.txt', 'w') as file:
        file.write(pprint.pformat(files_dict))




# def sendData():





startserver()
