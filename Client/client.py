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
 
#Swtich statement to handle different user requests
def user_request(user_input):
    match user_input:
      case 1:
        return user_registration() 
      case 2:
        return user_deregistration()
      case _:
        print(f"Invalid option! Please try again.")

def user_registration():
  print(f"Enter the following information to register yourself within the shopping system:\n")
  name = input(f"Name: ")
  ip = input(f"IP Address: ")
  udp = input(f"UDP socket#: ")
  tcp = input(f"TCP socket#: ")
  msg = f"REGISTER, {name}, {ip}, {udp}, {tcp}"
  return msg

def user_deregistration():
  name = input(f"Enter the name of the user to be de-registered: ")
  msg = f"DE-REGISTER, {name}"
  return msg

print(f"Welcome to the Peer-to-Peer Shopping System!\n")

#Sending a message to the server
while True:
  user_input = int(input(f"""Please choose one of the options below:\n
  [1] - Register
  [2] - De-Register
                
->"""))
  
  request_msg = user_request(user_input)

  try:
    s.sendto(request_msg.encode('utf-8'), (server_host,server_port)) #the string message is encoded into bytes before being sent to the server using the utf-8 encoding standard

    #storing the reply message of the server upon receiving the client request
    d = s.recvfrom(1024)
    reply = d[0].decode('utf-8') #Decode the message provided by the server into a string using the utf-8 decoding standard
    addr = d[1]
    
    #displaying the server's reply message
    print(f"\nServer reply: {reply}\n")
    
  except socket.error as msg:
    print("Error Occured!")
