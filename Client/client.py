import json
import random
import re
import socket
import sys
import threading
import time  # library used to simulate simutanous client reqeuest sent to

# the server for multi-threading test purposes.
# It can also be used to set timers for client offers.

# defining the socket parameters (IP + PORT)
client_host = "0.0.0.0"  # listening on all available netwrok interfaces
client_port = random.randint(1000, 9999)  # arbitrary port number for the client socket
# defining the TCP port number for testing purposes
client_TCP_port = 2100  # arbitrary number for now

request_number = 0
# Loads the current value of the request_number from the client_config.json file


# Updates the request_number in the client_config.json file
# Called everytime a request is sent to the server
def update_request_number(request_number):
    request_number += request_number


# Initializing the request_number by loading the current request_number from the config file

# Creating the UDP clinet socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print(f"Socket creation failed!")
    sys.exit()

# Binding the socket to its parameters
s.bind((client_host, client_port))

# Socket parameters of the server socket
server_host = "localhost"
server_port = 5000

# Variable to track the registration status of the client
# Used to allow the users to use some functions only if they are registered
is_registered = False
user_name = None


# Swtich statement to handle different user requests
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


# Prepares the registration request message to be sent to the server
def user_registration(request_number):
    print(
        f"Enter the following information to register yourself within the shopping system:\n"
    )
    name = input(f"Name: ")
    ip = socket.gethostbyname(socket.gethostname())
    udp = client_port
    tcp = client_TCP_port
    msg = f"REGISTER, {str(request_number)}, {name}, {ip}, {udp}, {tcp}"  # TODO: only a temporary solution for now, eventually we should wait for the server's response to set this value to true.
    user_name = name
    return msg


# Prepares the de-registration request message to be sent to the server
def user_deregistration(request_number):
    name = input(f"Enter the name of the user to be de-registered: ")
    ip = socket.gethostbyname(socket.gethostname())
    udp = client_port
    tcp = client_TCP_port
    msg = f"DE-REGISTER, {str(request_number)}, {name}, {ip}, {udp}, {tcp}"
    return msg


print(f"Welcome to the Peer-to-Peer Shopping System!\n")


# Sends a looking_for request to the server to indicate a search for an item
def looking_for(reqeuest_number):
    if is_registered == True:
        name = user_name
        print("What item are you looking for:")
        item_name = input("Item Name: ")
        item_description = input("Item Description: ")
        max_price = input("Max Price: ")
        msg = f"LOOKING_FOR, {str(request_number)}, {name}, {item_name}, {item_description}, {max_price}"
        return msg
    else:
        return None


# checks the reply message from the server to determine if the user is registered or not
# (we can add more logic here for other cases)
def recieve_logic(reply):
    global is_registered
    feedback = reply
    if re.search(rf'\b{"REGISTERED"}\b', feedback):
        is_registered = True
    elif re.search(rf'\b{"DEREGISTERED"}\b', feedback):
        is_registered = False


# start of the logic of constantly listening for messages from the server


def receive_messages():
    while True:
        try:
            d = s.recvfrom(1024)
            reply = d[0].decode("utf-8")
            addr = d[1]
            print(f"\nServer reply [{addr[0]}, {addr[1]}]: {reply}\n")
            recieve_logic(reply)
        except socket.error as msg:
            print("Error Occurred!")


# creates a thread to constantly listen for messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Sending a message to the server
while True:
    user_input = int(
        input(
            f"""Please choose one of the options below:\n
    [1] - Register
    [2] - De-Register
    [3] - Look for an Item

-> """
        )
    )

    request_msg = user_request(user_input)

    # Sending the request message to the server
    if request_msg is not None:
        try:
            s.sendto(request_msg.encode("utf-8"), (server_host, server_port))
            request_number += 1
            update_request_number(request_number)
        except socket.error as msg:
            print("Error Occurred!")
    else:
        print("User not registered! Please register first.")
