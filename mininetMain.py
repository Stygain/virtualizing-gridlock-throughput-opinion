from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.log import lg, info
from mininet.util import waitListening

import time

from loadBalancerTopology import lbTopology

def setupNetwork(network):
	loadBalancerCmd = 'python3 loadBalancer.py > lb.txt 2>&1 &'
	#serverCmd = 'python3 loadBalancedServer.py -ccount 3 -ip  > lbserv.txt 2>&1 &'

	switch = network['s1']

	loadBalancer = network['lbh']
	info( "\n\n*** Load Balancer:\n" )
	info(loadBalancer.name, loadBalancer.IP(), '\n')
	

	lbServers = []
	for netHost in network.hosts:
		if (netHost.name[:6] == 'server'):
			info( "\n\n*** SERVER:\n" )
			info(netHost.name, netHost.IP(), '\n')
			lbServers.append(netHost)
	
	clients = []
	for netHost in network.hosts:
		if (netHost.name[:6] == 'client'):
			info( "\n\n*** CLIENT:\n" )
			info(netHost.name, netHost.IP(), '\n')
			clients.append(netHost)
	
	info( "\n\n*** Starting up load balancer\n" )
	loadBalancer.cmd(loadBalancerCmd)

	info( "\n\n*** Starting up servers\n" )
	for lbServer in lbServers:
		lbServer.cmd('python3 loadBalancedServer.py -ccount 3 -ip ' + lbServer.IP() + ' -cport 4001 > lbserv.txt 2>&1 &')

	#info("*** Waiting for http servers to start\n")

	#for client in clients:
	#	for httpHost in lbServers:
	#		waitListening(client=httpClient, server=httpHost, port=80, timeout=5)

	#info( "\n*** Hosts are running http at the following addresses:\n" )
	#for httpHost in lbServers:
	#	info(httpHost.name, httpHost.IP(), '\n')
	#info("\n*** Type 'exit' or control-D to shut down network\n")

	#info( "\n*** Attempting to ping servers from clients\n" )
	#for httpClient in clients:
	#	httpClient.cmd(clientCmd)

#c = Controller('c2', port=6634)

def simpleTest():
	"Create and test a simple network"
	#topo = SingleSwitchTopo(n=4)
	topo = lbTopology()

	net = Mininet(topo)
	#net.addController(c)
	net.start()
	print "Dumping host connections"
	dumpNodeConnections(net.hosts)
	print "Testing network connectivity"
	net.pingAll()

	setupNetwork(net)

	time.sleep(4)
	net.stop()

if __name__ == '__main__':
	# Tell mininet to print useful information
	setLogLevel('info')
	simpleTest()
