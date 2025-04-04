import requests
from typing import List, Dict
from kubernetes import config, client

from server.settings import DEBUG, KUBE_CONFIG, PROMETHEUS_URL, NODE_EXPORTER_PORT


class NodeManager:

    def __init__(self):
        if DEBUG:
            config.load_kube_config(config_file=KUBE_CONFIG)
        else:
            config.load_incluster_config()

        self.v1 = client.CoreV1Api()
        self.nodes = {}
        self.update_nodes()

    
    def update_nodes(self):
        """
        Update details about worker nodes
        """
        nodes = self.v1.list_node()
        for node in nodes.items:
            if "agent" not in node.metadata.annotations["k3s.io/node-args"]:
                continue

            node_ip = node.status.addresses[0].address
            self.nodes[node.metadata.name] = {
                "name": node.metadata.name,
                "worker_type": node.metadata.labels['worker-type'],
                "ip": node_ip,
                "cpu_cores": int(node.status.allocatable["cpu"]),
                "memory": int(node.status.allocatable["memory"][:-2]),
                "os": node.status.node_info.operating_system,
                "os_image": node.status.node_info.os_image,
                "kernel_version": node.status.node_info.kernel_version,
                "architecture": node.status.node_info.architecture,
                "cpu_usage": self.get_cpu_usage(node_ip),
                "memory_usage": self.get_memory_usage(node_ip)
            }
    
    
    def get_cpu_usage(self, node_ip) -> float:
        """
        Get current CPU usage for a worker node between 0 and 1
        """
        instance = f"{node_ip}:{NODE_EXPORTER_PORT}"
        query = f'1 - avg(rate(node_cpu_seconds_total{{mode="idle", instance="{instance}"}}[30s]))'
        response = requests.get(PROMETHEUS_URL, params={"query": query}).json()
        result = response["data"]["result"][0]
        usage = float(result["value"][1])

        return round(usage, 2)


    def get_memory_usage(self, node_ip: str) -> float:
        """
        Get current memory usage for a worker node between 0 and 1
        """
        instance = f"{node_ip}:{NODE_EXPORTER_PORT}"
        query = f'1 - (node_memory_MemAvailable_bytes{{instance="{instance}"}} / node_memory_MemTotal_bytes{{instance="{instance}"}})'
        response = requests.get(PROMETHEUS_URL, params={"query": query}).json()
        result = response["data"]["result"][0]
        usage = float(result["value"][1])

        return round(usage, 2)
    

    def get_nodes(self, node_types: List = [], sort_params: List = [], descending=False) -> List[Dict]:
        """
        Get details about worker nodes
        :param node_types: List of node types to filter by
        :param sort_params: Sort nodes by specified parameters
        :param descending: Sort in descending order
        :return: List of nodes
        """
        # Filter
        if not node_types:
            nodes = list(self.nodes.values())            
        else:
            nodes = [n for n in self.nodes.values() if n["worker_type"] in node_types]
        
        # Sort
        if sort_params:
            nodes = sorted(
                nodes,
                key=lambda x: [x[k] for k in sort_params],
                reverse=descending
            )

        return nodes
