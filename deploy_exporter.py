import time
import requests
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from kubernetes import client, config 

config.load_incluster_config()
K8S = client.CoreV1Api()


with open('/run/secrets/kubernetes.io/serviceaccount/token', 'r') as file:
        K8S_TOKEN = file.read()

AUTH_HEADERS = { 'Authorization': 'Bearer'+ str(K8S_TOKEN) }

class KubeletCollector(object):
    def collect(self):
        nodes = K8S.list_node()
        metric = GaugeMetricFamily(
            'kubernetes_pod_ephemeral_storage_used_bytes',
            'Kubernetes Pod ephemeral storage used in bytes',
            labels=['pod_node','pod_namespace','pod_name'])
        for node in nodes.items:
            node_name = node.metadata.name
            ip_addresses = [ i for i in node.status.addresses if i.type =='InternalIP' ]
            ip_address = ip_addresses[0].address
            response = requests.get(f"https://{ip_address}:10250/stats/summary", headers=AUTH_HEADERS, verify=False)
            result = response.json()
            for pod in result['pods']:
                name = pod['podRef']['name']
                namespace = pod['podRef']['namespace']
                used_bytes = pod['ephemeral_storage']['usedBytes']
                labels=[node_name,namespace,name]
                metric.add_metric(labels, used_bytes)
        yield metric

if __name__ == "__main__":
    REGISTRY.register(KubeletCollector())
    start_http_server(9118)
    while True: time.sleep(10)