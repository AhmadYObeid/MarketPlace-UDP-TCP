def register(client_socket, server_ip, server_port, name, client_ip, udp_port, tcp_port):
    message = f"REGISTER 1 {name} {client_ip} {udp_port} {tcp_port}"
    client_socket.sendto(message.encode('utf-8'), (server_ip, server_port))
    response, _ = client_socket.recvfrom(1024)
    return response.decode('utf-8')

def deregister(client_socket, server_ip, server_port, name):
    message = f"DE-REGISTER 2 {name}"
    client_socket.sendto(message.encode('utf-8'), (server_ip, server_port))
    response, _ = client_socket.recvfrom(1024)
    return response.decode('utf-8')
