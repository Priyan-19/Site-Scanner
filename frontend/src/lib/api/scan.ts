import { scanStore } from '$lib/stores/scanStore.svelte';

export class ScanAPI {
	private static BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

	static async startScan(url: string) {
		try {
			const response = await fetch(`${this.BASE_URL}/scan`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ target: url })
			});

			if (!response.ok) throw new Error('Failed to start scan');

			const data = await response.json();
			return data.scan_id;
		} catch (error) {
			console.error('Scan error:', error);
			throw error;
		}
	}

	static async getResults(scanId: string) {
		const response = await fetch(`${this.BASE_URL}/scan/${scanId}`);
		return await response.json();
	}
}
