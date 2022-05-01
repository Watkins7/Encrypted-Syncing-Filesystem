import socketserver
import json
import socket
import logging.config
import sys
import time
from ftplib import FTP
from main_functions import list_of_all_files

# Get running IP
HOST = socket.gethostbyname(socket.gethostname())

# list of all servers
serverList = []

# global list of all the locked file
global lockedFileslist
lockedFileslist = []

# Main Logger
logging.basicConfig(filename='mainServer.log', level=logging.DEBUG, filemode='w',
                    format='%(asctime)s\tLogger: %(name)s\tLevel: %(levelname)s\tEvent: %(message)s',
                    datefmt='%Y:%m:%d %H:%M:%S')

# Set Logging Configurations
serverLog = logging.getLogger("Main Server")
loggingHandler = logging.StreamHandler(stream=sys.stdout)
serverLog.addHandler(loggingHandler)
serverLog.setLevel(logging.DEBUG)


# Handler for the user class
class UserHandler(socketserver.BaseRequestHandler):

    # initial handler
    def handle(self):

        # gets initial handle request
        self.data = self.request.recv(1024).strip()

        # log request
        log_event = "[+] CLIENT: " + str(self.client_address[0]) + ":" + str(self.client_address[1]) + " REQUEST: " + str(self.data.decode())
        serverLog.info(log_event)

        #################################################################################
        # statements below filter the request
        #################################################################################

        # a new server joins main
        if "serverip" in format(self.data):
            ipadd = self.data.decode("utf-8").split(":")[1]
            if ipadd not in serverList:
                serverList.append(self.data.decode("utf-8").split(":")[1])
            self.request.sendall(bytes(';'.join(serverList) , "utf-8"))

            # log new server to server list
            log_event = "Server " + str(len(serverList)) + " has stared on " + self.data.decode("utf-8").split(":")[1] + ":50000"
            serverLog.info(log_event)

            time.sleep(1)
            # check server's file list

            # connect to the new FTP server
            ftp = FTP()
            ftp.connect(str(self.data.decode("utf-8").split(":")[1]), 50000)

            # sign in with "MAIN" account
            ftp.login(user='main', passwd='12345')

            # request list of fileso
            try:
                ftp.sendcmd("SITE SENDALLFILES x")
                time.sleep(1)
            except Exception as E:
                print(E)

            try:
                with open('knownfiles.txt', 'wb') as fp:
                    resp = ftp.retrbinary("RETR knownfiles.txt", fp.write)
            except Exception as E:
                print(resp, E)

            # quit FTP
            ftp.quit()

            # get all the files on the permission server
            permission_file_list = list_of_all_files("permissions.json")


            localfile = open("knownfiles.txt", "r")
            # check files
            all_lines = localfile.readlines()

            # Look to see if every permission file is on the server
            for i in permission_file_list:
                if i not in all_lines:
                    log_event = "ERROR " + i + " NOT FOUND IN SEDFS!"
                    serverLog.warning(log_event)

            for i in all_lines:
                if i not in permission_file_list:
                    log_event = "ERROR " + i + " UNKNOWN FILE FOUND IN SEDFS!"
                    serverLog.warning(log_event)


        # a server requests all of main's IPs
        if "getip" in format(self.data):
            self.request.sendall(bytes(';'.join(serverList) , "utf-8"))

            log_event = "[+] Active server list returned to: " + str(self.client_address[0])
            serverLog.info(log_event)

        # returns locked files
        if "getlockedfiles" in format(self.data):
            global lockedFileslist
            self.request.sendall(bytes(';'.join(lockedFileslist), "utf-8"))

        # returns userdata
        if "userdata" in format(self.data):

            file = open("userConfig.txt", mode='r')
            lines = file.readlines()
            data = ""

            # for all the USERS, send what is in i the userConfig.txt file
            for line in lines:
                if data != "":
                    data = data + ";" + line
                else:
                    data = data + line
            self.request.sendall(bytes(str(data) + "\n" , "utf-8"))

        # locks a file
        if "lockfile" in format(self.data):
            filename = self.data.decode("utf-8").split(":")[1]
            if filename not in lockedFileslist:
                lockedFileslist.append(filename)

            log_event = "[*] " + str(self.data) + " has been locked"
            serverLog.info(log_event)

        # unlocks a file
        if "unlockfile" in format(self.data):
            filename = self.data.decode("utf-8").split(":")[1]
            while(filename in lockedFileslist):
                lockedFileslist.remove(filename)

            log_event = "[*] " + str(self.data) + " has been unlocked"
            serverLog.info(log_event)

        # gets permission in the json file
        if "getPermissions" in format(self.data):
            data = json.loads(self.data)
            file = open("permissions.json")
            filedata = json.load(file)

            # sends the requested information
            if data['filename'] in filedata:
                result = filedata[data['filename']]
                jsData = json.dumps(result)
                self.request.sendall(bytes(jsData, "utf-8"))
            else:
                self.request.sendall(bytes("NONE", "utf-8"))

        # insert new permissions in the json file
        if "insertPermissions" in format(self.data):
            data = json.loads(self.data)
            file = open("permissions.json")
            filedata = json.load(file)

            # ?????????
            if data['fileDetails']['name'] in filedata:
                temp = filedata[data['fileDetails']['name']]['users']
                temp[data['fileDetails']['users']['name']] = data['fileDetails']['users']['per']
                filedata[data['fileDetails']['name']] = {"name" : data['fileDetails']['name'], "owner": filedata[data['fileDetails']['name']]['owner'], "users":  temp}

            # ????????????
            else:
                filedata[data['fileDetails']['name']] =  {"name" : data['fileDetails']['name'], "owner": data['fileDetails']['owner'], "users":  {}}

            # ???????????
            with open("permissions.json", "w") as file1:
                json.dump(filedata, file1)

            # ???????????
            self.request.sendall(bytes(str("200"), "utf-8"))

        # deletes a given permission in the json file
        if "delPermissions" in format(self.data):
            data = json.loads(self.data)
            file = open("permissions.json")
            filedata = json.load(file)

            # ?????????????
            if data['filename'] in filedata:
                del filedata[data['filename']]

            with open("permissions.json", "w") as file1:
                json.dump(filedata, file1)

            # ??????????????
            self.request.sendall(bytes(str("200"), "utf-8"))

        # ??????????????????
        if "updatePermissions" in format(self.data):
            data = json.loads(self.data)
            file = open("permissions.json")
            filedata = json.load(file)

            # ??????????????
            if data['filename'] in filedata:
                temp = filedata[data['filename']]
                temp['name'] =  data['newfilename']
                filedata[data['newfilename']] = temp
                del filedata[data['oldfilename']]

            with open("permissions.json", "w") as file1:
                json.dump(filedata, file1)

            # ????????????????
            self.request.sendall(bytes(str("200"), "utf-8"))


if __name__ == "__main__":

    # Start Server
    with socketserver.TCPServer((HOST, 0), UserHandler) as server:

        # get IP and PORT
        ip, port = server.server_address

        # Display IP and Port
        log_event ="[+] Main Server Started on IP:" + ip +" and PORT: ", port
        serverLog.info(log_event)

        # Serve forever
        server.serve_forever()
