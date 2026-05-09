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
		low: 'text-emerald-600 bg-emerald-50 border-emerald-100',
		medium: 'text-amber-600 bg-amber-50 border-amber-100',
		high: 'text-red-600 bg-red-50 border-red-100',
		critical: 'text-white bg-slate-900 border-slate-800'
	};
	return colors[severity.toLowerCase() as keyof typeof colors] || 'text-slate-600 bg-slate-50';
}
