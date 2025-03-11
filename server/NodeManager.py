from kubernetes import config, client
import json

from server.settings import DEBUG, KUBE_CONFIG


class NodeManager:

    def __init__(self):
        if DEBUG:
            config.load_kube_config(config_file=KUBE_CONFIG)
        else:
            config.load_incluster_config()

        self.v1 = client.CoreV1Api()
        self.nodes = {}
        self.get_nodes()

        print(json.dumps(self.nodes, indent=4, default=str))

    
    def get_nodes(self):
        """
        Get info about all worker nodes
        """
        nodes = self.v1.list_node(pretty="true")
        for node in nodes.items:
            if "agent" in node.metadata.annotations["k3s.io/node-args"]:
                self.nodes[node.metadata.name] = {
                    "name": node.metadata.name,
                    "ip": node.status.addresses[0].address,
                    "cpu_capacity": node.status.capacity["cpu"],
                    "memory_capacity": node.status.capacity["memory"],
                    "cpu_allocatable": node.status.allocatable["cpu"],
                    "memory_allocatable": node.status.allocatable["memory"],
                    "max_pods": node.status.allocatable["pods"],
                    "os": node.status.node_info.operating_system,
                    "os_image": node.status.node_info.os_image,
                    "kernel_version": node.status.node_info.kernel_version,
                    "architecture": node.status.node_info.architecture
                }