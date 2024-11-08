import json
import threading

lock = threading.Lock()

def load_users(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users, file_path):
    with open(file_path, 'w') as file:
        json.dump(users, file)

def handle_registration(message, users, max_clients):
    parts = message.split()
    if len(parts) < 6 and not (len(parts) == 3 and parts[0] == "DE-REGISTER"):
        return "ERROR: Invalid registration format."

    command = parts[0]
    rq_number = parts[1]  # Extract RQ number for response tracking

    if command == "REGISTER":
        name, client_ip, udp_port, tcp_port = parts[2], parts[3], int(parts[4]), int(parts[5])

        with lock:
            if name in users:
                return f"ERROR: User '{name}' is already registered. (RQ#: {rq_number})"

            if len(users) >= max_clients:
                return f"ERROR: Server cannot handle more clients. (RQ#: {rq_number})"

            # Register the user
            users[name] = {
                "RQ#": rq_number,
                "IP": client_ip,
                "UDP_Port": udp_port,
                "TCP_Port": tcp_port
            }
            save_users(users, 'data/server_data.json')
        
        return f"SUCCESS: User '{name}' registered. (RQ#: {rq_number})"

    elif command == "DE-REGISTER":
        name = parts[2]

        with lock:
            if name not in users:
                return f"ERROR: User '{name}' not found. (RQ#: {rq_number})"
            del users[name]
            save_users(users, 'data/server_data.json')
        
        return f"SUCCESS: User '{name}' has been deregistered. (RQ#: {rq_number})"

    else:
        return f"ERROR: Unsupported command. (RQ#: {rq_number})"
