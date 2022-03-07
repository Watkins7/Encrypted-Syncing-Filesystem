from ftplib import FTP
import io
import os
import shutil
from pathlib import Path

ServerPort = 50000  # server port
clientConnection = None

quit = ["QUIT", "Q", "quit", "q", "exit", "EXIT", "E", "e"]
listOfYes = ["yes", "y", "YES", "Y"]
listOfNo = ["no", "n", "NO", "N"]
list_of_known_servers = []
is_file = ["F", "FILE", "f", "file", ]
is_directory = ["D", "DIRECTORY", "d", "directory"]
currentDirectory = ""

# Prompts user for a server IP
# If successful, prompts user for credentials
# Returns a FTP object on success
def connect_to_server():

    global clientConnection     # Global server IPS
    new_ftp = FTP()             # return object


    os.mkdir("test")
    os.chmod("test", 0o222)

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
            new_ftp.set_pasv(True)                      # Set to passive mode if time out
            break

        except Exception as e:
            print(e)

        # ask if wish to continue
        print("\nDo you wish to quit?\n >> ", end='')
        response = input()
        if response in listOfYes:
            return False

    list_of_known_servers.append(serverIP)          # Append server information
    return new_ftp                                  # return FTP object


# Makes a blank file or directory in SEDFS
def create_blank_file_or_directory():

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
            print(" << ", response)

        except Exception as e:
            print(" << ERROR:", e)


    # create BLANK DIRECTORY
    else:
        print("Create directory name\n >> ", end='')
        client_directory = input()

        try:
            response = ftp.mkd(client_directory)
            print(" << ", response)

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
def delete(ftp):

    name = input("Enter name to delete\n >> ")

    # Ask if user wants new path
    while True:
        print("Enter new path?\n >> ", end='')
        ans = input().lower()

        if ans in listOfYes or ans in listOfNo:
            break

    if ans in listOfNo:
        try:
            ftp.delete(name)
            return

        except Exception as e:
            print(e)
            return

    else:
        print("Enter existing path\n >> ", end='')
        new_path = input()

        try:
            ftp.delete(new_path + name)
            return

        except Exception as e:
            print(e)
            return


# navigate to new folder
def navigate(ftp):

    new_path = input("Enter new path\n >> ")

    try:
        ftp.cwd(new_path)
        currentDirectory = new_path

    except Execption as e:
        print(e)


# list all current files and directories
def ftp_list(ftp):
    try:
        # ftp.retrlines('LIST')
        # ftp.retrlines('LIST *README*')
        all_objects = ftp.nlst()

        for obj in all_objects:
            print(obj)

    except Exception as E:
        print("Error: ", E)


# change file permissions
def change_permissions(ftp):
    filename = input("Input filename\n >> ")
    permissions = input("Input new permissions\n >> ").strip()
    ftp.sendcmd("SITE " + permissions + " " + filename)


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
          "\t'h' == Help\n")


# write to SEDFS
def write(ftp):

    local_name = input("Local file to upload\n >> ")
    try:
        file = open(local_name, 'rb')
    except Exception as E:
        print(E)
        return

    try:
        ftp.storbinary('STOR ', local_name, file)  # send the file
        file.close()
    except Exception as E:
        print(E)

# read from sedfs
def read(ftp):

    sedfs_name = input("SEDFS file to download\n >> ")
    try:
        ftp.retrbinary("RETR ",sedfs_name, print)
    except Exception as E:
        print(E)
        return


def go_back(ftp):

    try:
        ftp.cwd("../")
    except Exception as E:
        print(E)


class Execption:
    pass

if __name__ == '__main__':

    ftp = connect_to_server()

    if ftp:

        help(ftp)
        currentDirectory = ftp.pwd()

        while 1:
            print("%s >> " % currentDirectory, end='')
            clientRequest = input().lower()

            # Create
            if clientRequest == "create" or clientRequest == "c":
                try:
                    create_blank_file_or_directory()
                    print(" << SUCCESS")

                except Exception as e:
                    print(" << ERROR")

            # Write
            elif clientRequest == "write" or clientRequest == "w":
                print("Not Tested")
                write(ftp)

            # read
            elif clientRequest == "read" or clientRequest == "r":
                print("Not Tested")
                read(ftp)

            # change permissions
            elif clientRequest == "permissions" or clientRequest == "p":
                print("Not tested")
                change_permissions(ftp)

            # Navigate
            elif clientRequest == "n" or clientRequest == "navigate":
                navigate(ftp)

            # Back 1 Directory
            elif clientRequest == "b" or clientRequest == "back":
                print("Not tested")
                go_back(ftp)

            # Delete
            elif clientRequest == "d" or clientRequest == "delete":
                delete(ftp)

            # List
            elif clientRequest == "l" or clientRequest == "list":
                ftp_list(ftp)

            # Open program with file
            elif clientRequest == "o" or clientRequest == "open" or clientRequest == "text editor" or\
                clientRequest == "open editor" or clientRequest == "open text editor" or\
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
