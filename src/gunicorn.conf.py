from omotes_rest import main

bind = '0.0.0.0:9200'
workers = 1
loglevel = "INFO"
timeout = 300

# Server Hooks
on_starting = main.on_starting
