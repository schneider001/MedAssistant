# Enable logging to console
errorlog = '-'  # Log to stdout
accesslog = '-'
loglevel = 'debug'  # Set log level to error

# Set eventlet debug level to debug
import eventlet
eventlet.hubs.use_hub()