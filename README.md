# kubelet-stats-exporter
Prometheus exporter to expose epehmeral storage usage stats from Kubelets

The Kubernetes Kubelet has some metrics on tephemeral storage usage that are not currently exposed elsewhere. It may be useful to present these in a format that can be collected by Prometheus.

This repository has an example Python script that can be run inside a Pod / DaemonSet to acheive this. Assumes the Kubelet is running on each node, exposed on the default port (10250). Authentication is done to the kubelet using a service account that is configured in `k8s-resources/ns-rbac.yaml`.