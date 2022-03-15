from ftplib import FTP
import io
from logging import exception
import os
import shutil
from pathlib import Path
from pyftpdlib.authorizers import DummyAuthorizer
import socket

ServerPort = 50000  # server port
clientConnection = None

serverIps = ["10.211.55.5","10.211.55.6"]
quit = ["QUIT", "Q", "quit", "q", "exit", "EXIT", "E", "e"]
listOfYes = ["yes", "y", "YES", "Y"]
listOfNo = ["no", "n", "NO", "N"]
list_of_known_servers = []
is_file = ["F", "FILE", "f", "file", ]
is_directory = ["D", "DIRECTORY", "d", "directory"]
currentDirectory = ""

# MainServer details
MAINSERVERHOST, MAINSERVERPORT = "10.211.55.6", 60000


# Prompts user for a server IP
# If successful, prompts user for credentials
# Returns a FTP object on success
def connect_to_server():
    global clientConnection  # Global server IPS
    new_ftp = FTP()  # return object
    childServersList = [] # array to maintain child servers
    serverIP = ""

    # find a server connection
    while 1:
        print("\nInput SEDFS Server IPv4 Address ('quit' to exit)\n >> ", end='')
        serverIP = input().strip()

        if serverIP in quit:
            print("No connection made. Goodbye.")
            return False

        # Try server connection
        try:
            new_ftp.connect(serverIP, ServerPort, timeout=5)
            break

        except Exception as e:
            print(" << ERROR:", e)
            continue

    # Loop login attempt
    while True:

        # Get Username and Password
        username = input("\nPlease enter username:\n >> ")
        password = input("\nPlease enter password:\n >> ")

        # attempt login
        try:
            new_ftp.login(username, password)
            print(" << Login Success!")
            new_ftp.set_pasv(True)  # Set to passive mode if time out
            #Fetching active servers details from main server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((MAINSERVERHOST, MAINSERVERPORT))
                ip = socket.gethostbyname(socket.gethostname())
                sock.sendall(bytes("getip\n", "utf-8"))
                received = str(sock.recv(1024), "utf-8")
            activeservers = received.split(";")
            serverIps = activeservers
            print("\nCurrent active servers :",activeservers,"\n")
            for ips in serverIps:
                if ips.strip() != serverIP.strip():
                    con = FTP()
                    con.connect(ips.strip(), ServerPort, timeout=5)
                    con.login(username, password)
                    childServersList.append(con)
            break
        except Exception as e:
            print(e)

        # ask if wish to continue
        print("\nDo you wish to quit?\n >> ", end='')
        response = input()
        if response in listOfYes:
            return False

    list_of_known_servers.append(serverIP)  # Append server information
    return new_ftp, childServersList  # return FTP object


# Makes a blank file or directory in SEDFS
def create_blank_file_or_directory(childServ):
    # loop until user says 'FILE' or 'DIRECTORY'
    while True:
        print(" >> File (F) or Directory (D)\n >> ", end='')
        response = input()

        if response in is_file or response in is_directory:
            break

    # create BLANK FILE
    if response in is_file:
        print("Create file name\n >> ", end='')
        client_file = input()
        command = 'STOR ' + client_file

        try:
            response = ftp.storbinary(command, io.BytesIO(b''))
            #print(" << ", response)
            print("------File created in parent server-----------\n")
            print("------Creating File in child servers----------\n")
            for ser in childSer:
                ser.storbinary(command, io.BytesIO(b''))

            print("-------File creation completed successfully--------\n")

        except Exception as e:
            print(" << ERROR:", e)


    # create BLANK DIRECTORY
    else:
        print("Create directory name\n >> ", end='')
        client_directory = input()

        try:
            response = ftp.mkd(client_directory)
            #print(" << ", response)
            print("------Directory created in parent server-----------\n")
            print("------Creating Directory in child servers----------\n")
            for ser in childServ:
                ser.mkd(client_directory)

            print("-------Directory creation completed successfully--------\n")

        except Exception as e:
            print(" << ERROR:", e)


# Open Text Editor
# Gets notepad on Windows, Nano on Linux
def open_program():
    text_editor = input("\nPlease enter text editor:\n >> ")
    file = input("\nPlease enter file:\n >> ")

    editor_path = shutil.which(text_editor)
    is_a_file = Path(file).is_file()

    if not editor_path:
        print(" << ERROR; Text Editor, '%s', does not exist", text_editor)
        return

    if not is_a_file:
        print(" << ERROR; Path incorrect or is not file")
        return

    try:
        os.system(editor_path + " " + file)
        print()

    except Exception as e:
        print(e)


# Delete 'file' or 'directory'
def delete(ftp, childServ):
    name = input("Enter name to delete\n >> ")

    # Ask if user wants new path
    while True:
        print("Do you want to enter new path?\n >> ", end='')
        ans = input().lower()

        if ans in listOfYes or ans in listOfNo:
            break

    if ans in listOfNo:
        try:
            ftp.delete(name)
            for ser in childServ:
                ser.delete(name)
            print("----------deletion successfully completed-------\n")
            return

        except Exception as e:
            print(e)
            return

    else:
        print("Enter existing path\n >> ", end='')
        new_path = input()

        try:
            ftp.delete(new_path + name)
            for ser in childServ:
                ser[0].delete(new_path + name)
            print("----------deletion successfully completed-------\n")
            return

        except Exception as e:
            print(e)
            return


# navigate to new folder
def navigate(ftp, childServ):
    new_path = input("Enter new path\n >> ")

    try:
        ftp.cwd(new_path)
        for ser in childServ:
            ser.cwd(new_path)
        currentDirectory = new_path

        print("-------Directory changed succesfully--------\n")

    except Exception as e:
        print(e)

def rename(ftp, childServ):
    old_name = input("Enter the file name to rename \n >> ")
    new_name = input("Enter the new file name\n >> ")
    resp = ftp.rename(old_name, new_name)
    #print(resp)
    print("------File renamed succesfully in parent server-------\n")
    print("------Changing file name in child servers----------\n")
    for ser in childServ:
        ser.rename(old_name, new_name)

    print("------File renaming is completed succesfully-------\n")




# list all current files and directories
def ftp_list(ftp):
    try:

        # ftp.retrlines('LIST *README*')
        # all_objects = ftp.nlst()
        print("\n\n-------Begin of List------\n")
        # for obj in all_objects:
        # print(obj)
        ftp.retrlines('LIST')
        print("\n-------End of List------\n\n")

    except Exception as E:
        print("Error: ", E)


# change file permissions
def change_permissions(ftp, childServ):
    filename = input("Input filename\n >> ")
    permissions = input("Input new permissions\n >> ").strip()
    try:
        ftp.sendcmd("SITE CHMOD " + permissions + " " + filename)
        for ser in childServ:
            ser.sendcmd("SITE CHMOD" + permissions + " " + filename)
        print("-------------Permission changed succesfully------------")


    except Exception as E:
        print(E)


def change_owner(ftp, childServ):
    filename = input("Input filename\n >> ")
    owner = input("Input new owner\n >> ").strip()
    try:
        ftp.sendcmd("SITE CHOWN" + owner + " " + filename)
        for ser in childServ:
            ser.sendcmd("SITE CHOWN" + owner + " " + filename)
        print("-------------Owner changed succesfully------------")
    except Exception as E:
        print(E)


# Display Help Menu
def help(ftp):
    print("============================\n",
          "\nCurrent Path: " + ftp.pwd() + "\n\n",
          "\t'q' == Quit SEDFS\n",
          "\t'r' == Read SEDFS file\n",
          "\t'w' == Write to SEDFS\n",
          "\t'p' == Change permissions\n",
          "\t'c' == Create new SEDFS file/directory\n",
          "\t'n' == Navigate to new directory\n",
          "\t'b' == Move back 1 directory\n",
          "\t'l' == List directory contents contents\n",
          "\t'd' == Delete file/directory\n",
          "\t's' == Display Server Information\n",
          "\t'o' == Open Text Editor\n",
          "\t'k' == Change Owner\n",
          "\t'u' == Rename File\n",
          "\t'h' == Help\n")


# write to SEDFS
def write(ftp, childServ):
    local_name = input("Enter Local file path to upload\n >> ")
    try:
        print("\n-------File uploading started------")
        file = open(local_name, 'rb')
    except Exception as E:
        print(E)
        return

    try:
        ftp.storbinary('STOR ' + local_name, file)  # send the file
        file.close()
        print("-------File has uploaded to primary server----")
        print("-------Writing Files in child servers---------")
        for ser in childServ:
            fileChildServ = open(local_name, 'rb')
            ser.storbinary('STOR ' + local_name, fileChildServ)
            fileChildServ.close()

      
        print("-------File has uploaded successfully------\n\n")
        
    except Exception as E:
        print(E)


# update to SEDFS
def update(ftp, childServ):
    sedfs_name = input("Enter SEDFS file path to download\n >> ")
    try:
        print("\n\n-------Begin of current content------\n")
        ftp.retrlines("RETR " + sedfs_name, fileLinePrinting)
        print("\n-------EOF------\n\n")
        newcontent = input("---------Enter content to append in the file\n------")
        file = open(sedfs_name, 'a')
        file.write(newcontent)
        file.close()
        file1 = open(sedfs_name, 'rb')
        ftp.storbinary('STOR ' + sedfs_name, file1)
        file1.close()
        for ser in childServ:
            fileChildServ = open(sedfs_name, 'rb')
            ser.storbinary('STOR ' + sedfs_name, fileChildServ)
            fileChildServ.close()
                  
        print("-------File has updated successfully------\n\n")
        
    except Exception as E:
        print(E)

def test(ftp, childServ):
    local_name = input("Enter Local file path to write\n >> ")
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((MAINSERVERHOST, MAINSERVERPORT))
        sock.sendall(bytes("getlockedfiles"+ "\n", "utf-8"))
        # Receive users data from the server and shut down
        received = str(sock.recv(1024), "utf-8")
    lockedfilelist = received.split(";")
    print("locked file list:", lockedfilelist)
    if local_name in lockedfilelist:
        print("\nThe requested file is currently using by others, please try again later!!!\n")
        return
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MAINSERVERHOST, MAINSERVERPORT))
        sock.sendall(bytes("lockfile:"+local_name+"\n", "utf-8"))
    try:
        li = ftp.nlst()
        print("file slist : ", li)
        print("file name: ",local_name)
        if local_name in li:
            print("\n\n-------Begin of current content------\n")
            ftp.retrlines("RETR " + local_name, fileLinePrinting)
            print("\n-------EOF------\n\n")
            newcontent = input("---------Enter content to append in the file\n------")
            file = open(local_name, 'a')
            file.write(newcontent)
            file.close()
            file1 = open(local_name, 'rb')
            ftp.storbinary('STOR ' + local_name, file1)
            file1.close()
            for ser in childServ:
                fileChildServ = open(local_name, 'rb')
                ser.storbinary('STOR ' + local_name, fileChildServ)
                fileChildServ.close()
            print("-------File has updated successfully------\n\n")
        else:
            try:
                print("\n-------File uploading started------")
                file = open(local_name, 'w')
                newcontent = input("---------Enter content to write in the file\n------")
                file.write(newcontent)
                file.close()
            except Exception as E:
                print(E)
                return
            try:
                file1 = open(local_name, 'rb')
                ftp.storbinary('STOR ' + local_name, file1)  # send the file
                file1.close()
                print("-------File has uploaded to primary server----")
                print("-------Writing Files in child servers---------")
                for ser in childServ:
                    fileChildServ = open(local_name, 'rb')
                    ser.storbinary('STOR ' + local_name, fileChildServ)
                    fileChildServ.close()
                print("-------File has uploaded successfully------\n\n")
            except Exception as E:
                print(E)
    except Exception as E:
        print(E)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MAINSERVERHOST, MAINSERVERPORT))
        sock.sendall(bytes("unlockfile:"+local_name+"\n", "utf-8"))

def fileLinePrinting(line):
    contentLine = "#%s#"%line
    print(contentLine)

# read from sedfs
def read(ftp):
    sedfs_name = input("Enter SEDFS file path to download\n >> ")
    try:
        print("\n\n-------Begin------\n")
        ftp.retrlines("RETR " + sedfs_name, fileLinePrinting)
        print("\n-------EOF------\n\n")
    except Exception as E:
        print(E)
        return


def go_back(ftp, childServ):
    try:
        ftp.cwd("../")
        for ser in childServ:
            ser.cwd("../")
    except Exception as E:
        print(E)


class Execption:
    pass


if __name__ == '__main__':

    ftp, childSer = connect_to_server()

    if ftp:

        help(ftp)
        currentDirectory = ftp.pwd()

        while 1:
            # print("%s >> " % currentDirectory, end='')
            print("\n****** Current Directory : %s *******\n" % ftp.pwd())
            print("Enter a command to perform operation or type 'h' to see the menu >> ", end='')
            clientRequest = input().lower()

            # Create
            if clientRequest == "create" or clientRequest == "c":
                try:
                    create_blank_file_or_directory(childSer)
                    print(" << SUCCESS")

                except Exception as e:
                    print(" << ERROR")

            # Write
            elif clientRequest == "write" or clientRequest == "w":
                write(ftp, childSer)

            # read
            elif clientRequest == "read" or clientRequest == "r":
                read(ftp)

            # update 
            elif clientRequest == "update" or clientRequest == "up":
                update(ftp, childSer)

            elif clientRequest == "test" or clientRequest == "test":
                test(ftp, childSer)

            # read
            elif clientRequest == "rename" or clientRequest == "u":
                rename(ftp, childSer)

            # change permissions
            elif clientRequest == "permissions" or clientRequest == "p":
                change_permissions(ftp, childSer)

            # Navigate
            elif clientRequest == "n" or clientRequest == "navigate":
                navigate(ftp, childSer)

            # Navigate
            elif clientRequest == "k" or clientRequest == "chown":
                change_owner(ftp, childSer)

            # Back 1 Directory
            elif clientRequest == "b" or clientRequest == "back":
                go_back(ftp, childSer)

            # Delete
            elif clientRequest == "d" or clientRequest == "delete":
                delete(ftp, childSer)

            # List
            elif clientRequest == "l" or clientRequest == "list":
                ftp_list(ftp)

            # Open program with file
            elif clientRequest == "o" or clientRequest == "open" or clientRequest == "text editor" or \
                    clientRequest == "open editor" or clientRequest == "open text editor" or \
                    clientRequest == "open text":

                open_program()

            # Status
            elif clientRequest == "s" or clientRequest == "status":
                print(" << List of known SEDFS servers", list_of_known_servers)

            # Quit
            elif clientRequest in quit:
                print(" << Quiting SEDFS...Goodbye")
                ftp.quit()

            # Help
            elif clientRequest == "help" or clientRequest == "h":
                help(ftp)

            # Default
            else:
                print(" << Unknown Command, type 'h' or 'help'")