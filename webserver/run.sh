#!/bin/bash

echo "Running proxy..."
python3 -u /app/proxy.py > /app/logs/log.log 2>&1 &

sleep 1

echo "Running app webserver..."
python3 -u /app/app.py &

while true; do sleep 1000; done

