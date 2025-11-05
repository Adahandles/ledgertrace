<script>
    import { darkMode } from '../stores/darkMode.js';
    import { Sun, Moon } from 'lucide-svelte';
    
    export let size = 'md'; // sm, md, lg
    
    const sizeClasses = {
        sm: 'w-8 h-8',
        md: 'w-10 h-10', 
        lg: 'w-12 h-12'
    };
    
    const iconSizes = {
        sm: 16,
        md: 20,
        lg: 24
    };
</script>

<button
    on:click={darkMode.toggle}
    class="relative {sizeClasses[size]} rounded-xl bg-dark-800/20 dark:bg-white/10 border border-primary-500/20 hover:border-primary-400/40 transition-all duration-300 flex items-center justify-center group hover:scale-105 hover:shadow-glow backdrop-blur-sm"
    aria-label="Toggle dark mode"
>
    <!-- Sun icon (visible in dark mode) -->
    <div class="absolute transition-all duration-300 {$darkMode ? 'opacity-100 rotate-0' : 'opacity-0 rotate-90'}">
        <Sun size={iconSizes[size]} class="text-warning-400" />
    </div>
    
    <!-- Moon icon (visible in light mode) -->
    <div class="absolute transition-all duration-300 {!$darkMode ? 'opacity-100 rotate-0' : 'opacity-0 -rotate-90'}">
        <Moon size={iconSizes[size]} class="text-primary-400" />
    </div>
    
    <!-- Glow effect on hover -->
    <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-500/20 to-accent-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm"></div>
</button>

<style>
    /* Additional CSS for smooth icon transitions */
    button {
        backdrop-filter: blur(8px);
    }
</style>