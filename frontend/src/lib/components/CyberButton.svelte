<script>
    export let variant = 'primary'; // primary, secondary, success, warning, danger
    export let size = 'md'; // sm, md, lg, xl
    export let glow = false;
    export let pulse = false;
    export let loading = false;
    export let disabled = false;
    export let href = null;
    export let target = null;
    export let type = 'button';
    
    // Button variants
    const variants = {
        primary: {
            base: 'bg-gradient-to-r from-primary-500 to-accent-500 text-white border-transparent',
            hover: 'hover:from-primary-400 hover:to-accent-400 hover:shadow-glow',
            glow: 'shadow-glow animate-glow'
        },
        secondary: {
            base: 'bg-dark-800 text-primary-400 border-primary-500/30',
            hover: 'hover:bg-dark-700 hover:border-primary-400/50 hover:text-primary-300',
            glow: 'shadow-glow'
        },
        success: {
            base: 'bg-gradient-to-r from-success-500 to-success-600 text-white border-transparent',
            hover: 'hover:from-success-400 hover:to-success-500 hover:shadow-success-glow',
            glow: 'shadow-success-glow animate-glow'
        },
        warning: {
            base: 'bg-gradient-to-r from-warning-500 to-warning-600 text-white border-transparent',
            hover: 'hover:from-warning-400 hover:to-warning-500',
            glow: 'shadow-glow'
        },
        danger: {
            base: 'bg-gradient-to-r from-danger-500 to-danger-600 text-white border-transparent',
            hover: 'hover:from-danger-400 hover:to-danger-500 hover:shadow-danger-glow',
            glow: 'shadow-danger-glow animate-glow'
        },
        ghost: {
            base: 'bg-transparent text-primary-400 border-primary-500/30',
            hover: 'hover:bg-primary-500/10 hover:border-primary-400/50',
            glow: 'shadow-inner-glow'
        },
        outline: {
            base: 'bg-transparent text-primary-400 border-primary-500/50',
            hover: 'hover:bg-primary-500 hover:text-white hover:border-primary-500',
            glow: 'shadow-glow'
        }
    };
    
    // Size configurations
    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-6 py-3 text-base',
        lg: 'px-8 py-4 text-lg',
        xl: 'px-10 py-5 text-xl'
    };
    
    $: variantConfig = variants[variant] || variants.primary;
    $: baseClasses = `
        inline-flex items-center justify-center gap-2 font-medium rounded-xl
        border transition-all duration-300 transform
        ${sizes[size]}
        ${variantConfig.base}
        ${!disabled ? variantConfig.hover : ''}
        ${glow ? variantConfig.glow : ''}
        ${pulse ? 'animate-pulse-slow' : ''}
        ${!disabled ? 'hover:scale-105 hover:-translate-y-0.5 active:scale-95' : ''}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${loading ? 'cursor-wait' : ''}
        focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 focus:ring-offset-dark-900
    `.trim().replace(/\s+/g, ' ');
    
    function handleClick(event) {
        if (disabled || loading) {
            event.preventDefault();
            return;
        }
    }
</script>

{#if href}
    <a
        {href}
        {target}
        class={baseClasses}
        on:click={handleClick}
        {...$$restProps}
    >
        {#if loading}
            <div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
        {/if}
        <slot />
        
        <!-- Shine effect overlay -->
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -skew-x-12 transform -translate-x-full transition-transform duration-700 group-hover:translate-x-full"></div>
    </a>
{:else}
    <button
        {type}
        {disabled}
        class="{baseClasses} relative overflow-hidden group"
        on:click={handleClick}
        {...$$restProps}
    >
        {#if loading}
            <div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
        {/if}
        <slot />
        
        <!-- Shine effect overlay -->
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -skew-x-12 transform -translate-x-full transition-transform duration-700 group-hover:translate-x-full"></div>
    </button>
{/if}

<style>
    /* Additional button-specific animations */
    button:active, a:active {
        transform: translateY(0) scale(0.98);
    }
</style>