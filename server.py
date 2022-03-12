from fileinput import fileno

# for file server
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import UnixAuthorizer
from pyftpdlib.filesystems import UnixFilesystem

#ip address
from subprocess import check_output
import netifaces as ni


# For file sync
from ftplib import FTP
from pyftpdlib.filesystems import AbstractedFS

# General Libs need for OS
import socket, os, sys, stat
from os import path

# Used to display logging to stdout
import logging.config

# Date and time
from datetime import datetime

#######################################
# Global Logger
#######################################
# Set logging configuration

"""
logging.basicConfig(filename='SEDFS_EVENT_LOG.log', level=logging.DEBUG, filemode='w',
                    format='%(asctime)s\tLogger: %(name)s\tLevel: %(levelname)s\tEvent: %(message)s',
                    datefmt='%Y:%m:%d %H:%M:%S')
"""
logging.basicConfig(filename='SEDFS_EVENT_LOG.log', level=logging.DEBUG, filemode='w',
                    format='%(asctime)s\tLogger: %(name)s\tEvent: %(message)s',
                    datefmt='%d/%m: %H/%M/%S')

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
        self.current_path = "/"
        #self.virtual_filesystem = AbstractedFS("/SEDFS", self)


        # Log handler event
        ip = str(conn.getpeername())

        print(datetime.now().strftime("DATE: %Y:%m:%d /// TIME: %H:%M:%S /// EVENT: "), end="")
        log_event = "[+] SEDFS Handle Started at: " + ip
        serverLog.info(log_event)

        # parent handler init
        FTPHandler.__init__(self, conn, server)

        return

    # Polymorph of on_login
    def on_login(self, username):
        self.handler_user = self.authorizer.return_user()
        self.handler_pass = self.authorizer.return_pass()
        print(self.handler_user)
        print(self.handler_pass)


        try:
            print(self.fs.cwd)
        except Exception as E:
            print(E)

        super().on_login(username)

    def on_file_received(self, file):

        try:
            print(self.fs.cwd)
        except Exception as E:
            print(E)

        super().on_file_received(file)


    def ftp_CWD(self, path):

        super().ftp_CWD(path)

        try:
            self.current_path = self.fs.cwd
        except Exception as E:
            print(E)


    # Creates a directory on both current server and remote
    def ftp_MKD(self, path):

        list_of_servers = self.other_servers()
        print(list_of_servers)

        try:
            for i in list_of_servers:
                new_ftp = FTP()
                new_ftp.connect(i,50000, timeout=2)
                new_ftp.login(self.handler_user, self.handler_user)
                new_ftp.mkd(path)
                new_ftp.close()

        except Exception as E:
            print(E)

        super().ftp_MKD(path)



    def other_servers(self):
        if exists("/configuration files/knownServers.txt"):
            my_file = open("/configuration files/knownServers.txt", "r")
            content = my_file.read()
            my_file.close()
            return content


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
        # print(self.user_is)
        # print(self.pass_is)

        UnixAuthorizer.validate_authentication(self, username, password, handler)

    def return_user(self):
        return self.user_is

    def return_pass(self):
        return self.pass_is


def SEDFS_setup():
    # Get local address information

    #Remove later
    #server_IP = socket.gethostbyname(socket.gethostname())

    # List of IPS on system
    ips = check_output(['hostname', '--all-ip-addresses']).strip()

    print("\n-----------Welcome Admin----------\n")
    print(" >> A list of all possible IPS on your system\n", ips)
    print("\n")

    try:
        ni.ifaddresses('eth0')
        server_IP = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

    except Exception as E:
        print(E)
        print("By default SEDFS uses eth0, please edit code to select default interface")
        print("Goodbye")
        return

    address = (server_IP, 50000)

    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = SEDFS_authorizer()

    # if base directory doesnt exist, make it
    if not os.path.exists("SEDFS"):
        os.mkdir("SEDFS")

    # Make sure that the directory is public
    os.chmod("SEDFS", 0o777)

    # LOAD username, password, home directory, permissions
    authorizer.override_user(username='sara', homedir='./SEDFS')
    authorizer.override_user(username='alice', homedir='./SEDFS')
    # load_users(authorizer)

    # Instantiate FTP handler class
    handler = SEDFS_handler
    handler.abstract_fs = UnixFilesystem("./SEDFS", handler)

    """
    try:
    #    variable = AbstractedFS("/SEDFS", handler)
        print(handler.abstract_fs.cwd)

    except Exception as E:
        print(E)
    """

    handler.authorizer = authorizer
    handler.timeout = None
    handler.banner = " << Welcome to SEDFS (Simple Encrypted Distributed File System)"

    # Instantiate FTP server class and listen on ??????:50000
    server = SEDFS_server(address, handler)

    # set a limit for connections
    server.max_cons = 100000
    server.max_cons_per_ip = 5



    print(" >> Server Setup complete...")
    print(" >> Default Server IP: ", server_IP)
    print(" >> Default Server Port: ", 50000)
    print(" >> SEDFS Server Online")

    # start ftp server
    server.serve_forever()


if __name__ == '__main__':

    if path.exists("/configuration files/knownServers.txt"):
        my_file = open("/configuration files/knownServers.txt", "r")
        content = my_file.read()
        print(content)

    if os.geteuid() != 0:
        print("Error: Server needs to be run as a sudo user\nGoodbye.")
        exit(0)

    SEDFS_setup()
