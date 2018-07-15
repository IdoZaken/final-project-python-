import os
import socket
from datetime import datetime
from threading import Thread
from switch import Switch #import class switch from file switch
import time
import pprint
import json

root = os.getcwd()

def error_replay(clientsocket,Error):
    clientsocket.sendall(b'0')
    clientsocket.sendall(str(len(Error)).decode('utf8'))
    clientsocket.sendall(Error.encode('utf8'))

def send_data(clientsocket,data):
    while count < 5:
        count = 0
        size = str(len(data)).encode('utf8')
        clientsocket.sendall(size)
        clientsocket.sendall(data.encode('utf8'))

        if clientsocket.recv(size).decode('utf8') != size:
            clientsocket.sendall(b'0')
        else:
            clientsocket.sendall(b'1')
            break
    else:
        error_replay(clientsocket,"Failed to send to long\n")



#handle the clinets connection
def client_thread(clientsocket, ip, port,serverID , MAX_BUFFER = 4096):       # MAX_BUFFER_SIZE is how big the message can be

    #recv user name from client
    size = clientsocket.recv(16)
    size = int(size, 2)
    clientName = clientsocket.recv(size).decode("utf8")

    #check if user exsist
    if not os.path.exists(os.getcwd()+'/'+clientName):
        #if not create new folder for user
        os.mkdir(os.getcwd() + '/' + clientName)
        clientsocket.sendall(b'1')
        os.chdir('/'+clientName)
        size = clientsocket.recv(16)
        size = int(size, 2)
        with open(clientName+'.json', "w+") as f:
            json.dump({"total_size" : size , "used_space" : 0}, f)
    else:
        #if exsist go to folder
        os.chdir('/' + clientName)

    #send 'connected signel'
    clientsocket.sendall(b'11')

    #waiting for commend to recvice
    option = clientsocket.recv(3)

    with Switch(option) as case:
        #create new folder
        if case == b'000':
            size = clientsocket.recv(16)
            size = int(size, 2)
            size = clientsocket.recv(16)
            size = int(size, 2)
            clientName = clientsocket.recv(size).decode("utf8")
            folderPath = clientsocket.recv(size).decode("utf8")
            try:
                os.mkdir(os.getcwd() + '/' +folderPath)
                clientsocket.sendall(b'1')
            except FileExistsError as e:
                error_replay(clientsocket,"Folder already exsist by that path\n")

        if case == b'001':
            startpath = os.getcwd()
            buffer = ''
            for root, dirs, files in os.walk(startpath):
                level = root.replace(startpath, '').count(os.sep)
                indent = ' ' * 4 * (level)
                buffer += '{}{}/\n'.format(indent, os.path.basename(root))
                subindent = ' ' * 4 * (level + 1)
                for f in files:
                    buffer += '{}{}\n'.format(subindent, f)








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

    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = get_ip()
    port = 5000;
    print('Listen on: ' + host + ':' + str(port))
    serversock.bind((host,port));
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
