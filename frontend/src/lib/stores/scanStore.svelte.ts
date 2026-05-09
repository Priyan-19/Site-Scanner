export type ScanStage =
	| 'idle'
	| 'initializing'
	| 'checking_http'
	| 'headers_analysis'
	| 'port_scanning'
	| 'whois_lookup'
	| 'subdomain_discovery'
	| 'ssl_analysis'
	| 'finalizing'
	| 'completed'
	| 'failed';

export interface ScanLog {
	timestamp: string;
	level: 'info' | 'warning' | 'error' | 'success';
	message: string;
}

export interface ScanResult {
	id: string;
	target: string;
	score: number;
	riskLevel: 'Low' | 'Medium' | 'High' | 'Critical';
	timestamp: string;
	issues: any[];
	summary: {
		headers: number;
		ports: number;
		ssl: number;
		subdomains: number;
	};
}

class ScanStore {
	activeScanId = $state<string | null>(null);
	stage = $state<ScanStage>('idle');
	progress = $state(0);
	logs = $state<ScanLog[]>([]);
	result = $state<ScanResult | null>(null);
	error = $state<string | null>(null);

	reset() {
		this.activeScanId = null;
		this.stage = 'idle';
		this.progress = 0;
		this.logs = [];
		this.result = null;
		this.error = null;
	}

	addLog(message: string, level: ScanLog['level'] = 'info') {
		this.logs = [
			...this.logs,
			{
				timestamp: new Date().toLocaleTimeString(),
				level,
				message
			}
		];
	}

	setStage(stage: ScanStage, progress: number) {
		this.stage = stage;
		this.progress = progress;
	}
}

export const scanStore = new ScanStore();
