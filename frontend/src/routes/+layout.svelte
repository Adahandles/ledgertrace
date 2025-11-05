<script>
	import { onMount } from 'svelte';
	import { darkMode } from '../lib/stores/darkMode.js';
	import '../app.css';
	
	onMount(() => {
		darkMode.init();
	});
</script>

<div class="min-h-screen transition-colors duration-300">
	<slot />
</div>