# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 11:32:50 2017


"""

import sys
import socket
import re
import time
from multiprocessing import Process, Manager  #python inbuit libarary which allow to use multiple process concurrently
Ser_Address = (HOST, PORT) = '', 8877 
Q_Size = 150  #maximum request queue size which sever socket can handle
Socket_pos = {} # dictionary which wll contain conn_ID as key a socket object as a value
Proc_pos = {} # dictionary which wll contain conn_ID as key a procedure object as a value
 
 #method which run by each procedure
def Method(conn_ID,Left_time,Socket_pos,Time_pos,client_conn):
        remain_time = int(Left_time)
        # taking sleeping time on each second and update corresponding time_position from dictionary 
        while remain_time>0:
           time.sleep(1)
           remain_time=remain_time-1
           Time_pos[conn_ID]=remain_time
        http_return = """\
        {"status":"OK"}
        """
        client_conn.sendall(http_return)
        del Time_pos[conn_ID]  #Since the time of procedure is completed, delete conn_ID from dictionary 
        client_conn.close() #close the socket
        sys.exit(0) #terminate the process


def server_always():
    # socket creation
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Function socket.socket creates a socket with Address Family: AF_INET and socket type: SOCK_STREAM
    s.bind(Ser_Address) #Bind a socket to a particular address and port
    s.listen(Q_Size) # Put the socket in listening mode to listen for connections
    
    #creation of python process manager which help us to share dictionary among all procedure or process
    M_ger= Manager()
    Time_pos = M_ger.dict()
    
    #loop which run continuosly and wait for client to connect
    while True:
        client_conn, client_address = s.accept()
        request = client_conn.recv(1638467)
        print request
        data=request.decode()
        print data
        d=data.split(" ")
        print d

        """ Check whether a request is GET OR PUT.Here I am deciding everthing by 
        getting header of request & checking everything manually."""
        
        if d[0]=='GET':
            if 'conn_ID' in d[1]:
                #Get value of conn_ID & remaining_time from request
                value_regex = re.compile("(?<=conn_ID=)(?P<value>.*?)(?=&)")
                match = value_regex.search(d[1])
                conn_ID =match.group('value')
                p=d[1].split("&timeout=")
                #Setting key & value in time_status dictionary
                Time_pos[conn_ID]=p[1]
                # Assigning proces to each connId
                p1 = Process(target=Method, args=(conn_ID,p[1],Socket_pos,Time_pos,client_conn))
                Socket_pos[conn_ID]=client_conn
                Proc_pos[conn_ID]=p1
                p1.start()
                
            elif 'api/serverStatus' in d[1]:
                # Creating Response which contain time remaining time of each connection with connection Id
                http_return="{"
                for key,value in Time_pos.items():
                    http_return=http_return+"'"+str(key)+"':"+"'" +str(value)+"',"
                http_return=http_return+"}"
                client_conn.sendall(http_return)
                client_conn.close() 


        # If request is PUT
        elif d[1]=='/api/kill':
            # Extracting connId from Put request & delete 
        corresponding socket,process,time
            y= d[7].split(":")
            z=y[1].split("}")
            conn_ID = z[0]
            if Time_pos.has_key(conn_ID):
                    socket_pos[conn_ID].close() #closing socket
                    proc_pos[conn_ID].terminate() # terminating process corresponding to given conn_ID
                    del Time_pos[conn_ID]
                    del socket_pos[conn_ID]
                    del proc_pos[conn_ID] 
                    http_return = """{"status":"kill"}""" 
                    client_conn.sendall(http_return)
                    client_conn.close()
                    
            else: 
                    http_return = """{invaild connection Id :"""+str(conn_ID)+"}"
                    client_conn.sendall(http_return)
                    client_conn.close()
             
        
if __name__ == '__main__':
    server_always()