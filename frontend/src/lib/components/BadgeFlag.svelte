<script>
    import { AlertTriangle, XCircle, AlertCircle, DollarSign, Scale, Globe, Building, Shield, Info } from 'lucide-svelte';
    
    export let type = 'warning'; // danger, warning, info, success
    export let variant = 'default'; // default, outlined, filled
    export let size = 'md'; // sm, md, lg
    export let icon = null;
    export let tooltip = '';
    export let pulse = false;
    export let glow = false;
    
    // Predefined badge types for common entity flags
    const flagTypes = {
        'no-ein': {
            type: 'warning',
            icon: AlertTriangle,
            text: 'No EIN',
            tooltip: 'Entity ID Number not provided - potential compliance issue'
        },
        'foreclosure': {
            type: 'danger',
            icon: Building,
            text: 'Foreclosure',
            tooltip: 'Entity involved in foreclosure proceedings'
        },
        'bankruptcy': {
            type: 'danger',
            icon: DollarSign,
            text: 'Bankruptcy',
            tooltip: 'Entity has bankruptcy filings on record'
        },
        'tax-lien': {
            type: 'warning',
            icon: AlertCircle,
            text: 'Tax Lien',
            tooltip: 'Outstanding tax obligations identified'
        },
        'court-active': {
            type: 'warning',
            icon: Scale,
            text: 'Active Litigation',
            tooltip: 'Currently involved in active court cases'
        },
        'no-website': {
            type: 'info',
            icon: Globe,
            text: 'No Web Presence',
            tooltip: 'No active website or digital presence detected'
        },
        'high-risk-trust': {
            type: 'danger',
            icon: AlertTriangle,
            text: 'High-Risk Trust',
            tooltip: 'Trust structure identified as high-risk category'
        },
        'offshore': {
            type: 'danger',
            icon: Building,
            text: 'Offshore Entity',
            tooltip: 'Entity registered in offshore jurisdiction'
        },
        'verified': {
            type: 'success',
            icon: Shield,
            text: 'Verified',
            tooltip: 'Entity verification completed successfully'
        },
        'monitoring': {
            type: 'info',
            icon: Info,
            text: 'Under Monitoring',
            tooltip: 'Entity is currently under regulatory monitoring'
        }
    };
    
    // Size configurations
    const sizeClasses = {
        sm: 'px-2 py-1 text-xs',
        md: 'px-3 py-1.5 text-sm',
        lg: 'px-4 py-2 text-base'
    };
    
    const iconSizes = {
        sm: 12,
        md: 14,
        lg: 16
    };
    
    // Get badge configuration
    function getBadgeConfig(flagType) {
        if (flagTypes[flagType]) {
            return flagTypes[flagType];
        }
        return {
            type: type,
            icon: icon,
            text: flagType,
            tooltip: tooltip
        };
    }
    
    $: config = getBadgeConfig($$props.flagType || 'default');
    $: badgeType = config.type || type;
    $: badgeIcon = config.icon || icon;
    $: badgeText = config.text || $$slots.default;
    $: badgeTooltip = config.tooltip || tooltip;
    
    // Style classes based on type and variant
    function getBadgeClasses(badgeType, variant) {
        const baseClasses = `inline-flex items-center gap-1.5 rounded-full font-medium transition-all duration-300 border ${sizeClasses[size]}`;
        
        if (variant === 'outlined') {
            const outlinedClasses = {
                danger: 'text-danger-400 border-danger-500/50 bg-transparent hover:bg-danger-500/10',
                warning: 'text-warning-400 border-warning-500/50 bg-transparent hover:bg-warning-500/10',
                success: 'text-success-400 border-success-500/50 bg-transparent hover:bg-success-500/10',
                info: 'text-accent-400 border-accent-500/50 bg-transparent hover:bg-accent-500/10'
            };
            return `${baseClasses} ${outlinedClasses[badgeType]}`;
        }
        
        if (variant === 'filled') {
            const filledClasses = {
                danger: 'text-white bg-danger-500 border-danger-600 hover:bg-danger-600',
                warning: 'text-white bg-warning-500 border-warning-600 hover:bg-warning-600',
                success: 'text-white bg-success-500 border-success-600 hover:bg-success-600',
                info: 'text-white bg-accent-500 border-accent-600 hover:bg-accent-600'
            };
            return `${baseClasses} ${filledClasses[badgeType]}`;
        }
        
        // Default variant (glass effect)
        const defaultClasses = {
            danger: 'text-danger-400 bg-danger-500/20 border-danger-500/30 hover:bg-danger-500/25 hover:border-danger-400/40',
            warning: 'text-warning-400 bg-warning-500/20 border-warning-500/30 hover:bg-warning-500/25 hover:border-warning-400/40',
            success: 'text-success-400 bg-success-500/20 border-success-500/30 hover:bg-success-500/25 hover:border-success-400/40',
            info: 'text-accent-400 bg-accent-500/20 border-accent-500/30 hover:bg-accent-500/25 hover:border-accent-400/40'
        };
        
        return `${baseClasses} ${defaultClasses[badgeType]} backdrop-blur-sm`;
    }
    
    $: badgeClasses = getBadgeClasses(badgeType, variant);
    $: pulseClass = pulse ? 'animate-pulse' : '';
    $: glowClass = glow ? (badgeType === 'danger' ? 'shadow-danger-glow' : 'shadow-glow') : '';
    
    let showTooltip = false;
    let tooltipElement;
    
    function handleMouseEnter() {
        if (badgeTooltip) {
            showTooltip = true;
        }
    }
    
    function handleMouseLeave() {
        showTooltip = false;
    }
</script>

<div class="relative inline-block">
    <!-- Badge -->
    <span 
        class="{badgeClasses} {pulseClass} {glowClass} cursor-help select-none"
        on:mouseenter={handleMouseEnter}
        on:mouseleave={handleMouseLeave}
        role="button"
        tabindex="0"
    >
        <!-- Icon -->
        {#if badgeIcon}
            <svelte:component this={badgeIcon} size={iconSizes[size]} />
        {/if}
        
        <!-- Text content -->
        <span>
            {#if badgeText}
                {badgeText}
            {:else}
                <slot />
            {/if}
        </span>
        
        <!-- Pulsing indicator for critical badges -->
        {#if pulse && badgeType === 'danger'}
            <div class="w-2 h-2 bg-current rounded-full animate-ping"></div>
        {/if}
    </span>
    
    <!-- Tooltip -->
    {#if showTooltip && badgeTooltip}
        <div 
            bind:this={tooltipElement}
            class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-dark-800 text-white text-xs rounded-lg shadow-lg z-50 whitespace-nowrap animate-fade-in backdrop-blur-sm border border-primary-500/20"
            style="max-width: 200px; white-space: normal;"
        >
            {badgeTooltip}
            <!-- Tooltip arrow -->
            <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-dark-800"></div>
        </div>
    {/if}
</div>

<!-- Predefined badge components for common use cases -->
<style>
    /* Additional hover effects for badges */
    span[role="button"]:hover {
        transform: translateY(-1px) scale(1.05);
    }
    
    span[role="button"]:active {
        transform: translateY(0) scale(1.02);
    }
</style>