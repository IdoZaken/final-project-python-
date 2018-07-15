import os
import socket
from datetime import datetime
from threading import Thread
from switch import Switch #import class switch from file switch
import time
import pprint
import json

#hold root
root = os.getcwd()

#flags
FAILED = b'0'
SUCCCESS = b'1'
LOGGED = b'11'

#will update user config
def update_user_memory(clientName,newspace):
    global root
    with open(root + '\\' + clientName + '.json','rw') as load:
        userCon = json.load(load)
        userCon['used_space'] = userCon['total_size'] - newspace
        json.dump(userCon,load)

#get error msg to send
def error_replay(clientsocket,error):
    #send FAILED flage to client
    clientsocket.sendall(FAILED)

    #send error data to client
    send_data(clientsocket,error)

#send data from server to client
def send_data(clientsocket,data, size = None):

    #send SUCC flage to client
    clientsocket.sendall(SUCCCESS)

    if size:
        #calculate data size and incode it before send
        size = str(len(data)).encode('utf8')
    else:
        size = str(size.encode('utf8'))
    #send data size
    clientsocket.sendall(size)
    #send data
    clientsocket.sendall(data.encode('utf8'))


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
        clientsocket.sendall(SUCCCESS)
        os.chdir('/'+clientName)
        size = clientsocket.recv(16)
        size = int(size, 2)
        with open(clientName+'.json', "w+") as f:
            json.dump({"total_size" : size , "used_space" : 0}, f)
    else:
        #if exsist go to folder
        os.chdir('/' + clientName)

    #send 'connected signel'
    clientsocket.sendall(LOGGED)

    global root
    with open(root + '\\' + clientName + '.json','r') as load:
        userCon = json.load(load)

    current_free_space = userCon["total_size"] - userCon["used_space"]

    #waiting for commend to recvice
    option = clientsocket.recv(3)

    #pick action base on option
    with Switch(option) as case:
        #create new folder
        if case(b'0000'):
            #incoming data size
            size = clientsocket.recv(16)
            size = int(size, 2)
            #incoming data folder path name
            folderPath = clientsocket.recv(size).decode("utf8")
            try:
                os.mkdir(os.getcwd() + '\\' +folderPath)
                clientsocket.sendall(SUCCCESS)
            except FileExistsError as e:
                error_replay(clientsocket,"Folder already exsist by that path\n")

        #get file list
        if case(b'0001'):
            startpath =  root + '\\' + clientName
            buffer = ''
            #root - > current focuse folder, dirs - > folders in currnet folder, files - > file in current folder
            for root, dirs, files in os.walk(startpath):
                level = root.replace(startpath, '').count(os.sep)
                indent = ' ' * 4 * (level)
                buffer += '{}{}/\n'.format(indent, os.path.basename(root))
                subindent = ' ' * 4 * (level + 1)
                for f in files:
                    buffer += '{}{}\n'.format(subindent, f)
            send_data(clientsocket,buffer)


        if case(b'0010'):
            size = clientsocket.recv(16)
            size = int(size, 2)
            file = clientsocket.recv(size).decode("utf8")
            buffer = ''
            #go through all files in root dir in search of the file
            for root, dirs, files in os.walk(startpath):
                if file in files:
                    buffer = root + '\\' + file
            if buffer == '':
                error_replay(clientsocket,"File not found\n")
            else:
                send_data(clientsocket,buffer)

        #send file from server
        if case(b'0011'):
            #get recive data size
            size = clientsocket.recv(16)
            size = int(size, 2)
            #get full path name
            fileFullPath = clientsocket.recv(size).decode("utf8")

            try:
                file_to_send = open(fileFullPath,'rb')
                file_size = os.path.getsize(fileFullPath)
                send_data(clientsocket,file_to_send.read(),file_size)
            except FileNotFoundError:
                error_replay(clientsocket, "File not found\n")

        #move into folder
        if case(b'0100'):
            size = clientsocket.recv(16)
            size = int(size, 2)
            #get folder to move into
            goto = clientsocket.recv(size).decode("utf8")
            try:
                #try to move to chdir
                os.chdir(goto)
                clientsocket.sendall(SUCCCESS)
            except OSError as e:
                try:
                    #failed so try from root dir
                    os.chdir(root + '\\' + clientName + '\\' + goto)
                    clientsocket.sendall(SUCCCESS)
                except  OSError as e:
                    #failed both local dir and root dir return error
                    error_replay(clientsocket,"I/O error({0}): {1}".format(e.errno, e.strerror))


        #load files from client folder to currnet folder
        if case(b'0101'):
            while True:
                #recive file name size
                size = clientsocket.recv(16)
                size = int(size, 2)
                #if no more data client will send 0 size
                if size == 0:
                    update_user_memory(clientName, current_free_space)
                    break
                #get file path to load
                file = clientsocket.recv(size).decode("utf8")
                file = os.getcwd() + '\\' + file

                #recive file size
                size = clientsocket.recv(16)
                size = int(size, 2)

                if (size/(1024*1024)) > current_free_space:
                    error_replay(clientsocket,"Not enough free space")
                    break

                #create the dir if not already exists
                os.makedirs(os.path.dirname(file), exist_ok=True)
                buffer = size
                with open(file, 'wb') as f:
                    while buffer > 0:
                        if buffer < MAX_BUFFER:
                            recive_file = clientsocket.recv(buffer)
                        else:
                            recive_file = clientsocket.recv(MAX_BUFFER)
                        f.write(recive_file)
                        buffer -= MAX_BUFFER
                print('File received successfully from Device')

                # send SUCC flage to client
                clientsocket.sendall(SUCCCESS)
                current_free_space -= size/(1024*1024)

        #delete file
        if case(b'0110'):



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
