<script lang="ts">
	import { ShieldAlert, ShieldCheck, Info } from 'lucide-svelte';

	interface Props {
		score: number;
		riskLevel: 'Low' | 'Medium' | 'High' | 'Critical';
	}

	let { score = 0, riskLevel = 'Low' }: Props = $props();

	const colors = {
		Low: 'text-success',
		Medium: 'text-warning',
		High: 'text-error',
		Critical: 'text-red-700'
	};

	const bgColors = {
		Low: 'bg-emerald-50',
		Medium: 'bg-amber-50',
		High: 'bg-red-50',
		Critical: 'bg-red-100'
	};

	// SVG Gauge Calculations
	const radius = 80;
	const circumference = 2 * Math.PI * radius;
	const offset = $derived(circumference - (score / 100) * circumference);
</script>

<div class="card overflow-hidden">
	<div class="border-b border-[#222222] bg-[#111111] px-6 py-4">
		<h3 class="text-sm font-bold tracking-widest text-neutral-200 uppercase">Security Score</h3>
	</div>
	<div class="flex flex-col items-center p-8 text-center">
		<div class="relative inline-flex items-center justify-center">
			<!-- SVG Gauge -->
			<svg viewBox="0 0 192 192" class="h-32 w-32 -rotate-90 transform sm:h-48 sm:w-48">
				<circle
					cx="96"
					cy="96"
					r={radius}
					stroke="currentColor"
					stroke-width="12"
					fill="transparent"
					class="text-slate-100"
				/>
				<circle
					cx="96"
					cy="96"
					r={radius}
					stroke="currentColor"
					stroke-width="12"
					fill="transparent"
					stroke-dasharray={circumference}
					style="stroke-dashoffset: {offset}"
					class="transition-all duration-1000 ease-out {colors[riskLevel]}"
				/>
			</svg>

			<div class="absolute flex flex-col items-center justify-center">
				<span class="text-4xl font-black text-neutral-200 sm:text-5xl">{score}</span>
				<span class="text-xs font-bold tracking-widest text-neutral-500 uppercase">Points</span>
			</div>
		</div>

		<div class="mt-8 w-full">
			<div
				class="inline-flex items-center space-x-2 rounded-full px-4 py-2 {bgColors[
					riskLevel
				]} {colors[riskLevel]} font-bold"
			>
				{#if riskLevel === 'Low'}
					<ShieldCheck class="h-5 w-5" />
				{:else if riskLevel === 'Medium'}
					<Info class="h-5 w-5" />
				{:else}
					<ShieldAlert class="h-5 w-5" />
				{/if}
				<span>{riskLevel} Risk</span>
			</div>

			<p class="mt-4 text-sm leading-relaxed text-neutral-400">
				Your security posture is
				<span class="font-bold text-neutral-300">
					{score > 80 ? 'Excellent' : score > 60 ? 'Good' : score > 40 ? 'Fair' : 'Critical'}
				</span>.
				{score < 60
					? 'Immediate action is recommended to address critical findings.'
					: 'Review minor findings to further harden your system.'}
			</p>
		</div>
	</div>
</div>
