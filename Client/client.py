import socket 
import sys
import json
import time #library used to simulate simutanous client reqeuest sent to 
            #the server for multi-threading test purposes.
            #It can also be used to set timers for client offers.

#defining the socket parameters (IP + PORT)
client_host = "0.0.0.0" #listening on all available netwrok interfaces
client_port = 2000 #arbitrary port number for the client socket
#defining the TCP port number for testing purposes
client_TCP_port = 2100 #arbitrary number for now

#Loads the current value of the request_number from the client_config.json file
def load_request_number():
  try:
    with open('client_config.json', 'r') as json_file:
      data = json.load(json_file)
      return data
  except FileNotFoundError:
    return 1 #returns 1 if file is not exisiting yet, meaning we are starting fresh
  except json.JSONDecodeError:
    return 1 #returns 1 if the file exists but is empty 

#Updates the request_number in the client_config.json file
#Called everytime a request is sent to the server
def update_request_number(request_number):
  with open("client_config.json", "w") as json_file:
    json.dump(request_number, json_file, indent=4)

#Initializing the request_number by loading the current request_number from the config file
request_number = load_request_number()

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

#Variable to track the registration status of the client
#Used to allow the users to use some functions only if they are registered
is_registered = False
 
#Swtich statement to handle different user requests
def user_request(user_input):
    match user_input:
      case 1:
        return user_registration(request_number) 
      case 2:
        return user_deregistration(request_number)
      case 3:
        return looking_for(request_number)
      case _:
        print(f"Invalid option! Please try again.")

#Prepares the registration request message to be sent to the server
def user_registration(request_number):
  print(f"Enter the following information to register yourself within the shopping system:\n")
  name = input(f"Name: ")
  ip = socket.gethostbyname(socket.gethostname())
  udp = client_port
  tcp = client_TCP_port
  msg = f"REGISTER, {str(request_number)}, {name}, {ip}, {udp}, {tcp}"
  global is_registered 
  is_registered = True #TODO: only a temporary solution for now, eventually we should wait for the server's response to set this value to true.
  return msg

#Prepares the de-registration request message to be sent to the server
def user_deregistration(request_number):
  name = input(f"Enter the name of the user to be de-registered: ")
  msg = f"DE-REGISTER, {name}"
  global is_registered 
  is_registered = False
  return msg

print(f"Welcome to the Peer-to-Peer Shopping System!\n")

#Sends a looking_for request to the server to indicate a search for an item
def looking_for(reqeuest_number):
  if (is_registered == True):
    name = input("Enter your name: ") #TODO: potentially replace this with a variable that holds the name of
    #the user once they register. However, that might be a problem if the client creats multiple
    #users on the same device.
    print("What item are you looking for:")
    item_name = input("Item Name: ")
    item_description = input("Item Description: ")
    max_price = input("Max Price: ")
    msg = f"LOOKING_FOR, {str(request_number)}, {name}, {item_name}, {item_description}, {max_price}"
    return msg
  else:
    return None
    

# #just a method to test multi request transmission (uncomment to use)
# def test_multiThreading():
#   name = 'Larry'
#   ip = socket.gethostbyname(socket.gethostname())
#   udp = client_port
#   tcp = client_TCP_port
#   msg = f"REGISTER, {str(request_number)}, {name}, {ip}, {udp}, {tcp}"
#   return msg

#Sending a message to the server
while True:
#   #Prompting the user to choose a feature offered by the shopping system
  user_input = int(input(f"""Please choose one of the options below:\n
  [1] - Register
  [2] - De-Register
  [3] - Look for an Item
                
->"""))
  
#   #Processing the user's input and saving it 
  request_msg = user_request(user_input)
  
  # num_requests = 2 #Arbitrary number of requests to send multiple requests at once
  if (request_msg != None):
    try:
        s.sendto(request_msg.encode('utf-8'), (server_host,server_port)) #the string message is encoded into bytes before being sent to the server using the utf-8 encoding standard
        request_number += 1 #incrementing the request number for the next requests to be sent
        update_request_number(request_number) #updating the client_config.json file with the newest request number

        #storing the reply message of the server upon receiving the client request
        d = s.recvfrom(1024)
        reply = d[0].decode('utf-8') #Decode the message provided by the server into a string using the utf-8 decoding standard
        addr = d[1]

        #displaying the server's reply message
        print(f"\nServer reply [{addr[0]}, {addr[1]}]: {reply}\n")

        #small delay between requests to simulate a new client request
        #time.sleep(0.1)

    except socket.error as msg:
      print("Error Occured!")
  else:
    print("User not registered! Please register first.")