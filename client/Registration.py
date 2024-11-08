def register(client_socket, server_ip, server_port, name, client_ip, udp_port, tcp_port, rq_number):
    message = f"REGISTER {rq_number} {name} {client_ip} {udp_port} {tcp_port}"
    client_socket.sendto(message.encode('utf-8'), (server_ip, server_port))
    response, _ = client_socket.recvfrom(1024)
    return response.decode('utf-8')

def deregister(client_socket, server_ip, server_port, name, rq_number):
    message = f"DE-REGISTER {rq_number} {name}"
    client_socket.sendto(message.encode('utf-8'), (server_ip, server_port))
    response, _ = client_socket.recvfrom(1024)
    return response.decode('utf-8')
