626_FILESYSTEM_Group-7

William Atkins Readme.MD

Code Requirements:

    Servers need to have the 'Linux Operating System' and 'Python3'
  
    Server must be run/executed as SUDO
  
    To sync multiple Servers, their IPs must be MANUALLY LOADED into 'knownServers.txt"
      (Must put all OTHER servers IP (not the current server IP) in the file)
      (This file is only loaded/checked once, therefore all other server IPs must be in the file before the server goes active/online/running)
      (To add more servers after running, you must MANUALLY add them into knownServers.txt, then rerun the server)
    
    Servers need to already have the 'user' on their operating system
      (By default 'sara' and 'alice' are loaded from userConfig.txt as example users)
      (Inorder for server sync to function, the SAME PASSWORD and USERNAME must be on all concurrent servers)
  
    External Libraries:
      'pyftpdlib'
      'ftplib'
   
   
Defaults:

    While the server displays all possible IPs on the system, the default is 'eth0'
      (If the Linux system uses a different network interface, you will need to HARDCODE THE CHANGE from 'eth0' to whatever interface you want)
    
    pyftplib defaults can be adjusted/modifed in the code, such as increasing the number of connections from 10,000 to 'x'
  
    Please see online pyftplib documentation on how to adjust
  
  
  Server Install:
    
    On linux, to run server "sudo python3 server.py"
    
    First Question:
      Loads users from config file
      FAILURE to load userConfig will prevent any user from using the system
      
    Second Question
      One time load of OTHER server IPs into memory
      To add more servers after running, modify knownServers.txt, then rerun the server
      
  
  Client:
  
    Tested on linux:  "python3 client.py"
    
    Enter known server IP, followed by username and password on Linux System
