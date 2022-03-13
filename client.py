from ftplib import FTP
import io, sys
import os, signal
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

    global clientConnection  # Global server IPS
    new_ftp = FTP()  # return object

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
            break

        except Exception as e:
            print(e)

        # ask if wish to continue
        print("\nDo you wish to quit?\n >> ", end='')
        response = input()
        if response in listOfYes:
            return False

    list_of_known_servers.append(serverIP)  # Append server information
    return new_ftp  # return FTP object


# Makes a blank file or directory in SEDFS
def create_blank_file():

    print("Create file name\n >> ", end='')
    client_file = input()
    command = 'STOR ' + client_file

    try:
        response = ftp.storbinary(command, io.BytesIO(b''))
        print(" << ", response)

    except Exception as e:
        print(e)

def create_blank_directory():

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


# Delete 'file'
def file_delete(ftp):

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

        except Exception as e:
            print(e)

    else:
        print("Enter existing path\n >> ", end='')
        new_path = input()

        try:
            ftp.delete(new_path + name)

        except Exception as e:
            print(e)

# Delete 'Directory'
def directory_delete(ftp):

    name = input("Enter name to delete\n >> ")

    # Ask if user wants new path
    while True:
        print("Enter new path?\n >> ", end='')
        ans = input().lower()

        if ans in listOfYes or ans in listOfNo:
            break

    if ans in listOfNo:
        try:
            ftp.rmd(name)

        except Exception as e:
            print(e)

    else:
        print("Enter existing path\n >> ", end='')
        new_path = input()

        try:
            ftp.rmd(new_path + name)

        except Exception as e:
            print(e)


# navigate to new folder
def navigate(ftp):

    new_path = input("Enter new path\n >> ")

    try:
        ftp.cwd(new_path)
        # currentDirectory = new_path

    except Exception as e:
        print(e)


def rename(ftp):

    old_name = input("Enter old name\n >> ")
    new_name = input("Enter new name\n >> ")

    try:
        resp = ftp.rename(old_name, new_name)
    except Exception as E:
        print(E)

    print(resp)


# list all current files and directories
def ftp_list(ftp):

    try:

        print("\n\n-------Begin of List------\n")
        ftp.retrlines('LIST')
        print("\n-------End of List------\n\n")

    except Exception as E:
        print("Error: ", E)


# change file permissions
def change_permissions(ftp):
    filename = input("Input filename\n >> ")
    permissions = input("Input new permissions\n >> ").strip()
    try:
        ftp.sendcmd("SITE CHMOD " + permissions + " " + filename)
    except Exception as E:
        print(E)


"""
def change_owner(ftp):
    filename = input("Input filename\n >> ")
    owner = input("Input new owner\n >> ").strip()
    try:
        ftp.sendcmd("SITE CHOWN " + owner + " " + filename)
    except Exception as E:
        print(E)
"""


# Display Help Menu
def help(ftp):
    print("============================\n",
          # "\nCurrent Path: " + currentDirectory + "\n\n",
          "\t'cf' == Create new SEDFS file\n",
          "\t'cd' == Create new SEDFS directory\n",
          "\t'w' == Write to SEDFS\n",
          "\t'r' == Read SEDFS file\n",
          "\t'l' == List directory contents contents\n",
          "\t'n' == Navigate to new directory\n",
          "\t'b' == Move back 1 directory\n",
          "\t'u' == Change Name\n",
          "\t'p' == Change permissions\n",
          "\t'df' == Delete file\n",
          "\t'dd' == Delete directory\n",

          #"\t'k' == Change Owner\n",

          "\t's' == Display Server Information\n",
          "\t'o' == Open Text Editor\n",
          "\t'q' == Quit SEDFS\n",
          "\t'h' == Help\n")


# WRITE to SEDFS
def write(ftp):
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
        print("-------File has uploaded successfully------\n\n")
    except Exception as E:
        print(E)


# READ from SEDFS
def read(ftp):
    sedfs_name = input("Enter SEDFS file path to download\n >> ")
    try:
        print("\n\n-------Begin------\n")
        #ftp.retrbinary("RETR " + sedfs_name, print)
        respMessage = ftp.retrlines("RETR " + sedfs_name, print)
        print("\n-------EOF------\n\n")
    except Exception as E:
        print(E)
        return


# ../
def go_back(ftp):
    try:
        ftp.cwd("../")
        # currentDirectory = ftp.pwd()
    except Exception as E:
        print(E)

#####
#insert EXECPTION Class

# Capture 'Control + C'
def signal_handler(sig, frame):
    print("Exiting client.py")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':

    ftp = connect_to_server()

    if ftp:

        help(ftp)

        while 1:

            print("Enter a command (or type 'h' to see the menu) >> ", end='')
            clientRequest = input().lower()

            # Create blank file
            if clientRequest == "create" or clientRequest == "cf" or clientRequest == "touch":
                create_blank_file()

            # Create directory
            elif clientRequest == "create directory" or clientRequest == "cd" or clientRequest == "mkdir":
                create_blank_directory()

            # Write
            elif clientRequest == "write" or clientRequest == "w":
                write(ftp)

            # read
            elif clientRequest == "read" or clientRequest == "r":
                read(ftp)

            # read
            elif clientRequest == "rename" or clientRequest == "u":
                rename(ftp)

            # change permissions
            elif clientRequest == "permissions" or clientRequest == "p" or clientRequest == "chmod":
                print("Not tested")
                change_permissions(ftp)

            # Navigate
            elif clientRequest == "n" or clientRequest == "navigate":
                navigate(ftp)

            # Navigate
            #elif clientRequest == "k" or clientRequest == "chown":
            #    change_owner(ftp)

            # Back 1 Directory
            elif clientRequest == "b" or clientRequest == "back":
                print("Not tested")
                go_back(ftp)

            # Delete file
            elif clientRequest == "df" or clientRequest == "delete file" or clientRequest == "rf":
                file_delete(ftp)

            elif clientRequest == "dd" or clientRequest == "delete directory" or clientRequest == "rmdir":
                directory_delete(ftp)

            # List
            elif clientRequest == "l" or clientRequest == "list" or clientRequest == "ls":
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
