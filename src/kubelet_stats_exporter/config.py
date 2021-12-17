import os

# application
EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', "9118"))

# exporter
KUBERNETES_API_TIMEOUT = int(os.getenv("KUBERNETES_API_TIMEOUT", "5"))

# logging
JSON_LOGGER = os.getenv('JSON_LOGGER', "false" )
LOG_LEVEL = os.getenv('LOG_LEVEL', "INFO" )
