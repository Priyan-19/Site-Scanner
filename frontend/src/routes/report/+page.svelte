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

	const reportData = {
		target: 'example-corporate.com',
		id: 'SCAN-2026-X882',
		date: 'May 07, 2026',
		status: 'Completed',
		score: 82,
		totalIssues: 14,
		categories: [
			{ name: 'HTTP Security Headers', issues: 4, score: 75 },
			{ name: 'SSL/TLS Configuration', issues: 1, score: 95 },
			{ name: 'Port Vulnerabilities', issues: 2, score: 60 },
			{ name: 'Subdomain Exposure', issues: 7, score: 88 }
		]
	};

	function handlePrint() {
		window.print();
	}
</script>

<Navbar />

<div class="min-h-screen bg-slate-50 px-4 py-12 print:bg-white print:p-0">
	<div class="mx-auto max-w-4xl">
		<!-- Report Actions (Hidden on Print) -->
		<div
			class="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center print:hidden"
		>
			<a
				href="/"
				class="hover:text-primary flex items-center space-x-2 text-sm font-bold text-slate-500"
			>
				<span>← Back to Dashboard</span>
			</a>
			<div class="flex items-center space-x-3">
				<button
					onclick={handlePrint}
					class="flex items-center space-x-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50"
				>
					<Printer class="h-4 w-4" />
					<span>Print</span>
				</button>
				<button
					class="flex items-center space-x-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-colors hover:bg-red-700"
				>
					<Download class="h-4 w-4" />
					<span>Download PDF</span>
				</button>
			</div>
		</div>

		<!-- The Report Document -->
		<div
			class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl print:rounded-none print:border-none print:shadow-none"
		>
			<!-- Header Area -->
			<div class="bg-slate-900 p-10 text-white">
				<div class="flex flex-col items-start justify-between gap-6 sm:flex-row">
					<div>
						<div class="mb-6 flex items-center space-x-2">
							<div class="bg-primary rounded-lg p-2">
								<Shield class="h-8 w-8 text-white" />
							</div>
							<span class="text-2xl font-black tracking-tight"
								>Site<span class="text-primary">Scanner</span></span
							>
						</div>
						<h1 class="mb-2 text-4xl font-extrabold">Security Assessment Report</h1>
						<p class="font-medium text-slate-400">Confidential • For Internal Use Only</p>
					</div>
					<div class="text-left sm:text-right">
						<div class="mb-1 text-xs font-black tracking-widest text-slate-500 uppercase">
							Report ID
						</div>
						<div class="text-primary font-mono text-lg font-bold">{reportData.id}</div>
					</div>
				</div>
			</div>

			<!-- Overview Grid -->
			<div class="border-b border-slate-100 p-10">
				<div class="grid grid-cols-1 gap-8 md:grid-cols-3">
					<div>
						<div
							class="mb-2 flex items-center space-x-1.5 text-xs font-bold tracking-widest text-slate-400 uppercase"
						>
							<Globe class="h-3.5 w-3.5" />
							<span>Target Asset</span>
						</div>
						<div class="text-xl font-bold text-slate-800">{reportData.target}</div>
					</div>
					<div>
						<div
							class="mb-2 flex items-center space-x-1.5 text-xs font-bold tracking-widest text-slate-400 uppercase"
						>
							<Calendar class="h-3.5 w-3.5" />
							<span>Scan Date</span>
						</div>
						<div class="text-xl font-bold text-slate-800">{reportData.date}</div>
					</div>
					<div>
						<div
							class="mb-2 flex items-center space-x-1.5 text-xs font-bold tracking-widest text-slate-400 uppercase"
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
				<h2 class="mb-6 text-2xl font-bold text-slate-900">Executive Summary</h2>
				<div
					class="mb-10 flex flex-col items-center gap-10 rounded-2xl bg-slate-50 p-8 md:flex-row"
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
							class="absolute inset-0 flex items-center justify-center text-3xl font-black text-slate-800"
						>
							{reportData.score}
						</div>
					</div>
					<div>
						<p class="text-lg leading-relaxed text-slate-700">
							The security assessment for <span class="font-bold">{reportData.target}</span> yielded
							a score of <span class="text-primary font-bold">{reportData.score}/100</span>. While
							the asset shows strong resilience in SSL/TLS configuration, significant
							vulnerabilities were identified in public-facing ports and HTTP header configurations.
						</p>
					</div>
				</div>

				<!-- Findings Table -->
				<h3 class="mb-6 text-xl font-bold text-slate-900">Finding Categories</h3>
				<div class="overflow-x-auto rounded-xl border border-slate-200">
					<table class="w-full text-left">
						<thead>
							<tr
								class="border-b border-slate-200 bg-slate-50 text-xs font-bold tracking-widest text-slate-500 uppercase"
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
									<td class="px-6 py-4 font-bold text-slate-800">{cat.name}</td>
									<td class="px-6 py-4 text-slate-600">{cat.issues} issues identified</td>
									<td class="px-6 py-4">
										<div class="flex items-center space-x-2">
											<div class="h-2 w-24 overflow-hidden rounded-full bg-slate-100">
												<div class="bg-primary h-full" style="width: {cat.score}%"></div>
											</div>
											<span class="font-bold text-slate-700">{cat.score}%</span>
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
			<div class="flex items-center justify-between border-t border-slate-200 bg-slate-50 p-10">
				<div class="text-xs font-medium text-slate-400">
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
		<div class="mt-12 hidden text-center text-xs text-slate-400 print:block">
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
