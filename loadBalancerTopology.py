from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch
from mininet.topo import Topo

class lbTopology(Topo):

    "Load Balancer Topology"

    def __init__(self):
        "Create Load Balancer Topology"

        Topo.__init__(self)

        # Add hosts
        lbh = self.addHost('lbh', cls=Host, ip='10.0.0.1', defaultRoute=None)
        h1 = self.addHost('h1', cls=Host, ip='10.0.0.2', defaultRoute=None)
        h2 = self.addHost('h2', cls=Host, ip='10.0.0.3', defaultRoute=None)

        c1 = self.addHost('c1', cls=Host, ip='10.0.0.50', defaultRoute=None)
        c2 = self.addHost('c2', cls=Host, ip='10.0.0.51', defaultRoute=None)

	# Add switches
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch)
        #s2 = self.addSwitch('s2', cls=OVSKernelSwitch)

	# Add links
	# Connect clients to switch
        self.addLink(c1, s1)
        self.addLink(c2, s1)

	# Connect load balancer to switch
	self.addLink(lbh, s1)
	#self.addLink(lbh, s2)

	# Connect endpoints to switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)

#topos = { 'lbTopo': (lambda: loadBalancerTopology() ) }
