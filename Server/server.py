import socket
import threading
import sys
import json
import random
import time

# Server parameters
HOST = '0.0.0.0'
PORT = 5000

# UDP socket creation and binding
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Socket created!\n")
except OSError as e:
    print(f"Socket creation failed: {e}")
    sys.exit()

try:
    s.bind((HOST, PORT))
except OSError as e:
    print(f"Binding failed: {e}")
    sys.exit()

print("Socket successfully bound!\n")

s.settimeout(5)

# Load existing users and items
try:
    with open('users.json', 'r') as json_file:
        users = json.load(json_file)
except FileNotFoundError:
    users = {}

items = {}  # This will hold items each user has

lock = threading.Lock()

# Method to simulate item ownership
def has_item():
    return random.choice([True, False])

# Handle different request types
def handle_request(request_type, data, addr):
    match request_type:
        case "REGISTER":
            return handle_registration(data, addr)
        case "DE-REGISTER":
            return handle_deregistration(data, addr)
        case "LOOKING_FOR":
            return handle_search_request(data, addr)
        case "OFFER":
            return handle_offer(data, addr)
        case _:
            print("Invalid request!")

# Registration handler
def handle_registration(data, addr):
    request_type, request_number, name, ip, udp, tcp = data.split(", ")
    lock.acquire()
    try:
        if name not in users:
            users[name] = {"ip": ip, "udp": udp, "tcp": tcp}
            with open('users.json', 'w') as json_file:
                json.dump(users, json_file, indent=4)
            reply_msg = f"REGISTERED, {request_number}"
        else:
            reply_msg = f"REGISTER-DENIED, {request_number}, User already exists!"
    finally:
        lock.release()

    s.sendto(reply_msg.encode('utf-8'), addr)
    print(f"Message from [{addr[0]}, {addr[1]}]: {data}")

# De-registration handler
def handle_deregistration(data, addr):
    request_type, name, client_ip, client_udp = data.split(", ")
    lock.acquire()
    try:
        if name in users:
            user_info = users[name]
            if user_info['ip'] == client_ip and user_info['udp'] == client_udp:
                del users[name]
                with open('users.json', 'w') as json_file:
                    json.dump(users, json_file, indent=4)
                reply_msg = f"User [{name}] removed!"
            else:
                reply_msg = f"De-registration failed: IP/UDP mismatch."
        else:
            reply_msg = f"User [{name}] does not exist!"
    finally:
        lock.release()

    s.sendto(reply_msg.encode('utf-8'), addr)
    print(f"Message from [{addr[0]}, {addr[1]}]: {data}")

# Search handler
def handle_search_request(data, addr):
    _, request_number, buyer_name, item_name, item_description, max_price = data.split(", ")
    search_msg = f"SEARCH, {request_number}, {item_name}, {item_description}"
    
    for user, details in users.items():
        if user != buyer_name:
            has_item_response = has_item()
            if has_item_response:
                offer_msg = f"OFFER, {request_number}, {user}, {item_name}, {random.randint(int(max_price), int(max_price) + 20)}"
                s.sendto(offer_msg.encode('utf-8'), (details['ip'], int(details['udp'])))
                print(f"Sent offer from {user} for '{item_name}'")

    print(f"Sent search request for '{item_name}' to all users except {buyer_name}")

# Offer handler (received from clients)
def handle_offer(data, addr):
    _, request_number, name, item_name, price = data.split(", ")
    print(f"Offer received from {name}: Item '{item_name}' at price {price}")

# Main loop to listen for requests
while True:
    try:
        d = s.recvfrom(1024)
        data = d[0].decode('utf-8')
        addr = d[1]

        if not data:
            break
        else:
            request_type = data.split(',')[0]
            client_thread = threading.Thread(target=handle_request, args=(request_type, data, addr))
            client_thread.start()
            client_thread.join()

    except socket.timeout:
        pass

s.close()
