#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os

sys.path.append("../lib")       # for params
import params

from encapFramedSock import EncapFramedSock    

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

fileName = input("Enter the file name from the client: ")
remoteFileName = input("Enter the remote name for the server: ")
separator = ":"

addrFamily = socket.AF_INET
socktype = socket.SOCK_STREAM
addrPort = (serverHost, serverPort)

sock = socket.socket(addrFamily, socktype)

if sock is None:
    print('could not open socket')
    sys.exit(1)

sock.connect(addrPort)

fsock = EncapFramedSock((sock, addrPort))

try:

    sizeOfFile = os.path.getsize(fileName)
    if sizeOfFile == 0:
        print("There's nothing in the file")
        sys.exit(0)


    fName = f"{fileName}".encode()
    fsock.send(fName,debug)
    print("file name is sent so that it can be checked to see if its being used")

    i = input("Press Any key to continue -- The file is about to be written to on the server\n"
        )
    
    info = (f"{fileName}{separator}{sizeOfFile}{separator}{remoteFileName}".encode())
    print(info)

    
    print("The file's name, size and remote name file was sent")
    fsock.send(info,debug)
    content = ""

    with open (fileName, "r") as a:
        
        for data in fileName:
            data = a.read()
            if not data:
                break
                
            else:
                content = data.encode()
                print("File data is being sent...")
                fsock.send(content,debug)
                

    print("File data was sent back to the client")
    fsock.receive(debug)
            
except FileNotFoundError as e:

    print("The file doesn't exist")
    sys.exit(0)

