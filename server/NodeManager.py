import requests
from typing import Dict
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
        self.update_node_details()

    
    def update_node_details(self):
        """
        Update details about worker nodes
        """
        nodes = self.v1.list_node()
        for node in nodes.items:
            if "agent" in node.metadata.annotations["k3s.io/node-args"]:
                node_ip = node.status.addresses[0].address
                self.nodes[node.metadata.name] = {
                    "name": node.metadata.name,
                    "ip": node_ip,
                    "cpu_capacity": node.status.capacity["cpu"],
                    "memory_capacity": node.status.capacity["memory"],
                    "cpu_allocatable": node.status.allocatable["cpu"],
                    "memory_allocatable": node.status.allocatable["memory"],
                    "max_pods": node.status.allocatable["pods"],
                    "os": node.status.node_info.operating_system,
                    "os_image": node.status.node_info.os_image,
                    "kernel_version": node.status.node_info.kernel_version,
                    "architecture": node.status.node_info.architecture,
                    "cpu_usage": self.get_cpu_usage(node_ip),
                    "memory_usage": self.get_memory_usage(node_ip)
                }
    
    
    def get_cpu_usage(self, node_ip) -> float:
        """
        Get current CPU usage for a worker node
        """
        instance = f"{node_ip}:{NODE_EXPORTER_PORT}"
        query = f'100 * (1 - avg(rate(node_cpu_seconds_total{{mode="idle", instance="{instance}"}}[30s])))'
        response = requests.get(PROMETHEUS_URL, params={"query": query}).json()
        result = response["data"]["result"][0]
        usage = float(result["value"][1])

        return round(usage, 2)


    def get_memory_usage(self, node_ip: str) -> float:
        """
        Get current memory usage for a worker node
        """
        instance = f"{node_ip}:{NODE_EXPORTER_PORT}"
        query = f'100 * (1 - (node_memory_MemAvailable_bytes{{instance="{instance}"}} / node_memory_MemTotal_bytes{{instance="{instance}"}}))'
        response = requests.get(PROMETHEUS_URL, params={"query": query}).json()
        result = response["data"]["result"][0]
        usage = float(result["value"][1])

        return round(usage, 2)
    

    def get_nodes(self) -> Dict:
        """
        Get details about worker nodes
        """
        self.update_node_details()
        return self.nodes
