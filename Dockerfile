# Use a Python base image
FROM python:3.9-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libx11-xcb1 \
    libasound2 \
    xvfb \
    socat \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Install Camoufox with the geoip option
RUN pip install --no-cache-dir camoufox[geoip]

# Fetch the latest Camoufox browser
RUN python -m camoufox fetch

# Copy the launch script
COPY launch_server.py /app/launch_server.py

# Copy the dynamic port extraction script
COPY extract_port.sh /app/extract_port.sh
RUN chmod +x /app/extract_port.sh

# Expose the port for the server
EXPOSE 34091

# Start Xvfb and then the Camoufox server with dynamic port forwarding
CMD ["sh", "-c", "Xvfb :99 -ac & export DISPLAY=:99 && python /app/launch_server.py | tee /app/server.log & for i in $(seq 1 10); do if grep -q 'ws://localhost:[0-9]\\+' /app/server.log; then break; else sleep 1; fi; done && /app/extract_port.sh"]
