from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.log import lg, info
from mininet.util import waitListening

from loadBalancerTopology import lbTopology

def setupNetwork(network, cmd='python -m SimpleHTTPServer 80 &'):
	switch = network['s1']

	httpHosts = []
	for host in network.hosts:
		if (host.name[:1] == 'h'):
			httpHosts.append(host)
	
	httpClients = []
	for host in network.hosts:
		if (host.name[:1] == 'c'):
			httpClients.append(host)
	
	for httpHost in httpHosts:
		httpHost.cmd(cmd)

	info("*** Waiting for http servers to start\n")

	for httpClient in httpClients:
		for httpHost in httpHosts:
			waitListening(client=httpClient, server=httpHost, port=80, timeout=5)

	info( "\n*** Hosts are running http at the following addresses:\n" )
	for httpHost in httpHosts:
		info(httpHost.name, httpHost.IP(), '\n')
	info("\n*** Type 'exit' or control-D to shut down network\n")

def simpleTest():
	"Create and test a simple network"
	#topo = SingleSwitchTopo(n=4)
	topo = lbTopology()

	net = Mininet(topo)
	net.start()
	print "Dumping host connections"
	dumpNodeConnections(net.hosts)
	print "Testing network connectivity"
	net.pingAll()

	setupNetwork(net)

	net.stop()

if __name__ == '__main__':
	# Tell mininet to print useful information
	setLogLevel('info')
	simpleTest()
