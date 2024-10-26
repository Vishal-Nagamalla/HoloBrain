import socket
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 65432))
server_socket.listen(1)
print("Waiting for Unity to connect...")

client_socket, _ = server_socket.accept()
print("Unity connected!")

try:
    while True:
        test_message = "rotate_left"
        client_socket.sendall(test_message.encode())
        print("Sent test message:", test_message)
        time.sleep(1)  # Send message every second
except KeyboardInterrupt:
    print("Closing connection...")
finally:
    client_socket.close()
    server_socket.close()