import socket
import json
import threading
from registration_handler import handle_registration, load_users, save_users

# Load server configuration
with open('config/server_config.json') as config_file:
    config = json.load(config_file)

SERVER_IP = config['SERVER_IP']
SERVER_PORT = config['SERVER_PORT']
MAX_CLIENTS = config.get('MAX_CLIENTS', 100)

# Initialize users with data from JSON file
users = load_users('data/server_data.json')
lock = threading.Lock()

def client_handler(message, client_address, server_socket):
    decoded_message = message.decode('utf-8')

    with lock:
        response = handle_registration(decoded_message, users, MAX_CLIENTS)
        save_users(users, 'data/server_data.json')

    server_socket.sendto(response.encode('utf-8'), client_address)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"Server is running on {SERVER_IP}:{SERVER_PORT}")

    while True:
        message, client_address = server_socket.recvfrom(1024)
        threading.Thread(target=client_handler, args=(message, client_address, server_socket)).start()

if __name__ == "__main__":
    main()
