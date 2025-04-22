<script>
    let { children } = $props();
    import "../app.css";
    import { Cpu, FileCode, Database, Settings } from '@lucide/svelte';
</script>

<aside class="fixed top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0" aria-label="Sidebar">
    <div class="h-full px-3 py-4 overflow-y-auto bg-gray-50 dark:bg-gray-800">
        <a href="/" class="flex items-center ps-2.5 mb-10">
            <span class="self-center text-xl font-semibold whitespace-nowrap dark:text-white">MlopX Dashboard</span>
        </a>
        <ul class="space-y-2 font-medium">
            <li>
                <a href="nodes" class="flex items-center p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group">
                <Cpu class="w-5 h-5 text-gray-600 dark:text-white" />
                <span class="ms-3 text-gray-600">Worker nodes</span>
                </a>
            </li>
            <li>
                <a href="pipelines" class="flex items-center p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group">
                <FileCode class="w-5 h-5 text-gray-600 dark:text-white" />
                <span class="ms-3 text-gray-600">ML Pipelines</span>
                </a>
            </li>
            <li>
                <a href="datasets" class="flex items-center p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group">
                <Database class="w-5 h-5 text-gray-600 dark:text-white" />
                <span class="ms-3 text-gray-600">Datasets</span>
                </a>
            </li>
            <li>
                <a href="server" class="flex items-center p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group">
                <Settings class="w-5 h-5 text-gray-600 dark:text-white" />
                <span class="ms-3 text-gray-600">Server settings</span>
                </a>
            </li>
        </ul>
    </div>
</aside>

<div class="py-10 px-20 sm:ml-64">
    {@render children()}
</div>
