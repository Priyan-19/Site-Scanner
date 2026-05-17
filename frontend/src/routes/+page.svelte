<script lang="ts">
	import Navbar from '$lib/components/Navbar.svelte';
	import ScanInput from '$lib/components/ScanInput.svelte';
	import ScanProgress from '$lib/components/ScanProgress.svelte';
	import RiskGauge from '$lib/components/RiskGauge.svelte';
	import VulnerabilityCard from '$lib/components/VulnerabilityCard.svelte';
	import ResultsTable from '$lib/components/ResultsTable.svelte';
	import Charts from '$lib/components/Charts.svelte';
	import { scanStore } from '$lib/stores/scanStore.svelte';
	import { fade, fly } from 'svelte/transition';
	import { ShieldAlert, ShieldCheck, Download, Share2, RefreshCw } from 'lucide-svelte';

	let isScanActive = $derived(scanStore.stage !== 'idle' || scanStore.result !== null);

	const mockVulnerabilities = [
		{
			title: 'Missing Content-Security-Policy Header',
			severity: 'Medium' as const,
			component: 'HTTP Headers',
			owasp: 'A05:2021-Security Misconfiguration',
			description:
				'The Content-Security-Policy (CSP) header is not implemented. This header helps prevent various types of attacks like Cross-Site Scripting (XSS) and data injection.',
			technical:
				"HTTP Response header 'Content-Security-Policy' is missing from the target domain.",
			remediation:
				'Implement a strict CSP header that allows only trusted sources for scripts, styles, and images.'
		},
		{
			title: 'Expired SSL Certificate',
			severity: 'Critical' as const,
			component: 'SSL/TLS',
			owasp: 'A02:2021-Cryptographic Failures',
			description:
				'The SSL/TLS certificate for this domain has expired or is invalid. This allows attackers to intercept traffic through man-in-the-middle attacks.',
			technical: "Certificate expired on 2026-04-15. Issuer: Let's Encrypt.",
			remediation: 'Renew the SSL certificate immediately through your certificate authority (CA).'
		},
		{
			title: 'Sensitive Port 3306 (MySQL) Exposed',
			severity: 'High' as const,
			component: 'Port Scanning',
			owasp: 'A05:2021-Security Misconfiguration',
			description:
				'The MySQL database port (3306) is open and accessible from the public internet. This exposes the database to brute-force attacks.',
			technical: 'Port 3306/tcp is OPEN. Service: mysql. Response: 5.7.33-0ubuntu0.18.04.1',
			remediation:
				'Close port 3306 on the public firewall. Use a VPN or SSH tunnel for remote database access.'
		}
	];
</script>

<div class="flex h-screen w-full flex-col overflow-hidden bg-[#0a0a0a]">
	<Navbar />

	<main
		class="flex w-full flex-1 flex-col {isScanActive
			? 'overflow-y-auto'
			: 'items-center justify-center overflow-hidden'}"
	>
		<div class="w-full {isScanActive ? 'pb-20 pt-8' : ''}">
			<ScanInput />

			<ScanProgress />

	{#if scanStore.result}
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" in:fade={{ delay: 300 }}>
			<!-- Dashboard Header -->
			<div class="mb-10 flex flex-col justify-between gap-4 md:flex-row md:items-center">
				<div>
					<h2 class="text-xl font-extrabold tracking-tight text-white sm:text-2xl md:text-3xl">
						Security Analysis Report
					</h2>
					<p class="font-medium text-neutral-400">
						Target: <span class="text-primary font-bold">{scanStore.result.target}</span> • Scanned
						on {new Date().toLocaleDateString()}
					</p>
				</div>
				<div class="flex flex-wrap items-center gap-3">
					<button
						class="flex items-center space-x-2 rounded-lg border border-[#333333] bg-[#111111] px-4 py-2 text-sm font-bold text-neutral-300 transition-colors hover:bg-[#111111]"
					>
						<Share2 class="h-4 w-4" />
						<span>Share</span>
					</button>
					<a
						href="/report"
						class="flex items-center space-x-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-colors hover:bg-red-700"
					>
						<Download class="h-4 w-4" />
						<span>Download PDF</span>
					</a>
				</div>
			</div>

			<!-- Row 1: Score & Key Findings -->
			<div class="mb-8 grid grid-cols-1 gap-8 lg:grid-cols-3">
				<div class="flex flex-col">
					<RiskGauge score={scanStore.result.score} riskLevel={scanStore.result.riskLevel} />
				</div>

				<div class="lg:col-span-2">
					<div class="mb-6 flex items-center justify-between">
						<h3 class="text-xl font-bold text-neutral-200">Key Findings</h3>
						<div class="flex items-center space-x-4 text-xs font-bold text-neutral-400">
							<span class="flex items-center space-x-1.5">
								<div class="h-2 w-2 rounded-full bg-red-500"></div>
								<span
									>{scanStore.result.issues.filter((i) => i.severity === 'Critical').length} Critical</span
								>
							</span>
							<span class="flex items-center space-x-1.5">
								<div class="h-2 w-2 rounded-full bg-amber-500"></div>
								<span
									>{scanStore.result.issues.filter(
										(i) => i.severity === 'High' || i.severity === 'Medium'
									).length} Warning</span
								>
							</span>
						</div>
					</div>

					<div class="space-y-4">
						{#each mockVulnerabilities as vuln, i}
							<div in:fly={{ y: 20, delay: 400 + i * 100 }}>
								<VulnerabilityCard {...vuln} />
							</div>
						{/each}
					</div>

					<button
						class="hover:border-primary hover:text-primary group mt-6 w-full rounded-xl border-2 border-dashed border-[#333333] py-4 font-bold text-neutral-500 transition-all"
					>
						<div class="flex items-center justify-center space-x-2">
							<RefreshCw class="h-4 w-4 transition-transform duration-500 group-hover:rotate-180" />
							<span>Load More Findings</span>
						</div>
					</button>
				</div>
			</div>

			<!-- Row 2: Detailed Summary & Full Table -->
			<div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
				<div class="flex flex-col">
					<div class="card overflow-hidden">
						<div class="border-b border-[#222222] bg-[#111111] px-6 py-4">
							<h4 class="text-sm font-bold tracking-widest text-neutral-200 uppercase">
								Scan Summary
							</h4>
						</div>
						<div class="divide-y divide-[#222222] p-0">
							{#each Object.entries(scanStore.result.summary) as [key, value]}
								<div
									class="flex items-center justify-between px-6 py-4 transition-colors hover:bg-[#111111]/50"
								>
									<span class="text-sm font-semibold text-neutral-400 capitalize">{key}</span>
									<div class="flex items-center space-x-2">
										<span class="text-sm font-bold text-white">{value}</span>
										<span class="text-[10px] font-bold text-neutral-500 uppercase">Issues</span>
									</div>
								</div>
							{/each}
						</div>
					</div>
				</div>

				<div class="lg:col-span-2">
					<ResultsTable
						findings={scanStore.result.issues.map((i, idx) => ({
							id: `VULN-00${idx + 1}`,
							title: i.title,
							severity: i.severity as any,
							component: i.category,
							status: 'Open'
						}))}
					/>
				</div>
			</div>

			<!-- Charts Section -->
			<div class="mt-16">
				<div class="mb-8">
					<h3 class="text-2xl font-bold tracking-tight text-white">Security Analytics</h3>
					<p class="text-neutral-400">Visual representation of the target's security posture.</p>
				</div>
				<Charts />
			</div>
		</div>
	{/if}
		</div>
	</main>
</div>
