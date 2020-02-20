from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch
from mininet.topo import Topo

CLIENTS = 50
HOSTS = 10

class lbTopology(Topo):

    "Load Balancer Topology"


    def __init__(self):
        "Create Load Balancer Topology"

        Topo.__init__(self)

        # Add hosts
        lbh = self.addHost('lbh', cls=Host, ip='10.0.0.1', defaultRoute=None)
        
	# Add switches
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch)

	# Connect load balancer to switch
	self.addLink(lbh, s1)
	
	for i in range(HOSTS):
	     ipAddr = '10.0.0.%s' % (i+2)
	     h = self.addHost('h%s' % (i+1), cls=Host, ip=ipAddr, defaultRoute=None)
             self.addLink(h, s1)

	for i in range(CLIENTS):
	     ipAddr = '10.0.0.%s' % (i+HOSTS+2)
	     c = self.addHost('c%s' % (i+1), cls=Host, ip=ipAddr, defaultRoute=None)
             self.addLink(c, s1)
        
#topos = { 'lbTopo': (lambda: loadBalancerTopology() ) }
