import json
import socket
import random
import sys
import threading
import time
from enum import Enum

# Defining the socket parameters
HOST = "0.0.0.0"  # listening on all available network interfaces
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

print("Socket was successfully bound!\n")

# Setting a timeout for the socket
s.settimeout(5)

# Load or initialize data




# Creating a mutex lock to avoid race conditions
lock = threading.Lock()

# User request handler
def handle_request(user_request, data, addr):
    if user_request == "REGISTER":
        handle_registration(data, addr)
    elif user_request == "DE-REGISTER":
        handle_deregistration(data, addr)
    elif user_request == "LOOKING_FOR":
        handle_looking_for(data, addr)
    elif user_request == "MAKE_OFFER":
        handle_make_offer(data, addr)
    else:
        print("Invalid Request!")

# Handles the register request
def handle_registration(data, addr):
    request_type, request_number, name, ip, udp, tcp = data.split(", ")
    lock.acquire()
    try:
        try:
            with open("users.json", "r") as json_file:
                users = json.load(json_file)
        except FileNotFoundError:
            users = {}
        if name not in users:
            users[name] = {
                "ip": ip,
                "udp": udp,
                "tcp": tcp,
                "status": UserStatus.REGISTERED.name,
            }
            with open("users.json", "w") as json_file:
                json.dump(users, json_file, indent=4)
            reply_msg = f"REGISTERED, {request_number}"
        elif users[name]["ip"] == ip:
            users[name] = {
                "ip": ip,
                "udp": udp,
                "tcp": tcp,
                "status": UserStatus.REGISTERED.name,
            }
            with open("users.json", "w") as json_file:
                json.dump(users, json_file, indent=4)
            reply_msg = f"REGISTERED, {request_number}"
        else:
            reply_msg = f"REGISTER-DENIED, {request_number}, The user already exists in the system!"
    finally:
        lock.release()

    s.sendto(reply_msg.encode("utf-8"), addr)
    print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")

# Handles the de-registration request
def handle_deregistration(data, addr):
    request_type, request_number, name, ip, udp, tcp = data.split(", ")
    lock.acquire()
    try:
        try:
            with open("users.json", "r") as json_file:
                users = json.load(json_file)
        except FileNotFoundError:
            users = {}
        if (
            name in users
            and users[name]["status"] == UserStatus.REGISTERED.name
            and users[name]["ip"] == ip
        ):
            users[name]["status"] = UserStatus.DEREGISTERED.name
            with open("users.json", "w") as json_file:
                json.dump(users, json_file, indent=4)
            reply_msg = f"DEREGISTERED, [{request_number}], [{name}] from the server!"
        elif name in users and users[name]["ip"] != ip:
            reply_msg = f"[{request_number}], You do not have access to this User: [{name}]!"
        else:
            reply_msg = f"[{request_number}], User [{name}] does not exist in the server!"
    finally:
        lock.release()

    s.sendto(reply_msg.encode("utf-8"), addr)
    print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")

# Generate unique item ID
def item_id_generator():
    while True:
        random_num = random.randint(1000, 9999)
        if random_num not in num_list:
            num_list.append(random_num)
            return str(random_num)

# Handles the looking_for request
def handle_looking_for(data, addr):
    request_type, request_number, name, item_name, item_description, max_price = (
        data.split(", ")
    )
    item_id = item_id_generator()

    # Prepare the search message
    search_msg = f"SEARCH, {request_number}, {item_name}, {item_description}, {item_id}"

    print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")

    # Update wanted_items
    lock.acquire()
    try:
        try:
            with open("Wanted_Items.json", "r") as json_file:
                wanted_items = json.load(json_file)
        except FileNotFoundError:
            wanted_items = {}
        wanted_items[item_id] = {
            "request_number": request_number,
            "item_name": item_name,
            "item_description": item_description,
            "max_price": max_price,
            "buyer": name,
        }
        with open("Wanted_Items.json", "w") as json_file:
            json.dump(wanted_items, json_file, indent=4)
    finally:
        pass

    # Broadcast the search message to all other clients
    try:
        try:
            with open("users.json", "r") as json_file:
                users = json.load(json_file)
        except FileNotFoundError:
            users = {}
        for user in users:
            if user != name and users[user]["status"] == UserStatus.REGISTERED.name:
                s.sendto(
                    search_msg.encode("utf-8"),
                    (users[user]["ip"], int(users[user]["udp"])),
                )
    finally:
        lock.release()

    # Start wait_and_compare in a new thread
    threading.Thread(target=wait_offer_handler, args=(item_id,)).start()

# Handles the make_offer request
def handle_make_offer(data, addr):
    request_type, request_number, name, item_id, price = data.split(", ")

    lock.acquire()

    try:
        try:
            with open("Offers.json", "r") as json_file:
                offers = json.load(json_file)
        except FileNotFoundError:
            offers = {}

        if item_id in offers:
            offers[item_id].append({
                "request_number": request_number,
                "price": price,
                "seller": name,
            })
        else:
            offers[item_id] = [{
                "request_number": request_number,
                "price": price,
                "seller": name,
            }]

        with open("Offers.json", "w") as json_file:
            json.dump(offers, json_file, indent=4)
    finally:
        lock.release()

    print(f"Message received from [{addr[0]}, {addr[1]}]: {data}")

# Waits for offers and compares them after the waiting period
def wait_offer_handler(item_id):
    # Wait for 5 minutes (300 seconds)
    time.sleep(60)

    best_offer = compare_prices(item_id)

    item = fetch_item_data(item_id)
    buyer = fetch_user_data(item["buyer"])


    if best_offer:
        print(f"Best Offer for item {item_id}: {best_offer}")

        seller = fetch_user_data(best_offer["seller"])

        if float(best_offer["price"]) <= float(item["max_price"]):

            # Notify buyer and seller

            #send the reserve message to the seller
            Reserve_msg = f"RESERVE, {item['request_number']}, {item_id}, {item['item_name']}, {best_offer['price']}"
            s.sendto(Reserve_msg.encode("utf-8"), (seller["ip"], int(seller["udp"])))


            #send found msg to buyer
            found_msg = f"FOUND, {item['request_number']}, {item_id}, {item['item_name']}, {best_offer['price']}"
            s.sendto(found_msg.encode("utf-8"), (buyer["ip"], int(buyer["udp"])))

        elif float(best_offer["price"]) > float(item["max_price"]):
            # negotiate with the seller
            negotiation_msg = f"NEGOTIATE, {item['request_number']}, {item_id}, {item['item_name']}, {item['max_price']}"
            s.sendto(negotiation_msg.encode("utf-8"), (seller["ip"], int(seller["udp"])))


    else:
        not_available_msg = f"NOT-AVAILABLE, {item['request_number']}, {item_id}, {item['item_name']}, {item['max_price']}"
        s.sendto(not_available_msg.encode("utf-8"), (buyer["ip"], int(buyer["udp"])))


# Compares offers to find the lowest price
def compare_prices(item_id):
    lock.acquire()
    try:
        # Read the offers from 'Offers.json'
        try:
            with open("Offers.json", "r") as json_file:
                offers = json.load(json_file)
        except FileNotFoundError:
            offers = {}

        if item_id in offers:
            offers_list = offers[item_id]
            # Find the best offer based on the lowest price
            best_offer = min(offers_list, key=lambda x: float(x["price"]))

            # Update the offers to keep only the best offer
            offers[item_id] = [best_offer]

            # Write the updated offers back to the JSON file
            with open("Offers.json", "w") as json_file:
                json.dump(offers, json_file, indent=4)

            return best_offer
        else:
            return None
    finally:
        lock.release()


def fetch_item_data(item_id):
    lock.acquire()
    try:
        with open("Wanted_Items.json", "r") as json_file:
            wanted_items = json.load(json_file)
    finally:
        lock.release()

    return wanted_items[item_id]

def fetch_user_data(user_name):
    lock.acquire()
    try:
        try:
            with open("users.json", "r") as json_file:
                users = json.load(json_file)
        except FileNotFoundError:
            users = {}
    finally:
        lock.release()

    return users[user_name]



# Main server loop
while True:
    try:
        d = s.recvfrom(1024)
        data = d[0].decode("utf-8")
        addr = d[1]

        if not data:
            break
        else:
            user_request = data.split(",")[0]
            client_thread = threading.Thread(
                target=handle_request, args=(user_request, data , addr)
            )
            client_thread.start()
            # Removed client_thread.join() to prevent blocking
    except socket.timeout:
        pass
    except KeyboardInterrupt:
        print("Server is shutting down.")
        break
    except Exception as e:
        print(f"An error occurred: {e}")

# Closing the UDP socket
s.close()
