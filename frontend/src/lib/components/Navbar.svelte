<script lang="ts">
	import { Shield, LayoutDashboard, Menu, X } from 'lucide-svelte';
	import { page } from '$app/stores';

	let isMobileMenuOpen = $state(false);

	const navItems = [{ name: 'Dashboard', path: '/', icon: LayoutDashboard }];
</script>

<nav class="glass border-border-light z-50 shrink-0 border-b">
	<div class="px-4 sm:px-6 lg:px-8">
		<div class="flex h-16 justify-between">
			<div class="flex items-center">
				<a href="/" class="flex items-center space-x-2">
					<Shield class="text-primary h-7 w-7" />
					<span class="text-lg font-bold tracking-tight text-neutral-200">
						Site<span class="text-primary">Scanner</span>
					</span>
				</a>
			</div>

			<!-- Desktop Navigation -->
			<div class="hidden items-center space-x-8 md:flex">
				{#each navItems as item}
					{@const Icon = item.icon}
					<a
						href={item.path}
						class="hover:text-primary flex items-center space-x-2 text-lg font-bold transition-colors {$page
							.url.pathname === item.path
							? 'text-primary'
							: 'text-neutral-400'}"
					>
						<Icon class="h-5 w-5" />
						<span>{item.name}</span>
					</a>
				{/each}
			</div>

			<!-- Mobile menu button -->
			<div class="flex items-center md:hidden">
				<button
					onclick={() => (isMobileMenuOpen = !isMobileMenuOpen)}
					class="text-neutral-400 hover:text-white focus:outline-none"
				>
					{#if isMobileMenuOpen}
						<X class="h-6 w-6" />
					{:else}
						<Menu class="h-6 w-6" />
					{/if}
				</button>
			</div>
		</div>
	</div>

	<!-- Mobile Navigation -->
	{#if isMobileMenuOpen}
		<div class="glass border-border-light border-t transition-all duration-300 md:hidden">
			<div class="space-y-1 px-2 pt-2 pb-3 sm:px-3">
				{#each navItems as item}
					{@const Icon = item.icon}
					<a
						href={item.path}
						class="flex items-center space-x-3 rounded-md px-3 py-2 text-lg font-bold {$page.url
							.pathname === item.path
							? 'bg-primary-light text-primary'
							: 'text-neutral-400 hover:bg-[#111111]'}"
						onclick={() => (isMobileMenuOpen = false)}
					>
						<Icon class="h-5 w-5" />
						<span>{item.name}</span>
					</a>
				{/each}
			</div>
		</div>
	{/if}
</nav>
