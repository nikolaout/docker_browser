#!/bin/sh
# Extract dynamic Camoufox port from logs
PORT=$(grep -oP 'ws://localhost:\K[0-9]+' /app/server.log)
echo "Camoufox dynamic port: $PORT"

# Start both port forwarding processes in background
socat TCP-LISTEN:34091,fork TCP:localhost:$PORT &

# Keep the script running
wait