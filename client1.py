import socket
host = ''
port = 8888
 
mySocket = socket.socket()
mySocket.connect((host,port))
 
message = raw_input()
mySocket.send(message.encode())
data = mySocket.recv(1024).decode()
print ('Received from server: ' + data)
		 
mySocket.close()
 
