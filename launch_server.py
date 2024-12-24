from camoufox.server import launch_server

launch_server(
    headless="virtual",  # Run in headless mode with virtual display
    geoip=True,
    block_images=True
)