import requests
from typing import List, Dict
from kubernetes import config, client

from server.settings import DEBUG, KUBE_CONFIG, PROMETHEUS_URL, NODE_EXPORTER_PORT, KUBE_APISERVER_PORT


class NodeManager:

    def __init__(self):
        self._load_kube_config()
        self.kube_client = client.CoreV1Api()
        self.nodes: Dict[str, Dict] = {}
        self.occupation: Dict[str, str] = {}

        self._fetch_nodes()
        self._initialize_occupation()


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
            conditions = node.status.conditions
            if "agent" not in annotations or not self._is_node_ready(conditions):
                continue

            node_name = node.metadata.name
            node_ip = node.status.addresses[0].address
            labels = node.metadata.labels
            info = node.status.node_info
            memory = int(node.status.allocatable["memory"][:-2])
            self.nodes[node_name] = {
                "name": node_name,
                "worker_type": labels.get("worker_type"),
                "ip": node_ip,
                "os": info.operating_system,
                "os_image": info.os_image,
                "kernel_version": info.kernel_version,
                "architecture": info.architecture,
                "cpu_cores": int(node.status.allocatable["cpu"]),
                "n_cpu_flags": int(labels.get("n_cpu_flags", 0)),
                "memory": memory,
                "memory_usage": self._get_memory_usage(node_ip, memory),
                "accelerator": labels.get("accelerator_type")
            }


    def _initialize_occupation(self):
        """
        Mark all known nodes as available initially.
        """
        self.occupation = {node_name: None for node_name in self.nodes}


    def _get_memory_usage(self, node_ip: str, total_memory: int) -> float:
        """
        Analyze memory usage on the node.
        """
        free_memory_avg = self._get_free_memory_avg(node_ip)
        kfp_memory_usage_avg = self._get_kfp_memory_usage_avg(node_ip)
        memory_usage_no_kfp = total_memory - free_memory_avg - kfp_memory_usage_avg
        memory_usage = memory_usage_no_kfp / total_memory
        return round(memory_usage, 2)
    

    def _is_node_ready(self, conditions: List) -> bool:
        """
        Check if the node is ready based on its conditions.
        """
        for condition in conditions:
            if condition.type == "Ready":
                return bool(condition.status)
        return False
        

    def _get_prometheus_metric(self, query: str) -> int:
        """
        Query Prometheus and return the result value.
        """
        response = requests.get(PROMETHEUS_URL, params={"query": query}).json()
        try:
            result = response["data"]["result"][0]
            return int(result["value"][1])
        except (IndexError, KeyError, ValueError):
            return 0


    def _get_free_memory_avg(self, node_ip: str) -> int:
        """
        Calculate average free memory (in KB) for a node (over 5 minutes).
        """
        instance = f"{node_ip}:{NODE_EXPORTER_PORT}"
        query = (
            f'round('
            f'avg_over_time(node_memory_MemAvailable_bytes{{instance="{instance}"}}[5m:]) '
            f'/ 1024)'
        )   
        return self._get_prometheus_metric(query)


    def _get_kfp_memory_usage_avg(self, node_ip: str) -> int:
        """
        Calculate average memory usage (in KB) for KFP containers on a node (over 5 minutes).
        """
        instance = f"{node_ip}:{KUBE_APISERVER_PORT}"
        query = (
            f'round('
            f'avg_over_time('
            f'sum by (instance) (container_memory_usage_bytes{{namespace="kubeflow", instance="{instance}", container!=""}})[5m:]'
            f') / 1024'
            f')'
        )
        return self._get_prometheus_metric(query)


    def update_nodes(self):
        """
        Update nodes metadata and metrics.
        """
        self._fetch_nodes()


    def get_node_by_name(self, name: str) -> Dict:
        """
        Returns the node by its name
        """
        return self.nodes.get(name)


    def get_nodes(
        self,
        filters: Dict = {},
        sort_params: List[str] = [],
        descending: bool = False
    ) -> List[Dict]:
        """
        Get node details, optionally filtered by worker type and sorted.

        :param filters: Additional filters to apply to nodes
        :param sort_params: Fields to sort nodes by
        :param descending: Whether to sort in descending order
        :return: List of node metadata dictionaries
        """
        nodes = list(self.nodes.values())

        # Apply filters
        if filters:
            for node in self.nodes.values():
                for k, v in filters.items():
                    if (isinstance(v, list) and node[k] not in v) or (not isinstance(v, list) and node[k] != v):
                        nodes.remove(node)
                        break
                
        if sort_params:
            nodes.sort(
                key=lambda node: [node[param] for param in sort_params],
                reverse=descending
            )

        return nodes


    def nodes_available(self, node_names: List[str]) -> bool:
        """
        Check if all nodes in the list are available.

        :param node_names: List of node names to check
        :return: True if all nodes are available, False otherwise
        """
        return all([self.occupation[node] is None for node in node_names])


    def reserve_nodes(self, node_names: List[str], pipeline_id: str):
        """
        Mark nodes as reserved (unavailable).

        :param node_names: List of node names to reserve
        :param pipeline_id: ID of the pipeline reserving the nodes
        """
        for node in node_names:
            self.occupation[node] = pipeline_id


    def release_nodes(self, node_names: List[str], pipeline_id: str):
        """
        Mark nodes as released (available again).

        :param node_names: List of node names to release
        :param pipeline_id: ID of the pipeline releasing the nodes
        """
        for node in node_names:
            if self.occupation[node] == pipeline_id:
                self.occupation[node] = None


    def get_node_platform(self, node: str) -> str:
        """
        Get the platform of a node to be used for docker images tagging.

        :param node_name: Name of the node
        :return: Platform of the node
        """
        accelerator = self.nodes[node]["accelerator"]
        if accelerator != "none":
            return accelerator
        return self.nodes[node]["architecture"]