<script>
    import { Badge } from 'flowbite-svelte';

    export let node_details = undefined;
    export let n_assignments = 0;
</script>

<div class="w-full p-5 mb-5 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
    <h5 class="text-xl font-semibold tracking-tight text-gray-900 dark:text-white">{node_details.name}</h5>
    <hr class="h-px mb-2 mt-3 bg-gray-200 border-0 dark:bg-gray-700">

    <div class="mb-1 mb">
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Status: </span>
        <Badge class="ml-1" color="green">Running</Badge>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Tasks Assigned: </span>
        <Badge class="ml-1" color="purple">{n_assignments}</Badge>
    </div>

    <div class="mb-1">
        <span class="text-black dark:text-gray-400 font-semibold text-sm">CPU: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.cpu_cores} cores</span>
    </div>

    <div class="mb-1">
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Architecture: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.architecture}</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Memory: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{Math.round(node_details.memory / 1000000)} GB</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Accelerator: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.accelerator}</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">OS: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.os}</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">OS Image: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.os_image}</span>
    </div>

</div>