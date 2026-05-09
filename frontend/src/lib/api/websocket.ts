import { scanStore } from '$lib/stores/scanStore.svelte';
import { historyStore } from '$lib/stores/historyStore.svelte';

export class ScanWebSocket {
	private socket: WebSocket | null = null;
	private static WS_URL = 'ws://localhost:8000/api/v1/ws/scan';

	connect(scanId: string) {
		this.socket = new WebSocket(`${ScanWebSocket.WS_URL}/${scanId}`);

		this.socket.onopen = () => {
			console.log('WebSocket Connected');
			scanStore.addLog('Connected to scanning engine.', 'success');
		};

		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);

			if (data.type === 'progress') {
				scanStore.setStage(data.stage, data.progress);
			} else if (data.type === 'log') {
				scanStore.addLog(data.message, data.level || 'info');
			} else if (data.type === 'complete') {
				import('./scan').then(({ ScanAPI }) => {
					ScanAPI.getResults(data.scan_id).then((result) => {
						scanStore.stage = 'completed';
						scanStore.progress = 100;
						// Map backend result to frontend model
						scanStore.result = {
							id: result.scan_id,
							target: result.target,
							score: result.security_score,
							riskLevel: result.risk_level,
							timestamp: result.timestamp,
							issues: result.issues || [],
							summary: {
								headers: result.headers?.length || 0,
								ports: result.ports?.filter((p: any) => p.open).length || 0,
								ssl: result.ssl?.has_ssl ? 1 : 0,
								subdomains: result.subdomains?.length || 0
							}
						};

						// Add to history to update trend charts
						historyStore.addEntry(scanStore.result);
					});
				});
			} else if (data.type === 'error') {
				scanStore.error = data.error;
				scanStore.addLog(`Error: ${data.error}`, 'error');
			}
		};

		this.socket.onclose = () => {
			console.log('WebSocket Disconnected');
		};

		this.socket.onerror = (error) => {
			console.error('WebSocket Error:', error);
			scanStore.addLog('Connection lost. Attempting to reconnect...', 'error');
		};
	}

	disconnect() {
		if (this.socket) {
			this.socket.close();
			this.socket = null;
		}
	}
}

export const scanWS = new ScanWebSocket();
