class ToastStore {
	toasts = $state<{ id: number; message: string; type: 'success' | 'error' | 'info' }[]>([]);
	private nextId = 0;

	add(message: string, type: 'success' | 'error' | 'info' = 'info') {
		const id = this.nextId++;
		this.toasts = [...this.toasts, { id, message, type }];

		// Auto-remove after 4 seconds
		setTimeout(() => {
			this.remove(id);
		}, 4000);
	}

	remove(id: number) {
		this.toasts = this.toasts.filter((t) => t.id !== id);
	}
}

export const toastStore = new ToastStore();
