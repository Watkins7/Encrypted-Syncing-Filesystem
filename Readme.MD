626_FILESYSTEM_Group-7

-Download the following externals libraries
        "pyftpdlib"
        "ftplib"
        "csync"
        "python3"
        
    
-Hardcode "mainserver.py" with the apporiate IP of the system
(mainserver.py is the server that clients connect to)

        -Run mainserver first with:  "python3 mainserver.py"
        
        
        
-Hardcode "server.py" with the apporiate IP of 'mainserver'
(server.py are the replication servers that support copies of the filesystem)

        -Run replication server with:   "python3 server.py"
        
        
        
-Run client software
(client software will request mainserver IP in prompt)

        -Run client software with:      "python3 client.py"
  
