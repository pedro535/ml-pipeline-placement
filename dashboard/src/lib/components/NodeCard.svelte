<script>
    export let node_details = {
        name: "",
        status: "",
        cpu: 0,
        architecture: "",
        os: "",
        os_version: "",
        memory: 0,
        gpu: false,
        running_pipeline: false,
        waiting_pipelines: 0
    };
</script>

<div class="w-full p-5 mb-5 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
    <h5 class="text-xl font-semibold tracking-tight text-gray-900 dark:text-white">{node_details.name}</h5>
    <hr class="h-px mb-2 mt-3 bg-gray-200 border-0 dark:bg-gray-700">

    <div class="mb-1 mb">
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Status: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.status}</span>
    </div>

    <div class="mb-1">
        <span class="text-black dark:text-gray-400 font-semibold text-sm">CPU: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.cpu} cores</span>
    </div>

    <div class="mb-1">
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Architecture: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.architecture}</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">OS: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.os}</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">OS Version: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.os_version}</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Memory: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.memory} GB</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">GPU: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.gpu ? "Yes" : "No"}</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Running Pipeline: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.running_pipeline ? "Yes" : "No"}</span>
    </div>

    <div>
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Pipelines waiting: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{node_details.waiting_pipelines}</span>
    </div>
</div>