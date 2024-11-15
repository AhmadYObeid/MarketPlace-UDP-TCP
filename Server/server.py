import socket
import threading #Threading library to make the server multi-threaded
import sys
import json

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
s.settimeout(5)

#Implements a switch statement to handle the different requests coming from the client
def handle_request(user_request, data, addr):
  match user_request:
    case "REGISTER":
      return handle_registration(data, addr)
    case "DE-REGISTER":
      return handle_deregistration(data, addr)
    case _:
      print("Invalid Request!")

#Creating a dictionary to store the users information within the server (the dictionary is restored using the json file everytime the server runs again)
try:
  with open('users.json', 'r') as json_file:
    users = json.load(json_file) #loading the json file users' info into the dictionary of users
  
except FileNotFoundError:
  users = {} #JSON file does not exist, meaning no users have registred yet, therefore we start fresh

#Creating a mutex lock to avoid race conditions for the users.json file
lock = threading.Lock()

#Handles the register request
def handle_registration(data, addr):
  request_type, request_number, name, ip, udp, tcp = data.split(", ") #splitting the data into the different fields provided
  msg = None #msg variable to store the reply message sent by the server to the client after handling the request
  #TODO: Add the condition where the server cannot add any more clients
  #Acquiring the lock before modifying the 'users' dictionary
  lock.acquire()
  #Encapsulating the lock release within a try-finally to ensure its release even if an error occurs
  try:
    if name not in users:
    #Adding the user into the users dictionary
      users[name] = {
        "ip": ip,
        "udp": udp,
        "tcp": tcp
      }
      #Save the user info in the users.json file
      with open('users.json', 'w') as json_file:
          json.dump(users, json_file, indent=4)

      reply_msg = f"REGISTERED, {request_number}"
    else:
      reply_msg = f"REGISTER-DENIED, {request_number}, The user already exists in the system!"
  finally:
    lock.release() #Releasing the lock after successful modification

  #Sending the handled request message back to the client
  s.sendto(reply_msg.encode('utf-8'), addr)
  print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")

#Handles the de-registration request 
def handle_deregistration(data, addr):
  request_type, name = data.split(", ") 
  msg = None

  #Acquiring the lock before modifying the 'users' dictionary
  lock.acquire()
  #Encapsulating the lock release within a try-finally to ensure its release even if an error occurs
  try:
    if name in users:
      del users[name] #Deleting the user from the dictionary of users
      # Updating the users.json file with the changes user changes
      with open('users.json', 'w') as json_file:
          json.dump(users, json_file, indent=4)
      reply_msg = f"User [{name}] was successfully removed from the server!\n"
    else:
      reply_msg = f"User [{name}] does not exist in the server!"
  finally:
    lock.release() #Releasing the lock after successful modification

  #Sending the handled request message back to the client
  s.sendto(reply_msg.encode('utf-8'), addr)
  print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")

#Listening for client requests indefinitely
while True:
  try:
    
    d = s.recvfrom(1024) #receiving the data from the client with a buffer size of 1024 bytes
    data = d[0].decode('utf-8') #storing the data after decoding it into string type
    addr = d[1] #storing the socket parameters of the client (IP + PORT)

    #break the loop if there is no data sent from the client
    if not data:
      break
    #Multi-threading
    #Once the listener detects a client request, it creates a new thread and passes the handle_request method as target to handle the request
    else:
      user_request = data.split(',')[0] #splitting the request message sent by the client to only have the type of request (e.i. REGISTER, DE-REGISTER, etc...
      client_thread = threading.Thread(target=handle_request, args=(user_request,data,addr)) #Creating a new thread to handle the coming client request
      client_thread.start() #starting the thread
      client_thread.join() #waiting for the thread to be complete before the next one can resume
  
  except socket.timeout:
    pass #Continues to the next iteration without performing any error handling action

#closing the UDP socket
s.close()