import socketserver
import json
import socket

# Get free socket
sock = socket.socket()
sock.bind(('', 0))
PORT = int(sock.getsockname()[1])

# Get running IP
HOST = sock.getsockname()[1]

serverList = []
global lockedFileslist
lockedFileslist = []

#
class UserHandler(socketserver.BaseRequestHandler):

    # intial handler
    def handle(self):

        # gets initial handle request
        self.data = self.request.recv(1024).strip()

        # statements below filter the request

        #
        if "serverip" in format(self.data):
            ipadd = self.data.decode("utf-8").split(":")[1]
            if ipadd not in serverList:
                serverList.append(self.data.decode("utf-8").split(":")[1])
            self.request.sendall(bytes(';'.join(serverList) , "utf-8"))
            print("Server",len(serverList)," has stared on -",self.data.decode("utf-8").split(":")[1],":50000")

        #
        if "getip" in format(self.data):
            self.request.sendall(bytes(';'.join(serverList) , "utf-8"))
            print("Returned active servers list")

        #
        if "getlockedfiles" in format(self.data):
            global lockedFileslist
            self.request.sendall(bytes(';'.join(lockedFileslist), "utf-8"))

        #
        if "userdata" in format(self.data):

            file = open("configuration files/userConfig.txt", mode='r')
            lines = file.readlines()
            data = ""

            #
            for line in lines:
                if data != "":
                    data = data + ";" + line
                else:
                    data = data + line
            self.request.sendall(bytes(str(data) + "\n" , "utf-8"))

        #
        if "lockfile" in format(self.data):
            filename = self.data.decode("utf-8").split(":")[1]
            if filename not in lockedFileslist:
                lockedFileslist.append(filename)
            print(self.data, "has been locked")
            print("current locked files are: ", lockedFileslist)

        #
        if "unlockfile" in format(self.data):
            filename = self.data.decode("utf-8").split(":")[1]
            while(filename in lockedFileslist):
                lockedFileslist.remove(filename)
            print(self.data, "has been unlocked")
            print("current locked files are: ", lockedFileslist)

        #
        if "getPermissions" in format(self.data):
            data = json.loads(self.data)
            file = open("configuration files/permissions.json")
            filedata = json.load(file)

            #
            if data['filename'] in filedata:
                result = filedata[data['filename']]
                jsData = json.dumps(result)
                self.request.sendall(bytes(jsData, "utf-8"))
            else:
                self.request.sendall(bytes("NONE", "utf-8"))

        #
        if "insertPermissions" in format(self.data):
            data = json.loads(self.data)
            file = open("configuration files/permissions.json")
            filedata = json.load(file)

            #
            if data['fileDetails']['name'] in filedata:
                temp = filedata[data['fileDetails']['name']]['users']
                temp[data['fileDetails']['users']['name']] = data['fileDetails']['users']['per']
                filedata[data['fileDetails']['name']] = {"name" : data['fileDetails']['name'], "owner": filedata[data['fileDetails']['name']]['owner'], "users":  temp}

            #
            else:
                filedata[data['fileDetails']['name']] =  {"name" : data['fileDetails']['name'], "owner": data['fileDetails']['owner'], "users":  {}}

            #
            with open("configuration files/permissions.json", "w") as file1:
                json.dump(filedata, file1)

            #
            self.request.sendall(bytes(str("200"), "utf-8"))

                #
        if "delPermissions" in format(self.data):
            data = json.loads(self.data)
            file = open("configuration files/permissions.json")
            filedata = json.load(file)

            #
            if data['filename'] in filedata:
                del filedata[data['filename']]

            with open("configuration files/permissions.json", "w") as file1:
                json.dump(filedata, file1)

            #
            self.request.sendall(bytes(str("200"), "utf-8"))


if __name__ == "__main__":

    # Start Server
    with socketserver.TCPServer((HOST, PORT), UserHandler) as server:
        print("main server started on ", HOST, "-", PORT)
        server.serve_forever()