# A simple app where a central AI agent controls a fleet of autonomous bots to collect resources and build a spaceship.

from hub import Hub

# Create a hub
hub = Hub()

# Create a fleet of bots
hub.create_bots(10)

# Run the hub
hub.run()