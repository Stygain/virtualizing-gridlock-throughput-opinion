Virtualizing Gridlock Throughput Opinion  
  
To run: `sudo python ./mininetMain.py`  
  
To clean: `sudo mn -c`
  
  
  
To test load balancer, load balanced server, and client locally:  
1. `python3 loadBalancer.py`  
2. `python3 loadBalancedServer.py -cport NUM -ccount NUM -ip "127.0.0.1"`  
3. `python3 client.py`  
  
Example:  
`python3 loadBalancer.py`  
`python3 loadBalancedServer.py -cport 4007 -ccount 3 -ip "127.0.0.1"`  
`python3 client.py`  
