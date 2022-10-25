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

