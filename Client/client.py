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
client_port = 4444  # arbitrary port number for the client socket
client_TCP_port = 5555  # arbitrary number for now

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print(f"Socket creation failed!")
    sys.exit()

s.bind((client_host, client_port))


def get_request_number():
    try:
        with open("rq_number.json", "r") as json_file:
            saved_request_number = json.load(json_file)["request_number"]
    except FileNotFoundError:
        saved_request_number = 1
        with open("rq_number.json", "w") as json_file:
            json.dump({"request_number": saved_request_number}, json_file)
    return saved_request_number


request_number = get_request_number()


def get_server_ip():
    try:
        with open("Server_IP.json", "r") as json_file:
            IP_json = json.load(
                json_file
            )  # loading the json file users' info into the dictionary of users

    except FileNotFoundError:
        IP_json = (
            {}
        )

    return IP_json["Server"]["ip"]


server_host = get_server_ip()

# Socket parameters of the server socket
server_port = 5000
is_registered = False

# Variable to track the registration status of the client
# Used to allow the users to use some functions only if they are registered
user_name = None
negotiation_items_info = {}
found_items_info = {}


def update_request_number(request_number):
    with open("rq_number.json", "w") as json_file:
        json.dump({"request_number": request_number}, json_file)


def user_request(user_input):
    match user_input:
        case 1:
            return user_registration(request_number)
        case 2:
            return user_deregistration(request_number)
        case 3:
            return looking_for(request_number)
        case 4:
            return make_offer(request_number)
        case 5:
            return accept_refuse()
        # case 6:
        #     return make_offer(request_number)
        case _:
            print(f"Invalid option! Please try again.")


# Swtich statement to handle different user requests


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
    global user_name
    user_name = name
    return msg


# Prepares the de-registration request message to be sent to the server
def user_deregistration(request_number):
    name = input(f"Enter the name of the user to be de-registered: ")
    ip = socket.gethostbyname(socket.gethostname())
    udp = client_port
    tcp = client_TCP_port
    msg = f"DE-REGISTER, {str(request_number)}, {name}, {ip}, {udp}, {tcp}"
    global user_name
    user_name = None
    return msg


print(f"Welcome to the Peer-to-Peer Shopping System!\n")


# Sends a looking_for request to the server to indicate a search for an item
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


# checks the reply message from the server to determine if the user is registered or not
# (we can add more logic here for other cases)
def recieve_logic(reply):
    global is_registered
    feedback = reply

    if re.search(rf'\b{"REGISTERED"}\b', feedback):
        is_registered = True
    elif re.search(rf'\b{"DEREGISTERED"}\b', feedback):
        is_registered = False

    if re.search(rf'\b{"NEGOTIATE"}\b', feedback):
        request_type, request_number, item_id, item_name, max_price = feedback.split(", ")
        negotiation_items_info[item_id] = (request_number, item_name, max_price)

    if re.search(rf'\b{"FOUND"}\b', feedback):
        request_type, request_number, item_id, item_name, price = feedback.split(", ")
        found_items_info[item_id] = (request_number, item_name, price)

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
    [4] - Make an Offer
    [5] - Accept/Refuse an Offer
    [6] - Buy/Cancel a Deal

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
        print("User not registered! Please register first. (OR A msg doesnt exist to be sent.)")
