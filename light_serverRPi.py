# server.py 
import socket                                         
import time

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = socket.gethostname()                           

port = 5641                                           
#Get own IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
local_ip_address = s.getsockname()[0]

# bind to the port
serversocket.bind(('', port))     
print("Host IP:", local_ip_address, " listening on port: ", port)
print("Waiting for connection")                             

# queue up to 5 requests
serversocket.listen(1)

while True:
    # establish a connection
    conn, addr = serversocket.accept()      

    print("Got a connection from %s" % str(addr))
    data = conn.recv(1024)
    if data:
        payload = data.decode("utf8")
        print("Got command: "+payload)
    if payload == "time":
        currentTime = time.ctime(time.time()) + "\r\n"
        conn.send(currentTime.encode('utf8'))
        print('Sending: '+currentTime)
    conn.close()