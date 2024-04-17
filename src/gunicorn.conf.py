from omotes_rest import main

bind = "0.0.0.0:9200"
workers = 1
loglevel = "info"
timeout = 300

# Server Hooks
post_fork = main.post_fork
