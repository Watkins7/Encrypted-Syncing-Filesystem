626_FILESYSTEM_Group-7

- Download the following externals libraries noted in the "requirements.txt"
- Note, that this program supports windows and is python based code

        - Note you can easy install these with "venv" and the command "python install -r requirements.txt"
    
- In the folder called "main server", there will be a file called "mainserver.py", this should be run first

        - the client will use this to get status on which filesystems are active        
        - mainserver.py will automatically grab a random port number, and the ip of the system
        - mainserver.py will talk to each file server when it comes online
        - mainserver will identify if a file server does or does not contain the appriopate files it should contain
        - Run mainserver first with:  "python3 mainserver.py"
           
- In the folder called "ftp server", there should be a script called "server.py", this will request the mainserver's IP and Port #

        - This script functions as the actual filserver
        - this server on default runs on port 50000
        - therefore only 1 vm/machine can support 1 file server at a time
        - Each of these servers communicate with "mainserver" before going online
        - Run replication server with:   "python3 server.py"
  
 -Run client software
(client software will request mainserver IP in prompt)

        - Run client software with:      "python3 client.py"
        - client will communicate with mainserver to get permmision list of files/directories
        - client will get all active file servers
        - Client can create folders/messages
        - Give permissions to other users
        - Encrypt data before transmission
        - see content on the filesystem it is connected to
  
- clients have a supported function where their data is encrypted before sending it to the server
- Each server, (including "mainserver"), has an individual logger that keeps track of what happens on the system
- Whenever a "server.py" comes online, when it communicates with "mainserver", mainserver can idenitify if any "server.py" is either missing files, or any additional files have been added
        
        

  
