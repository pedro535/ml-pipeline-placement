<script>
    import { onMount } from "svelte";
    import DatasetCard from '$lib/components/DatasetCard.svelte';
    import { Spinner } from 'flowbite-svelte';

    let datasets = [];
    let loading = true;

    onMount(async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/datasets/");
            const data = await response.json();
            datasets = data.datasets;
            loading = false;
        } catch (error) {
            console.log(error);
            loading = true;
        }
    });
</script>

<div>
    <h1 class="text-4xl font-bold mb-10">Stored Datasets</h1>
    {#if loading}
        <div class="text-center mt-5">
            <Spinner size={10} />
        </div>
    {:else}
        {#each datasets as dataset}
            <DatasetCard dataset_details={dataset} />
        {/each}
    {/if}
</div>
