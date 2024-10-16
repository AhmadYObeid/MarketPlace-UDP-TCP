import socket
import json

# Load client configuration
with open('config/client_config.json') as config_file:
    config = json.load(config_file)

SERVER_IP = config['SERVER_IP']
SERVER_PORT = config['SERVER_PORT']

def main():
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # User input for registration details
    name = input("Enter your name: ")
    ip_address = input("Enter your IP address: ")
    udp_port = int(input("Enter your UDP port: "))
    tcp_port = int(input("Enter your TCP port: "))

    # Format the registration message according to the expected format
    message = f"REGISTER 1 {name} {ip_address} {udp_port} {tcp_port}"

    # Send registration message to the server
    client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))

    # Wait for the response from the server
    response, _ = client_socket.recvfrom(1024)
    print("Server response:", response.decode('utf-8'))

    # Ask if the user wants to de-register before exiting
    deregister_prompt = input("Do you want to de-register? (yes/no): ").lower()
    if deregister_prompt == 'yes':
        deregister_name = input("Enter the name of the account you want to de-register: ")
        rq_number = 1  # You can assign or manage the RQ# appropriately.
        deregister_message = f"DE-REGISTER {rq_number} {deregister_name}"
        client_socket.sendto(deregister_message.encode('utf-8'), (SERVER_IP, SERVER_PORT))

        # Wait for the response from the server for de-registration
        deregister_response, _ = client_socket.recvfrom(1024)
        print("De-registration response:", deregister_response.decode('utf-8'))

    client_socket.close()

if __name__ == "__main__":
    main()
