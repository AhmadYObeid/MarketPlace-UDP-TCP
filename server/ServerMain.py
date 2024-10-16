import socket
import json
from registration_handler import handle_registration, load_users, save_users

# Load server configuration
with open('config/server_config.json') as config_file:
    config = json.load(config_file)

SERVER_IP = config['SERVER_IP']
SERVER_PORT = config['SERVER_PORT']
MAX_CLIENTS = config.get('MAX_CLIENTS', 100)  # Default limit is 100 clients

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"Server is running on {SERVER_IP}:{SERVER_PORT}")

    # Load users from persistent storage
    users = load_users('data/server_data.json')

    while True:
        message, client_address = server_socket.recvfrom(1024)
        decoded_message = message.decode('utf-8')
        response = handle_registration(decoded_message, users, MAX_CLIENTS)

        # Save the updated users dictionary
        save_users(users, 'data/server_data.json')

        # Send the response back to the client
        server_socket.sendto(response.encode('utf-8'), client_address)

if __name__ == "__main__":
    main()
