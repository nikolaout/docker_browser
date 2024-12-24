#!/bin/sh
PORT=$(grep -oP 'ws://localhost:\K[0-9]+' /app/server.log)
echo "Dynamic port: $PORT"
socat TCP-LISTEN:34091,fork TCP:localhost:$PORT