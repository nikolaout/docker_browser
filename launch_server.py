from camoufox.server import launch_server
import threading
import time
from api_server import start_api_server

# Start FastAPI server in a separate thread
api_thread = threading.Thread(target=start_api_server, daemon=True)
api_thread.start()

# Give FastAPI server time to start
time.sleep(2)

# Launch Camoufox server
launch_server(
    headless="virtual",  # Run in headless mode with virtual display
    geoip=True
)
