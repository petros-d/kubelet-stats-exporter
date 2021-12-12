import os

# application
EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', "9118"))

# exporter
SCRAPE_TIMEOUT = float(os.getenv("SCRAPE_TIMEOUT", "30.0"))

# logging
JSON_LOGGER = os.getenv('JSON_LOGGER', "false" )
LOG_LEVEL = os.getenv('LOG_LEVEL', "INFO" )
