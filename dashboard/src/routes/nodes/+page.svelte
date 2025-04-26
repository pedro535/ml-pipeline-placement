<script>
    import { onMount } from "svelte";
    import NodeCard from '$lib/components/NodeCard.svelte';
    import { Spinner } from 'flowbite-svelte';

    let nodes = [];
    let assignments = {};
    let loading = true;

    onMount(async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/nodes/");
            const data = await response.json();
            nodes = data.nodes;
            assignments = data.assignments;
            loading = false;
        } catch (error) {
            console.log(error);
            loading = true;
        }
    });
</script>

<div>
    <h1 class="text-4xl font-bold mb-10">Worker Nodes</h1>
    {#if loading}
        <div class="text-center mt-5">
            <Spinner size={10} />
        </div>
    {:else}
        <div class="grid lg:grid-cols-3 grid-cols-1 gap-5">
            {#each nodes as node}
                <NodeCard node_details={node} n_assignments={assignments[node.name]} />
            {/each}
        </div>
    {/if}
</div>
