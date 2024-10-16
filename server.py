import socket
import sys

#Defining the socket parameters
HOST = '0.0.0.0' #listening on all available netwrok interfaces
PORT = 5000 #arbitrary port number chosen for the server socket

#Creating the UDP socket
try:
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  print("Socket Created!\n")
except OSError as e:
  print (f"Failed to create the socket.\nError Code: {e.errno}\nMessage: {e.strerror}\n")
  sys.exit()
  
#Binding the socket to the host and port number
try:
  s.bind((HOST,PORT))
except OSError as e:
  print (f"Binding failed!\nError Code: {e.errno}\nMessage: {e.strerror}\n")
  sys.exit()

print ("Socket was successfuly bound!\n")

#Setting a timeout for the socket
#If no data is received within 2 seconds, the timeout exception is raised
#This allows the program to escape from the infinite loop of recvfrom()
#Used to allow KeyboardInterrupt to trigger
s.settimeout(10)

#Listening for client requests indefinitely
while True:
  try:
    
    d = s.recvfrom(1024) #receiving the data from the client with a buffer size of 1024 bytes
    data = d[0].decode('utf-8') #storing the data 
    addr = d[1] #storing the socket parameters of the client (IP + PORT)

    #break the loop if there is no data sent from the client
    if not data:
      break
    
    #initialize a reply variable to be sent to the client upon successful receipt of the data
    reply = "OK..." + data

    #send the reply message back to the client
    s.sendto(reply.encode('utf-8'), addr)
    print(f"Message from [{addr[0]}:{addr[1]}]: {data}")
  
  except socket.timeout:
    pass #Continues to the next iteration without performing any error handling action

#closing the UDP socket
s.close()