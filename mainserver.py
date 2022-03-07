from socket import socket
import socketserver

HOST, PORT = "10.211.55.6", 60000

serverList = []

class UserHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        if "serverip" in format(self.data):
            ipadd = self.data.decode("utf-8").split(":")[1]
            if ipadd not in serverList:
                serverList.append(self.data.decode("utf-8").split(":")[1])
            self.request.sendall(bytes(';'.join(serverList) , "utf-8"))
            print("Server",len(serverList)," has stared on -",self.data.decode("utf-8").split(":")[1],":50000")
        if "getip" in format(self.data):
            self.request.sendall(bytes(';'.join(serverList) , "utf-8"))
            print("Returned active servers list")
        if "userdata" in format(self.data):   
            file = open("configuration files/userConfig.txt", mode='r')
            lines = file.readlines()
            data = ""
            for line in lines:
                if data != "":
                    data = data + ";" + line
                else:
                    data = data + line
            self.request.sendall(bytes(str(data) + "\n" , "utf-8"))


if __name__ == "__main__":
    with socketserver.TCPServer((HOST, PORT), UserHandler) as server:
        print("users server started on ", HOST, "-", PORT)
        server.serve_forever()