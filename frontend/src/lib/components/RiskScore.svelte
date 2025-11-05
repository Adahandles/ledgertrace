<script>
    import { onMount } from 'svelte';
    import { AlertTriangle, Shield, AlertCircle, TrendingUp } from 'lucide-svelte';
    
    export let score = 0;
    export let size = 'lg'; // sm, md, lg, xl
    export let showLabel = true;
    export let animated = true;
    
    let displayScore = 0;
    let barWidth = 0;
    
    // Size configurations
    const sizes = {
        sm: { height: 'h-2', text: 'text-sm', container: 'w-32' },
        md: { height: 'h-3', text: 'text-base', container: 'w-48' },
        lg: { height: 'h-4', text: 'text-lg', container: 'w-64' },
        xl: { height: 'h-6', text: 'text-2xl', container: 'w-80' }
    };
    
    function getRiskData(score) {
        if (score >= 75) return {
            level: 'Critical',
            color: 'danger',
            gradient: 'risk-bar-critical',
            icon: AlertTriangle,
            emoji: '🚨',
            bgColor: 'bg-danger-500/10',
            textColor: 'text-danger-400',
            glowColor: 'shadow-danger-glow'
        };
        if (score >= 50) return {
            level: 'High',
            color: 'warning',
            gradient: 'risk-bar-high',
            icon: AlertTriangle,
            emoji: '⚠️',
            bgColor: 'bg-warning-500/10',
            textColor: 'text-warning-400',
            glowColor: 'shadow-glow'
        };
        if (score >= 25) return {
            level: 'Medium',
            color: 'warning',
            gradient: 'risk-bar-medium',
            icon: AlertCircle,
            emoji: '🟡',
            bgColor: 'bg-warning-500/10',
            textColor: 'text-warning-400',
            glowColor: 'shadow-glow'
        };
        return {
            level: 'Low',
            color: 'success',
            gradient: 'risk-bar-low',
            icon: Shield,
            emoji: '✅',
            bgColor: 'bg-success-500/10',
            textColor: 'text-success-400',
            glowColor: 'shadow-success-glow'
        };
    }
    
    $: riskData = getRiskData(score);
    
    // Animate score counting and bar filling
    onMount(() => {
        if (animated) {
            // Animate score counter
            const duration = 1500; // 1.5 seconds
            const steps = 60;
            const increment = score / steps;
            let current = 0;
            
            const counter = setInterval(() => {
                current += increment;
                if (current >= score) {
                    displayScore = score;
                    clearInterval(counter);
                } else {
                    displayScore = Math.floor(current);
                }
            }, duration / steps);
            
            // Animate bar fill with delay
            setTimeout(() => {
                barWidth = Math.min(score, 100);
            }, 300);
        } else {
            displayScore = score;
            barWidth = Math.min(score, 100);
        }
    });
</script>

<div class="risk-score-container {sizes[size].container}">
    <!-- Score Display -->
    <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
            <span class="text-2xl animate-bounce-slow">{riskData.emoji}</span>
            <span class="text-sm font-medium text-gray-600 dark:text-gray-300">Risk Score:</span>
        </div>
        <div class="flex items-center gap-2">
            <div class="flex items-center gap-1">
                <svelte:component 
                    this={riskData.icon} 
                    class="h-5 w-5 {riskData.textColor} animate-pulse-slow" 
                />
                <span class="{sizes[size].text} font-bold text-cyber-gradient">
                    {displayScore}/100
                </span>
            </div>
        </div>
    </div>
    
    <!-- Risk Level Badge -->
    {#if showLabel}
        <div class="flex justify-center mb-4">
            <div class="badge-{riskData.color} px-4 py-2 rounded-full {riskData.glowColor} animate-glow">
                <span class="font-semibold">{riskData.level} Risk</span>
            </div>
        </div>
    {/if}
    
    <!-- Animated Progress Bar -->
    <div class="relative">
        <!-- Background bar -->
        <div class="w-full {sizes[size].height} bg-dark-700 dark:bg-gray-200 rounded-full overflow-hidden">
            <!-- Animated fill -->
            <div 
                class="{sizes[size].height} {riskData.gradient} rounded-full transition-all duration-1500 ease-out transform origin-left"
                style="width: {barWidth}%"
            >
                <!-- Shimmer effect -->
                <div class="w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
            </div>
        </div>
        
        <!-- Scale markers -->
        <div class="flex justify-between text-xs text-gray-500 mt-2">
            <span class="flex items-center gap-1">
                <div class="w-2 h-2 bg-success-400 rounded-full"></div>
                <span>0</span>
            </span>
            <span class="flex items-center gap-1">
                <div class="w-2 h-2 bg-warning-400 rounded-full"></div>
                <span>25</span>
            </span>
            <span class="flex items-center gap-1">
                <div class="w-2 h-2 bg-warning-500 rounded-full"></div>
                <span>50</span>
            </span>
            <span class="flex items-center gap-1">
                <div class="w-2 h-2 bg-danger-400 rounded-full"></div>
                <span>75</span>
            </span>
            <span class="flex items-center gap-1">
                <div class="w-2 h-2 bg-danger-600 rounded-full"></div>
                <span>100</span>
            </span>
        </div>
    </div>
    
    <!-- Pulsing danger indicator for high risk -->
    {#if score >= 75}
        <div class="flex items-center justify-center mt-3 animate-pulse">
            <div class="flex items-center gap-2 px-3 py-1 bg-danger-500/20 rounded-full border border-danger-500/30">
                <div class="w-2 h-2 bg-danger-400 rounded-full animate-ping"></div>
                <span class="text-xs font-medium text-danger-400">High Risk Alert</span>
            </div>
        </div>
    {/if}
</div>

<style>
    .risk-score-container {
        @apply p-4 rounded-xl;
        background: rgba(30, 41, 59, 0.3);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(45, 212, 191, 0.1);
    }
    
    .dark .risk-score-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(156, 163, 175, 0.2);
    }
</style>