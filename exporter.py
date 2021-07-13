import time
import requests
import os
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

NODE_IP = os.getenv('NODE_IP')
NODE_NAME = os.getenv('NODE_NAME')

with open('/run/secrets/kubernetes.io/serviceaccount/token', 'r') as file:
        K8S_TOKEN = file.read()

AUTH_HEADERS = { 'Authorization': 'Bearer'+ str(K8S_TOKEN) }

class KubeletCollector(object):
    def collect(self):
        response = requests.get(f"https://{NODE_IP}:10250/stats/summary", headers=AUTH_HEADERS, verify=False)
        result = response.json()
        metric = GaugeMetricFamily(
            'kubernetes_pod_ephemeral_storage_used_bytes',
            'Kubernetes Pod ephemeral storage used in bytes',
            labels=['pod_node','pod_namespace','pod_name']
        )
        for pod in result['pods']:
            name = pod['podRef']['name']
            namespace = pod['podRef']['namespace']
            used_bytes = pod['ephemeral_storage']['usedBytes']
            labels=[NODE_NAME,namespace,name]
            metric.add_metric(labels, used_bytes)
        yield metric

if __name__ == "__main__":
    REGISTRY.register(KubeletCollector())
    start_http_server(9118)
    while True: time.sleep(10)