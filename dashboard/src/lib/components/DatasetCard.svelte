<script>
    import { Badge } from 'flowbite-svelte';

    export let dataset_details = undefined;
    console.log(dataset_details);
</script>

<div class="w-full p-5 mb-5 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
    <h5 class="text-xl font-semibold tracking-tight text-gray-900 dark:text-white">{dataset_details.name}</h5>
    <hr class="h-px mb-2 mt-3 bg-gray-200 border-0 dark:bg-gray-700">

    <div class="mb-1">
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Path: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{dataset_details.path}</span>
    </div>

    <div class="mb-1">
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Size: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{dataset_details.size} KB</span>
    </div>

    <div class="mb-1">
        <span class="text-black dark:text-gray-400 font-semibold text-sm">Modified at: </span>
        <span class="font-light text-gray-500 dark:text-gray-400 text-sm">{dataset_details.modified_at}</span>
    </div>
</div>