import os
from fileinput import fileno

from pyftpdlib.authorizers import UnixAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.filesystems import UnixFilesystem

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

# logging.basicConfig(filename='fileServer.log', level=logging.DEBUG, filemode='w',
# format='%(asctime)s\tLogger: %(name)s\tLevel: %(levelname)s\tEvent: %(message)s',
# datefmt='%Y:%m:%d %H:%M:%S')

# Create Logger
serverLog = logging.getLogger("SEDFS Server")

# Create Handler, set level to at least DEBUG
loggingHandler = logging.StreamHandler(stream=sys.stdout)
serverLog.addHandler(loggingHandler)
serverLog.setLevel(logging.DEBUG)

known_servers = []
listOfNo = ["no", "n", "NO", "N"]


class SEDFS_server(FTPServer):

    # init for child class
    def __init__(self, address, childHandler):
        # init Parent Class
        FTPServer.__init__(self, address, childHandler)

        return


class SEDFS_handler(FTPHandler):

    # child handler init
    def __init__(self, conn, server, ioloop):
        self.handler_user = None
        self.handler_pass = None

        # Log handler event
        print(datetime.now().strftime("DATE: %Y:%m:%d\tTIME: %H:%M:%S\tEVENT: "), end="")
        serverLog.info("[+] SEDFS Handle Started")

        # parent handler init
        FTPHandler.__init__(self, conn, server)

        return

    # Polymorph of on_login
    def on_login(self, username):
        self.handler_user = self.authorizer.return_user()
        self.handler_pass = self.authorizer.return_pass()
        print(self.handler_user)
        print(self.handler_pass)

        FTPHandler.on_login(username)


class SEDFS_authorizer(UnixAuthorizer):

    def __init__(self, global_perm="elradfmwMT", allowed_users=None, rejected_users=None, require_valid_shell=True,
                 anonymous_user=None, msg_login="Login successful.", msg_quit="Goodbye."):
        self.user_is = None
        self.pass_is = None

        UnixAuthorizer.__init__(self, global_perm="elradfmwMT",
                                allowed_users=None,
                                rejected_users=None,
                                require_valid_shell=True,
                                anonymous_user=None,
                                msg_login="SEDFS Login successful!",
                                msg_quit="Exiting SEDFS, Goodbye.")

    def validate_authentication(self, username, password, handler):
        self.user_is = username
        self.pass_is = password
        print(self.user_is)
        print(self.pass_is)

        UnixAuthorizer.validate_authentication(self, username, password, handler)

    def return_user(self):
        return self.user_is

    def return_pass(self):
        return self.pass_is


def SEDFS_setup():
    # Get local address information
    server_IP = socket.gethostbyname(socket.gethostname())
    address = (server_IP, 50000)

    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = SEDFS_authorizer()

    # if base directory doesnt exist, make it
    if not os.path.exists("SEDFS"):
        os.mkdir("SEDFS")

    # LOAD username, password, home directory, permissions
    authorizer.override_user(username='sara', homedir='./SEDFS')
    # load_users(authorizer)

    # Instantiate FTP handler class
    handler = SEDFS_handler
    handler.abstract_fs = UnixFilesystem
    handler.authorizer = authorizer
    handler.banner = " << Welcome to SEDFS (Simple Encrypted Distributed File System)"

    # Instantiate FTP server class and listen on ??????:50000
    server = SEDFS_server(address, handler)

    # set a limit for connections
    server.max_cons = 100000
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()


if __name__ == '__main__':
    SEDFS_setup()