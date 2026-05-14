import type { ScanResult } from './scanStore.svelte';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class HistoryStore {
	items = $state<ScanResult[]>([]);
	isLoading = $state(false);
	error = $state<string | null>(null);

	async fetchHistory() {
		this.isLoading = true;
		try {
			const response = await fetch(`${API_BASE_URL}/history`);
			if (response.ok) {
				const data = await response.json();
				// Map backend response to frontend model if needed, but assuming they match for now
				this.items = data.map((item: any) => ({
					id: item.scan_id,
					target: item.target,
					score: item.security_score || 0,
					riskLevel: item.risk_level || 'Low',
					timestamp: new Date(item.timestamp).toLocaleString(),
					issues: [], // Summaries don't have issues
					summary: { headers: 0, ports: 0, ssl: 0, subdomains: 0 } // Placeholder
				}));
			}
		} catch (e) {
			this.error = 'Failed to fetch history';
		} finally {
			this.isLoading = false;
		}
	}

	addEntry(result: ScanResult) {
		this.items = [result, ...this.items];
	}
}

export const historyStore = new HistoryStore();
