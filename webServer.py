from http.server import BaseHTTPRequestHandler
from urllib import parse
from http.server import HTTPServer


class Host():
	def __init__(self, IP):
		self.ip = IP
		self.connections = 0
		self.accepting = True

	def Accepting(self):
		return self.accepting

	def GetIp(self):
		return self.ip

class LoadBalancer():
	def __init__(self):
		#self.hosts = [ Host('10.0.0.2') ]
		self.hosts = [ Host('https://www.google.com'),
				Host('https://www.wikipedia.org') ]

	def GetNextHost(self):
		# Determine the next host to balance to
		for host in self.hosts:
			if (host.Accepting()):
				return host.GetIp()
		

class GetHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		global lb
		parsed_path = parse.urlparse(self.path)
		message_parts = [
			'CLIENT VALUES:',
			'client_address={} ({})'.format(
					self.client_address,
					self.address_string()),
			'command={}'.format(self.command),
			'path={}'.format(self.path),
			'real path={}'.format(parsed_path.path),
			'query={}'.format(parsed_path.query),
			'request_version={}'.format(self.request_version),
			'',
			'SERVER VALUES:',
			'server_version={}'.format(self.server_version),
			'sys_version={}'.format(self.sys_version),
			'protocol_version={}'.format(self.protocol_version),
			'',
			'HEADERS RECEIVED:',
		]

		for name, value in sorted(self.headers.items()):
			message_parts.append('{}={}'.format(name, value.rstrip()))

		message_parts.append('')
		message = '\r\n'.join(message_parts)
		self.send_response(301)
		self.send_header('Content-Type', 'text/plain; charset=utf-8')
		# This will redirect it to another host
		self.send_header('Location', lb.GetNextHost())
		self.end_headers()
		self.wfile.write(message.encode('utf-8'))


if __name__ == '__main__':
	lb = LoadBalancer()
	server = HTTPServer(('localhost', 8080), GetHandler)
	print('Starting server, use <Ctrl-C> to stop')
	server.serve_forever()


