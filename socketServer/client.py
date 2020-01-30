#!/usr/bin/env python3

import socket
import time

HOST = '127.0.0.1'
PORT = 8081

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	sock.connect((HOST, PORT))
	for i in range(1, 5):
		print('Awake!')
		sock.sendall(b'Hello, world!')
		data = sock.recv(1024)
		print('Received: ', repr(data))
		print('Sleeping...')
		time.sleep(5)

