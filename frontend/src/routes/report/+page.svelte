<script lang="ts">
	import Navbar from '$lib/components/Navbar.svelte';
	import {
		Shield,
		FileText,
		Download,
		Printer,
		Share2,
		Globe,
		Calendar,
		CheckCircle2
	} from 'lucide-svelte';
	import { fade } from 'svelte/transition';

	import { scanStore } from '$lib/stores/scanStore.svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let reportData = $derived(
		scanStore.result
			? {
					target: scanStore.result.target,
					id: scanStore.result.id,
					date: new Date(scanStore.result.timestamp).toLocaleDateString('en-US', {
						month: 'short',
						day: '2-digit',
						year: 'numeric'
					}),
					status: 'Completed',
					score: scanStore.result.score,
					totalIssues: scanStore.result.issues ? scanStore.result.issues.length : 0,
					categories: [
						{
							name: 'HTTP Security Headers',
							issues: scanStore.result.summary?.headers || 0,
							score: Math.max(0, 100 - (scanStore.result.summary?.headers || 0) * 10)
						},
						{
							name: 'SSL/TLS Configuration',
							issues: scanStore.result.summary?.ssl || 0,
							score: Math.max(0, 100 - (scanStore.result.summary?.ssl || 0) * 20)
						},
						{
							name: 'Port Vulnerabilities',
							issues: scanStore.result.summary?.ports || 0,
							score: Math.max(0, 100 - (scanStore.result.summary?.ports || 0) * 25)
						},
						{
							name: 'Subdomain Exposure',
							issues: scanStore.result.summary?.subdomains || 0,
							score: Math.max(0, 100 - (scanStore.result.summary?.subdomains || 0) * 10)
						}
					]
				}
			: {
					target: 'Loading...',
					id: 'N/A',
					date: 'N/A',
					status: 'N/A',
					score: 0,
					totalIssues: 0,
					categories: []
				}
	);

	onMount(() => {
		if (!scanStore.result) {
			goto('/');
		}
	});

	function handlePrint() {
		window.print();
	}

	function handleDownloadPdf() {
		if (!reportData.id || reportData.id === 'N/A') return;
		const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';
		window.location.href = `${baseUrl}/report/${reportData.id}?format=pdf`;
	}
</script>

<Navbar />

<div class="min-h-screen bg-[#111111] px-4 py-12 print:bg-[#111111] print:p-0">
	<div class="mx-auto max-w-4xl">
		<!-- Report Actions (Hidden on Print) -->
		<div
			class="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center print:hidden"
		>
			<a
				href="/"
				class="hover:text-primary flex items-center space-x-2 text-sm font-bold text-neutral-400"
			>
				<span>← Back to Dashboard</span>
			</a>
			<div class="flex items-center space-x-3">
				<button
					onclick={handlePrint}
					class="flex items-center space-x-2 rounded-lg border border-[#333333] bg-[#111111] px-4 py-2 text-sm font-bold text-neutral-300 hover:bg-[#111111]"
				>
					<Printer class="h-4 w-4" />
					<span>Print</span>
				</button>
				<button
					onclick={handleDownloadPdf}
					class="flex items-center space-x-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-colors hover:bg-red-700"
				>
					<Download class="h-4 w-4" />
					<span>Download PDF Report</span>
				</button>
			</div>
		</div>
		<!-- The Report Document -->
		<div
			id="report-document"
			class="overflow-hidden rounded-2xl border border-[#333333] bg-[#111111] shadow-2xl print:rounded-none print:border-none print:shadow-none"
		>
			<!-- Header Area -->
			<div class="bg-[#00e6b8] p-10 text-[#093022]">
				<div class="flex flex-col items-start justify-between gap-6 sm:flex-row">
					<div>
						<div class="mb-6 flex items-center space-x-2">
							<div class="rounded-lg bg-[#093022] p-2 text-[#00e6b8]">
								<Shield class="h-8 w-8" />
							</div>
							<span class="text-2xl font-black tracking-tight text-[#051f15]"
								>Site<span class="text-[#093022]/60">Scanner</span></span
							>
						</div>
						<h1 class="mb-2 text-4xl font-extrabold text-[#051f15]">Security Assessment Report</h1>
						<p class="font-bold text-[#093022]/70">Confidential • For Internal Use Only</p>
					</div>
					<div class="text-left sm:text-right">
						<div class="mb-1 text-xs font-black tracking-widest text-[#093022]/70 uppercase">
							Report ID
						</div>
						<div class="font-mono text-lg font-bold text-[#051f15]">{reportData.id}</div>
					</div>
				</div>
			</div>

			<!-- Overview Grid -->
			<div class="border-b border-[#222222] p-10">
				<div class="grid grid-cols-1 gap-8 md:grid-cols-3">
					<div>
						<div
							class="mb-2 flex items-center space-x-1.5 text-xs font-bold tracking-widest text-neutral-500 uppercase"
						>
							<Globe class="h-3.5 w-3.5" />
							<span>Target Asset</span>
						</div>
						<div class="text-xl font-bold text-neutral-200">{reportData.target}</div>
					</div>
					<div>
						<div
							class="mb-2 flex items-center space-x-1.5 text-xs font-bold tracking-widest text-neutral-500 uppercase"
						>
							<Calendar class="h-3.5 w-3.5" />
							<span>Scan Date</span>
						</div>
						<div class="text-xl font-bold text-neutral-200">{reportData.date}</div>
					</div>
					<div>
						<div
							class="mb-2 flex items-center space-x-1.5 text-xs font-bold tracking-widest text-neutral-500 uppercase"
						>
							<CheckCircle2 class="h-3.5 w-3.5" />
							<span>Overall Status</span>
						</div>
						<div
							class="inline-flex items-center space-x-2 rounded-full bg-emerald-50 px-3 py-1 text-sm font-bold text-emerald-700"
						>
							<div class="h-2 w-2 animate-pulse rounded-full bg-emerald-500"></div>
							<span>{reportData.status}</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Executive Summary -->
			<div class="p-10">
				<h2 class="mb-6 text-2xl font-bold text-white">Executive Summary</h2>
				<div
					class="mb-10 flex flex-col items-center gap-10 rounded-2xl bg-[#111111] p-8 md:flex-row"
				>
					<div class="relative h-32 w-32 shrink-0">
						<svg class="h-full w-full -rotate-90 transform">
							<circle cx="64" cy="64" r="58" stroke="#e2e8f0" stroke-width="12" fill="none" />
							<circle
								cx="64"
								cy="64"
								r="58"
								stroke="#0066ff"
								stroke-width="12"
								fill="none"
								stroke-dasharray="364.4"
								stroke-dashoffset={364.4 * (1 - reportData.score / 100)}
							/>
						</svg>
						<div
							class="absolute inset-0 flex items-center justify-center text-3xl font-black text-neutral-200"
						>
							{reportData.score}
						</div>
					</div>
					<div>
						<p class="text-lg leading-relaxed text-neutral-300">
							The security assessment for <span class="font-bold">{reportData.target}</span> yielded
							a score of <span class="text-primary font-bold">{reportData.score}/100</span>. While
							the asset shows strong resilience in SSL/TLS configuration, significant
							vulnerabilities were identified in public-facing ports and HTTP header configurations.
						</p>
					</div>
				</div>

				<!-- Findings Table -->
				<h3 class="mb-6 text-xl font-bold text-white">Finding Categories</h3>
				<div class="overflow-x-auto rounded-xl border border-[#333333]">
					<table class="w-full text-left">
						<thead>
							<tr
								class="border-b border-[#333333] bg-[#111111] text-xs font-bold tracking-widest text-neutral-400 uppercase"
							>
								<th class="px-6 py-4">Category</th>
								<th class="px-6 py-4">Issues Found</th>
								<th class="px-6 py-4">Health Score</th>
								<th class="px-6 py-4 text-right">Status</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-slate-200 text-sm">
							{#each reportData.categories as cat}
								<tr>
									<td class="px-6 py-4 font-bold text-neutral-200">{cat.name}</td>
									<td class="px-6 py-4 text-neutral-400">{cat.issues} issues identified</td>
									<td class="px-6 py-4">
										<div class="flex items-center space-x-2">
											<div class="h-2 w-24 overflow-hidden rounded-full bg-[#1a1a1a]">
												<div class="bg-primary h-full" style="width: {cat.score}%"></div>
											</div>
											<span class="font-bold text-neutral-300">{cat.score}%</span>
										</div>
									</td>
									<td class="px-6 py-4 text-right">
										<span
											class="rounded px-2 py-1 text-[10px] font-black uppercase {cat.score > 80
												? 'bg-emerald-50 text-emerald-600'
												: cat.score > 50
													? 'bg-amber-50 text-amber-600'
													: 'bg-red-50 text-red-600'}"
										>
											{cat.score > 80 ? 'Secure' : cat.score > 50 ? 'Warning' : 'Critical'}
										</span>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>

			<!-- Footer Area -->
			<div class="flex items-center justify-between border-t border-[#333333] bg-[#111111] p-10">
				<div class="text-xs font-medium text-neutral-500">
					Generated by SiteScanner Engine v2.4.1 • © 2026 SiteScanner Inc.
				</div>
				<div class="flex items-center space-x-4 opacity-50 grayscale">
					<div class="h-4 w-12 rounded bg-slate-300"></div>
					<div class="h-4 w-12 rounded bg-slate-300"></div>
					<div class="h-4 w-12 rounded bg-slate-300"></div>
				</div>
			</div>
		</div>

		<!-- Print Footer -->
		<div class="mt-12 hidden text-center text-xs text-neutral-500 print:block">
			This report was automatically generated and is valid for 30 days from the date of issue.
		</div>
	</div>
</div>

<style>
	@media print {
		:global(body) {
			background-color: white !important;
		}
	}
</style>
