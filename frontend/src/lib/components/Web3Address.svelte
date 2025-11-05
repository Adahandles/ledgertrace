<script>
    import { Copy, ExternalLink, Check } from 'lucide-svelte';
    
    export let address = '';
    export let network = 'ethereum'; // ethereum, polygon, solana, etc.
    export let label = '';
    export let explorerUrl = '';
    export let copyable = true;
    export let truncate = true;
    export let size = 'md'; // sm, md, lg
    
    let copied = false;
    
    // Network configurations
    const networks = {
        ethereum: {
            color: 'text-blue-400',
            bgColor: 'bg-blue-500/20',
            borderColor: 'border-blue-500/30',
            symbol: 'ETH',
            explorer: 'https://etherscan.io'
        },
        polygon: {
            color: 'text-purple-400',
            bgColor: 'bg-purple-500/20',
            borderColor: 'border-purple-500/30',
            symbol: 'MATIC',
            explorer: 'https://polygonscan.com'
        },
        solana: {
            color: 'text-green-400',
            bgColor: 'bg-green-500/20',
            borderColor: 'border-green-500/30',
            symbol: 'SOL',
            explorer: 'https://explorer.solana.com'
        },
        bitcoin: {
            color: 'text-orange-400',
            bgColor: 'bg-orange-500/20',
            borderColor: 'border-orange-500/30',
            symbol: 'BTC',
            explorer: 'https://blockstream.info'
        }
    };
    
    // Size configurations
    const sizeClasses = {
        sm: 'px-2 py-1 text-xs',
        md: 'px-3 py-2 text-sm',
        lg: 'px-4 py-3 text-base'
    };
    
    $: networkConfig = networks[network] || networks.ethereum;
    $: displayAddress = truncate && address ? 
        `${address.slice(0, 6)}...${address.slice(-4)}` : 
        address;
    $: fullExplorerUrl = explorerUrl || `${networkConfig.explorer}/address/${address}`;
    
    async function copyToClipboard() {
        if (!address || !copyable) return;
        
        try {
            await navigator.clipboard.writeText(address);
            copied = true;
            setTimeout(() => {
                copied = false;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy to clipboard:', err);
        }
    }
</script>

<div class="inline-flex items-center gap-2 {sizeClasses[size]} rounded-lg {networkConfig.bgColor} {networkConfig.borderColor} border backdrop-blur-sm transition-all duration-300 hover:scale-105 group">
    <!-- Network indicator -->
    <div class="flex items-center gap-1">
        <div class="w-2 h-2 rounded-full {networkConfig.color.replace('text-', 'bg-')} animate-pulse"></div>
        <span class="{networkConfig.color} font-mono font-medium">
            {networkConfig.symbol}
        </span>
    </div>
    
    <!-- Address -->
    <span class="font-mono {networkConfig.color} select-all">
        {displayAddress}
    </span>
    
    <!-- Action buttons -->
    <div class="flex items-center gap-1">
        <!-- Copy button -->
        {#if copyable}
            <button
                on:click={copyToClipboard}
                class="p-1 rounded hover:bg-white/10 transition-colors duration-200 group-hover:scale-110"
                title="Copy full address"
            >
                {#if copied}
                    <Check size={12} class="text-success-400" />
                {:else}
                    <Copy size={12} class="{networkConfig.color} opacity-70 hover:opacity-100" />
                {/if}
            </button>
        {/if}
        
        <!-- Explorer link -->
        {#if explorerUrl || address}
            <a
                href={fullExplorerUrl}
                target="_blank"
                rel="noopener noreferrer"
                class="p-1 rounded hover:bg-white/10 transition-colors duration-200 group-hover:scale-110"
                title="View on {networkConfig.explorer}"
            >
                <ExternalLink size={12} class="{networkConfig.color} opacity-70 hover:opacity-100" />
            </a>
        {/if}
    </div>
</div>