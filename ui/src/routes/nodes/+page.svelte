<script>
    import { Card } from 'flowbite-svelte';
    import NodeCard from '$lib/components/NodeCard.svelte';

    let node1 = {
        name: "ml-worker-high-cpu-01",
        status: "running",
        cpu: 8,
        architecture: "x86_64",
        os: "Linux",
        os_version: "Ubuntu 20.04",
        memory: 32,
        gpu: true,
        running_pipeline: true,
        waiting_pipelines: 4
    };
</script>

<div>
    <h1 class="text-4xl font-bold mb-10">
        Worker Nodes
    </h1>

    <div class="grid lg:grid-cols-3 grid-cols-1 gap-5">
        <NodeCard node_details={node1} />
        <NodeCard node_details={node1} />
        <NodeCard node_details={node1} />
        <NodeCard node_details={node1} />
        <NodeCard node_details={node1} />
        <NodeCard node_details={node1} />
        <NodeCard node_details={node1} />
    </div>
</div>