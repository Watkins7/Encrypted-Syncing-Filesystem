from ftplib import FTP
import io
import os
import shutil
from pathlib import Path

ServerPort = 50000  # server port
clientConnection = None

quit = ["QUIT", "Q", "quit", "q", "exit", "EXIT", "E", "e"]
listOfYes = ["yes", "y", "YES", "Y"]
list_of_known_servers = []
is_file = ["F", "FILE", "f", "file", ]
is_directory = ["D", "DIRECTORY", "d", "directory"]


# Prompts user for a server IP
# If successful, prompts user for credentials
# Returns a FTP object on success
def connect_to_server():

    global clientConnection     # Global server IPS
    new_ftp = FTP()             # return object

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


# Display Help Menu
def help(ftp):
    print("============================\n",
          "\nCurrent Path: " + ftp.pwd() + "\n\n",
          "\t'q' == Quit SEDFS\n",
          "\t'r' == Read SEDFS file\n",
          "\t'w' == Write to SEDFS\n",
          "\t'c' == Create new SEDFS file/directory\n",
          "\t'n' == Navigate to new directory\n",
          "\t'b' == Move back 1 directory\n",
          "\t'l' == List directory contents contents\n",
          "\t'd' == Delete file/directory\n",
          "\t's' == Display Server Information\n",
          "\t'o' == Open Text Editor\n",
          "\t'h' == Help\n")


class Execption:
    pass

if __name__ == '__main__':
    ftp = connect_to_server()

    if ftp:

        help(ftp)

        while 1:
            print(" >> ", end='')
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
                print("Not Implemented")

            # Navigate
            elif clientRequest == "n" or clientRequest == "navigate":
                print("Not Implemented")

            # Back 1 Directory
            elif clientRequest == "b" or clientRequest == "back":
                print("Not Implemented")

            # Delete
            elif clientRequest == "d" or clientRequest == "delete":
                print("Not Implemented")

            # List
            elif clientRequest == "l" or clientRequest == "list":
                try:
                    ftp.retrlines('LIST')
                except Exception as E:
                    print('Error fetching file listing')

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
            if clientRequest == "help" or clientRequest == "h":
                help()

            # Default
            else:
                print(" << Unknown Command, type 'h' or 'help'")
