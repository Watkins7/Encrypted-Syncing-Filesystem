import os, shutil, socket, json
from pathlib import Path
import tests
import io
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


listOfYes = ["yes", "y", "YES", "Y"]
listOfNo = ["no", "n", "NO", "N"]
is_file = ["F", "FILE", "f", "file", ]
is_directory = ["D", "DIRECTORY", "d", "directory"]

# crypto variables
BLOCK_SIZE = 32
KEY = "0123456789abcdef".encode()
cipher = AES.new(KEY, AES.MODE_ECB)
decipher = AES.new(KEY, AES.MODE_ECB)


#######################################################################################
# Display Help Menu
#######################################################################################
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

#
########################################################################################
# Open Text Editor
# Gets notepad on Windows, Nano on Linux
#######################################################################################
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

#######################################################################################
# Makes a blank file or directory in SEDFS
#######################################################################################
def create_blank_file_or_directory(childServ, ftp, username, MAINSERVERHOST, MAINSERVERPORT):
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

        # encrypt file name
        enc_client_file = doEncrypt(client_file)

        command = 'STOR ' + enc_client_file

        # create file for all servers
        try:
            response = ftp.storbinary(command, io.BytesIO(b''))
            print(" << ", response)

            for ser in childServ:
                ser.storbinary(command, io.BytesIO(b''))

            # ?????????????????
            try:
                createPermission("insert", doEncrypt(client_file), username, MAINSERVERHOST, MAINSERVERPORT)
            except Exception as E:
                print("Failed to create permissions")
                print(E)

        except Exception as e:
            print("------FAILED: File/Directory could not be made----------\n")
            print(" << ERROR:", e)
            return

        print("-------File creation completed successfully--------\n")

    # create BLANK DIRECTORY
    else:

        print("Create directory name\n >> ", end='')
        client_directory = input()


        # encypt directory name
        client_directory = doEncrypt(client_directory)

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

#######################################################################################
#
#######################################################################################
def createPermission(flag, filename, owner, MAINSERVERHOST, MAINSERVERPORT, user=None):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MAINSERVERHOST, MAINSERVERPORT))
        ip = socket.gethostbyname(socket.gethostname())

        #
        if flag=="insert":
            data = {"type":"insertPermissions", "fileDetails": {"name": filename, "owner": owner, "users":{}}}

        #
        else:
            data = {"type":"insertPermissions", "fileDetails": {"name": filename, "owner": owner, "users":{"name":user['name'],"per":user['per']}}}

        #
        jsData = json.dumps(data)
        sock.sendall(bytes(jsData, encoding="utf-8"))
        received = sock.recv(1024)
        data = received

        #
        return str(data)

#######################################################################################
#
#######################################################################################
def getPermission(filename, MAINSERVERHOST, MAINSERVERPORT):

    #
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MAINSERVERHOST, MAINSERVERPORT))
        data = {"type":"getPermissions", "filename":filename}
        jsData = json.dumps(data)
        sock.sendall(bytes(jsData, encoding="utf-8"))
        received = sock.recv(1024)

    #
    data = received.decode('utf-8')
    dat = json.loads(data)

    #
    return dat


#######################################################################################
# delete permissions
#######################################################################################
def delPermission(filename, MAINSERVERHOST, MAINSERVERPORT):

    #
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MAINSERVERHOST, MAINSERVERPORT))
        data = {"type":"delPermissions", "filename":filename}
        jsData = json.dumps(data)
        sock.sendall(bytes(jsData, encoding="utf-8"))
        received = sock.recv(1024)

    #
    data = received.decode('utf-8')

#######################################################################################
# Delete 'file' or 'directory'
#######################################################################################
def delete(ftp, childServ, MAINSERVERHOST, MAINSERVERPORT):
  
    name = input("Enter name to delete\n >> ")
    li = ftp.nlst()
    token = ""
    for nam in li:
        if name == doDecrypt(nam):
            token = nam
    if token == "":
        print("No sunch File found.....")
        return

    # Ask if user wants new path
    while True:
        print("Do you want to enter new path?\n >> ", end='')
        ans = input().lower()

        if ans in listOfYes or ans in listOfNo:
            break
    #
    if ans in listOfNo:
        try:
            ftp.delete(token)
            for ser in childServ:
                ser.delete(token)
            delPermission(name, MAINSERVERHOST, MAINSERVERPORT)
            print("----------deletion successfully completed-------\n")
            return

        except Exception as e:
            print(e)
            return

    #
    else:
        print("Enter existing path\n >> ", end='')
        new_path = input()

        #
        try:
            ftp.delete(new_path + name)

            #
            for ser in childServ:
                ser[0].delete(new_path + name)
            print("----------deletion successfully completed-------\n")
            return

        #
        except Exception as e:
            print(e)
            return

#######################################################################################
# navigate to new folder
#######################################################################################
def navigate(ftp, childServ):

    new_path = input("Enter new path\n >> ")

    # encrypt path
    new_path = doEncrypt(new_path)

    # change current path in parent and all other child servers
    try:
        ftp.cwd(new_path)
        for ser in childServ:
            ser.cwd(new_path)

        print("-------Directory changed succesfully--------\n")

    except Exception as e:
        print(e)

#######################################################################################
# rename file on all known servers
#######################################################################################
def rename(ftp, childServ):

    resp = ''
    old_name = input("Enter the file name to rename \n >> ")
    new_name = input("Enter the new file name\n >> ")

    # encrypt oldname
    old_name = doEncrypt(old_name)

    # encrypt newname
    new_name = doEncrypt(new_name)

    try:
        resp = ftp.rename(old_name, new_name)
    except Exception as E:
        print(resp)
        print("------FAILED to rename file in parent server-------\n")
        return

    # rename files in child servers
    for ser in childServ:

        try:
            resp = ser.rename(old_name, new_name)
        except Exception as E:
            print(resp)
            print("------FAILED to rename file in ONE or MORE child servers-------\n")
            return

    print("------File renaming is completed succesfully-------\n")

#######################################################################################
# list all current files and directories
#######################################################################################
def ftp_list(ftp):

    try:
        print("\n\n-------Begin of List------\n")
        li = ftp.nlst()
        for i in li:
            print(doDecrypt(i))
        print("\n-------End of List------\n\n")

    except Exception as E:
        print("Error: ", E)


#######################################################################################
# change file permissions
#######################################################################################
def change_permissions(ftp, childServ):


    # encrypt file name
    filename = input("Input filename\n >> ")
    filename = doEncrypt(filename)

    # get permissions
    permissions = input("Input new permissions\n >> ").strip()

    #
    try:
        ftp.sendcmd("SITE CHMOD " + permissions + " " + filename)
        for ser in childServ:
            ser.sendcmd("SITE CHMOD" + permissions + " " + filename)
        print("-------------Permission changed succesfully------------")


    except Exception as E:
        print(E)

#######################################################################################
#
#######################################################################################
def change_owner(ftp, childServ):

    # encrypt file name
    filename = input("Input filename\n >> ")
    filename = doEncrypt(filename)

    owner = input("Input new owner\n >> ").strip()
    try:
        ftp.sendcmd("SITE CHOWN" + owner + " " + filename)
        for ser in childServ:
            ser.sendcmd("SITE CHOWN" + owner + " " + filename)
        print("-------------Owner changed succesfully------------")
    except Exception as E:
        print(E)

#######################################################################################
# upload local files to SEDFS
#######################################################################################
def uploadlocalfiles(ftp, childServ):

    # encrypt file
    local_name = input("Enter Local file path to upload\n >> ")

    # try to encrypt file and send it
    try:

        # open file
        with open(local_name, 'rb') as fo:
            plaintext = fo.read()

        # ENCRYPT ALL the file text
        enc_text = doEncrypt(plaintext)

        # Make encryted text as ".enc"
        with open(local_name + ".enc", 'wb') as fo:
            fo.write(enc_text)

        print("\n-------File uploading started------")

    # failed to open / encrypt file
    except Exception as E:
        print(E)
        return

    # try to send ".enc" file
    try:

        # encrypt local_name
        enc_local_name = doEncrypt(local_name)

        # open encrypt file
        file_to_send = open(enc_local_name, 'rb')

        ftp.storbinary('STOR ' + enc_local_name, file_to_send)  # send the file
        print("-------File has uploaded to primary server----")
        print("-------Writing Files in child servers---------")

        # send file to all child servers
        for ser in childServ:
            fileChildServ = open(enc_local_name, 'rb')
            ser.storbinary('STOR ' + enc_local_name, fileChildServ)
            fileChildServ.close()

        print("-------File has uploaded successfully------\n\n")

    except Exception as E:
        print(E)


#######################################################################################
# write to SEDFS
#######################################################################################
def write(ftp, childServ, MAINSERVERHOST, MAINSERVERPORT):

    local_name = input("Enter Local file path to write\n >> ")

    #
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MAINSERVERHOST, MAINSERVERPORT))
        sock.sendall(bytes("lockfile:"+local_name+"\n", "utf-8"))

    #
    try:
        li = ftp.nlst()
        print("file slist : ", li)
        print("file name: ",local_name)

        #
        if local_name in li:

            print("\n\n-------Begin of current content------\n")
            ftp.retrlines("RETR " + local_name, tests.fileLinePrinting)
            print("\n-------EOF------\n\n")

            #
            newcontent = input("---------Enter content to append in the file\n------")
            file = open(local_name, 'a')
            file.write(newcontent)
            file.close()
            file1 = open(local_name, 'rb')
            ftp.storbinary('STOR ' + local_name, file1)

            file1.close()

            #
            for ser in childServ:
                fileChildServ = open(local_name, 'rb')
                ser.storbinary('STOR ' + local_name, fileChildServ)
                fileChildServ.close()

            print("-------File has updated successfully------\n\n")

        #
        else:
            try:
                print("\n-------File uploading started------")
                file = open(local_name, 'w')
                newcontent = input("---------Enter content to write in the file\n------")
                file.write(newcontent)
                file.close()

            #
            except Exception as E:
                print(E)
                return

            #
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

            #
            except Exception as E:
                print(E)

    #
    except Exception as E:
        print(E)

    #
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MAINSERVERHOST, MAINSERVERPORT))
        sock.sendall(bytes("unlockfile:"+local_name+"\n", "utf-8"))

#######################################################################################
# update to SEDFS
#######################################################################################
def update(ftp, childServ):

    # encrypt local_name
    sedfs_name = input("Enter SEDFS file path to download\n >> ")
    enc_sedfs_name = doEncrypt(sedfs_name)

    #
    try:

        # Get file
        print("\n\n-------Begin of current content------\n")
        ftp.retrlines("RETR " + enc_sedfs_name, tests.fileLinePrinting)
        print("\n-------EOF------\n\n")

        newcontent = input("---------Enter content to append in the file\n------")

        file = open(sedfs_name, 'a')
        file.write(newcontent)
        file.close()

        # encrypt file
        try:
            # open file
            with open(sedfs_name, 'rb') as fo:
                plaintext = fo.read()

            # ENCRYPT ALL the file text
            enc_text = doEncrypt(plaintext).encode()

            # Make encryted text as ".enc"
            with open(sedfs_name + ".enc", 'wb') as fo:
                fo.write(enc_text)
                fo.close

        except Exception as E:
            print(E)
            return

        # send encrypted file to parent server
        file_to_send = open(enc_sedfs_name, 'rb')
        ftp.storbinary('STOR ' + enc_sedfs_name, file_to_send)
        file_to_send.close()

        # send encrypted file to all servers
        for ser in childServ:
            fileChildServ = open(enc_sedfs_name, 'rb')
            ser.storbinary('STOR ' + enc_sedfs_name, fileChildServ)
            fileChildServ.close()

        print("-------File has updated successfully------\n\n")

    #
    except Exception as E:
        print(E)

#######################################################################################
# read from sedfs
#######################################################################################
def read(ftp):

    # encrypt local_name
    sedfs_name = input("Enter SEDFS file path to download\n >> ")
    sedfs_name = doEncrypt(sedfs_name)

    try:
        print("\n\n-------Begin------\n")
        ftp.retrlines("RETR " + sedfs_name, tests.fileLinePrinting)
        print("\n-------EOF------\n\n")

    except Exception as E:
        print(E)
        return

#######################################################################################
# go back one directory
#######################################################################################
def go_back(ftp, childServ):
    # go back in current server, and other servers
    try:
        ftp.cwd("../")
        for ser in childServ:
            ser.cwd("../")

    # print error
    except Exception as E:
        print(E)


#######################################################################################
# encryption
#######################################################################################
def doEncrypt(content):

    # assuming content is string
    # convert to bytes
    data = bytes(content, 'utf-8')

    # pad then encrypt data
    msg = cipher.encrypt(pad(data, BLOCK_SIZE))

    # returns string, (convert from hex)
    return msg.hex()


#######################################################################################
# decryption
#######################################################################################
def doDecrypt(content):

    # assuming content is string
    # change to hex
    data = bytes.fromhex(content)

    # decrypt data
    plain_text = decipher.decrypt(data)

    # unpad data
    msg_dec = unpad(plain_text, BLOCK_SIZE)

    # return string
    return msg_dec.decode(encoding="utf-8")

#######################################################################################
# needed for error handling
#######################################################################################
class Execption:
    pass