import socket
import threading
import select

LISTEN_PORT = 8080
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 22
BUFFER_SIZE = 131072 

def handle_client(client_socket):
    try:
        request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')
        
        if "Upgrade: websocket" in request_data or "upgrade: websocket" in request_data:
            handshake_response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n\r\n"
            )
            client_socket.sendall(handshake_response.encode('utf-8'))
            
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((TARGET_HOST, TARGET_PORT))
            
            sockets_list = [client_socket, server_socket]
            
            while True:
                read_sockets, _, _ = select.select(sockets_list, [], [])
                for sock in read_sockets:
                    data = sock.recv(BUFFER_SIZE)
                    if not data:
                        return
                    
                    if sock == client_socket:
                        server_socket.sendall(data)
                    else:
                        client_socket.sendall(data)
                        
    except Exception:
        pass
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen(100)
    
    while True:
        client_conn, _ = server.accept()
        handler_thread = threading.Thread(target=handle_client, args=(client_conn,))
        handler_thread.daemon = True
        handler_thread.start()

if __name__ == "__main__":
    main()
