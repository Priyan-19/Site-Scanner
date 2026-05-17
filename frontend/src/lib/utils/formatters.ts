/**
 * Utility functions for formatting data in the SiteScanner UI.
 */

export function formatDate(date: string | Date): string {
	const d = new Date(date);
	return d.toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
}

export function formatUrl(url: string): string {
	try {
		const u = new URL(url.startsWith('http') ? url : `https://${url}`);
		return u.hostname;
	} catch {
		return url;
	}
}

export function getSeverityColor(severity: string): string {
	const colors = {
		low: 'bg-black text-emerald-500 border-emerald-500',
		medium: 'bg-black text-amber-500 border-amber-500',
		high: 'bg-black text-orange-500 border-orange-500',
		critical: 'bg-black text-red-500 border-red-500'
	};
	return colors[severity.toLowerCase() as keyof typeof colors] || 'text-neutral-400 bg-[#111111]';
}
