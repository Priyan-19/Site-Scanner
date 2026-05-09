<script lang="ts">
	import { toastStore } from '$lib/stores/toastStore.svelte';
	import { CheckCircle2, AlertCircle, Info, X } from 'lucide-svelte';
	import { fly, fade } from 'svelte/transition';
	import { flip } from 'svelte/animate';

	const icons = {
		success: CheckCircle2,
		error: AlertCircle,
		info: Info
	} as const;

	const styles = {
		success: 'bg-emerald-50 border-emerald-100 text-emerald-800',
		error: 'bg-red-50 border-red-100 text-red-800',
		info: 'bg-blue-50 border-blue-100 text-blue-800'
	} as const;
</script>

<div class="pointer-events-none fixed right-6 bottom-6 z-[9999] flex flex-col gap-3">
	{#each toastStore.toasts as toast (toast.id)}
		{@const Icon = icons[toast.type]}
		<div
			animate:flip={{ duration: 300 }}
			in:fly={{ x: 100, duration: 400 }}
			out:fade={{ duration: 200 }}
			class="pointer-events-auto flex max-w-sm min-w-[300px] items-center justify-between rounded-xl border p-4 shadow-lg {styles[
				toast.type
			]}"
		>
			<div class="flex items-center space-x-3">
				<Icon class="h-5 w-5" />
				<span class="text-sm font-bold">{toast.message}</span>
			</div>
			<button
				onclick={() => toastStore.remove(toast.id)}
				class="rounded-full p-1 transition-colors hover:bg-black/5"
			>
				<X class="h-4 w-4" />
			</button>
		</div>
	{/each}
</div>
