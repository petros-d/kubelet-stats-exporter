import requests
import random
from concurrent.futures import ThreadPoolExecutor
from kubernetes import client, config
from prometheus_client.core import GaugeMetricFamily
from kubelet_stats_exporter.config import KUBERNETES_API_TIMEOUT
from kubelet_stats_exporter.logging import logger

# Custom Collector
class KubeletCollector():
    """
    Custom Collector Class
    Collects Kubelet Metrics from Kubernetes nodes
    """
    def __init__(self):

        # k8s config
        config.load_incluster_config()
        self.k8s_client = client.CoreV1Api()
        self.ca_file = '/run/secrets/kubernetes.io/serviceaccount/ca.crt'
        self.k8s_token = open('/run/secrets/kubernetes.io/serviceaccount/token', "r").read()
        self.auth_headers = { 'Authorization': 'Bearer ' + str(self.k8s_token) }
        self.timeout = KUBERNETES_API_TIMEOUT

        # multithread config
        self.futures = []

        # Prometheus metrics to collect
        self.metric = GaugeMetricFamily(
            'kube_pod_ephemeral_storage_used_bytes',
            'Kubernetes Pod ephemeral storage used in bytes',
            labels=['node','namespace','pod'])

    def collect(self):
        """
        Main Function for Custom Collector
        Get the list of nodes and iterate
        """
        logger.debug(f"Retrieving list of nodes")
        nodes = self.k8s_client.list_node()

        # Multithread executor
        executor = ThreadPoolExecutor(max_workers=len(nodes.items))

        # Send nodes to executors
        for node in nodes.items:
            self.futures.append(executor.submit(self.scrape_node_metrics, node=node))

        for future in self.futures:
            future.result()

        logger.debug(f"Save metric content.")
        yield self.metric

    def get_node_info(self, node_name):
        """Retrieves node information
        Parameters
        ----------
        node_name: string
            Name of the node to retrieve the information from
        Returns
        -------
        response - Mapping
            Response returned from node /proxy/stats/summary endpoint.
        None - NoneType
            Returned when exception is raised requesting to node /proxy/stats/summary endpoint.
        """
        logger.debug(f"Collecting metrics from node {node_name}")
        try:
            response = requests.get(
                f"https://kubernetes.default.svc/api/v1/nodes/{node_name}/proxy/stats/summary",
                headers=self.auth_headers, verify=self.ca_file, timeout=self.timeout)
            logger.debug(f"Response received from kubernetes API for node {node_name}")
        except requests.ConnectTimeout:
            logger.warning(f"Connection timeout to Kubernetes API for node {node_name}")
        except Exception as err:
            logger.warning(f"Unable to request summary stats from node {node_name} - {str(err)}")
            return None
        return response.json()

    def get_pod_metrics(self, pod_id):
        """Retrieves metrics from pod
        Parameters
        ----------
        pod_id: string
            Pod ID
        Returns
        -------
        name: string
            Pod name
        namespace: string
            Pod namespace
        used_bytes: int
            Ephemeral Storage - Used bytes metric value
        """
        logger.debug(f"Parsing info from pod: {pod_id}")
        name = pod_id['podRef']['name']
        namespace = pod_id['podRef']['namespace']
        try:
            used_bytes = pod_id['ephemeral-storage']['usedBytes']
        except Exception as err:
            used_bytes = 0
            logger.warning(f"Unable to get usedBytes metrics for pod {name}, setting to 0 - {str(err)}")
        return name, namespace, used_bytes

    def scrape_node_metrics(self, node):
        """Scrapes information from nodes to create the metric to be exported
        Parameters
        ----------
        node: object
            Kubernetes Node Information
        """
        node_name = node.metadata.name
        logger.debug(f"Processing node {node_name}")
        # Check Node is in Ready status
        ready_status = [x for x in node.status.conditions if x.type == 'Ready']
        if len(ready_status) > 0 and ready_status[0].status == 'True':
            logger.debug(f"Node name: {node_name}, status: {ready_status[0].status}")
            node_info = self.get_node_info(node_name)
            if node_info is not None and 'pods' in node_info:
                for pod in node_info['pods']:
                    name, namespace, used_bytes = self.get_pod_metrics(pod)
                    labels=[node_name,namespace,name]
                    self.metric.add_metric(labels, used_bytes)
            else:
                logger.warning(f"Failed to fetch info from {node_name}")
        else:
            logger.warning(f"Node {node_name} is not in Ready status")
        logger.debug(f"Finished processing node {node_name}")
