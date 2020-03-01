from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.topo import Topo

CLIENTS = 1
SERVERS = 1

class lbTopology(Topo):
    def build(self):
        # Add hosts
        lbh = self.addHost('lbh', cls=Host, ip='10.0.0.1', defaultRoute=None)
        
	# Add switches
        #s1 = self.addSwitch('s1', cls=UserSwitch)
        switch = self.addSwitch('s1')

	# Connect load balancer to switch
	self.addLink(lbh, switch)
	
	for i in range(SERVERS):
	     ipAddr = '10.0.0.%s' % (i+2)
	     h = self.addHost('server%s' % (i+1), cls=Host, ip=ipAddr, defaultRoute=None)
             self.addLink(h, switch)

	for i in range(CLIENTS):
	     ipAddr = '10.0.0.%s' % (i+SERVERS+2)
	     c = self.addHost('client%s' % (i+1), cls=Host, ip=ipAddr, defaultRoute=None)
             self.addLink(c, switch)
        
#topos = { 'lbTopo': (lambda: loadBalancerTopology() ) }
