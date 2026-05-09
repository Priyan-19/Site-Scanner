<script lang="ts">
	import { Chart, registerables } from 'chart.js';
	import { Pie, Bar, Line } from 'svelte-chartjs';
	import { scanStore } from '$lib/stores/scanStore.svelte';
	import { historyStore } from '$lib/stores/historyStore.svelte';

	Chart.register(...registerables);

	// Helper to count issues by severity for the Pie Chart
	const severityCounts = $derived(() => {
		const counts = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
		if (!scanStore.result) return [1, 0, 0, 0]; // Default placeholder

		scanStore.result.issues.forEach((issue) => {
			const sev = issue.severity as keyof typeof counts;
			if (counts[sev] !== undefined) counts[sev]++;
		});

		return [counts.LOW, counts.MEDIUM, counts.HIGH, counts.CRITICAL];
	});

	// Helper to get category data for the Bar Chart
	const categoryData = $derived(() => {
		if (!scanStore.result) return [0, 0, 0, 0, 0];
		const s = scanStore.result.summary;
		return [s.headers, s.ssl, s.ports, s.subdomains, 0]; // DNS/Auth not implemented yet in backend
	});

	// Helper to get historical trends for the Line Chart
	const trendData = $derived(() => {
		if (historyStore.items.length === 0) {
			// If no history, show current score as the only point
			return {
				labels: ['Initial'],
				data: [scanStore.result?.score || 0]
			};
		}

		// Take last 5-10 scans and sort by date
		const history = [...historyStore.items].reverse().slice(-10);
		return {
			labels: history.map((h) =>
				new Date(h.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
			),
			data: history.map((h) => h.score)
		};
	});

	const pieData = $derived({
		labels: ['Low', 'Medium', 'High', 'Critical'],
		datasets: [
			{
				data: severityCounts(),
				backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#7f1d1d'],
				borderWidth: 0
			}
		]
	});

	const barData = $derived({
		labels: ['Headers', 'SSL', 'Ports', 'Subs', 'DNS'],
		datasets: [
			{
				label: 'Findings',
				data: categoryData(),
				backgroundColor: '#3b82f6',
				borderRadius: 8
			}
		]
	});

	const lineData = $derived({
		labels: trendData().labels,
		datasets: [
			{
				label: 'Security Score',
				data: trendData().data,
				borderColor: '#3b82f6',
				backgroundColor: 'rgba(59, 130, 246, 0.1)',
				fill: true,
				tension: 0.4
			}
		]
	});

	const defaultOptions = {
		responsive: true,
		maintainAspectRatio: false,
		plugins: {
			legend: {
				position: 'bottom' as const,
				labels: {
					usePointStyle: true,
					padding: 20,
					font: {
						size: 12,
						weight: 'bold' as const
					}
				}
			}
		}
	};

	const pieOptions = {
		...defaultOptions,
		plugins: {
			legend: {
				display: false
			}
		}
	};

	const legendItems = [
		{ label: 'Low', color: '#10b981' },
		{ label: 'Medium', color: '#f59e0b' },
		{ label: 'High', color: '#ef4444' },
		{ label: 'Critical', color: '#7f1d1d' }
	];
</script>

<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
	<div class="card h-[320px] p-6 sm:h-[400px]">
		<h4 class="mb-6 text-sm font-bold tracking-widest text-slate-800 uppercase">
			Risk Distribution
		</h4>
		<div class="h-[180px] sm:h-[260px]">
			<Pie data={pieData} options={pieOptions} />
		</div>
		<div
			class="mt-6 grid grid-cols-2 gap-x-2 gap-y-3 sm:flex sm:flex-wrap sm:justify-center sm:gap-6"
		>
			{#each legendItems as item}
				<div class="flex items-center space-x-2">
					<div class="h-3 w-3 rounded-full" style="background-color: {item.color}"></div>
					<span class="text-xs font-bold text-slate-600 sm:text-sm">{item.label}</span>
				</div>
			{/each}
		</div>
	</div>

	<div class="card h-[320px] p-6 sm:h-[400px] lg:col-span-2">
		<h4 class="mb-6 text-sm font-bold tracking-widest text-slate-800 uppercase">
			Findings by Category
		</h4>
		<div class="h-[220px] sm:h-[300px]">
			<Bar data={barData} options={defaultOptions} />
		</div>
	</div>

	<div class="card h-[320px] p-6 sm:h-[400px] lg:col-span-3">
		<h4 class="mb-6 text-sm font-bold tracking-widest text-slate-800 uppercase">
			Security Score Trend
		</h4>
		<div class="h-[220px] sm:h-[300px]">
			<Line data={lineData} options={defaultOptions} />
		</div>
	</div>
</div>
