<script>
	import { Search, AlertTriangle, ExternalLink, TrendingUp, Shield, AlertCircle, Info, MapPin, DollarSign, Building } from 'lucide-svelte';
	
	let searchQuery = '';
	let searchAddress = '';
	let loading = false;
	let entityData = null;
	let error = null;

	const API_BASE = 'http://localhost:8000';
	
	async function searchEntity() {
		if (!searchQuery.trim()) return;
		
		loading = true;
		error = null;
		entityData = null;
		
		try {
			const response = await fetch(`${API_BASE}/analyze`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					name: searchQuery,
					address: searchAddress || null,
					ein: null,
					officers: []
				})
			});
			
			if (!response.ok) {
				throw new Error('Failed to analyze entity');
			}
			
			entityData = await response.json();
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	}
	
	function getRiskColor(score) {
		if (score >= 75) return 'text-red-700 bg-gradient-to-r from-red-50 to-red-100 border-red-200';
		if (score >= 50) return 'text-red-600 bg-gradient-to-r from-red-50 to-orange-50 border-red-200';
		if (score >= 25) return 'text-yellow-700 bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200';
		if (score >= 10) return 'text-yellow-600 bg-gradient-to-r from-yellow-50 to-yellow-100 border-yellow-200';
		return 'text-green-700 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200';
	}
	
	function getRiskLabel(score) {
		if (score >= 75) return 'Critical Risk';
		if (score >= 50) return 'High Risk';
		if (score >= 25) return 'Medium Risk';
		if (score >= 10) return 'Low Risk';
		return 'Minimal Risk';
	}
	
	function getRiskIcon(score) {
		if (score >= 75) return 'AlertTriangle';
		if (score >= 50) return 'AlertTriangle';
		if (score >= 25) return 'AlertCircle';
		if (score >= 10) return 'Info';
		return 'Shield';
	}
	
	function getRiskBarColor(score) {
		if (score >= 75) return 'bg-gradient-to-r from-red-500 to-red-600';
		if (score >= 50) return 'bg-gradient-to-r from-red-400 to-orange-500';
		if (score >= 25) return 'bg-gradient-to-r from-yellow-400 to-amber-500';
		if (score >= 10) return 'bg-gradient-to-r from-yellow-300 to-yellow-400';
		return 'bg-gradient-to-r from-green-400 to-emerald-500';
	}
	
	function getTrustTypeColor(trustType) {
		if (trustType.includes('Charitable')) return 'bg-green-100 text-green-800 border-green-200';
		if (trustType.includes('Business') || trustType.includes('Foreign')) return 'bg-red-100 text-red-800 border-red-200';
		if (trustType.includes('Investment') || trustType.includes('REIT')) return 'bg-blue-100 text-blue-800 border-blue-200';
		if (trustType.includes('Family') || trustType.includes('Living')) return 'bg-purple-100 text-purple-800 border-purple-200';
		return 'bg-gray-100 text-gray-800 border-gray-200';
	}
	
	function getTrustRiskIndicatorColor(indicator) {
		if (indicator.includes('high_risk') || indicator.includes('offshore')) return 'bg-red-50 text-red-700 border-red-200';
		if (indicator.includes('requires_regulation')) return 'bg-yellow-50 text-yellow-700 border-yellow-200';
		return 'bg-blue-50 text-blue-700 border-blue-200';
	}

	function getSourceUrl(entityName, source) {
		const encodedName = encodeURIComponent(entityName);
		const sources = {
			sunbiz: `http://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults?InquiryType=EntityName&SearchTerm=${encodedName}`,
			irs: `https://apps.irs.gov/app/eos/allSearch?names=${encodedName}`,
			sba: `https://www.sba.gov/partners/contracting-officials/procurement-center-representatives/search?name=${encodedName}`
		};
		return sources[source] || '#';
	}
</script>

<svelte:head>
	<title>LedgerTrace - Entity Risk Analysis</title>
	<style>
		@import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');
	</style>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
	<!-- Header -->
	<header class="bg-white shadow-sm border-b">
		<div class="max-w-7xl mx-auto px-4 py-6">
			<div class="flex items-center space-x-3">
				<Shield class="h-8 w-8 text-indigo-600" />
				<h1 class="text-3xl font-bold text-gray-900">LedgerTrace</h1>
				<span class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">Entity Risk Analysis</span>
			</div>
		</div>
	</header>

	<main class="max-w-4xl mx-auto px-4 py-8">
		<!-- Search Section -->
		<div class="bg-white rounded-lg shadow-lg p-6 mb-8">
			<div class="text-center mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-2">Search Entity</h2>
				<p class="text-gray-600">Enter an organization name to analyze risk factors and red flags</p>
			</div>
			
			<form on:submit|preventDefault={searchEntity} class="space-y-4">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label for="entity-name" class="block text-sm font-medium text-gray-700 mb-2">Entity Name</label>
						<input
							id="entity-name"
							bind:value={searchQuery}
							type="text"
							placeholder="Enter entity name (e.g., ABC Corp)"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
							disabled={loading}
						/>
					</div>
					<div>
						<label for="entity-address" class="block text-sm font-medium text-gray-700 mb-2">Address (Optional)</label>
						<input
							id="entity-address"
							bind:value={searchAddress}
							type="text"
							placeholder="Enter address for property analysis"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
							disabled={loading}
						/>
					</div>
				</div>
				<div class="flex justify-center">
					<button
						type="submit"
						disabled={loading || !searchQuery.trim()}
						class="px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
					>
						<Search class="h-5 w-5" />
						<span>{loading ? 'Analyzing...' : 'Analyze Entity'}</span>
					</button>
				</div>
			</form>
		</div>

		<!-- Error Display -->
		{#if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
				<div class="flex items-center space-x-2">
					<AlertTriangle class="h-5 w-5 text-red-600" />
					<p class="text-red-800">Error: {error}</p>
				</div>
			</div>
		{/if}

		<!-- Entity Profile -->
		{#if entityData}
			<div class="bg-white rounded-lg shadow-lg p-6">
				<!-- Entity Header -->
				<div class="border-b pb-6 mb-6">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-2xl font-bold text-gray-900">{entityData.name}</h3>
						<div class="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
							Analysis Complete
						</div>
					</div>
					
					<!-- Risk Score -->
					<div class="flex items-center space-x-4">
						<div class="flex items-center space-x-2">
							<TrendingUp class="h-5 w-5 text-gray-500" />
							<span class="text-sm text-gray-600">Risk Assessment:</span>
						</div>
						<div class={`px-4 py-2 rounded-lg font-semibold border shadow-sm ${getRiskColor(entityData.risk_score)} flex items-center space-x-2`}>
							{#if getRiskIcon(entityData.risk_score) === 'AlertTriangle'}
								<AlertTriangle class="h-4 w-4" />
							{:else if getRiskIcon(entityData.risk_score) === 'AlertCircle'}
								<AlertCircle class="h-4 w-4" />
							{:else if getRiskIcon(entityData.risk_score) === 'Info'}
								<Info class="h-4 w-4" />
							{:else}
								<Shield class="h-4 w-4" />
							{/if}
							<span>{entityData.risk_score}/100 - {getRiskLabel(entityData.risk_score)}</span>
						</div>
					</div>
					
					<!-- Risk Score Bar -->
					<div class="mt-4">
						<div class="w-full bg-gray-200 rounded-full h-4 shadow-inner">
							<div 
								class="h-4 rounded-full transition-all duration-500 shadow-sm {getRiskBarColor(entityData.risk_score)}"
								style="width: {Math.min(entityData.risk_score, 100)}%"
							></div>
						</div>
						<div class="flex justify-between text-xs text-gray-500 mt-2">
							<span class="flex items-center space-x-1">
								<Shield class="h-3 w-3 text-green-500" />
								<span>0 - Minimal</span>
							</span>
							<span class="flex items-center space-x-1">
								<AlertCircle class="h-3 w-3 text-yellow-500" />
								<span>25 - Medium</span>
							</span>
							<span class="flex items-center space-x-1">
								<AlertTriangle class="h-3 w-3 text-red-500" />
								<span>75 - Critical</span>
							</span>
						</div>
					</div>
				</div>

				<!-- Entity Classification Section -->
				{#if entityData.entity_type && (entityData.entity_type.is_trust || entityData.entity_type.trust_types.length > 0)}
					<div class="mb-6">
						<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
							<Shield class="h-5 w-5 text-indigo-600" />
							<span>Entity Classification</span>
						</h4>
						
						<div class="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-4">
							<!-- Trust Type Badges -->
							{#if entityData.entity_type.trust_types.length > 0}
								<div class="mb-4">
									<div class="text-sm text-gray-600 mb-2">Trust Types:</div>
									<div class="flex flex-wrap gap-2">
										{#each entityData.entity_type.trust_types as trustType}
											<span class="px-3 py-1 rounded-full text-sm font-medium border {getTrustTypeColor(trustType)}">
												{trustType}
											</span>
										{/each}
									</div>
								</div>
							{/if}
							
							<!-- Trust Status Indicators -->
							<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
								<!-- Regulation Status -->
								<div class="flex items-center space-x-2">
									{#if entityData.entity_type.requires_regulation}
										<AlertTriangle class="h-5 w-5 text-yellow-600" />
										<div>
											<div class="text-sm font-medium text-gray-900">Regulated Entity</div>
											<div class="text-xs text-gray-600">Requires compliance filings</div>
										</div>
									{:else}
										<Shield class="h-5 w-5 text-green-600" />
										<div>
											<div class="text-sm font-medium text-gray-900">Standard Entity</div>
											<div class="text-xs text-gray-600">No special regulation</div>
										</div>
									{/if}
								</div>
								
								<!-- Risk Level -->
								<div class="flex items-center space-x-2">
									{#if entityData.entity_type.high_risk}
										<AlertTriangle class="h-5 w-5 text-red-600" />
										<div>
											<div class="text-sm font-medium text-gray-900">High-Risk Type</div>
											<div class="text-xs text-gray-600">Enhanced monitoring suggested</div>
										</div>
									{:else}
										<Shield class="h-5 w-5 text-blue-600" />
										<div>
											<div class="text-sm font-medium text-gray-900">Standard Risk</div>
											<div class="text-xs text-gray-600">Normal trust structure</div>
										</div>
									{/if}
								</div>
								
								<!-- Match Terms -->
								{#if entityData.entity_type.match_terms.length > 0}
									<div class="flex items-start space-x-2">
										<Search class="h-5 w-5 text-gray-500 mt-0.5" />
										<div>
											<div class="text-sm font-medium text-gray-900">Detection Keywords</div>
											<div class="text-xs text-gray-600">{entityData.entity_type.match_terms.join(', ')}</div>
										</div>
									</div>
								{/if}
							</div>
							
							<!-- Risk Indicators -->
							{#if entityData.entity_type.risk_indicators.length > 0}
								<div class="mt-4 pt-4 border-t border-indigo-200">
									<div class="text-sm text-gray-600 mb-2">Risk Indicators:</div>
									<div class="flex flex-wrap gap-2">
										{#each entityData.entity_type.risk_indicators as indicator}
											<span class="px-2 py-1 rounded text-xs font-medium border {getTrustRiskIndicatorColor(indicator)}">
												{indicator.replace('_', ' ').replace(':', ': ')}
											</span>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Red Flags Section -->
				<div class="mb-6">
					<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
						<AlertTriangle class="h-5 w-5 text-yellow-600" />
						<span>Red Flags ({entityData.anomalies.length})</span>
					</h4>
					
					{#if entityData.anomalies.length > 0}
						<div class="space-y-3">
							{#each entityData.anomalies as anomaly, index}
								<div class="flex items-start space-x-3 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
									<div class="flex-shrink-0 w-6 h-6 rounded-full bg-yellow-100 border border-yellow-300 flex items-center justify-center">
										<AlertTriangle class="h-4 w-4 text-yellow-600" />
									</div>
									<div class="flex-1">
										<span class="text-yellow-900 font-medium">{anomaly}</span>
										{#if anomaly.includes('EIN')}
											<p class="text-xs text-yellow-700 mt-1">Business registration may be incomplete or unverified.</p>
										{:else if anomaly.includes('PO Box')}
											<p class="text-xs text-yellow-700 mt-1">Physical location verification recommended.</p>
										{:else if anomaly.includes('officers')}
											<p class="text-xs text-yellow-700 mt-1">Complex organizational structure may require additional review.</p>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="text-center py-8 text-gray-500">
							<Shield class="h-12 w-12 mx-auto mb-2 text-green-500" />
							<p>No red flags detected for this entity.</p>
						</div>
					{/if}
				</div>

				<!-- Property Information -->
				{#if entityData.property}
					<div class="mb-6">
						<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
							<Building class="h-5 w-5 text-blue-600" />
							<span>Property Information</span>
						</h4>
						
						<div class="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<!-- Property Address -->
								<div class="flex items-start space-x-3">
									<MapPin class="h-5 w-5 text-blue-600 mt-0.5" />
									<div>
										<div class="text-sm text-gray-600">Address</div>
										<div class="font-medium text-gray-900">{entityData.property.address}</div>
										<div class="text-sm text-blue-600">{entityData.property.county} County</div>
									</div>
								</div>
								
								<!-- Property Owner -->
								<div class="flex items-start space-x-3">
									<Building class="h-5 w-5 text-blue-600 mt-0.5" />
									<div>
										<div class="text-sm text-gray-600">Property Owner</div>
										<div class="font-medium text-gray-900">{entityData.property.owner_name}</div>
										<div class="text-sm text-gray-500">{entityData.property.land_use}</div>
									</div>
								</div>
								
								<!-- Market Value -->
								<div class="flex items-start space-x-3">
									<DollarSign class="h-5 w-5 text-blue-600 mt-0.5" />
									<div>
										<div class="text-sm text-gray-600">Market Value</div>
										<div class="font-medium text-gray-900">{entityData.property.market_value}</div>
									</div>
								</div>
								
								<!-- Tax Status -->
								<div class="flex items-start space-x-3">
									{#if entityData.property.delinquent_taxes}
										<AlertTriangle class="h-5 w-5 text-red-600 mt-0.5" />
									{:else}
										<Shield class="h-5 w-5 text-green-600 mt-0.5" />
									{/if}
									<div>
										<div class="text-sm text-gray-600">Tax Status</div>
										<div class="font-medium {entityData.property.delinquent_taxes ? 'text-red-700' : 'text-green-700'}">
											{entityData.property.delinquent_taxes ? 'Delinquent Taxes' : 'Current'}
										</div>
									</div>
								</div>
							</div>
							
							<!-- View Property Record -->
							<div class="mt-4 pt-4 border-t border-blue-200">
								<a
									href={entityData.property.source_url}
									target="_blank"
									rel="noopener noreferrer"
									class="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
								>
									<ExternalLink class="h-4 w-4" />
									<span>View {entityData.property.county} County Records</span>
								</a>
							</div>
						</div>
					</div>
				{/if}

				<!-- Source Documents -->
				<div>
					<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
						<ExternalLink class="h-5 w-5 text-blue-600" />
						<span>Source Documents</span>
						{#if entityData.entity_type && entityData.entity_type.is_trust}
							<span class="text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded">Trust-Optimized</span>
						{/if}
					</h4>
					
					{#if entityData.source_links && Object.keys(entityData.source_links).length > 0}
						<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
							{#each Object.entries(entityData.source_links) as [key, url]}
								<a
									href={url}
									target="_blank"
									rel="noopener noreferrer"
									class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
								>
									<div class="flex-1">
										{#if key === 'sunbiz'}
											<div class="font-medium text-gray-900">Florida Sunbiz</div>
											<div class="text-sm text-gray-500">Corporate records</div>
										{:else if key === 'irs'}
											<div class="font-medium text-gray-900">IRS Tax Records</div>
											<div class="text-sm text-gray-500">501(c) status</div>
										{:else if key === 'irs_990'}
											<div class="font-medium text-gray-900">IRS 990 Forms</div>
											<div class="text-sm text-gray-500">Charitable filing</div>
										{:else if key === 'charity_navigator'}
											<div class="font-medium text-gray-900">Charity Navigator</div>
											<div class="text-sm text-gray-500">Charity ratings</div>
										{:else if key === 'sec_edgar'}
											<div class="font-medium text-gray-900">SEC EDGAR</div>
											<div class="text-sm text-gray-500">Investment filings</div>
										{:else if key === 'court_records'}
											<div class="font-medium text-gray-900">Court Records</div>
											<div class="text-sm text-gray-500">Probate filings</div>
										{:else if key === 'sba'}
											<div class="font-medium text-gray-900">SBA Directory</div>
											<div class="text-sm text-gray-500">Small business info</div>
										{:else}
											<div class="font-medium text-gray-900">{key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
											<div class="text-sm text-gray-500">Public records</div>
										{/if}
									</div>
									<ExternalLink class="h-4 w-4 text-gray-400 flex-shrink-0" />
								</a>
							{/each}
						</div>
					{:else}
						<div class="text-center py-8 text-gray-500">
							<ExternalLink class="h-8 w-8 mx-auto mb-2 text-gray-400" />
							<p>No source documents available for this entity.</p>
						</div>
					{/if}
				</div>
			</div>
		{/if}

		<!-- Demo Hint -->
		{#if !entityData && !loading}
			<div class="text-center mt-12">
				<div class="bg-white rounded-lg shadow p-6">
					<h3 class="text-lg font-medium text-gray-900 mb-2">Try searching for:</h3>
					<div class="flex flex-wrap justify-center gap-2">
						<button
							on:click={() => { searchQuery = 'Florida Educational Charitable Trust'; searchEntity(); }}
							class="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
						>
							Charitable Trust
						</button>
						<button
							on:click={() => { searchQuery = 'Offshore Investment Business Trust LLC'; searchEntity(); }}
							class="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
						>
							High-Risk Business Trust
						</button>
						<button
							on:click={() => { searchQuery = 'Smith Family Living Trust'; searchEntity(); }}
							class="px-3 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors"
						>
							Family Trust
						</button>
						<button
							on:click={() => { searchQuery = 'ABC Corporation'; searchEntity(); }}
							class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
						>
							Villages Holdings
						</button>
					</div>
				</div>
			</div>
		{/if}
	</main>

				<!-- Footer -->
	<footer class="bg-gray-50 border-t mt-16">
		<div class="max-w-7xl mx-auto px-4 py-8">
			<!-- Main Footer Content -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
				<!-- About -->
				<div>
					<h3 class="text-sm font-semibold text-gray-900 mb-4">About LedgerTrace</h3>
					<p class="text-xs text-gray-600 mb-4">
						AI-powered entity risk analysis using publicly available government data for transparency and due diligence.
					</p>
					<div class="flex items-center space-x-2 text-xs text-gray-500">
						<Shield class="h-3 w-3" />
						<span>Open Source • Transparent • Verifiable</span>
					</div>
				</div>
				
				<!-- How We Score -->
				<div>
					<h3 class="text-sm font-semibold text-gray-900 mb-4">How We Score Risk</h3>
					<ul class="space-y-2 text-xs text-gray-600">
						<li>• Missing EIN: +20 points</li>
						<li>• PO Box address: +15 points</li>
						<li>• Delinquent taxes: +20 points</li>
						<li>• Vacant property: +15 points</li>
						<li>• Mail drop service: +25 points</li>
					</ul>
				</div>
				
				<!-- Data Sources -->
				<div>
					<h3 class="text-sm font-semibold text-gray-900 mb-4">Data Sources</h3>
					<ul class="space-y-2 text-xs text-gray-600">
						<li>• Florida Division of Corporations (Sunbiz)</li>
						<li>• County Property Appraiser Records</li>
						<li>• IRS Exempt Organization Database</li>
						<li>• Small Business Administration</li>
					</ul>
				</div>
				
				<!-- Support -->
				<div>
					<h3 class="text-sm font-semibold text-gray-900 mb-4">Support & Feedback</h3>
					<ul class="space-y-2 text-xs text-gray-600">
						<li><a href="https://github.com/Adahandles/ledgertrace/issues" class="hover:text-indigo-600">Report Issues</a></li>
						<li><a href="https://github.com/Adahandles/ledgertrace" class="hover:text-indigo-600">View Source Code</a></li>
						<li><a href="https://github.com/Adahandles/ledgertrace/discussions" class="hover:text-indigo-600">Request Corrections</a></li>
						<li><a href="mailto:transparency@ledgertrace.org" class="hover:text-indigo-600">Contact Us</a></li>
					</ul>
				</div>
			</div>
			
			<!-- Legal Disclaimer -->
			<div class="border-t border-gray-200 pt-6">
				<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
					<div class="flex items-start space-x-3">
						<AlertTriangle class="h-5 w-5 text-yellow-600 mt-0.5" />
						<div class="text-sm">
							<h4 class="font-semibold text-yellow-900 mb-2">Important Legal Disclaimer</h4>
							<div class="text-yellow-800 space-y-2">
								<p><strong>Public Records Only:</strong> All information is derived from publicly available government databases and records.</p>
								<p><strong>Not Accusations:</strong> Risk scores indicate data patterns and potential areas for further investigation—they are not accusations of wrongdoing.</p>
								<p><strong>No Legal Advice:</strong> This tool provides informational analysis only and should not be used as the sole basis for legal, financial, or business decisions.</p>
								<p><strong>Verify Information:</strong> Users should independently verify all information through official government sources before taking action.</p>
								<p><strong>Report Errors:</strong> If you believe information about your organization is incorrect, please submit a correction request.</p>
							</div>
						</div>
					</div>
				</div>
				
				<!-- Copyright and Terms -->
				<div class="flex flex-col md:flex-row justify-between items-center text-xs text-gray-500">
					<div class="mb-4 md:mb-0">
						<p>© 2025 LedgerTrace. Licensed under MIT License.</p>
						<p>Built with ❤️ for transparency and accountability.</p>
					</div>
					<div class="flex space-x-6">
						<a href="https://github.com/Adahandles/ledgertrace/blob/main/LICENSE" class="hover:text-gray-700">License</a>
						<a href="https://github.com/Adahandles/ledgertrace/blob/main/PRIVACY.md" class="hover:text-gray-700">Privacy</a>
						<a href="https://github.com/Adahandles/ledgertrace/blob/main/TERMS.md" class="hover:text-gray-700">Terms</a>
					</div>
				</div>
			</div>
		</div>
	</footer>
</div>