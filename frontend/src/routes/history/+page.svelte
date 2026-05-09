<script lang="ts">
	import Navbar from '$lib/components/Navbar.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';
	import { onMount } from 'svelte';
	import { Search, Calendar, Globe, Shield, ChevronRight, Filter, Download } from 'lucide-svelte';
	import { fade, fly } from 'svelte/transition';

	onMount(() => {
		historyStore.fetchHistory();
	});

	let searchQuery = $state('');
	let filteredItems = $derived(
		historyStore.items.filter((item: any) =>
			item.target.toLowerCase().includes(searchQuery.toLowerCase())
		)
	);
</script>

<Navbar />

<main class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
	<div class="mb-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
		<div>
			<h1 class="text-4xl font-extrabold tracking-tight text-slate-900">Scan History</h1>
			<p class="mt-2 text-slate-500">Manage and review your previous security assessments.</p>
		</div>

		<div class="flex items-center space-x-3">
			<div class="relative">
				<Search class="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-400" />
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Search domains..."
					class="focus:ring-primary/20 focus:border-primary min-w-[240px] rounded-lg border border-slate-200 bg-white py-2 pr-4 pl-10 text-sm outline-none focus:ring-2"
				/>
			</div>
			<button
				class="rounded-lg border border-slate-200 bg-white p-2 text-slate-600 hover:bg-slate-50"
			>
				<Filter class="h-4 w-4" />
			</button>
		</div>
	</div>

	{#if historyStore.isLoading}
		<div class="space-y-4">
			{#each Array(4) as _}
				<div class="h-24 w-full animate-pulse rounded-xl bg-slate-100"></div>
			{/each}
		</div>
	{:else if filteredItems.length > 0}
		<div class="grid grid-cols-1 gap-4">
			{#each filteredItems as item, i}
				<div
					in:fly={{ y: 20, delay: i * 50 }}
					class="card group hover:border-primary/30 flex cursor-pointer flex-col justify-between gap-4 p-5 md:flex-row md:items-center"
				>
					<div class="flex items-center space-x-5">
						<div
							class="bg-primary-light text-primary flex h-12 w-12 items-center justify-center rounded-xl"
						>
							<Globe class="h-6 w-6" />
						</div>
						<div>
							<h3 class="text-lg font-bold text-slate-800">{item.target}</h3>
							<div class="mt-1 flex items-center space-x-4 text-sm text-slate-500">
								<span class="flex items-center space-x-1">
									<Calendar class="h-3.5 w-3.5" />
									<span>{item.timestamp}</span>
								</span>
								<span class="flex items-center space-x-1">
									<Shield class="h-3.5 w-3.5" />
									<span>Score: <span class="font-bold text-slate-700">{item.score}</span></span>
								</span>
							</div>
						</div>
					</div>

					<div class="flex items-center space-x-6">
						<div class="hidden items-center space-x-2 sm:flex">
							{#each Object.entries(item.summary) as [key, value]}
								<div
									class="rounded border border-slate-100 bg-slate-50 px-2 py-1 text-[10px] font-bold text-slate-400 uppercase"
								>
									{key[0]}{value}
								</div>
							{/each}
						</div>

						<div class="flex items-center space-x-3">
							<button class="p-2 text-slate-400 transition-colors hover:text-red-600">
								<Download class="h-5 w-5" />
							</button>
							<button
								class="text-primary flex items-center space-x-1 text-sm font-bold transition-transform group-hover:translate-x-1"
							>
								<span>View Results</span>
								<ChevronRight class="h-4 w-4" />
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else}
		<div class="rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 py-20 text-center">
			<div
				class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100"
			>
				<Search class="h-8 w-8 text-slate-300" />
			</div>
			<h3 class="text-lg font-bold text-slate-800">No scans found</h3>
			<p class="mx-auto mt-2 max-w-xs text-slate-500">
				We couldn't find any scans matching your search query. Try another term or start a new scan.
			</p>
			<a href="/" class="btn-primary mt-6 inline-block px-6 py-2 text-sm">Start New Scan</a>
		</div>
	{/if}
</main>
