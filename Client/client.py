import socket
import sys
import json
import threading
import random
import time

# Socket parameters
client_host = "0.0.0.0"
client_port = 2000
client_TCP_port = 2100
server_host = "localhost"
server_port = 5000

# Load and update request number
def load_request_number():
    try:
        with open('client_config.json', 'r') as json_file:
            data = json.load(json_file)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return 1

def update_request_number(request_number):
    with open("client_config.json", "w") as json_file:
        json.dump(request_number, json_file, indent=4)

request_number = load_request_number()

# UDP client socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print("Socket creation failed!")
    sys.exit()

s.bind((client_host, client_port))

# Define user actions
def user_request(user_input):
    match user_input:
        case 1:
            return user_registration(request_number)
        case 2:
            return user_deregistration(request_number)
        case 3:
            return item_search(request_number)
        case _:
            print("Invalid option! Please try again.")

# Registration request
def user_registration(request_number):
    print("Enter registration details:")
    name = input("Name: ")
    ip = socket.gethostbyname(socket.gethostname())
    udp = client_port
    tcp = client_TCP_port
    msg = f"REGISTER, {str(request_number)}, {name}, {ip}, {udp}, {tcp}"
    return msg

# De-registration request
def user_deregistration(request_number):
    name = input("Enter the name of the user to de-register: ")
    ip = socket.gethostbyname(socket.gethostname())
    udp = client_port
    msg = f"DE-REGISTER, {name}, {ip}, {udp}"
    return msg

# Item search request
def item_search(request_number):
    print("Enter details for item search:")
    name = input("Your Name: ")
    item_name = input("Item Name: ")
    item_description = input("Item Description: ")
    max_price = input("Max Price: ")
    msg = f"LOOKING_FOR, {str(request_number)}, {name}, {item_name}, {item_description}, {max_price}"
    return msg

print("Welcome to the Peer-to-Peer Shopping System!")

# Main loop for client requests
while True:
    user_input = int(input("""Choose an option:
  [1] - Register
  [2] - De-Register
  [3] - Search for an Item
-> """))

    request_msg = user_request(user_input)

    try:
        s.sendto(request_msg.encode('utf-8'), (server_host, server_port))
        request_number += 1
        update_request_number(request_number)

        d = s.recvfrom(1024)
        reply = d[0].decode('utf-8')
        addr = d[1]

        print(f"\nServer reply [{addr[0]}, {addr[1]}]: {reply}\n")
    
    except socket.error as msg:
        print("Error occurred!")
