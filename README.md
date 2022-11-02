Uhhhhh. need to know difference about peer/our surplus. Something is not right. 
see update_inbound_flow and update_outbound_flow in Connection.py
Need to compare to what we have on seq-ack-branch.

1) We can modify the packet if we maintain the same length and everything works as expected
2) IF we modify the length of the TCP packet, then it fails despite updating the IP.len field
3) I believe this is because the ACK that comes back is wrong. ACK that comes back will
have old seq/ack numbers that are off by the length of the change we made.
4) Steps
    a)  [x] add in iptables to catch packets coming back from the server (aka ACKS)
    b)  [x] match streams by direction -> client->server needs to be connected to server->client
    c)  [ ] Maintain ACKs/seq numbers. these increment by the length of pkt[TCP].load




Create docker network
```
sudo docker network create proxy-netw
```

Build container
```
cd webserver
sudo docker build  -t gregcusack/flask_app:v2 .
```

Deploy container `d0` and proxy
```
sudo docker run --rm -d -p 8000:5000 --net proxy-netw --name d0 --cap-add=NET_ADMIN gregcusack/flask_app:v2
```

Deploy container `d1` and proxy
```
sudo docker run --rm -d -p 8001:5000 --net proxy-netw --name d1 --cap-add=NET_ADMIN gregcusack/flask_app:v2
```


Modify Payload
```
curl -X GET -H "modify-header: true" 192.168.5.92:8000/mirror/greg/lila
```

Just Get payload
```
curl -X GET 192.168.5.92:8000/get
```

Just query
```
curl 192.168.5.92:8000
```