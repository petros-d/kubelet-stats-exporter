from flask import Blueprint, Response, abort, request
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest
from kubelet_stats_exporter.collector import KubeletCollector
from kubelet_stats_exporter.config import SCRAPE_TIMEOUT
from kubelet_stats_exporter.logging import logger

bp = Blueprint('exporter', __name__)

def get_timeout():
    """Gets the exporter response timeout
    Returns
    -------
    timeout - float
        Timeout setting extracted from prometheus request or default value
    """
    try:
        return float(request.headers.get('X-Prometheus-Scrape-Timeout-Seconds'))
    except Exception:
        return SCRAPE_TIMEOUT

def register_metrics_collector(registry):
    """Registers the main collector in the registry
    Parameters
    ----------
    registry: object
        Prometheus Exporter Collector Registry Object
    """
    timeout = get_timeout()
    collector = KubeletCollector(timeout)
    registry.register(collector)

# Application Paths
@bp.route("/health")
def health():
    '''
    Health Endpoint
    '''
    return 'ok'

@bp.route("/metrics")
def metrics():
    '''
    Metrics endpoint for prometheus scraping
    '''
    registry = CollectorRegistry()
    register_metrics_collector(registry)
    try:
        content = generate_latest(registry)
        return content, 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as err:
        logger.error(f"Scrape Failed - {err}")
        abort(Response(f"Scrape failed: {err}", status=502))
