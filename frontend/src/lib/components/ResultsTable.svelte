<script lang="ts">
	import {
		Shield,
		AlertCircle,
		Info,
		ShieldAlert,
		ChevronRight,
		ExternalLink
	} from 'lucide-svelte';
	import { getSeverityColor } from '$lib/utils/formatters';

	interface Finding {
		id: string;
		title: string;
		severity: 'Low' | 'Medium' | 'High' | 'Critical';
		component: string;
		status: string;
	}

	let { findings = [] }: { findings: Finding[] } = $props();

	const icons = {
		Low: Info,
		Medium: AlertCircle,
		High: ShieldAlert,
		Critical: Shield
	};
</script>

<div class="card overflow-hidden">
	<div class="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
		<h3 class="text-sm font-bold tracking-widest text-slate-800 uppercase">
			All Security Findings
		</h3>
		<span
			class="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-[10px] font-black text-slate-500 uppercase"
		>
			{findings.length} Items
		</span>
	</div>

	<div class="overflow-x-auto">
		<table class="w-full text-left">
			<thead>
				<tr
					class="border-b border-slate-50 text-[10px] font-black tracking-widest text-slate-400 uppercase"
				>
					<th class="px-6 py-4">Status</th>
					<th class="px-6 py-4">Finding</th>
					<th class="px-6 py-4">Category</th>
					<th class="px-6 py-4">Severity</th>
					<th class="px-6 py-4 text-right">Action</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-slate-50">
				{#each findings as finding}
					<tr class="group transition-colors hover:bg-slate-50/50">
						<td class="px-4 py-3 sm:px-6 sm:py-4">
							<div
								class="h-2 w-2 rounded-full {finding.severity === 'Critical'
									? 'bg-red-500'
									: finding.severity === 'High'
										? 'bg-orange-500'
										: 'bg-blue-500'}"
							></div>
						</td>
						<td class="px-4 py-3 sm:px-6 sm:py-4">
							<div class="flex flex-col">
								<span class="text-sm font-bold whitespace-nowrap text-slate-700"
									>{finding.title}</span
								>
								<span class="text-xs text-slate-400">ID: {finding.id}</span>
							</div>
						</td>
						<td class="px-4 py-3 sm:px-6 sm:py-4">
							<span class="text-xs font-medium whitespace-nowrap text-slate-500"
								>{finding.component}</span
							>
						</td>
						<td class="px-4 py-3 sm:px-6 sm:py-4">
							<span
								class="rounded border px-2 py-0.5 text-[10px] font-black uppercase {getSeverityColor(
									finding.severity
								)}"
							>
								{finding.severity}
							</span>
						</td>
						<td class="px-4 py-3 text-right sm:px-6 sm:py-4">
							<button
								class="hover:text-primary p-2 text-slate-300 transition-all group-hover:translate-x-1"
							>
								<ChevronRight class="h-4 w-4" />
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
