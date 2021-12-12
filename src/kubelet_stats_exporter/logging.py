import logging
from pythonjsonlogger import jsonlogger
from kubelet_stats_exporter.config import JSON_LOGGER, LOG_LEVEL

# create filter for all requests
class NoRequests(logging.Filter):
    '''Logging Filter class that filters all werkzeug requests
    '''
    def filter(self, record):
        return '/' not in record.getMessage()

# set root logger
level = logging.getLevelName(LOG_LEVEL)
if JSON_LOGGER == "true":
    logger = logging.getLogger()
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s -  %(levelname)s - %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(level)
else:
    logging.basicConfig(level=level, format='%(asctime)s -  %(levelname)s - %(message)s')
    logger = logging.getLogger()

# Set werkzeug logger filter for requests when DEBUG Logging Level is not set.
if LOG_LEVEL != "DEBUG":
    logging.getLogger("werkzeug").addFilter(NoRequests())
