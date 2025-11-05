<script>
    import { onMount } from 'svelte';
    import { 
        Building, MapPin, AlertTriangle, Shield, ExternalLink, 
        TrendingUp, Scale, DollarSign, Globe, Users, Download,
        Eye, Clock, CheckCircle, XCircle, FileText
    } from 'lucide-svelte';
    
    export let entityData;
    export let onExportPDF = () => {};
    export let onExportJSON = () => {};
    
    let activeTab = 'overview';
    let riskBarWidth = 0;
    
    // Animate risk bar on mount
    onMount(() => {
        setTimeout(() => {
            riskBarWidth = Math.min(entityData.risk_score, 100);
        }, 500);
    });
    
    const tabs = [
        { id: 'overview', label: 'Overview', icon: Eye },
        { id: 'property', label: 'Property', icon: MapPin },
        { id: 'court', label: 'Legal', icon: Scale },
        { id: 'links', label: 'Sources', icon: ExternalLink }
    ];
    
    function getRiskLevel(score) {
        if (score >= 75) return { level: 'Critical', color: 'danger', emoji: '🚨' };
        if (score >= 50) return { level: 'High', color: 'warning', emoji: '⚠️' };
        if (score >= 25) return { level: 'Medium', color: 'warning', emoji: '🟡' };
        return { level: 'Low', color: 'success', emoji: '✅' };
    }
    
    function getRiskBarClass(score) {
        if (score >= 75) return 'risk-bar-critical';
        if (score >= 50) return 'risk-bar-high';
        if (score >= 25) return 'risk-bar-medium';
        return 'risk-bar-low';
    }
    
    const riskInfo = getRiskLevel(entityData.risk_score);
</script>

<div class="entity-card dark:entity-card animate-fade-in">
    <!-- Header with risk score -->
    <div class="flex items-start justify-between mb-6">
        <div class="flex-1">
            <h2 class="text-2xl font-bold text-cyber-gradient mb-2 flex items-center gap-3">
                <Building class="h-6 w-6 text-primary-400" />
                {entityData.name}
            </h2>
            
            {#if entityData.property?.address}
                <p class="text-gray-400 dark:text-gray-500 flex items-center gap-2 mb-3">
                    <MapPin class="h-4 w-4" />
                    {entityData.property.address}
                </p>
            {/if}
            
            <!-- Risk Score Display -->
            <div class="glass-panel dark:glass-panel-light p-4 mb-4">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                        <span class="text-sm font-medium text-gray-600 dark:text-gray-300">Risk Assessment:</span>
                        <span class="text-2xl">{riskInfo.emoji}</span>
                    </div>
                    <div class="text-right">
                        <div class="text-3xl font-bold text-cyber-gradient">{entityData.risk_score}/100</div>
                        <div class="text-sm badge-{riskInfo.color} px-2 py-1">{riskInfo.level} Risk</div>
                    </div>
                </div>
                
                <!-- Animated Risk Bar -->
                <div class="risk-bar bg-dark-700 dark:bg-gray-200">
                    <div 
                        class="risk-fill {getRiskBarClass(entityData.risk_score)}"
                        style="width: {riskBarWidth}%"
                    ></div>
                </div>
                
                <div class="flex justify-between text-xs text-gray-500 mt-2">
                    <span class="flex items-center gap-1">
                        <Shield class="h-3 w-3 text-success-400" />
                        0 - Minimal
                    </span>
                    <span class="flex items-center gap-1">
                        <AlertTriangle class="h-3 w-3 text-danger-400" />
                        100 - Critical
                    </span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Export Buttons -->
    <div class="flex gap-3 mb-6">
        <button
            on:click={onExportPDF}
            class="btn-cyber flex-1 group"
        >
            <Download class="h-4 w-4 mr-2 group-hover:animate-bounce" />
            📄 PDF Report
        </button>
        <button
            on:click={onExportJSON}
            class="btn-secondary flex-1 group"
        >
            <FileText class="h-4 w-4 mr-2 group-hover:animate-pulse" />
            🧬 JSON Data
        </button>
    </div>
    
    <!-- Tab Navigation -->
    <div class="flex space-x-1 mb-6 bg-dark-700/30 dark:bg-gray-100 rounded-xl p-1">
        {#each tabs as tab}
            <button
                class="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg text-sm font-medium transition-all duration-200 {activeTab === tab.id ? 'nav-item-active' : 'nav-item'}"
                on:click={() => activeTab = tab.id}
            >
                <svelte:component this={tab.icon} class="h-4 w-4" />
                {tab.label}
            </button>
        {/each}
    </div>
    
    <!-- Tab Content -->
    <div class="tab-content">
        {#if activeTab === 'overview'}
            <div class="space-y-4 animate-slide-up">
                <!-- Entity Type -->
                {#if entityData.entity_type?.is_trust}
                    <div class="glass-panel p-4">
                        <h4 class="font-semibold text-warning-400 mb-2 flex items-center gap-2">
                            <AlertTriangle class="h-4 w-4" />
                            Trust Entity Detected
                        </h4>
                        {#if entityData.entity_type.trust_types.length > 0}
                            <div class="flex flex-wrap gap-2">
                                {#each entityData.entity_type.trust_types as trustType}
                                    <span class="badge-warning">{trustType}</span>
                                {/each}
                            </div>
                        {/if}
                    </div>
                {/if}
                
                <!-- Anomalies -->
                {#if entityData.anomalies?.length > 0}
                    <div class="glass-panel p-4">
                        <h4 class="font-semibold text-danger-400 mb-3 flex items-center gap-2">
                            <AlertTriangle class="h-4 w-4" />
                            Detected Anomalies ({entityData.anomalies.length})
                        </h4>
                        <div class="space-y-2">
                            {#each entityData.anomalies.slice(0, 3) as anomaly}
                                <div class="text-sm text-gray-300 dark:text-gray-600 flex items-start gap-2">
                                    <div class="w-2 h-2 bg-danger-400 rounded-full mt-2 flex-shrink-0"></div>
                                    {anomaly}
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}
                
                <!-- Quick Stats -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="glass-panel p-4 text-center">
                        <Scale class="h-6 w-6 mx-auto mb-2 text-accent-400" />
                        <div class="text-2xl font-bold text-cyber-gradient">{entityData.court_data?.case_count || 0}</div>
                        <div class="text-sm text-gray-400">Court Cases</div>
                    </div>
                    <div class="glass-panel p-4 text-center">
                        <Globe class="h-6 w-6 mx-auto mb-2 text-primary-400" />
                        <div class="text-2xl font-bold text-cyber-gradient">{entityData.domain_data?.domain_count || 0}</div>
                        <div class="text-sm text-gray-400">Domains</div>
                    </div>
                </div>
            </div>
        {/if}
        
        {#if activeTab === 'property' && entityData.property}
            <div class="space-y-4 animate-slide-up">
                <!-- Property Info -->
                <div class="glass-panel p-4">
                    <h4 class="font-semibold text-primary-400 mb-3 flex items-center gap-2">
                        <MapPin class="h-4 w-4" />
                        {entityData.property.county} County Property
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="text-gray-400">Owner:</span>
                            <span class="ml-2 font-medium">{entityData.property.owner_name}</span>
                        </div>
                        <div>
                            <span class="text-gray-400">Land Use:</span>
                            <span class="ml-2 font-medium">{entityData.property.land_use}</span>
                        </div>
                        <div>
                            <span class="text-gray-400">Market Value:</span>
                            <span class="ml-2 font-medium text-success-400">{entityData.property.market_value}</span>
                        </div>
                        <div>
                            <span class="text-gray-400">Parcel ID:</span>
                            <span class="ml-2 font-mono text-accent-400">{entityData.property.parcel_id}</span>
                        </div>
                    </div>
                </div>
                
                <!-- County Offices -->
                {#if entityData.property.offices}
                    <div class="space-y-3">
                        <h4 class="font-semibold text-gray-300 dark:text-gray-600">Government Offices</h4>
                        {#each Object.entries(entityData.property.offices) as [type, office]}
                            <div class="glass-panel p-4 hover:border-primary-400/40 transition-all duration-300">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <div class="font-medium text-primary-400 flex items-center gap-2">
                                            {#if type.includes('property')}
                                                📄
                                            {:else if type.includes('tax')}
                                                💰
                                            {:else}
                                                ⚖️
                                            {/if}
                                            {office.name}
                                        </div>
                                        <div class="text-sm text-gray-400 mt-1">{office.description}</div>
                                    </div>
                                    <div class="flex gap-2">
                                        <a 
                                            href={office.url} 
                                            target="_blank" 
                                            class="btn-secondary py-1 px-3 text-xs hover:scale-105"
                                        >
                                            <ExternalLink class="h-3 w-3 mr-1" />
                                            Visit
                                        </a>
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        {/if}
        
        {#if activeTab === 'court' && entityData.court_data}
            <div class="space-y-4 animate-slide-up">
                <!-- Court Summary -->
                <div class="glass-panel p-4">
                    <h4 class="font-semibold text-accent-400 mb-3 flex items-center gap-2">
                        <Scale class="h-4 w-4" />
                        Legal Activity Summary
                    </h4>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div class="flex items-center justify-between">
                            <span class="text-gray-400">Foreclosure:</span>
                            {#if entityData.court_data.has_foreclosure}
                                <XCircle class="h-4 w-4 text-danger-400" />
                            {:else}
                                <CheckCircle class="h-4 w-4 text-success-400" />
                            {/if}
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-gray-400">Bankruptcy:</span>
                            {#if entityData.court_data.has_bankruptcy}
                                <XCircle class="h-4 w-4 text-danger-400" />
                            {:else}
                                <CheckCircle class="h-4 w-4 text-success-400" />
                            {/if}
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-gray-400">Tax Liens:</span>
                            {#if entityData.court_data.has_tax_lien}
                                <XCircle class="h-4 w-4 text-danger-400" />
                            {:else}
                                <CheckCircle class="h-4 w-4 text-success-400" />
                            {/if}
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-gray-400">Civil Litigation:</span>
                            {#if entityData.court_data.has_civil}
                                <XCircle class="h-4 w-4 text-danger-400" />
                            {:else}
                                <CheckCircle class="h-4 w-4 text-success-400" />
                            {/if}
                        </div>
                    </div>
                </div>
                
                <!-- Recent Cases -->
                {#if entityData.court_data.cases?.length > 0}
                    <div class="space-y-3">
                        <h4 class="font-semibold text-gray-300 dark:text-gray-600">Recent Court Cases</h4>
                        {#each entityData.court_data.cases.slice(0, 3) as case}
                            <div class="glass-panel p-4">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1">
                                        <div class="font-medium text-primary-400">{case.case_type}</div>
                                        <div class="text-sm text-gray-400 mt-1">
                                            Case #{case.case_number} • Filed {case.filed_date}
                                        </div>
                                        {#if case.amount}
                                            <div class="text-sm text-warning-400 mt-1">Amount: {case.amount}</div>
                                        {/if}
                                    </div>
                                    <div class="badge-{case.status === 'Open' ? 'danger' : 'info'} ml-4">
                                        {case.status}
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        {/if}
        
        {#if activeTab === 'links'}
            <div class="space-y-4 animate-slide-up">
                <!-- Verification Links -->
                {#if entityData.property?.verification_links}
                    <div class="glass-panel p-4">
                        <h4 class="font-semibold text-success-400 mb-3 flex items-center gap-2">
                            <ExternalLink class="h-4 w-4" />
                            Direct Verification Links
                        </h4>
                        <div class="space-y-2">
                            {#each Object.entries(entityData.property.verification_links) as [type, url]}
                                <a 
                                    href={url} 
                                    target="_blank"
                                    class="block p-3 rounded-lg bg-dark-700/30 dark:bg-gray-100 hover:bg-primary-500/10 transition-colors duration-200 group"
                                >
                                    <div class="flex items-center justify-between">
                                        <span class="text-sm font-medium text-primary-400 group-hover:text-primary-300">
                                            {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                        </span>
                                        <ExternalLink class="h-4 w-4 text-gray-400 group-hover:text-primary-400 transition-colors duration-200" />
                                    </div>
                                </a>
                            {/each}
                        </div>
                    </div>
                {/if}
                
                <!-- Source Links -->
                {#if entityData.source_links}
                    <div class="glass-panel p-4">
                        <h4 class="font-semibold text-accent-400 mb-3 flex items-center gap-2">
                            <Globe class="h-4 w-4" />
                            Public Records Sources
                        </h4>
                        <div class="space-y-2">
                            {#each Object.entries(entityData.source_links) as [source, url]}
                                <a 
                                    href={url} 
                                    target="_blank"
                                    class="block p-3 rounded-lg bg-dark-700/30 dark:bg-gray-100 hover:bg-accent-500/10 transition-colors duration-200 group"
                                >
                                    <div class="flex items-center justify-between">
                                        <span class="text-sm font-medium text-accent-400 group-hover:text-accent-300">
                                            {source.toUpperCase()}
                                        </span>
                                        <ExternalLink class="h-4 w-4 text-gray-400 group-hover:text-accent-400 transition-colors duration-200" />
                                    </div>
                                </a>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>