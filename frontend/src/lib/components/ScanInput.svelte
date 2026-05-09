<script lang="ts">
	import { Search, Globe, ShieldCheck, ArrowRight, Loader2, AlertCircle } from 'lucide-svelte';
	import { scanStore } from '$lib/stores/scanStore.svelte';
	import { toastStore } from '$lib/stores/toastStore.svelte';
	import { ScanAPI } from '$lib/api/scan';
	import { scanWS } from '$lib/api/websocket';
	import { fade } from 'svelte/transition';
	import { onMount } from 'svelte';

	let targetUrl = $state('');
	let isFocused = $state(false);
	let error = $state<string | null>(null);

	onMount(() => {
		const urlParams = new URLSearchParams(window.location.search);
		const targetParam = urlParams.get('target');
		if (targetParam) {
			targetUrl = targetParam;
			// Small delay to ensure stores are ready
			setTimeout(() => {
				handleStartScan();
			}, 500);
		}
	});

	let isValid = $derived(
		targetUrl.length > 3 && (targetUrl.includes('.') || targetUrl.startsWith('http'))
	);

	async function handleStartScan() {
		if (scanStore.stage !== 'idle' && scanStore.stage !== 'completed') return;

		if (!isValid) {
			error = 'Please enter a valid domain or URL';
			toastStore.add('Invalid URL format', 'error');
			return;
		}

		error = null;
		scanStore.reset();
		scanStore.stage = 'initializing';

		try {
			// 1. Start scan via REST API
			const scanId = await ScanAPI.startScan(targetUrl);

			// 2. Connect WebSocket for real-time updates
			scanWS.connect(scanId);

			toastStore.add(`Scan started for ${targetUrl}`, 'info');
			scanStore.addLog(`Initializing connection for ${targetUrl}...`, 'info');
		} catch (err: any) {
			error = err.message || 'Failed to start scan';
			scanStore.stage = 'idle';
			toastStore.add('Connection error', 'error');
		}
	}
</script>

<div class="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-32">
	<div class="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<div class="mx-auto mb-12 max-w-3xl text-center">
			<div
				class="bg-primary-light text-primary animate-pulse-soft mb-6 inline-flex items-center space-x-2 rounded-full px-3 py-1 text-xs font-bold tracking-wider uppercase"
			>
				<ShieldCheck class="h-4 w-4" />
				<span>Enterprise Vulnerability Scanner</span>
			</div>
			<h1
				class="mb-6 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl lg:text-6xl"
			>
				Secure your web <span class="text-primary">infrastructure</span> in real-time.
			</h1>
			<p class="mb-10 text-lg leading-relaxed text-slate-600">
				SiteScanner provides deep security analysis of your domains, uncovering vulnerabilities,
				configuration errors, and exposure risks with a single click.
			</p>

			<div class="group relative mx-auto max-w-2xl">
				<div
					class="from-primary to-secondary absolute -inset-1 rounded-2xl bg-gradient-to-r opacity-25 blur transition duration-1000 group-hover:opacity-40 group-hover:duration-200 {isFocused
						? 'opacity-50'
						: ''}"
				></div>
				<div
					class="relative flex flex-col gap-3 rounded-xl border bg-white p-2 shadow-xl sm:flex-row {error
						? 'border-red-200'
						: 'border-slate-200'} transition-all duration-300"
				>
					<div class="relative flex-1">
						<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
							<Globe class="h-5 w-5 {error ? 'text-red-400' : 'text-slate-400'}" />
						</div>
						<input
							type="text"
							bind:value={targetUrl}
							placeholder="Enter domain or URL (e.g., example.com)"
							class="block w-full border-none bg-transparent py-3 pr-4 pl-11 text-base text-slate-900 placeholder-slate-400 focus:ring-0 sm:py-4 sm:text-lg"
							onkeydown={(e) => e.key === 'Enter' && handleStartScan()}
							onfocus={() => (isFocused = true)}
							onblur={() => (isFocused = false)}
						/>
					</div>
					<button
						onclick={handleStartScan}
						disabled={scanStore.stage !== 'idle' && scanStore.stage !== 'completed'}
						class="btn-primary group/btn flex w-full items-center justify-center space-x-2 px-6 py-3 text-base disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto sm:px-8 sm:py-4 sm:text-lg"
					>
						{#if scanStore.stage !== 'idle' && scanStore.stage !== 'completed'}
							<Loader2 class="h-5 w-5 animate-spin" />
							<span>Scanning...</span>
						{:else}
							<span>Start Scan</span>
							<ArrowRight class="h-5 w-5 transition-transform group-hover/btn:translate-x-1" />
						{/if}
					</button>
				</div>
				{#if error}
					<div
						class="absolute -bottom-8 left-0 flex items-center space-x-1.5 text-xs font-bold text-red-500"
						transition:fade
					>
						<AlertCircle class="h-3.5 w-3.5" />
						<span>{error}</span>
					</div>
				{/if}
			</div>

			<div class="mt-8 flex flex-wrap justify-center gap-6 text-sm font-medium text-slate-500">
				<div class="flex items-center space-x-1.5">
					<div class="bg-success h-1.5 w-1.5 rounded-full"></div>
					<span>Deep Port Scanning</span>
				</div>
				<div class="flex items-center space-x-1.5">
					<div class="bg-primary h-1.5 w-1.5 rounded-full"></div>
					<span>SSL/TLS Validation</span>
				</div>
				<div class="flex items-center space-x-1.5">
					<div class="bg-secondary h-1.5 w-1.5 rounded-full"></div>
					<span>Header Analysis</span>
				</div>
			</div>
		</div>
	</div>
</div>
