#Importing necessary libraries
import json
import re
import socket
import sys
import threading

# defining the socket parameters (IP + PORT)
client_host = "0.0.0.0"  # listening on all available netwrok interfaces
client_port = 4444  # arbitrary port number for the client socket
client_TCP_port = 6000  # arbitrary number
server_TCP_port = 6000 #arbitrary number

#Creating the udp socket 
try:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print(f"Socket creation failed!")
    sys.exit()

#Binding the upd socket to the client's host and port number
udp_socket.bind((client_host, client_port))

#Loads the current value of the request number.
#If not existent, it resets and starts from '1'
def get_request_number():
    try:
        with open("rq_number.json", "r") as json_file:
            saved_request_number = json.load(json_file)["request_number"]
    except FileNotFoundError:
        saved_request_number = 1
        with open("rq_number.json", "w") as json_file:
            json.dump({"request_number": saved_request_number}, json_file)
    return saved_request_number

#Fetching the request number
request_number = get_request_number()

#Returns the server's IP address stored in a local json file
#The value needs to be manually modified if the testing environment changes
def get_server_ip():
    try:
        with open("Server_IP.json", "r") as json_file:
            IP_json = json.load(
                json_file
            ) 

    except FileNotFoundError:
        IP_json = (
            {}
        )

    return IP_json["Server"]["ip"]

# Socket parameters of the server socket
server_host = get_server_ip() #Fetching the server's ip
server_port = 5000 #Arbitrary number for server's port

# Variable to track the registration status of the client
# Used to allow the users to use some functions only if they are registered
is_registered = False

#Variable to store the name of the user
user_name = None

# Negotiation and Found dictionaries to store the incoming found and negotiation items
negotiation_items_info = {}
found_items_info = {}

#Updates the rq number and stores it in the json file after each request sent to the server
def update_request_number(request_number):
    with open("rq_number.json", "w") as json_file:
        json.dump({"request_number": request_number}, json_file)

#Switch statement to handle different client requests
def user_request(user_input):
    if user_input == 1:
        return user_registration(request_number)
    elif user_input == 2:
        return user_deregistration(request_number)
    elif user_input == 3:
        return looking_for(request_number)
    elif user_input == 4:
        return make_offer(request_number)
    elif user_input == 5:
        return accept_refuse()
    elif user_input == 6:
        return buy_cancel()
    else:
        print(f"Invalid option! Please try again.")


# Returns the registration request message to be sent to the server
def user_registration(request_number):
    print(
        f"Enter the following information to register yourself within the shopping system:\n"
    )
    name = input(f"Name: ")
    ip = socket.gethostbyname(socket.gethostname())
    udp = client_port
    tcp = client_TCP_port
    msg = f"REGISTER, {str(request_number)}, {name}, {ip}, {udp}, {tcp}" 
    global user_name
    user_name = name
    return msg


# Returns the de-registration request message to be sent to the server
def user_deregistration(request_number):
    name = input(f"Enter the name of the user to be de-registered: ")
    ip = socket.gethostbyname(socket.gethostname())
    udp = client_port
    tcp = client_TCP_port
    msg = f"DE-REGISTER, {str(request_number)}, {name}, {ip}, {udp}, {tcp}"
    global user_name
    user_name = None
    return msg


# Returns the looking_for request message to be sent to the server
def looking_for(reqeuest_number):
    if is_registered == True:
        global user_name
        name = user_name
        print("What item are you looking for:")
        item_name = input("Item Name: ")
        item_description = input("Item Description: ")
        max_price = input("Max Price: ")
        msg = f"LOOKING_FOR, {str(request_number)}, {name}, {item_name}, {item_description}, {max_price}"
        return msg
    else:
        return None

#Returns the offer request message to be sent to the server
def make_offer(request_number):
    if is_registered == True:
        global user_name
        name = user_name
        print("What item are you making an offer for:")
        item_id = input("Item ID: ")
        price = input("Price: ")
        msg = f"MAKE_OFFER, {str(request_number)}, {name}, {item_id}, {price}"
        return msg
    else:
        return None

#Returns the accept/refuse message to be sent to the server
def accept_refuse():
    if is_registered == True:
        print("What item are you accepting/refusing the negotiation for:")
        item_id = input("Item ID: ")

        if item_id in negotiation_items_info:
            request_number, item_name, price = negotiation_items_info[item_id]

            accept = input("Do you want to accept the negotiation (Y/N): ")

            if accept == "Y":
                msg = f"ACCEPT, {request_number}, {item_id}, {item_name}, {price}"
            elif accept == "N":
                msg = f"REFUSE, {request_number}, {item_id}, {item_name}, {price}"
            else:
                print("Invalid input")
        else:
            print("Invalid item ID")

        return msg
    else:
        return None


#Returns the buy/cancel message to be sent to the server
def buy_cancel():
    if is_registered == True:
        print("What item are you buying/cancelling the deal for:")
        item_id = input("Item ID: ")

        if item_id in found_items_info:
            request_number, item_name, price = found_items_info[item_id]
            buy = input("Do you want to buy the item (Y/N): ")
            if buy == "Y":
                msg = f"BUY, {request_number}, {item_id}, {item_name}, {price}"
            elif buy == "N":
                msg = f"CANCEL, {request_number}, {item_id}, {item_name}, {price}"
            else:
                print("Invalid input")
        else:
            print("Invalid item ID")
        return msg
    else:
        return None

#Handles the tcp connection with the server during the buying phase
def tcp_connection(request_number):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.connect((server_host, client_TCP_port))  # Connect to the server
        print(f"Connected to {server_host}:{client_TCP_port}")

        global user_name

        tcp_socket.sendall(b"Hello, Server!")  # Send a message to the server

        data = tcp_socket.recv(1024)
        print(f"Received: {data.decode()}")

        CC = input(f"Now enter these details for the transaction: CC: ")
        CC_Exp_Date = input(f"CC Expiration Date: ")
        Address = input(f"Address: ")

        inform_respond_mes = f"INFORM_Req, {request_number}, {user_name}, {CC}, {CC_Exp_Date}, {Address}!"

        tcp_socket.sendall(inform_respond_mes.encode("utf-8"))

        # Receive a response from the server
        data = tcp_socket.recv(1024)
        print(f"Received: {data.decode()}")



# Defines the logic for the client's behaviour upon reception of various server's messages
def recieve_logic(reply):
    global is_registered
    feedback = reply

    #Updates the cient's registration status based on the server's response
    if re.search(rf'\b{"REGISTERED"}\b', feedback):
        is_registered = True
    elif re.search(rf'\b{"DEREGISTERED"}\b', feedback):
        is_registered = False

    #Creates a new item in the negotiation_items_info dictionary after a negotiation response
    if re.search(rf'\b{"NEGOTIATE"}\b', feedback):
        request_type, request_number, item_id, item_name, max_price = feedback.split(", ")
        negotiation_items_info[item_id] = (request_number, item_name, max_price)

    #Creates a new item in the found_items_info dictionary after a found response
    if re.search(rf'\b{"FOUND"}\b', feedback):
        request_type, request_number, item_id, item_name, price = feedback.split(", ")
        found_items_info[item_id] = (request_number, item_name, price)

    #Starts the tcp connection after a start_tcp response
    if re.search(rf'\b{"START_TCP"}\b', feedback):
        request_type, request_number = feedback.split(", ")
        tcp_connection(request_number)


# Listener loop for incoming server messages
# Handles the incoming responses using the receive_logic() method
def receive_messages():
    while True:
        try:
            d = udp_socket.recvfrom(1024)
            reply = d[0].decode("utf-8")
            addr = d[1]
            print(f"\nServer reply [{addr[0]}, {addr[1]}]: {reply}\n")
            recieve_logic(reply)
        except socket.error as msg:
            print("Error Occurred! 2.")


# creates a thread to constantly listen for messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Printing a welcome message 
print(f"Welcome to the Peer-to-Peer Shopping System!\n")
# Main loop for handling client's messages
while True:
    user_input = int(
        input(
            f"""Please choose one of the options below:\n
    [1] - Register
    [2] - De-Register
    [3] - Look for an Item
    [4] - Make an Offer
    [5] - Accept/Refuse an Offer
    [6] - Buy/Cancel a Deal

-> """
        )
    )

    #Storing the message to be sent based on the user's input
    request_msg = user_request(user_input)

    # Sending the request message to the server
    if request_msg is not None:
        try:
            udp_socket.sendto(request_msg.encode("utf-8"), (server_host, server_port))
            request_number += 1
            update_request_number(request_number)
        except socket.error as msg:
            print("Error Occurred! 1.")
    else:
        print("User not registered! Please register first. (OR A msg doesnt exist to be sent.)")
