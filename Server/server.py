import socket
import threading
import sys
import json
import random

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

# Users and items
try:
    with open('users.json', 'r') as json_file:
        users = json.load(json_file)
except FileNotFoundError:
    users = {}

items = {}  # Items available from users
lock = threading.Lock()

# Request handler
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
    _, request_number, name, ip, udp, tcp = data.split(", ")
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

# De-registration handler
def handle_deregistration(data, addr):
    _, name, client_ip, client_udp = data.split(", ")
    lock.acquire()
    try:
        if name in users and users[name]["ip"] == client_ip and users[name]["udp"] == client_udp:
            del users[name]
            with open('users.json', 'w') as json_file:
                json.dump(users, json_file, indent=4)
            reply_msg = f"User [{name}] removed!"
        else:
            reply_msg = f"De-registration failed!"
    finally:
        lock.release()

    s.sendto(reply_msg.encode('utf-8'), addr)

# Search handler
def handle_search_request(data, addr):
    _, request_number, buyer_name, item_name, item_description, max_price = data.split(", ")
    search_msg = f"SEARCH, {request_number}, {item_name}, {item_description}"
    for user, details in users.items():
        if user != buyer_name:
            s.sendto(search_msg.encode('utf-8'), (details["ip"], int(details["udp"])))

# Offer handler
def handle_offer(data, addr):
    _, request_number, name, item_name, price = data.split(", ")
    print(f"Offer received: {name} offers {item_name} for {price}")

# Main loop
while True:
    try:
        d = s.recvfrom(1024)
        data = d[0].decode('utf-8')
        addr = d[1]
        request_type = data.split(",")[0]
        threading.Thread(target=handle_request, args=(request_type, data, addr)).start()
    except socket.timeout:
        pass

s.close()
