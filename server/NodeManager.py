import requests
from typing import List, Dict
from kubernetes import config, client

from server.settings import DEBUG, KUBE_CONFIG, PROMETHEUS_URL, NODE_EXPORTER_PORT


class NodeManager:
    def __init__(self):
        self._load_kube_config()
        self.kube_client = client.CoreV1Api()
        self.nodes: Dict[str, Dict] = {}
        self.availability: Dict[str, bool] = {}

        self._fetch_nodes()
        self._initialize_availability()


    def _load_kube_config(self):
        """
        Load Kubernetes configuration depending on DEBUG flag.
        """
        if DEBUG:
            config.load_kube_config(config_file=KUBE_CONFIG)
        else:
            config.load_incluster_config()


    def _fetch_nodes(self):
        """
        Fetch and update metadata and metrics for all agent worker nodes.
        """
        nodes_response = self.kube_client.list_node()

        for node in nodes_response.items:
            annotations = node.metadata.annotations.get("k3s.io/node-args", "")
            if "agent" not in annotations:
                continue

            node_name = node.metadata.name
            node_ip = node.status.addresses[0].address
            labels = node.metadata.labels
            info = node.status.node_info

            self.nodes[node_name] = {
                "name": node_name,
                "worker_type": labels.get("worker-type"),
                "ip": node_ip,
                "cpu_cores": int(node.status.allocatable["cpu"]),
                "memory": int(node.status.allocatable["memory"][:-2]),
                "os": info.operating_system,
                "os_image": info.os_image,
                "kernel_version": info.kernel_version,
                "architecture": info.architecture,
                "cpu_usage": self._get_cpu_usage(node_ip),
                "memory_usage": self._get_memory_usage(node_ip)
            }


    def _initialize_availability(self):
        """
        Mark all known nodes as available initially.
        """
        self.availability = {node_name: True for node_name in self.nodes}


    def _get_prometheus_metric(self, query: str) -> float:
        """
        Query Prometheus and return the result value.
        """
        response = requests.get(PROMETHEUS_URL, params={"query": query}).json()
        try:
            result = response["data"]["result"][0]
            return round(float(result["value"][1]), 2)
        except (IndexError, KeyError, ValueError):
            return 0.0


    def _get_cpu_usage(self, node_ip: str) -> float:
        """
        Calculate CPU usage ratio (0 to 1) for a node.
        """
        instance = f"{node_ip}:{NODE_EXPORTER_PORT}"
        query = f'1 - avg(rate(node_cpu_seconds_total{{mode="idle", instance="{instance}"}}[30s]))'
        return self._get_prometheus_metric(query)


    def _get_memory_usage(self, node_ip: str) -> float:
        """
        Calculate memory usage ratio (0 to 1) for a node.
        """
        instance = f"{node_ip}:{NODE_EXPORTER_PORT}"
        query = (
            f'1 - (node_memory_MemAvailable_bytes{{instance="{instance}"}} / '
            f'node_memory_MemTotal_bytes{{instance="{instance}"}})'
        )
        return self._get_prometheus_metric(query)
    

    def update_nodes(self):
        """
        Update node metadata and metrics.
        """
        self._fetch_nodes()


    def get_node_by_name(self, name: str) -> Dict:
        """
        Returns the node by its name
        """
        return self.nodes.get(name)


    def get_nodes(
        self,
        node_types: List[str] = [],
        sort_params: List[str] = [],
        descending: bool = False
    ) -> List[Dict]:
        """
        Get node details, optionally filtered by worker type and sorted.

        :param node_types: List of worker types to include
        :param sort_params: Fields to sort nodes by
        :param descending: Whether to sort in descending order
        :return: List of node metadata dictionaries
        """
        filtered_nodes = [
            node for node in self.nodes.values()
            if not node_types or node["worker_type"] in node_types
        ]

        if sort_params:
            filtered_nodes.sort(
                key=lambda node: [node[param] for param in sort_params],
                reverse=descending
            )

        return filtered_nodes


    def nodes_available(self, node_names: List[str]) -> bool:
        """
        Check if all nodes in the list are available.

        :param node_names: List of node names to check
        :return: True if all nodes are available, False otherwise
        """
        return all(self.availability.get(node, False) for node in node_names)


    def reserve_nodes(self, node_names: List[str]):
        """
        Mark nodes as reserved (unavailable).

        :param node_names: List of node names to reserve
        """
        for node in node_names:
            self.availability[node] = False


    def release_nodes(self, node_names: List[str]):
        """
        Mark nodes as released (available again).

        :param node_names: List of node names to release
        """
        for node in node_names:
            self.availability[node] = True
