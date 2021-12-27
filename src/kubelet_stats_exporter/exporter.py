from flask import Blueprint, Response, abort
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest
from kubelet_stats_exporter.collector import KubeletCollector
from kubelet_stats_exporter.logging import logger

bp = Blueprint('exporter', __name__)
 
def register_metrics_collector(registry):
    """Registers the main collector in the registry
    Parameters
    ----------
    registry: object
        Prometheus Exporter Collector Registry Object
    """
    collector = KubeletCollector()
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
        logger.debug("Metrics payload content generated")
        return content, 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as err:
        logger.error(f"Scrape Failed - {str(err)}")
        abort(Response(f"Scrape failed: {str(err)}", status=502))
