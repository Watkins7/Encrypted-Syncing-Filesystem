from fileinput import fileno

# for file server
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import UnixAuthorizer
from pyftpdlib.filesystems import AbstractedFS
from pyftpdlib.filesystems import UnixFilesystem

# ip address
from subprocess import check_output
import netifaces as ni

# For file sync
from ftplib import FTP

# General Libs need for OS
import os, sys
from os import path
from os.path import exists

# Used to display logging to stdout
import logging.config

# Date and time
from datetime import datetime

#######################################
# Exit if user is not sudo
#######################################
if os.getuid() != 0:
    print("Error: Server needs to be run as a sudo user\nGoodbye.")
    sys.exit(0)

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
known_users = []
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
        # self.virtual_filesystem = AbstractedFS("/SEDFS", self)

        # Log handler event
        ip = str(conn.getpeername())

        print(datetime.now().strftime("DATE: %Y:%m:%d /// TIME: %H:%M:%S /// EVENT: "), end="")
        log_event = "[+] SEDFS Handle Started at: " + ip
        serverLog.info(log_event)

        # parent handler init
        FTPHandler.__init__(self, conn, server)

        self.proto_cmds.update(
            {'SITE SIDEMKD': dict(perm='m', auth=True, arg=True, path=True,
                                  help='Side channel for make dir on other servers'),
             'SITE SIDEDELE': dict(perm='d', auth=True, arg=True,
                                   help='Side channel for delete file on other server'),
             'SITE SIDERNFR': dict(perm='f', auth=True, arg=True,
                                   help='One/two side channel for rename'),
             'SITE SIDERNTO': dict(perm=None, auth=True, arg=True,
                                   help='two/two side channel for rename'),
             'SITE SIDECHMOD': dict(perm='M', auth=True, arg=True,
                                    help='Side channel for permissions'),
             'SITE SIDESTOR': dict(perm='w', auth=True, arg=True,
                                   help='Side channel for storing files'),
             'SITE SIDERMD': dict(perm='d', auth=True, arg=True,
                                  help='Side channel for remove directory')}
        )

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

    ####################################################################################
    # Make Directory on Server and ALL other server
    def ftp_MKD(self, path):

        new_path = self.fs.fs2ftp(path)
        current_path = self.fs.cwd
        # current_path = self.fs.fs2ftp(current_path)

        print("Testing multi MKD", new_path)
        print("Current path is ", current_path)

        # Make directory in all other servers
        for i in known_servers:
            new_FTP = FTP()
            new_FTP.connect(i, 50000)
            new_FTP.login(self.handler_user, self.handler_pass)
            try:
                new_FTP.cwd(self.fs.cwd)
            except Exception as E:
                print(E)
            try:
                new_FTP.sendcmd("SITE SIDEMKD " + new_path)
            except Exception as E:
                print(E)
            new_FTP.close()

        super().ftp_MKD(path)

    # Sidechannel on making directory only
    def ftp_SITE_SIDEMKD(self, path):
        actual_path = self.fs.fs2ftp(path)
        actual_path = self.fs.ftp2fs(actual_path)
        print(actual_path)

        super().ftp_MKD(actual_path)

    ####################################################################################
    # Renaming on Server and ALL other Server
    def ftp_RNFR(self, path):

        new_path = self.fs.fs2ftp(path)

        print("Testing multi RNFR", new_path)

        # Make directory in all other servers
        for i in known_servers:
            new_FTP = FTP()
            new_FTP.connect(i, 50000)
            new_FTP.login(self.handler_user, self.handler_pass)
            new_FTP.cwd(self.current_path)
            new_FTP.sendcmd("SITE SIDERNFR " + new_path)
            new_FTP.close()

        super().ftp_RNFR(path)

    def ftp_RNTO(self, path):

        new_path = self.fs.fs2ftp(path)

        print("Testing multi RNTO", path)

        # Make directory in all other servers
        for i in known_servers:
            new_FTP = FTP()
            new_FTP.connect(i, 50000)
            new_FTP.login(self.handler_user, self.handler_pass)
            new_FTP.cwd(self.current_path)
            new_FTP.sendcmd("SITE SIDERNTO " + new_path)
            new_FTP.close()

        super().ftp_RNTO(path)

    # Sidechannel on renaming only
    def ftp_SITE_SIDERNFR(self, path):
        super().ftp_RNFR(path)

    def ftp_SITE_SIDERNTO(self, path):
        super().ftp_RNTO(path)

    ####################################################################################
    # Make File on server
    def ftp_STOR(self, file, mode='w'):

        print("Testing multi STOR")

        # Make directory in all other servers
        for i in known_servers:
            new_FTP = FTP()
            new_FTP.connect(i, 50000)
            new_FTP.login(self.handler_user, self.handler_pass)
            new_FTP.cwd(self.current_path)
            new_FTP.sendcmd("SITE SIDESTOR " + file)
            new_FTP.close()

        super().ftp_STOR(file, mode)

    # Sidechannel making file on other servers
    def ftp_SIDESTOR(self, file, mode='w'):
        super().ftp_STOR(file, mode)

    ####################################################################################
    # Delete File on server
    def ftp_DELE(self, path):

        new_path = self.fs.fs2ftp(path)

        print("Testing multi DELE", new_path)

        # Make directory in all other servers
        for i in known_servers:
            new_FTP = FTP()
            new_FTP.connect(i, 50000)
            new_FTP.login(self.handler_user, self.handler_pass)
            new_FTP.cwd(self.current_path)
            new_FTP.sendcmd("SITE SIDEDELE " + new_path)
            new_FTP.close()

        super().ftp_DELE(path)

    # Sidechannel deleting file on other servers
    def ftp_SIDEDELE(self, path):
        super().ftp_DELE(path)

    ####################################################################################
    # Delete directory on server
    def ftp_RMD(self, path):

        new_path = self.fs.fs2ftp(path)

        print("Testing multi RNFR", new_path)

        # Make directory in all other servers
        for i in known_servers:
            new_FTP = FTP()
            new_FTP.connect(i, 50000)
            new_FTP.login(self.handler_user, self.handler_pass)
            new_FTP.cwd(self.current_path)
            new_FTP.sendcmd("SITE SIDERMD " + new_path)
            new_FTP.close()

        super().ftp_RMD(path)

    # Sidechannel delete other files on server
    def ftp_SIDERMD(self, path):
        super().ftp_RMD(path)

    ####################################################################################
    # Change permissions on server
    def ftp_SITE_CHMOD(self, path, mode):

        new_path = self.fs.fs2ftp(path)

        print("Testing multi CHMOD", new_path, mode)

        # Make directory in all other servers
        for i in known_servers:
            new_FTP = FTP()
            new_FTP.connect(i, 50000)
            new_FTP.login(self.handler_user, self.handler_pass)
            new_FTP.cwd(self.current_path)
            new_FTP.sendcmd("SITE SIDECHMOD " + mode + " " + new_path)
            new_FTP.close()

        super().ftp_SITE_CHMOD(path, mode)

    # Sidechannel changing permissions on other servers
    def ftp_SITE_SIDECHMOD(self, path, mode):
        super().ftp_SITE_CHMOD(path, mode)


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


def multiServerLoad():
    global known_servers

    if exists("configuration files/knownServers.txt"):

        print("Multi-Server Configuration File Found")

        ans = input(" Load File (y/yes) >> ").lower()
        if ans == "yes" or ans == "y":
            my_file = open("configuration files/knownServers.txt", "r")
            content = my_file.readlines()
            my_file.close()
            for i in range(len(content)):
                content[i] = content[i].strip()
                known_servers.append(content[i])

        else:
            print("Multi-Server Config not loaded")

    else:
        print("Warning... No multi-server configuration file found")


def multiUserLoad():
    global known_users

    if exists("configuration files/userConfig.txt"):

        print("User Configuration File Found")

        ans = input(" Load File (y/yes) >> ").lower()
        if ans == "yes" or ans == "y":
            my_file = open("configuration files/userConfig.txt", "r")
            content = my_file.readlines()
            my_file.close()
            for i in range(len(content)):
                content[i] = content[i].strip()
                known_users.append(content[i])

        else:
            print("WARNING... Multi-user Config not loaded!!!")
            print("WARNING... No users are authorized to use server")

    else:
        print("WARNING... No multi-user configuration file found!!!")
        print("WARNING... No users are authorized to use server")


def SEDFS_setup():
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
    print(" >> Default Server IP: ", server_IP)
    print(" >> Default Server Port: ", 50000)

    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = SEDFS_authorizer()

    # if base directory doesnt exist, make it
    if not os.path.exists("SEDFS"):
        os.mkdir("SEDFS")

    # Make sure that the directory is public
    os.chmod("SEDFS", 0o777)

    # LOAD username, password, home directory, permissions
    multiUserLoad()
    for i in range(len(known_users)):
        try:
            home = os.path.abspath("SEDFS")
            authorizer.override_user(known_users[i], homedir=home)
        except Exception as E:
            print(E)

    # LOAD multi-server config
    multiServerLoad()

    # Instantiate FTP handler class
    handler = SEDFS_handler
    # handler.abstract_fs = UnixFilesystem("/SEDFS", handler)
    handler.abstracted_fs = AbstractedFS

    # testing code
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
    #handler.abstracted_fs = AbstractedFS("/SEDFS",handler)
    #handler.abstracted_fs = UnixFilesystem

    # Instantiate FTP server class and listen on ??????:50000
    server = SEDFS_server(address, handler)

    # set a limit for connections
    server.max_cons = 100000
    server.max_cons_per_ip = 5

    print(" >> Server Setup complete...")
    print(" >> SEDFS Server Online")

    # start ftp server
    server.serve_forever()


if __name__ == '__main__':

    if path.exists("/configuration files/knownServers.txt"):
        my_file = open("/configuration files/knownServers.txt", "r")
        content = my_file.read()
        print(content)

    SEDFS_setup()
