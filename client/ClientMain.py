import socket
import json
import threading
import os

# Load client configuration
with open('config/client_config.json') as config_file:
    config = json.load(config_file)

SERVER_IP = config['SERVER_IP']
SERVER_PORT = config['SERVER_PORT']
UDP_PORT = 8000  # Default UDP port for client
TCP_PORT = 8001  # Default TCP port for client

RQ_FILE = "rq_number.txt"

def get_client_ip():
    # Detect the client's IP address.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

def load_rq_number():
    # Load the current RQ number from a file or initialize if it doesn't exist.
    if os.path.exists(RQ_FILE):
        with open(RQ_FILE, 'r') as file:
            return int(file.read().strip())
    return 0  # Default to 0 if the file doesn't exist

def save_rq_number(rq_number):
    # Save the current RQ number to a file.
    with open(RQ_FILE, 'w') as file:
        file.write(str(rq_number))

def get_next_rq_number():
    # Generate and increment the RQ number, and save it to file.
    rq_number = load_rq_number()
    next_rq = rq_number + 1
    save_rq_number(next_rq)
    return rq_number  # Use the current RQ number for this request

def send_registration(client_socket, name):
    rq = get_next_rq_number()
    ip_address = get_client_ip()
    message = f"REGISTER {rq} {name} {ip_address} {UDP_PORT} {TCP_PORT}"
    client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)
    print(f"Server response (RQ#: {rq}):", response.decode('utf-8'))

def send_deregistration(client_socket):
    name = input("Enter the name of the account you want to de-register: ")
    rq = get_next_rq_number()
    message = f"DE-REGISTER {rq} {name}"
    client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)
    print(f"De-registration response (RQ#: {rq}):", response.decode('utf-8'))

def main():
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    name = input("Enter your name: ")

    # Run registration in a thread
    reg_thread = threading.Thread(target=send_registration, args=(client_socket, name))
    reg_thread.start()
    reg_thread.join()

    # Prompt user to de-register before exiting
    deregister_prompt = input("Do you want to de-register? (yes/no): ").lower()
    if deregister_prompt == 'yes':
        deregister_thread = threading.Thread(target=send_deregistration, args=(client_socket,))
        deregister_thread.start()
        deregister_thread.join()

    client_socket.close()

if __name__ == "__main__":
    main()
