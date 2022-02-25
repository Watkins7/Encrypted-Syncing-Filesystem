import os
from fileinput import fileno

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import socket

# Used to display logging to stdout
import logging.config
import sys

from datetime import datetime

#######################################
# Global Logger
#######################################
# Set logging configuration

logging.basicConfig(filename='fileServer.log', level=logging.DEBUG, filemode='w',
                    format='%(asctime)s\tLogger: %(name)s\tLevel: %(levelname)s\tEvent: %(message)s',
                    datefmt='%Y:%m:%d %H:%M:%S')

#logging.basicConfig(filename='fileServer.log', level=logging.DEBUG, filemode='w',
                    #format='%(asctime)s\tLogger: %(name)s\tLevel: %(levelname)s\tEvent: %(message)s',
                    #datefmt='%Y:%m:%d %H:%M:%S')

# Create Logger
serverLog = logging.getLogger("SEDFS Server")

# Create Handler, set level to at least DEBUG
loggingHandler = logging.StreamHandler(stream=sys.stdout)
serverLog.addHandler(loggingHandler)
serverLog.setLevel(logging.DEBUG)


class SEDFS_server(FTPServer):

    def __init__(self, address, childHandler):

        # init Parent Class
        FTPServer.__init__(self, address, childHandler)

        return


class SEDFS_handler(FTPHandler):

    user = ""


    def __init__(self, conn, server, ioloop):

        print(datetime.now().strftime("DATE: %Y:%m:%d\tTIME: %H:%M:%S\tEVENT: "), end="")
        serverLog.info("[+] SEDFS Handle Started")

        FTPHandler.__init__(self, conn, server, ioloop)

        return

    def on_login(self, username):
        user = username
        self.on_login(username)



"""
def server_setup():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # Define a new user having full r/w permissions and a read-only
    # anonymous user

    authorizer.add_user('user', '12345', '.', perm='elradfmwMT')

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer

    # Define a customized banner (string returned when client connects)
    handler.banner = " << Welcome to SEDFS (Simple Encrypted Distributed File System)"

    # Specify a masquerade address and the range of ports to use for
    # passive connections. Decomment in case you're behind a NAT.
    # handler.masquerade_address = '151.25.42.11'
    # handler.passive_ports = range(60000, 65535)

    # Get local address information
    server_IP = socket.gethostbyname(socket.gethostname())
    address = (server_IP, 50000)

    # Instantiate FTP server class and listen on ??????:50000
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()
    
"""

def SEDFS_setup():

    # Get local address information
    server_IP = socket.gethostbyname(socket.gethostname())
    address = (server_IP, 50000)

    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # username, password, home directory, permissions
    authorizer.add_user('user', '12345', '/SEDFS', perm='elradfmwMT')

    # Instantiate FTP handler class
    handler = SEDFS_handler
    handler.authorizer = authorizer
    handler.banner = " << Welcome to SEDFS (Simple Encrypted Distributed File System)"

    # Instantiate FTP server class and listen on ??????:50000
    server = SEDFS_server(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()


if __name__ == '__main__':
    SEDFS_setup()
