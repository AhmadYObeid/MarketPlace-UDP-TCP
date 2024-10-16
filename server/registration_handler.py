import json

def load_users(file_path):
    """Load users from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users, file_path):
    """Save users to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(users, file)

def handle_registration(message, users, max_clients):
    parts = message.split()
    if len(parts) < 6 and not (len(parts) == 3 and parts[0] == "DE-REGISTER"):
        return "ERROR: Invalid registration format."

    command = parts[0]
    rq_number = parts[1]

    if command == "REGISTER":
        name, client_ip, udp_port, tcp_port = parts[2], parts[3], int(parts[4]), int(parts[5])

        # Check if the name is already registered
        if name in users:
            return f"ERROR: User '{name}' is already registered."

        # Check if the server can handle more clients
        if len(users) >= max_clients:
            return "ERROR: Server cannot handle more clients."

        # Assign a new unique RQ#
        new_rq_number = len(users) + 1

        # Register the user
        users[name] = {
            "RQ#": new_rq_number,
            "IP": client_ip,
            "UDP_Port": udp_port,
            "TCP_Port": tcp_port
        }
        return f"SUCCESS: User '{name}' registered with RQ#: {new_rq_number}."

    elif command == "DE-REGISTER":
        name = parts[2]

        if name not in users:
            return f"ERROR: User '{name}' not found."

        del users[name]
        return f"SUCCESS: User '{name}' has been deregistered."

    else:
        return "ERROR: Unsupported command."
