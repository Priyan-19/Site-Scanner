<script lang="ts">
	import { CheckCircle2, Circle, AlertCircle, Loader2, Terminal } from 'lucide-svelte';
	import { scanStore, type ScanStage } from '$lib/stores/scanStore.svelte';
	import { fade, slide } from 'svelte/transition';

	const stages: { key: ScanStage; label: string }[] = [
		{ key: 'initializing', label: 'Initializing Scan' },
		{ key: 'checking_http', label: 'HTTP Connectivity' },
		{ key: 'headers_analysis', label: 'Security Headers' },
		{ key: 'port_scanning', label: 'Port Scanning' },
		{ key: 'whois_lookup', label: 'WHOIS Information' },
		{ key: 'subdomain_discovery', label: 'Subdomain Discovery' },
		{ key: 'ssl_analysis', label: 'SSL/TLS Analysis' },
		{ key: 'finalizing', label: 'Report Generation' }
	];

	function getStageIndex(key: ScanStage) {
		return stages.findIndex((s) => s.key === key);
	}

	let currentStageIndex = $derived(getStageIndex(scanStore.stage));
</script>

{#if scanStore.stage !== 'idle'}
	<div class="mx-auto mb-12 mt-12 max-w-4xl px-4" transition:fade>
		<div class="card p-6 md:p-8">
			<div class="mb-8 flex items-center justify-between">
				<div>
					<h3 class="text-xl font-bold text-neutral-200">Scan Progress</h3>
					<p class="text-sm text-neutral-400">Real-time analysis in progress...</p>
				</div>
				<div class="text-right">
					<span class="text-primary text-3xl font-black">{scanStore.progress}%</span>
				</div>
			</div>

			<!-- Progress Bar -->
			<div class="mb-10 h-3 w-full overflow-hidden rounded-full bg-[#1a1a1a]">
				<div
					class="from-primary to-secondary h-full bg-gradient-to-r transition-all duration-500 ease-out"
					style="width: {scanStore.progress}%"
				></div>
			</div>

			<!-- Stages Grid -->
			<div class="mb-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
				{#each stages as stage, i}
					<div
						class="flex items-center space-x-3 rounded-lg border p-3 transition-colors {i <=
						currentStageIndex
							? 'border-primary-light bg-primary-light/30'
							: 'border-[#222222] bg-[#111111] opacity-60'}"
					>
						{#if i < currentStageIndex || scanStore.stage === 'completed'}
							<CheckCircle2 class="text-success h-5 w-5" />
						{:else if i === currentStageIndex}
							<Loader2 class="text-primary h-5 w-5 animate-spin" />
						{:else}
							<Circle class="h-5 w-5 text-neutral-600" />
						{/if}
						<span
							class="text-sm font-semibold {i <= currentStageIndex
								? 'text-neutral-200'
								: 'text-neutral-500'}">{stage.label}</span
						>
					</div>
				{/each}
			</div>

			<!-- Logs Terminal -->
			<div class="overflow-hidden rounded-xl bg-[#050505] shadow-inner border border-[#222222]">
				<div
					class="flex items-center justify-between border-b border-[#222222] bg-[#1a1a1a] px-4 py-2"
				>
					<div class="flex items-center space-x-2">
						<Terminal class="h-4 w-4 text-neutral-500" />
						<span class="font-mono text-xs tracking-widest text-neutral-500 uppercase">Live Logs</span
						>
					</div>
					<div class="flex space-x-1.5">
						<div class="h-2.5 w-2.5 rounded-full bg-red-500/50"></div>
						<div class="h-2.5 w-2.5 rounded-full bg-amber-500/50"></div>
						<div class="h-2.5 w-2.5 rounded-full bg-emerald-500/50"></div>
					</div>
				</div>
				<div
					class="scrollbar-hide h-48 space-y-1 overflow-y-auto p-3 font-mono text-xs sm:p-4 sm:text-sm"
				>
					{#each scanStore.logs as log}
						<div class="flex space-x-3" transition:slide={{ axis: 'y' }}>
							<span class="shrink-0 text-neutral-400">[{log.timestamp}]</span>
							<span
								class={log.level === 'success'
									? 'text-emerald-400'
									: log.level === 'warning'
										? 'text-amber-400'
										: log.level === 'error'
											? 'text-red-400'
											: 'text-blue-400'}
							>
								{log.message}
							</span>
						</div>
					{/each}
					{#if scanStore.stage !== 'completed' && scanStore.stage !== 'failed'}
						<div class="flex items-center space-x-2 text-neutral-500">
							<span class="animate-pulse">_</span>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
