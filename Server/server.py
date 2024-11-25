import json
import socket
import random
import sys
import threading  # Threading library to make the server multi-threaded
import time
from enum import Enum

# Defining the socket parameters
HOST = "0.0.0.0"  # listening on all available netwrok interfaces
PORT = 5000  # arbitrary port number chosen for the server socket

num_list = []

# User Status
class UserStatus(Enum):
    REGISTERED = "Registered"
    DEREGISTERED = "Deregistered"
    IDLE = "Idle"


# Creating the UDP socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Socket Created!\n")
except OSError as e:
    print(
        f"Failed to create the socket.\nError Code: {e.errno}\nMessage: {e.strerror}\n"
    )
    sys.exit()

# Binding the socket to the host and port number
try:
    s.bind((HOST, PORT))
except OSError as e:
    print(f"Binding failed!\nError Code: {e.errno}\nMessage: {e.strerror}\n")
    sys.exit()

print("Socket was successfuly bound!\n")

# Setting a timeout for the socket
# If no data is received within 2 seconds, the timeout exception is raised
# This allows the program to escape from the infinite loop of recvfrom()
# Used to allow KeyboardInterrupt to trigger
s.settimeout(5)


# Implements a switch statement to handle the different requests coming from the client
try:
    with open("users.json", "r") as json_file:
        users = json.load(
            json_file
)  # loading the json file users' info into the dictionary of users

except FileNotFoundError:
    users = (
        {}
    )  # JSON file does not exist, meaning no users have registred yet, therefore we start fresh

try:
    with open("Wanted_Items.json", "r") as json_file:
        wanted_items = json.load(
            json_file
        )
except FileNotFoundError:
    wanted_items = (
        {}
    )

try:
    with open("Offers.json", "r") as json_file:
        offers = json.load(
            json_file
        )
except FileNotFoundError:
    offers = (
        {}
    )
# Creating a dictionary to store the users information within the server (the dictionary is restored using the json file everytime the server runs again)
lock = threading.Lock()
# Creating a mutex lock to avoid race conditions for the users.json file
def handle_request(user_request, data, addr):
    match user_request:
        case "REGISTER":
            return handle_registration(data, addr)
        case "DE-REGISTER":
            return handle_deregistration(data, addr)
        case "LOOKING_FOR":
            return handle_looking_for(data, addr)
        case "MAKE_OFFER":
            return handle_make_offer(data, addr)
        case _:
            print("Invalid Request!")


def handle_registration(data, addr):
    request_type, request_number, name, ip, udp, tcp = data.split(
        ", "
    )  # splitting the data into the different fields provided
    # TODO: Add the condition where the server cannot add any more clients
    # Acquiring the lock before modifying the 'users' dictionary
    lock.acquire()
    # Encapsulating the lock release within a try-finally to ensure its release even if an error occurs
    try:
        if name not in users:
            # Adding the user into the users dictionary
            users[name] = {
                "ip": ip,
                "udp": udp,
                "tcp": tcp,
                "status": UserStatus.REGISTERED.name,
            }
            # Save the user info in the users.json file
            with open("users.json", "w") as json_file:
                json.dump(users, json_file, indent=4)

            reply_msg = f"REGISTERED, {request_number}"

        elif (
            name in users
            and users[name]["ip"] == ip
        ):
            users[name] = {
                "ip": ip,
                "udp": udp,
                "tcp": tcp,
                "status": UserStatus.REGISTERED.name,
            }
            # Save the user info in the users.json file
            with open("users.json", "w") as json_file:
                json.dump(users, json_file, indent=4)

            reply_msg = f"REGISTERED, {request_number}"

        else:
            reply_msg = f"REGISTER-DENIED, {request_number}, The user already exists in the system!"
    finally:
        lock.release()  # Releasing the lock after successful modification

    # Sending the handled request message back to the client
    s.sendto(reply_msg.encode("utf-8"), addr)
    print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")
# Handles the register request


def handle_deregistration(data, addr):

    request_type, request_number, name, ip, udp, tcp = data.split(
        ", "
    )  # splitting the data into the different fields provided

    # Acquiring the lock before modifying the 'users' dictionary
    lock.acquire()
    # Encapsulating the lock release within a try-finally to ensure its release even if an error occurs
    try:
        if (
            name in users
            and users[name]["status"] == UserStatus.REGISTERED.name
            and users[name]["ip"] == ip
        ):

            users[name] = {
                "ip": ip,
                "udp": udp,
                "tcp": tcp,
                "status": UserStatus.DEREGISTERED.name,
            }

            # Updating the users.json file with the changes user changes
            with open("users.json", "w") as json_file:
                json.dump(users, json_file, indent=4)

            reply_msg = f"DEREGISTERED, [{name}] from the server!\n"
        elif users[name]["ip"] != ip:
            reply_msg = (
                f"[{request_number}], You do not have access to this User: [{name}]!\n"
            )
        else:
            reply_msg = (
                f"[{request_number}], User [{name}] does not exist in the server!\n"
            )
    finally:
        lock.release()  # Releasing the lock after successful modification

    # Sending the handled request message back to the client
    s.sendto(reply_msg.encode("utf-8"), addr)
    print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")
# Handles the de-registration request

def item_id_generator():
    random_num = random.randint(1000, 9999)

    if random_num in num_list:
        item_id_generator()

    num_list.append(random_num)
    return random_num



# THE FOLLOWING IS A DANGEROUS EXPERIMENTAL CODE WITH A SEVERE LOGICAL ERROR
############################################################################################################
# Handles the looking_for request
def wait_and_compare(item_id):
    # 5 minutes timer to wait for offers
    time.sleep(30)
    best_price = compare_prices(item_id)
    print(f"Best Price: {best_price}")

def handle_looking_for(data, addr):
    request_type, reqeuest_number, name, item_name, item_description, max_price = (
        data.split(", ")
    )
    item_id = item_id_generator()


    # Preparing the reply message to be sent to all client of the system
    search_msg = (
        f"SEARCH, {reqeuest_number}, {item_name}, {item_description}, {item_id}"
    )

    print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")

    # Acquiring the lock before reading from the users dictionary
    lock.acquire()

    wanted_items[item_id] = {
        "request_number": reqeuest_number,
        "item_name": item_name,
        "item_description": item_description,
        "max_price": max_price,
        "buyer": name,
    }
    with open("Wanted_Items.json", "w") as json_file:
        json.dump(wanted_items, json_file, indent=4)

    try:
        for user in users:
            if user != name and users[user]["status"] == UserStatus.REGISTERED.name:
                # Sending the search message to all clients except the buyer
                s.sendto(
                    search_msg.encode("utf-8"),
                    (users[user]["ip"], int(users[user]["udp"])),
                )
            else:
                pass
    finally:
        lock.release()

def handle_make_offer(data, addr):

    request_type, reqeuest_number, name, item_id, price = (
        data.split(", ")
    )
    lock.acquire()
    try:
        if item_id in offers:
            offers[item_id].append({
                "request_number": reqeuest_number,
                "price": price,
                "seller": name,
            })
        else:
            offers[item_id] = [{
                "request_number": reqeuest_number,
                "price": price,
                "seller": name,
            }]

        with open("Offers.json", "w") as json_file:
            json.dump(offers, json_file, indent=4)
    finally:
        lock.release()

    print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")



def compare_prices(item_id):
    lowest_offer = {"price": float("inf"), "seller": None}

    lock.acquire()

    try:
        with open("Offers.json", "r") as json_file:
            offers = json.load(
                json_file
            )
    except FileNotFoundError:
        offers = (
            {}
        )

    try:
        if item_id in offers:
            for offer in offers[item_id]:
                price = float(offer["price"])
                name = offer["seller"]
                print(f"Price: {price}, Seller: {name}")
    finally:
        lock.release()

##############################################################################################################################



# Listening for client requests indefinitely
while True:
    try:
        d = s.recvfrom(
            1024
        )  # receiving the data from the client with a buffer size of 1024 bytes
        data = d[0].decode(
            "utf-8"
        )  # storing the data after decoding it into string type
        addr = d[1]  # storing the socket parameters of the client (IP + PORT)

        # break the loop if there is no data sent from the client
        if not data:
            break
        # Multi-threading
        # Once the listener detects a client request, it creates a new thread and passes the handle_request method as target to handle the request
        else:
            user_request = data.split(",")[
                0
            ]  # splitting the request message sent by the client to only have the type of request (e.i. REGISTER, DE-REGISTER, etc...
            client_thread = threading.Thread(
                target=handle_request, args=(user_request, data, addr)
            )  # Creating a new thread to handle the coming client request
            client_thread.start()  # starting the thread
            client_thread.join()  # waiting for the thread to be complete before the next one can resume

    except socket.timeout:
        pass  # Continues to the next iteration without performing any error handling action
    except Exception as e:
        print(f"An error occurred: {e}")
# closing the UDP socket
s.close()
