from ftplib import FTP

ServerPort = 50000  # server port
clientConnection = None

quit = ["QUIT", "Q", "quit", "q", "exit", "EXIT", "E", "e"]
list_of_known_servers = []


def connect_to_server():

    global clientConnection

    while 1:
        print("Input SEDFS Server IPv4 Address ('quit' to exit)\n>> ", end='')
        serverIP = input().strip()

        if serverIP in quit:
            print("No connection made. Goodbye.")
            return False

        # try to make a connection
        try:
            # Set 10 second time out, Attempt connection
            ftp = FTP()
            print("test")
            ftp.connect(serverIP, ServerPort)

            # Get Username and Password
            username = input("Please enter username:\n >> ")
            password = input("Please enter password:\n >> ")

            ftp.login(username, password)
            list_of_known_servers.append(serverIP)
            return ftp

        except Exception as e:
            print(e)


if __name__ == '__main__':
    if_ftp = connect_to_server()

    if if_ftp:
        print(" >> Login Success!")

        while 1:
            print(" >> ", end='')
            clientRequest = input().lower()

            

