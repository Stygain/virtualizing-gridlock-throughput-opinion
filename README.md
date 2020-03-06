Virtualizing Gridlock Throughput Opinion  
  
To run: `sudo python ./mininetMain.py`  
  
To clean: `sudo mn -c`
  
  
  
To test load balancer, load balanced server, and client locally:  
1. `python3 loadBalancer.py -algo {LEAST_CONNECTIONS|ROUND_ROBIN}`  
2. `python3 loadBalancedServer.py -cport NUM -ccount NUM -ip "127.0.0.1"`  
3. `python3 client.py`  
  
Example:  
`python3 loadBalancer.py -algo ROUND_ROBIN`  
`python3 loadBalancedServer.py -cport 4007 -ccount 3 -ip "127.0.0.1"`  
`python3 client.py`  
  

Another method:
`python3 networkSetup.py -serverCount NUM -clientCount NUM -algo {LEAST_CONNECTIONS|ROUND_ROBIN}`  
