#!/user/bin/env python3

import socket

HOST = '127.0.0.1'
PORT = 8081

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	sock.bind((HOST, PORT))
	sock.listen(2)
	while True:
		conn, addr = sock.accept()
		with conn:
			print('Connected by: ', addr)
			while True:
				data = conn.recv(1024)
				if not data:
					break
				conn.sendall(data)
