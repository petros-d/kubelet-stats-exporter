import logging
import time
import requests
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from kubernetes import client, config

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s')

config.load_incluster_config()
K8S = client.CoreV1Api()
CA_FILE = '/run/secrets/kubernetes.io/serviceaccount/ca.crt'

with open('/run/secrets/kubernetes.io/serviceaccount/token', 'r') as file:
    K8S_TOKEN = file.read()

AUTH_HEADERS = { 'Authorization': 'Bearer '+ str(K8S_TOKEN) }

class KubeletCollector(object):
    def collect(self):
        nodes = K8S.list_node()
        metric = GaugeMetricFamily(
            'kube_pod_ephemeral_storage_used_bytes',
            'Kubernetes Pod ephemeral storage used in bytes',
            labels=['node','namespace','pod'])
        for node in nodes.items:
            node_name = node.metadata.name
            try:
                response = requests.get(
                    f"https://kubernetes.default.svc/api/v1/nodes/{node_name}/proxy/stats/summary",
                    headers=AUTH_HEADERS, verify=CA_FILE)
            except:
                logging.warning(f"Failed to connect to node {node_name}")
                break
            result = response.json()
            for pod in result['pods']:
                name = pod['podRef']['name']
                namespace = pod['podRef']['namespace']
                try:
                    used_bytes = pod['ephemeral_storage']['usedBytes']
                except:
                    used_bytes = 0
                    logging.info(f"Unable to get usedBytes metrics for pod {name} on node {node}, setting to 0")
                labels=[node_name,namespace,name]
                metric.add_metric(labels, used_bytes)
        yield metric

if __name__ == "__main__":
    REGISTRY.register(KubeletCollector())
    start_http_server(9118)
    while True: time.sleep(10)
