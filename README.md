# kubelet-stats-exporter
Prometheus exporter to expose epehmeral storage usage stats from Kubelets

The Kubernetes Kubelet has some metrics on ephemeral storage usage that are not currently exposed elsewhere. It may be useful to present these in a format that can be collected by Prometheus.

This repository has an example Python script that can be run in a Pod. It accesses the Kubelet on each node, via the Kubernetes API proxy. Authentication is done to the kubelet using a service account that is configured in `k8s-resources/ns-rbac.yaml`.

When running as a DaemonSet, the local node details are passed to the container as an env var.

### Background reading:

https://github.com/kubernetes/kube-state-metrics/issues/1046 (https://github.com/kubernetes/kube-state-metrics/issues/1046#issuecomment-640161305)

https://github.com/kubernetes/kubernetes/issues/69507