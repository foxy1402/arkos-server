#!/usr/bin/env python3
"""
Simple SOCKS5 Proxy Server for ArkOS R36S
Run on port 1080 with username/password authentication
"""
import socket
import threading
import struct
import logging

# Configuration
PROXY_HOST = '0.0.0.0'
PROXY_PORT = 1080
PROXY_USER = 'arkproxy'
PROXY_PASS = 'arkproxy2026'

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SOCKS5Server:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.server = None

    def handle_client(self, client_socket, address):
        try:
            # SOCKS5 greeting
            version, nmethods = struct.unpack("!BB", client_socket.recv(2))
            methods = client_socket.recv(nmethods)
            
            # Check for username/password auth (method 2)
            if 2 not in methods:
                client_socket.sendall(struct.pack("!BB", 5, 255))  # No acceptable methods
                return
            
            # Request username/password auth
            client_socket.sendall(struct.pack("!BB", 5, 2))
            
            # Receive auth credentials
            auth_version = client_socket.recv(1)
            username_len = struct.unpack("!B", client_socket.recv(1))[0]
            username = client_socket.recv(username_len).decode()
            password_len = struct.unpack("!B", client_socket.recv(1))[0]
            password = client_socket.recv(password_len).decode()
            
            # Verify credentials
            if username != self.username or password != self.password:
                client_socket.sendall(struct.pack("!BB", 1, 1))  # Auth failed
                logger.warning(f"Auth failed from {address} - user: {username}")
                return
            
            # Auth success
            client_socket.sendall(struct.pack("!BB", 1, 0))
            
            # SOCKS5 request
            version, cmd, _, address_type = struct.unpack("!BBBB", client_socket.recv(4))
            
            if address_type == 1:  # IPv4
                address = socket.inet_ntoa(client_socket.recv(4))
            elif address_type == 3:  # Domain name
                domain_length = client_socket.recv(1)[0]
                address = client_socket.recv(domain_length).decode()
            else:
                return
            
            port = struct.unpack('!H', client_socket.recv(2))[0]
            
            # Connect to target
            try:
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((address, port))
                bind_address = remote.getsockname()
                logger.info(f"Connected to {address}:{port}")
            except Exception as e:
                logger.error(f"Connection failed to {address}:{port} - {e}")
                reply = struct.pack("!BBBBIH", 5, 5, 0, 1, 0, 0)
                client_socket.sendall(reply)
                return
            
            addr = struct.unpack("!I", socket.inet_aton(bind_address[0]))[0]
            port = bind_address[1]
            reply = struct.pack("!BBBBIH", 5, 0, 0, 1, addr, port)
            client_socket.sendall(reply)
            
            # Relay data
            self.relay(client_socket, remote)
            
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()

    def relay(self, client, remote):
        def forward(source, destination):
            try:
                while True:
                    data = source.recv(4096)
                    if not data:
                        break
                    destination.sendall(data)
            except:
                pass
            finally:
                source.close()
                destination.close()

        client_to_remote = threading.Thread(target=forward, args=(client, remote))
        remote_to_client = threading.Thread(target=forward, args=(remote, client))
        
        client_to_remote.start()
        remote_to_client.start()
        
        # Wait for both threads to complete
        client_to_remote.join()
        remote_to_client.join()

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        
        logger.info(f"SOCKS5 Proxy started on {self.host}:{self.port}")
        logger.info(f"Auth: {self.username} / {self.password}")
        
        while True:
            try:
                client, address = self.server.accept()
                logger.info(f"Connection from {address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client, address))
                client_thread.daemon = True
                client_thread.start()
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Server error: {e}")
        
        if self.server:
            self.server.close()

if __name__ == '__main__':
    proxy = SOCKS5Server(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
    proxy.start()
