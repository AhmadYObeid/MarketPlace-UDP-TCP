import socket 
import sys

#defining the socket parameters (IP + PORT)
client_host = "0.0.0.0" #listening on all available netwrok interfaces
client_port = 2000 #arbitrary port number for the client socket

#Creating the UDP clinet socket
try:
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
  print(f"Socket creation failed!")
  sys.exit()

#Binding the socket to its parameters
s.bind((client_host, client_port))

#Socket parameters of the server socket
server_host = "localhost"
server_port = 5000

#Sending a message to the server
while True:
  msg = input("Enter message to send: ")
  
  try:
    s.sendto(msg.encode('utf-8'), (server_host,server_port)) #the string message is encoded into bytes before being sent to the server using the utf-8 encoding standard

    #storing the reply message of the server upon receiving the client request
    d = s.recvfrom(1024)
    reply = d[0].decode('utf-8') #Decode the message provided by the server into a string using the utf-8 decoding standard
    addr = d[1]
    
    #displaying the server's reply message
    print(f"Server reply: {reply}")
    
  except socket.error as msg:
    print("Error Occured!")
