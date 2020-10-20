#! /usr/bin/env python3

import sys
sys.path.append("../lib")       # for params
import re, socket, params, os

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

from threading import Thread;
from encapFramedSock import EncapFramedSock
import threading

global filesBeingTransferred
global lock

filesBeingTransferred = []
lock = threading.Lock()

#Checks to see if file is already being transferred to
def fileTransferStart(fileName):
    if fileName in filesBeingTransferred:
        return True
    else:
        filesBeingTransferred.append(fileName)
        return False

#Removes file after transfer is done
def fileTransferEnd(fileName):
    filesBeingTransferred.remove(fileName)
        
class Server(Thread):
    def __init__(self, sockAddr):
        Thread.__init__(self)
        self.sock, self.addr = sockAddr
        self.fsock = EncapFramedSock(sockAddr)
    def run(self):
        print("new thread handling connection from", self.addr)

        fileName = (self.fsock.receive(debug)).decode()
        print("File name was recieved so it can check to see if it's currently being written to")

        print("Thread ", threading.current_thread() ,"is waiting for a lock")
        lock.acquire()
        print("Thread ", threading.current_thread() ,"lock was acquired")
        
        if fileTransferStart(fileName) is True:
            print("File is currently being transferred-Try Again")
            lock.release()
            sys.exit(0)

        else:
            print("File is not currently being transferred")
            pass


        fileInfo = (self.fsock.receive(debug)).decode()
        print("The file's name, size and remote name file was received")
        print("File Info: ", fileInfo)
        fileName, fileSize, remoteFileName = fileInfo.split(":")
        fileSize = int(fileSize)
        print("File is being check to see if it is currently being transferred...")

        #checks to see if file already exist
        path = os.getcwd()+"/"+remoteFileName
        if os.path.exists(path) is True:
            print("The file is already on the server")
            payload = self.fsock.receive(debug)
            self.fsock.send(payload, debug)

        else:
            with open (remoteFileName, "w") as f:
                print("File data is being recieved...")
                payload = self.fsock.receive(debug)

                #Decodes payload if it is not none and writes to the remote file
                #If payload is nothing is none then it writes nothing to the remote file

                if payload is not None:
                    payloadDecoded = payload.decode()
                    f.write(payloadDecoded)
                    self.fsock.send(payload, debug)
                    lock.release()
                    print("Thread ", threading.current_thread() ,"lock was released")
                    fileTransferEnd(fileName)
                    print("Exiting.....")    

while True:
    sockAddr = lsock.accept()
    server = Server(sockAddr)
    server.start()


