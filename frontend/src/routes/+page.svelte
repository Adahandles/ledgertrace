<script>
	import { onMount } from 'svelte';
	import { Search, AlertTriangle, ExternalLink, TrendingUp, Shield, AlertCircle, Info, MapPin, DollarSign, Building, Scale, Gavel, FileText, Calendar, Globe, Users, CreditCard, Bell, Eye, TrendingDown, CheckCircle, XCircle, Clock, Download, FileX } from 'lucide-svelte';
	
	// Import our new Web3 components
	import ThemeToggle from '../lib/components/ThemeToggle.svelte';
	import EntityCard from '../lib/components/EntityCard.svelte';
	import RiskScore from '../lib/components/RiskScore.svelte';
	import BadgeFlag from '../lib/components/BadgeFlag.svelte';
	import CyberButton from '../lib/components/CyberButton.svelte';
	import { darkMode } from '../lib/stores/darkMode.js';
	
	let searchQuery = '';
	let searchAddress = '';
	let loading = false;
	let entityData = null;
	let error = null;
	let exportLoading = false;
	let exportError = null;

	const API_BASE = 'http://localhost:8002';
	
	// Initialize dark mode on mount
	onMount(() => {
		darkMode.init();
	});
	
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

	function getCourtCaseColor(caseType) {
		if (caseType === 'Foreclosure') return 'bg-red-100 text-red-800 border-red-300';
		if (caseType === 'Bankruptcy') return 'bg-purple-100 text-purple-800 border-purple-300';
		if (caseType === 'Tax Lien') return 'bg-orange-100 text-orange-800 border-orange-300';
		if (caseType === 'Civil Litigation') return 'bg-blue-100 text-blue-800 border-blue-300';
		return 'bg-gray-100 text-gray-800 border-gray-300';
	}

	function getCourtCaseIcon(caseType) {
		if (caseType === 'Foreclosure') return 'Building';
		if (caseType === 'Bankruptcy') return 'DollarSign';
		if (caseType === 'Tax Lien') return 'AlertCircle';
		if (caseType === 'Civil Litigation') return 'Scale';
		return 'FileText';
	}

	function getCourtCaseStatus(status) {
		if (status === 'Open' || status === 'Active') return 'bg-red-100 text-red-700 border-red-200';
		if (status === 'Judgment' || status === 'Closed') return 'bg-gray-100 text-gray-700 border-gray-200';
		return 'bg-yellow-100 text-yellow-700 border-yellow-200';
	}

	async function exportReport(format) {
		if (!entityData) return;
		
		exportLoading = true;
		exportError = null;
		
		try {
			const exportRequest = {
				entity_input: {
					name: entityData.name,
					address: searchAddress || null,
					ein: null,
					officers: []
				},
				export_format: format,
				include_sections: [
					"entity_info", 
					"risk_score", 
					"county_offices", 
					"court_activity", 
					"domain_info", 
					"grants_data", 
					"monitoring_data"
				],
				template_style: "professional"
			};
			
			const response = await fetch(`${API_BASE}/export`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(exportRequest)
			});
			
			if (!response.ok) {
				throw new Error(`Export failed: ${response.statusText}`);
			}
			
			const exportResponse = await response.json();
			
			if (!exportResponse.success) {
				throw new Error(exportResponse.error_message || 'Export generation failed');
			}
			
			// Trigger download
			const downloadUrl = `${API_BASE}${exportResponse.download_url}`;
			const link = document.createElement('a');
			link.href = downloadUrl;
			link.download = exportResponse.file_name;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			
		} catch (err) {
			exportError = err.message;
		} finally {
			exportLoading = false;
		}
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

<div class="min-h-screen transition-all duration-300 {$darkMode ? 'bg-gradient-to-br from-dark-900 via-dark-850 to-dark-800 text-white' : 'bg-gradient-to-br from-light-50 to-light-100 text-dark-900'}">
	<!-- Header -->
	<header class="border-b {$darkMode ? 'border-primary-500/20 bg-dark-900/50' : 'border-primary-200 bg-white/80'} backdrop-blur-xl sticky top-0 z-50">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex items-center justify-between h-16">
				<div class="flex items-center space-x-4">
					<div class="flex items-center space-x-3">
						<div class="relative">
							<TrendingUp class="h-8 w-8 text-primary-400 animate-pulse-slow" />
							<div class="absolute inset-0 h-8 w-8 text-primary-400 animate-ping opacity-20">
								<TrendingUp class="h-8 w-8" />
							</div>
						</div>
						<h1 class="text-2xl font-bold cyber-gradient">LedgerTrace</h1>
					</div>
					<div class="hidden sm:flex items-center space-x-2">
						<div class="glass-panel px-4 py-2 rounded-xl">
							<span class="text-sm font-medium {$darkMode ? 'text-gray-300' : 'text-gray-600'}">AI-Powered Entity Intelligence</span>
						</div>
					</div>
				</div>
				<div class="flex items-center space-x-4">
					<div class="hidden lg:block text-xs {$darkMode ? 'text-gray-400' : 'text-gray-500'} font-medium">
						🧠🏛️📍 Leading the Future of Civic Intelligence
					</div>
					<ThemeToggle size="md" />
				</div>
			</div>
		</div>
	</header>

	<main class="max-w-6xl mx-auto px-4 py-8">
		<!-- Search Section -->
		<div class="glass-panel {$darkMode ? 'border-primary-500/20' : 'border-primary-200'} p-8 mb-8 animate-fade-in">
			<div class="text-center mb-8">
				<h2 class="text-3xl font-bold {$darkMode ? 'text-white' : 'text-dark-900'} mb-3">Entity Intelligence Search</h2>
				<p class="{$darkMode ? 'text-gray-300' : 'text-gray-600'} text-lg">Discover comprehensive risk analysis and entity intelligence</p>
			</div>
			
			<form on:submit|preventDefault={searchEntity} class="space-y-6">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div class="space-y-2">
						<label for="entity-name" class="block text-sm font-semibold {$darkMode ? 'text-gray-200' : 'text-gray-700'} mb-2">Entity Name</label>
						<input
							id="entity-name"
							bind:value={searchQuery}
							type="text"
							placeholder="Enter entity name (e.g., ABC Corp)"
							class="cyber-input w-full px-4 py-3 {$darkMode ? 'bg-dark-800 border-primary-500/30 text-white placeholder-gray-400' : 'bg-white border-primary-300 text-dark-900 placeholder-gray-500'} rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200"
							disabled={loading}
						/>
					</div>
					<div class="space-y-2">
						<label for="entity-address" class="block text-sm font-semibold {$darkMode ? 'text-gray-200' : 'text-gray-700'} mb-2">Address (Optional)</label>
						<input
							id="entity-address"
							bind:value={searchAddress}
							type="text"
							placeholder="Enter address for property analysis"
							class="cyber-input w-full px-4 py-3 {$darkMode ? 'bg-dark-800 border-primary-500/30 text-white placeholder-gray-400' : 'bg-white border-primary-300 text-dark-900 placeholder-gray-500'} rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200"
							disabled={loading}
						/>
					</div>
				</div>
				<div class="flex justify-center">
					<CyberButton
						variant="primary"
						size="lg"
						disabled={loading || !searchQuery.trim()}
						onClick={searchEntity}
					>
						<Search class="h-5 w-5" />
						<span>{loading ? 'Analyzing...' : 'Analyze Entity'}</span>
					</CyberButton>
				</div>
			</form>
		</div>

		<!-- Error Display -->
		{#if error}
			<div class="glass-panel border-danger-500/20 p-6 mb-8 animate-slide-up">
				<div class="flex items-center space-x-3">
					<div class="p-2 bg-danger-100 rounded-lg">
						<AlertTriangle class="h-5 w-5 text-danger-600" />
					</div>
					<div>
						<h4 class="font-semibold text-danger-800 mb-1">Analysis Error</h4>
						<p class="{$darkMode ? 'text-danger-200' : 'text-danger-700'}">{error}</p>
					</div>
				</div>
			</div>
		{/if}

		<!-- Entity Intelligence Panel -->
		{#if entityData}
			<div class="space-y-8 animate-fade-in">
				<!-- Risk Score Header -->
				<div class="flex flex-col lg:flex-row gap-6">
					<div class="flex-1">
						<EntityCard 
							name={entityData.name} 
							status="Analysis Complete"
							description="Comprehensive entity intelligence and risk assessment"
							badges={[
								{ type: 'info', text: 'AI Analyzed', tooltip: 'Analysis powered by advanced AI algorithms' },
								{ type: 'success', text: 'Verified', tooltip: 'Entity verification completed' }
							]}
						>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
								<div>
									<RiskScore 
										score={entityData.risk_score}
										title="Risk Assessment"
										subtitle="Overall entity risk profile"
									/>
								</div>
								<div class="space-y-4">
									<div class="flex items-center space-x-3">
										<div class="p-2 bg-primary-100 rounded-lg">
											<TrendingUp class="h-5 w-5 text-primary-600" />
										</div>
										<div>
											<h4 class="font-semibold {$darkMode ? 'text-white' : 'text-dark-900'}">Analysis Metrics</h4>
											<p class="{$darkMode ? 'text-gray-300' : 'text-gray-600'} text-sm">Multi-source intelligence fusion</p>
										</div>
									</div>
									<div class="grid grid-cols-2 gap-4 text-sm">
										<div class="glass-panel p-3 rounded-lg">
											<div class="font-medium {$darkMode ? 'text-primary-400' : 'text-primary-600'}">{entityData.risk_score}/100</div>
											<div class="{$darkMode ? 'text-gray-300' : 'text-gray-600'}">Risk Score</div>
										</div>
										<div class="glass-panel p-3 rounded-lg">
											<div class="font-medium {$darkMode ? 'text-primary-400' : 'text-primary-600'}">
												{getRiskLabel(entityData.risk_score)}
											</div>
											<div class="{$darkMode ? 'text-gray-300' : 'text-gray-600'}">Classification</div>
										</div>
									</div>
								</div>
							</div>
						</EntityCard>
					</div>
				</div>
				
				<!-- Export Options -->
				<div class="glass-panel p-6 rounded-xl border border-primary-500/20">
					<div class="flex items-center justify-between">
						<div class="flex items-center space-x-3">
							<div class="p-2 bg-accent-100 rounded-lg">
								<FileText class="h-5 w-5 text-accent-600" />
							</div>
							<div>
								<h4 class="font-semibold {$darkMode ? 'text-white' : 'text-dark-900'}">Export Intelligence Report</h4>
								<p class="{$darkMode ? 'text-gray-300' : 'text-gray-600'} text-sm">Download comprehensive analysis</p>
							</div>
						<div class="flex items-center space-x-3">
							<CyberButton
								variant="primary"
								size="sm" 
								disabled={exportLoading}
								onClick={() => exportReport('pdf')}
							>
								{#if exportLoading}
									<Clock class="animate-spin h-4 w-4" />
								{:else}
									<Download class="h-4 w-4" />
								{/if}
								PDF Report
							</CyberButton>
							<CyberButton
								variant="secondary"
								size="sm"
								disabled={exportLoading}
								onClick={() => exportReport('json')}
							>
								{#if exportLoading}
									<Clock class="animate-spin h-4 w-4" />
								{:else}
									<FileX class="h-4 w-4" />
								{/if}
								Raw JSON
							</CyberButton>
						</div>
					{#if exportError}
						<div class="mt-4 glass-panel border-danger-500/20 p-4 rounded-lg">
							<div class="flex items-center space-x-3">
								<AlertTriangle class="h-5 w-5 text-danger-400" />
								<div>
									<h5 class="font-medium text-danger-600">Export Failed</h5>
									<p class="text-sm {$darkMode ? 'text-danger-200' : 'text-danger-700'}">{exportError}</p>
								</div>
							</div>
						</div>
					{/if}
					<div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs {$darkMode ? 'text-gray-300' : 'text-gray-500'}">
						<div class="flex items-center space-x-2">
							<span class="text-lg">📄</span>
							<span>PDF reports with professional formatting</span>
						</div>
						<div class="flex items-center space-x-2">
							<span class="text-lg">🧬</span>
							<span>JSON data for technical integration</span>
						</div>
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

				<!-- Court Activity Section -->
				{#if entityData.court_data && entityData.court_data.case_count > 0}
					<div class="mb-6">
						<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
							<Scale class="h-5 w-5 text-red-600" />
							<span>Court Activity ({entityData.court_data.case_count})</span>
							{#if entityData.court_data.has_foreclosure || entityData.court_data.has_bankruptcy}
								<span class="text-sm bg-red-100 text-red-800 px-2 py-0.5 rounded-full">High Risk</span>
							{/if}
						</h4>
						
						<div class="bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-lg p-4">
							<!-- Court Activity Summary -->
							<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
								{#if entityData.court_data.has_foreclosure}
									<div class="flex items-center space-x-2">
										<Building class="h-5 w-5 text-red-600" />
										<div>
											<div class="text-sm font-medium text-red-900">Foreclosure</div>
											<div class="text-xs text-red-600">Property at risk</div>
										</div>
									</div>
								{/if}
								
								{#if entityData.court_data.has_bankruptcy}
									<div class="flex items-center space-x-2">
										<DollarSign class="h-5 w-5 text-purple-600" />
										<div>
											<div class="text-sm font-medium text-purple-900">Bankruptcy</div>
											<div class="text-xs text-purple-600">Financial distress</div>
										</div>
									</div>
								{/if}
								
								{#if entityData.court_data.has_tax_lien}
									<div class="flex items-center space-x-2">
										<AlertCircle class="h-5 w-5 text-orange-600" />
										<div>
											<div class="text-sm font-medium text-orange-900">Tax Lien</div>
											<div class="text-xs text-orange-600">Tax delinquent</div>
										</div>
									</div>
								{/if}
								
								{#if entityData.court_data.has_civil}
									<div class="flex items-center space-x-2">
										<Scale class="h-5 w-5 text-blue-600" />
										<div>
											<div class="text-sm font-medium text-blue-900">Civil Case</div>
											<div class="text-xs text-blue-600">Legal dispute</div>
										</div>
									</div>
								{/if}
							</div>
							
							<!-- Individual Court Cases -->
							<div class="space-y-4">
								{#each entityData.court_data.cases as courtCase, index}
									<div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
										<div class="flex items-start justify-between mb-3">
											<div class="flex items-center space-x-3">
												<!-- Case Type Badge -->
												<span class="px-3 py-1 rounded-full text-sm font-medium border {getCourtCaseColor(courtCase.case_type)}">
													{courtCase.case_type}
												</span>
												
												<!-- Case Status -->
												<span class="px-2 py-1 rounded text-xs font-medium border {getCourtCaseStatus(courtCase.status)}">
													{courtCase.status}
												</span>
											</div>
											
											<!-- Case Number -->
											{#if courtCase.case_number}
												<div class="text-sm text-gray-600 font-mono">
													{courtCase.case_number}
												</div>
											{/if}
										</div>
										
										<!-- Case Details Grid -->
										<div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
											{#if courtCase.filed_date}
												<div class="flex items-center space-x-2">
													<Calendar class="h-4 w-4 text-gray-500" />
													<div>
														<span class="text-gray-600">Filed:</span>
														<span class="font-medium text-gray-900">{courtCase.filed_date}</span>
													</div>
												</div>
											{/if}
											
											{#if courtCase.county}
												<div class="flex items-center space-x-2">
													<MapPin class="h-4 w-4 text-gray-500" />
													<div>
														<span class="text-gray-600">County:</span>
														<span class="font-medium text-gray-900">{courtCase.county}</span>
													</div>
												</div>
											{/if}
											
											{#if courtCase.plaintiff}
												<div class="flex items-start space-x-2">
													<Gavel class="h-4 w-4 text-gray-500 mt-0.5" />
													<div>
														<span class="text-gray-600">Plaintiff:</span>
														<span class="font-medium text-gray-900">{courtCase.plaintiff}</span>
													</div>
												</div>
											{/if}
											
											{#if courtCase.amount}
												<div class="flex items-center space-x-2">
													<DollarSign class="h-4 w-4 text-gray-500" />
													<div>
														<span class="text-gray-600">Amount:</span>
														<span class="font-medium text-gray-900">{courtCase.amount}</span>
													</div>
												</div>
											{/if}
										</div>
										
										<!-- Additional Details -->
										{#if courtCase.description}
											<div class="mt-3 p-3 bg-gray-50 rounded-lg">
												<div class="text-sm text-gray-700">
													<span class="font-medium">Description:</span> {courtCase.description}
												</div>
											</div>
										{/if}
										
										{#if courtCase.property_address}
											<div class="mt-3 p-3 bg-blue-50 rounded-lg">
												<div class="text-sm text-blue-700">
													<span class="font-medium">Property:</span> {courtCase.property_address}
												</div>
											</div>
										{/if}
										
										<!-- Court Record Link -->
										{#if courtCase.search_url}
											<div class="mt-4 pt-3 border-t border-gray-200">
												<a
													href={courtCase.search_url}
													target="_blank"
													rel="noopener noreferrer"
													class="inline-flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
												>
													<ExternalLink class="h-4 w-4" />
													<span>View Court Records</span>
												</a>
											</div>
										{/if}
									</div>
								{/each}
							</div>
							
							<!-- Risk Indicators Summary -->
							{#if entityData.court_data.risk_indicators.length > 0}
								<div class="mt-4 pt-4 border-t border-red-200">
									<div class="text-sm text-gray-600 mb-2">Legal Risk Indicators:</div>
									<div class="flex flex-wrap gap-2">
										{#each entityData.court_data.risk_indicators as indicator}
											<span class="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700 border border-red-200">
												{indicator.replace('_', ' ').replace(':', ': ')}
											</span>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Domain Analysis Section -->
				{#if entityData.domain_data}
					<div class="mb-6">
						<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
							<Globe class="h-5 w-5 text-blue-600" />
							<span>Domain Analysis ({entityData.domain_data.domain_count})</span>
							{#if !entityData.domain_data.has_active_website}
								<span class="text-sm bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full">No Website</span>
							{/if}
						</h4>
						
						<div class="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg p-4">
							<!-- Domain Summary -->
							<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
								<div class="flex items-center space-x-2">
									{#if entityData.domain_data.has_active_website}
										<CheckCircle class="h-5 w-5 text-green-600" />
									{:else}
										<XCircle class="h-5 w-5 text-red-600" />
									{/if}
									<div>
										<div class="text-sm font-medium text-gray-900">Website Status</div>
										<div class="text-xs {entityData.domain_data.has_active_website ? 'text-green-600' : 'text-red-600'}">
											{entityData.domain_data.has_active_website ? 'Active' : 'No Active Site'}
										</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									{#if entityData.domain_data.has_privacy_protection}
										<Eye class="h-5 w-5 text-orange-600" />
									{:else}
										<Shield class="h-5 w-5 text-green-600" />
									{/if}
									<div>
										<div class="text-sm font-medium text-gray-900">WHOIS Privacy</div>
										<div class="text-xs {entityData.domain_data.has_privacy_protection ? 'text-orange-600' : 'text-green-600'}">
											{entityData.domain_data.has_privacy_protection ? 'Protected' : 'Public'}
										</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									{#if entityData.domain_data.recent_registration}
										<Clock class="h-5 w-5 text-yellow-600" />
									{:else}
										<CheckCircle class="h-5 w-5 text-green-600" />
									{/if}
									<div>
										<div class="text-sm font-medium text-gray-900">Registration</div>
										<div class="text-xs {entityData.domain_data.recent_registration ? 'text-yellow-600' : 'text-green-600'}">
											{entityData.domain_data.recent_registration ? 'Recent' : 'Established'}
										</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									<Globe class="h-5 w-5 text-blue-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">Domain Count</div>
										<div class="text-xs text-blue-600">{entityData.domain_data.domain_count} Found</div>
									</div>
								</div>
							</div>
							
							<!-- Domain Risk Indicators -->
							{#if entityData.domain_data.risk_indicators.length > 0}
								<div class="mt-4 pt-4 border-t border-blue-200">
									<div class="text-sm text-gray-600 mb-2">Domain Risk Indicators:</div>
									<div class="flex flex-wrap gap-2">
										{#each entityData.domain_data.risk_indicators as indicator}
											<span class="px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-700 border border-yellow-200">
												{indicator.replace('_', ' ').replace(':', ': ')}
											</span>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Officer Analysis Section -->
				{#if entityData.officer_data && (entityData.officer_data.officers.length > 0 || entityData.officer_data.cross_references.length > 0)}
					<div class="mb-6">
						<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
							<Users class="h-5 w-5 text-purple-600" />
							<span>Officer Analysis ({entityData.officer_data.officers.length})</span>
							{#if entityData.officer_data.has_problematic_officers}
								<span class="text-sm bg-red-100 text-red-800 px-2 py-0.5 rounded-full">Risk Found</span>
							{/if}
						</h4>
						
						<div class="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4">
							<!-- Officer Summary -->
							<div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
								<div class="flex items-center space-x-2">
									<Users class="h-5 w-5 text-purple-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">Officers Found</div>
										<div class="text-xs text-purple-600">{entityData.officer_data.officers.length} Active</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									<Building class="h-5 w-5 text-blue-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">Connected Entities</div>
										<div class="text-xs text-blue-600">{entityData.officer_data.total_entities_connected} Total</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									{#if entityData.officer_data.has_shared_officers}
										<AlertTriangle class="h-5 w-5 text-orange-600" />
									{:else}
										<CheckCircle class="h-5 w-5 text-green-600" />
									{/if}
									<div>
										<div class="text-sm font-medium text-gray-900">Cross-References</div>
										<div class="text-xs {entityData.officer_data.has_shared_officers ? 'text-orange-600' : 'text-green-600'}">
											{entityData.officer_data.cross_references.length} Found
										</div>
									</div>
								</div>
							</div>
							
							<!-- Officer Risk Indicators -->
							{#if entityData.officer_data.risk_indicators.length > 0}
								<div class="mt-4 pt-4 border-t border-purple-200">
									<div class="text-sm text-gray-600 mb-2">Officer Risk Indicators:</div>
									<div class="flex flex-wrap gap-2">
										{#each entityData.officer_data.risk_indicators as indicator}
											<span class="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700 border border-red-200">
												{indicator.replace('_', ' ').replace(':', ': ')}
											</span>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Grants Analysis Section -->
				{#if entityData.grants_data && entityData.grants_data.total_awards > 0}
					<div class="mb-6">
						<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
							<CreditCard class="h-5 w-5 text-green-600" />
							<span>Grant & Contract History ({entityData.grants_data.total_awards})</span>
							{#if entityData.grants_data.has_compliance_issues}
								<span class="text-sm bg-red-100 text-red-800 px-2 py-0.5 rounded-full">Compliance Issues</span>
							{/if}
						</h4>
						
						<div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4">
							<!-- Grants Summary -->
							<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
								<div class="flex items-center space-x-2">
									<DollarSign class="h-5 w-5 text-green-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">Total Funding</div>
										<div class="text-xs text-green-600">${entityData.grants_data.total_funding.toLocaleString()}</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									<Building class="h-5 w-5 text-blue-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">Federal Funding</div>
										<div class="text-xs {entityData.grants_data.has_federal_funding ? 'text-blue-600' : 'text-gray-500'}">
											{entityData.grants_data.has_federal_funding ? 'Yes' : 'None'}
										</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									<MapPin class="h-5 w-5 text-purple-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">State Funding</div>
										<div class="text-xs {entityData.grants_data.has_state_funding ? 'text-purple-600' : 'text-gray-500'}">
											{entityData.grants_data.has_state_funding ? 'Yes' : 'None'}
										</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									{#if entityData.grants_data.has_compliance_issues}
										<AlertTriangle class="h-5 w-5 text-red-600" />
									{:else}
										<CheckCircle class="h-5 w-5 text-green-600" />
									{/if}
									<div>
										<div class="text-sm font-medium text-gray-900">Compliance</div>
										<div class="text-xs {entityData.grants_data.has_compliance_issues ? 'text-red-600' : 'text-green-600'}">
											{entityData.grants_data.has_compliance_issues ? 'Issues Found' : 'Clean Record'}
										</div>
									</div>
								</div>
							</div>
							
							<!-- Grant Risk Indicators -->
							{#if entityData.grants_data.risk_indicators.length > 0}
								<div class="mt-4 pt-4 border-t border-green-200">
									<div class="text-sm text-gray-600 mb-2">Grant Risk Indicators:</div>
									<div class="flex flex-wrap gap-2">
										{#each entityData.grants_data.risk_indicators as indicator}
											<span class="px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-700 border border-yellow-200">
												{indicator.replace('_', ' ').replace(':', ': ')}
											</span>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Monitoring Section -->
				{#if entityData.monitoring_data && (entityData.monitoring_data.active_alert_count > 0 || entityData.monitoring_data.total_changes > 0)}
					<div class="mb-6">
						<h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
							<Bell class="h-5 w-5 text-orange-600" />
							<span>Monitoring & Alerts</span>
							{#if entityData.monitoring_data.active_alert_count > 0}
								<span class="text-sm bg-red-100 text-red-800 px-2 py-0.5 rounded-full">{entityData.monitoring_data.active_alert_count} Active</span>
							{/if}
						</h4>
						
						<div class="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-4">
							<!-- Monitoring Summary -->
							<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
								<div class="flex items-center space-x-2">
									<Bell class="h-5 w-5 text-orange-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">Active Alerts</div>
										<div class="text-xs text-orange-600">{entityData.monitoring_data.active_alert_count} Current</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									<TrendingUp class="h-5 w-5 text-blue-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">Total Changes</div>
										<div class="text-xs text-blue-600">{entityData.monitoring_data.total_changes} Detected</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									<Clock class="h-5 w-5 text-purple-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">Last Scan</div>
										<div class="text-xs text-purple-600">{new Date(entityData.monitoring_data.last_scan).toLocaleDateString()}</div>
									</div>
								</div>
								
								<div class="flex items-center space-x-2">
									<Shield class="h-5 w-5 text-gray-600" />
									<div>
										<div class="text-sm font-medium text-gray-900">Monitoring Score</div>
										<div class="text-xs {entityData.monitoring_data.monitoring_score > 50 ? 'text-red-600' : entityData.monitoring_data.monitoring_score > 25 ? 'text-yellow-600' : 'text-green-600'}">
											{entityData.monitoring_data.monitoring_score}/100
										</div>
									</div>
								</div>
							</div>
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
							
							<!-- Parcel ID -->
							{#if entityData.property.parcel_id}
								<div class="mt-4 pt-4 border-t border-blue-200">
									<div class="flex items-center space-x-2 text-sm">
										<FileText class="h-4 w-4 text-gray-500" />
										<span class="text-gray-600">Parcel ID:</span>
										<span class="font-mono text-gray-900 bg-gray-100 px-2 py-1 rounded">{entityData.property.parcel_id}</span>
									</div>
								</div>
							{/if}
							
							<!-- County Offices Section -->
							{#if entityData.property.offices && Object.keys(entityData.property.offices).length > 0}
								<div class="mt-4 pt-4 border-t border-blue-200">
									<h5 class="text-sm font-semibold text-gray-900 mb-3 flex items-center space-x-2">
										<Building class="h-4 w-4 text-blue-600" />
										<span>🏢 {entityData.property.county} County Offices</span>
										<span class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Official Links</span>
									</h5>
									
									<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
										{#if entityData.property.offices.property_appraiser}
											<a
												href={entityData.property.verification_links?.property_direct || entityData.property.offices.property_appraiser.search_url}
												target="_blank"
												rel="noopener noreferrer"
												class="group flex flex-col p-4 border-2 border-blue-200 rounded-xl hover:border-blue-400 hover:bg-gradient-to-br hover:from-blue-50 hover:to-indigo-50 transition-all duration-200 hover:shadow-md"
												title={entityData.property.offices.property_appraiser.description}
											>
												<div class="flex items-center space-x-3 mb-2">
													<div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
														<FileText class="h-4 w-4 text-blue-600" />
													</div>
													<div class="flex-1">
														<div class="font-medium text-gray-900 text-sm">Property Appraiser</div>
														<div class="text-xs text-blue-600">{entityData.property.offices.property_appraiser.name}</div>
													</div>
													<ExternalLink class="h-4 w-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
												</div>
												<div class="text-xs text-gray-600 mb-3">{entityData.property.offices.property_appraiser.description}</div>
												<div class="flex items-center space-x-2 text-xs text-gray-500">
													<div class="w-2 h-2 bg-green-400 rounded-full"></div>
													<span>Active System</span>
												</div>
											</a>
										{/if}
										
										{#if entityData.property.offices.tax_collector}
											<a
												href={entityData.property.verification_links?.tax_direct || entityData.property.offices.tax_collector.search_url}
												target="_blank"
												rel="noopener noreferrer"
												class="group flex flex-col p-4 border-2 border-green-200 rounded-xl hover:border-green-400 hover:bg-gradient-to-br hover:from-green-50 hover:to-emerald-50 transition-all duration-200 hover:shadow-md"
												title={entityData.property.offices.tax_collector.description}
											>
												<div class="flex items-center space-x-3 mb-2">
													<div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
														<DollarSign class="h-4 w-4 text-green-600" />
													</div>
													<div class="flex-1">
														<div class="font-medium text-gray-900 text-sm">Tax Collector</div>
														<div class="text-xs text-green-600">{entityData.property.offices.tax_collector.name}</div>
													</div>
													<ExternalLink class="h-4 w-4 text-gray-400 group-hover:text-green-500 transition-colors" />
												</div>
												<div class="text-xs text-gray-600 mb-3">{entityData.property.offices.tax_collector.description}</div>
												<div class="flex items-center space-x-2 text-xs text-gray-500">
													<div class="w-2 h-2 bg-green-400 rounded-full"></div>
													<span>Payment Portal</span>
												</div>
											</a>
										{/if}
										
										{#if entityData.property.offices.clerk_of_court}
											<a
												href={entityData.property.verification_links?.court_search || entityData.property.offices.clerk_of_court.search_url}
												target="_blank"
												rel="noopener noreferrer"
												class="group flex flex-col p-4 border-2 border-purple-200 rounded-xl hover:border-purple-400 hover:bg-gradient-to-br hover:from-purple-50 hover:to-pink-50 transition-all duration-200 hover:shadow-md"
												title={entityData.property.offices.clerk_of_court.description}
											>
												<div class="flex items-center space-x-3 mb-2">
													<div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-200 transition-colors">
														<Scale class="h-4 w-4 text-purple-600" />
													</div>
													<div class="flex-1">
														<div class="font-medium text-gray-900 text-sm">Clerk of Court</div>
														<div class="text-xs text-purple-600">{entityData.property.offices.clerk_of_court.name}</div>
													</div>
													<ExternalLink class="h-4 w-4 text-gray-400 group-hover:text-purple-500 transition-colors" />
												</div>
												<div class="text-xs text-gray-600 mb-3">{entityData.property.offices.clerk_of_court.description}</div>
												<div class="flex items-center space-x-2 text-xs text-gray-500">
													<div class="w-2 h-2 bg-green-400 rounded-full"></div>
													<span>Records Search</span>
												</div>
											</a>
										{/if}
									</div>
									
									{#if entityData.property.verification_links && entityData.property.parcel_id}
										<div class="mt-4 p-3 bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-200 rounded-lg">
											<div class="flex items-start space-x-2">
												<Info class="h-4 w-4 text-indigo-600 mt-0.5" />
												<div class="text-sm">
													<div class="font-medium text-indigo-900 mb-1">Direct Property Access</div>
													<div class="text-indigo-700 text-xs">
														These links include parcel ID <span class="font-mono bg-white px-1 rounded">{entityData.property.parcel_id}</span> for instant property lookup.
														Click any office above to jump directly to this property's official records.
													</div>
												</div>
											</div>
										</div>
									{/if}
								</div>
							{/if}
							
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
							on:click={() => { searchQuery = 'Sunshine Holdings LLC'; searchEntity(); }}
							class="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
						>
							🏛️ Foreclosure Case
						</button>
						<button
							on:click={() => { searchQuery = 'Business Investment Trust LLC'; searchEntity(); }}
							class="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
						>
							⚖️ DBPR Regulatory Action
						</button>
						<button
							on:click={() => { searchQuery = 'Offshore Holdings Trust'; searchEntity(); }}
							class="px-3 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors"
						>
							💰 Bankruptcy Case
						</button>
						<button
							on:click={() => { searchQuery = 'Coastal Development Trust'; searchEntity(); }}
							class="px-3 py-1 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 transition-colors"
						>
							🏛️ Tax Lien Case
						</button>
						<button
							on:click={() => { searchQuery = 'Smith Family Living Trust'; searchEntity(); }}
							class="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
						>
							✅ Clean Trust
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
						<li>• Trust & Corporate Analysis</li>
						<li>• Court Case History</li>
						<li>• Domain & Web Presence</li>
						<li>• Officer Cross-References</li>
						<li>• Grant Compliance Issues</li>
						<li>• Automated Change Detection</li>
					</ul>
				</div>
				
				<!-- Data Sources -->
				<div>
					<h3 class="text-sm font-semibled text-gray-900 mb-4">Comprehensive Data</h3>
					<ul class="space-y-2 text-xs text-gray-600">
						<li>• Corporate & Trust Records</li>
						<li>• Court Case Databases</li>
						<li>• WHOIS & Domain Registry</li>
						<li>• Officer Cross-References</li>
						<li>• Federal & State Grants</li>
						<li>• Automated Monitoring</li>
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