"""
LedgerTrace Ownership Tracer
Exposes hidden ownership chains and shell company structures through advanced entity relationship analysis.
"""

import asyncio
import aiohttp
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from difflib import SequenceMatcher
import logging
from urllib.parse import urljoin, quote
import time

logger = logging.getLogger(__name__)

@dataclass
class Officer:
    """Represents a corporate officer or manager."""
    name: str
    title: str
    address: str
    normalized_name: str = ""
    normalized_address: str = ""
    
    def __post_init__(self):
        self.normalized_name = self._normalize_name(self.name)
        self.normalized_address = self._normalize_address(self.address)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for fuzzy matching."""
        # Remove common prefixes/suffixes and normalize spacing
        name = re.sub(r'\b(mr|mrs|ms|dr|prof|jr|sr|ii|iii|iv)\b\.?', '', name.lower())
        name = re.sub(r'[^\w\s]', '', name)
        return ' '.join(name.split())
    
    def _normalize_address(self, address: str) -> str:
        """Normalize address for matching."""
        # Remove apartment/suite numbers and normalize
        addr = re.sub(r'\b(apt|suite|ste|unit|#)\s*\w+\b', '', address.lower())
        addr = re.sub(r'[^\w\s]', ' ', addr)
        return ' '.join(addr.split())

@dataclass
class Entity:
    """Represents a business entity with ownership data."""
    filing_id: str
    name: str
    status: str
    entity_type: str
    date_filed: datetime
    officers: List[Officer]
    registered_agent: Optional[str] = None
    registered_address: Optional[str] = None
    
    # Ownership tracking
    owned_by: List['Entity'] = None
    owns: List['Entity'] = None
    ownership_depth: int = 0
    shell_company_score: float = 0.0
    
    def __post_init__(self):
        if self.owned_by is None:
            self.owned_by = []
        if self.owns is None:
            self.owns = []

@dataclass
class OwnershipChain:
    """Represents a complete ownership chain from root to leaf entities."""
    root_entity: Entity
    chain: List[Entity]
    depth: int
    shell_indicators: List[str]
    risk_score: float
    obfuscation_patterns: List[str]

class OwnershipTracer:
    """Advanced ownership chain detection and shell company analysis."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.entity_cache: Dict[str, Entity] = {}
        self.officer_similarity_threshold = 0.85
        self.address_similarity_threshold = 0.80
        self.max_chain_depth = 10
        
        # Rate limiting for Sunbiz
        self.last_request_time = 0
        self.request_delay = 2.0  # 2 seconds between requests
        
    async def __aenter__(self):
        """Async context manager entry with security configurations."""
        # Secure session configuration
        connector = aiohttp.TCPConnector(
            ssl=True,  # Enforce SSL
            limit=10,  # Connection pool limit
            limit_per_host=5,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30, connect=10),
            headers={
                'User-Agent': 'LedgerTrace/1.0 (+https://ledgertrace.com) Compliance Analysis Tool',
                'Accept': 'text/html,application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'DNT': '1',  # Do Not Track
                'Connection': 'keep-alive'
            },
            connector=connector,
            raise_for_status=False  # Handle status codes manually
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def trace_ownership_chain(self, entity_name: str, max_depth: int = 5) -> List[OwnershipChain]:
        """
        Trace complete ownership chains for an entity, detecting shell company structures.
        
        Args:
            entity_name: Name of the root entity to trace
            max_depth: Maximum depth to search for ownership chains
            
        Returns:
            List of complete ownership chains with risk analysis
        """
        logger.info(f"Starting ownership chain trace for: {entity_name}")
        
        # Find root entity
        root_entity = await self._search_sunbiz_entity(entity_name)
        if not root_entity:
            logger.warning(f"Could not find entity: {entity_name}")
            return []
        
        # Build ownership network
        ownership_network = await self._build_ownership_network(root_entity, max_depth)
        
        # Detect ownership chains
        chains = self._detect_ownership_chains(ownership_network, root_entity)
        
        # Analyze each chain for shell company indicators
        analyzed_chains = []
        for chain in chains:
            analyzed_chain = await self._analyze_ownership_chain(chain)
            analyzed_chains.append(analyzed_chain)
        
        # Sort by risk score (highest first)
        analyzed_chains.sort(key=lambda x: x.risk_score, reverse=True)
        
        logger.info(f"Found {len(analyzed_chains)} ownership chains for {entity_name}")
        return analyzed_chains
    
    async def _search_sunbiz_entity(self, entity_name: str) -> Optional[Entity]:
        """Search for an entity in Florida Sunbiz database with security measures."""
        if not self.session:
            raise RuntimeError("OwnershipTracer must be used as async context manager")
        
        # Input validation and sanitization
        if not entity_name or len(entity_name.strip()) == 0:
            logger.warning("Empty entity name provided for search")
            return None
        
        # Sanitize entity name for URL parameters
        clean_name = re.sub(r'[^\w\s&.-]', '', entity_name.strip())[:200]
        if not clean_name:
            logger.warning(f"Entity name sanitization resulted in empty string: {entity_name}")
            return None
        
        # Rate limiting
        await self._rate_limit()
        
        try:
            # Sunbiz entity search endpoint - verified legitimate
            search_url = "https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults"
            
            # Search parameters with URL encoding
            params = {
                'inquiryType': 'EntityName',
                'searchNameOrder': 'A',
                'searchTerm': clean_name.upper()[:100],  # Limit length
            }
            
            logger.debug(f"Searching Sunbiz for: {clean_name[:50]}...")
            
            # Use timeout and validate SSL
            async with self.session.get(
                search_url, 
                params=params,
                ssl=True,  # Enforce SSL verification
                timeout=aiohttp.ClientTimeout(total=15)  # Shorter timeout
            ) as response:
                if response.status == 429:
                    logger.warning("Rate limited by Sunbiz, backing off")
                    await asyncio.sleep(10)
                    return None
                
                if response.status != 200:
                    logger.error(f"Sunbiz search failed with status {response.status}")
                    return None
                
                # Limit response size to prevent memory exhaustion
                html_content = await response.text()
                if len(html_content) > 1024 * 1024:  # 1MB limit
                    logger.warning("Response from Sunbiz too large, truncating")
                    html_content = html_content[:1024 * 1024]
                
                # Parse search results to find exact or close matches
                entity = await self._parse_sunbiz_search_results(html_content, clean_name)
                
                if entity:
                    # Get detailed entity information including officers
                    detailed_entity = await self._get_sunbiz_entity_details(entity.filing_id)
                    return detailed_entity
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error searching Sunbiz for {clean_name}: {e}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout searching Sunbiz for {clean_name}")
        except Exception as e:
            logger.error(f"Unexpected error searching Sunbiz for {clean_name}: {e}")
        
        return None
    
    async def _parse_sunbiz_search_results(self, html: str, target_name: str) -> Optional[Entity]:
        """Parse Sunbiz search results to find matching entities."""
        # This is a simplified parser - in production, use BeautifulSoup or similar
        # Looking for entity links in the format: /Inquiry/CorporationSearch/ByDocumentNumber?documentNumber=XXX
        
        import re
        
        # Find document numbers in search results
        pattern = r'/Inquiry/CorporationSearch/ByDocumentNumber\?documentNumber=([^"&]+)'
        matches = re.findall(pattern, html)
        
        # Also extract entity names and types from table rows
        name_pattern = r'<td[^>]*>([^<]*' + re.escape(target_name.upper()[:10]) + '[^<]*)</td>'
        name_matches = re.findall(name_pattern, html, re.IGNORECASE)
        
        if matches and name_matches:
            # Return first match - in production, implement better matching logic
            filing_id = matches[0]
            entity_name = name_matches[0].strip()
            
            return Entity(
                filing_id=filing_id,
                name=entity_name,
                status="ACTIVE",  # Will be updated in detailed fetch
                entity_type="CORPORATION",  # Will be updated in detailed fetch
                date_filed=datetime.now(),  # Will be updated in detailed fetch
                officers=[]
            )
        
        return None
    
    async def _get_sunbiz_entity_details(self, filing_id: str) -> Optional[Entity]:
        """Get detailed entity information including officers from Sunbiz."""
        if filing_id in self.entity_cache:
            return self.entity_cache[filing_id]
        
        await self._rate_limit()
        
        try:
            # Sunbiz entity details endpoint
            detail_url = f"https://search.sunbiz.org/Inquiry/CorporationSearch/ByDocumentNumber"
            params = {'documentNumber': filing_id}
            
            logger.debug(f"Fetching details for filing ID: {filing_id}")
            
            async with self.session.get(detail_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch entity details: {response.status}")
                    return None
                
                html_content = await response.text()
                entity = await self._parse_sunbiz_entity_details(html_content, filing_id)
                
                if entity:
                    self.entity_cache[filing_id] = entity
                
                return entity
                
        except Exception as e:
            logger.error(f"Error fetching entity details for {filing_id}: {e}")
        
        return None
    
    async def _parse_sunbiz_entity_details(self, html: str, filing_id: str) -> Optional[Entity]:
        """Parse detailed entity information from Sunbiz page."""
        # Simplified parser - in production use proper HTML parser
        import re
        
        try:
            # Extract entity name
            name_pattern = r'<span[^>]*id="MainContent_lblName"[^>]*>([^<]+)</span>'
            name_match = re.search(name_pattern, html)
            entity_name = name_match.group(1).strip() if name_match else "Unknown"
            
            # Extract entity status
            status_pattern = r'<span[^>]*id="MainContent_lblStatus"[^>]*>([^<]+)</span>'
            status_match = re.search(status_pattern, html)
            status = status_match.group(1).strip() if status_match else "Unknown"
            
            # Extract entity type
            type_pattern = r'<span[^>]*id="MainContent_lblEntityType"[^>]*>([^<]+)</span>'
            type_match = re.search(type_pattern, html)
            entity_type = type_match.group(1).strip() if type_match else "Unknown"
            
            # Extract filing date
            date_pattern = r'<span[^>]*id="MainContent_lblDateFiled"[^>]*>([^<]+)</span>'
            date_match = re.search(date_pattern, html)
            date_str = date_match.group(1).strip() if date_match else ""
            
            try:
                date_filed = datetime.strptime(date_str, "%m/%d/%Y") if date_str else datetime.now()
            except ValueError:
                date_filed = datetime.now()
            
            # Extract officers/managers
            officers = await self._parse_officers_from_html(html)
            
            entity = Entity(
                filing_id=filing_id,
                name=entity_name,
                status=status,
                entity_type=entity_type,
                date_filed=date_filed,
                officers=officers
            )
            
            logger.debug(f"Parsed entity: {entity_name} with {len(officers)} officers")
            return entity
            
        except Exception as e:
            logger.error(f"Error parsing entity details: {e}")
            return None
    
    async def _parse_officers_from_html(self, html: str) -> List[Officer]:
        """Parse officer information from Sunbiz entity page."""
        # Simplified officer parsing - look for officer table patterns
        import re
        
        officers = []
        
        # Pattern to find officer table rows
        # This is a simplified approach - production code should use proper HTML parsing
        officer_pattern = r'<tr[^>]*>.*?<td[^>]*>([^<]*(?:PRESIDENT|SECRETARY|TREASURER|DIRECTOR|MANAGER|MEMBER)[^<]*)</td>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]*)</td>.*?</tr>'
        
        matches = re.findall(officer_pattern, html, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            title = match[0].strip()
            name = match[1].strip()
            address = match[2].strip() if len(match) > 2 else ""
            
            if name and title:
                officer = Officer(
                    name=name,
                    title=title,
                    address=address
                )
                officers.append(officer)
        
        return officers
    
    async def _build_ownership_network(self, root_entity: Entity, max_depth: int) -> Dict[str, Entity]:
        """Build a network of related entities through shared officers and addresses."""
        network = {root_entity.filing_id: root_entity}
        entities_to_process = [root_entity]
        processed_entities = set()
        
        current_depth = 0
        
        while entities_to_process and current_depth < max_depth:
            current_level_entities = entities_to_process.copy()
            entities_to_process.clear()
            
            for entity in current_level_entities:
                if entity.filing_id in processed_entities:
                    continue
                
                processed_entities.add(entity.filing_id)
                entity.ownership_depth = current_depth
                
                # Find related entities through shared officers
                related_entities = await self._find_related_entities(entity)
                
                for related_entity in related_entities:
                    if related_entity.filing_id not in network:
                        network[related_entity.filing_id] = related_entity
                        entities_to_process.append(related_entity)
                        
                        # Establish ownership relationship
                        if self._is_ownership_relationship(entity, related_entity):
                            entity.owns.append(related_entity)
                            related_entity.owned_by.append(entity)
            
            current_depth += 1
        
        logger.info(f"Built ownership network with {len(network)} entities")
        return network
    
    async def _find_related_entities(self, entity: Entity) -> List[Entity]:
        """Find entities related through shared officers or addresses."""
        related_entities = []
        
        # Search for entities with shared officers
        for officer in entity.officers:
            # Search by officer name
            search_results = await self._search_entities_by_officer(officer.normalized_name)
            
            for result in search_results:
                if result.filing_id != entity.filing_id:
                    # Verify officer similarity
                    if self._has_shared_officer(entity, result):
                        related_entities.append(result)
        
        # Remove duplicates
        seen_ids = set()
        unique_entities = []
        for ent in related_entities:
            if ent.filing_id not in seen_ids:
                seen_ids.add(ent.filing_id)
                unique_entities.append(ent)
        
        return unique_entities
    
    async def _search_entities_by_officer(self, officer_name: str) -> List[Entity]:
        """Search for entities that have a specific officer."""
        # This would typically search a database or API
        # For now, return empty list - implement based on data source
        return []
    
    def _has_shared_officer(self, entity1: Entity, entity2: Entity) -> bool:
        """Check if two entities share officers based on name similarity."""
        for officer1 in entity1.officers:
            for officer2 in entity2.officers:
                name_similarity = self._calculate_similarity(
                    officer1.normalized_name, 
                    officer2.normalized_name
                )
                
                if name_similarity >= self.officer_similarity_threshold:
                    return True
        
        return False
    
    def _is_ownership_relationship(self, entity1: Entity, entity2: Entity) -> bool:
        """Determine if there's an ownership relationship between entities."""
        # Check for management/ownership indicators in officer titles
        ownership_titles = {
            'president', 'ceo', 'managing member', 'manager', 
            'sole member', 'owner', 'principal', 'managing director'
        }
        
        for officer in entity1.officers:
            title_lower = officer.title.lower()
            if any(ownership_title in title_lower for ownership_title in ownership_titles):
                # Check if this officer appears in entity2
                for officer2 in entity2.officers:
                    similarity = self._calculate_similarity(
                        officer.normalized_name, 
                        officer2.normalized_name
                    )
                    if similarity >= self.officer_similarity_threshold:
                        return True
        
        return False
    
    def _detect_ownership_chains(self, network: Dict[str, Entity], root_entity: Entity) -> List[List[Entity]]:
        """Detect ownership chains in the entity network."""
        chains = []
        
        def build_chain(entity: Entity, current_chain: List[Entity], visited: Set[str]):
            if entity.filing_id in visited or len(current_chain) > self.max_chain_depth:
                return
            
            visited.add(entity.filing_id)
            current_chain.append(entity)
            
            if entity.owns:
                for owned_entity in entity.owns:
                    build_chain(owned_entity, current_chain.copy(), visited.copy())
            else:
                # End of chain - store it if it has multiple entities
                if len(current_chain) > 1:
                    chains.append(current_chain.copy())
        
        build_chain(root_entity, [], set())
        
        return chains
    
    async def _analyze_ownership_chain(self, chain: List[Entity]) -> OwnershipChain:
        """Analyze an ownership chain for shell company indicators and risk factors."""
        shell_indicators = []
        obfuscation_patterns = []
        risk_score = 0.0
        
        # Check for shell company indicators
        for entity in chain:
            # Recent formation (shell companies often recently formed)
            if entity.date_filed > datetime.now() - timedelta(days=365):
                shell_indicators.append(f"Recent formation: {entity.name}")
                risk_score += 15
            
            # Minimal officer structure
            if len(entity.officers) <= 2:
                shell_indicators.append(f"Minimal officers: {entity.name}")
                risk_score += 20
            
            # Shared officers across chain
            shared_officers = self._count_shared_officers_in_chain(entity, chain)
            if shared_officers > 0:
                shell_indicators.append(f"Shared officers: {entity.name}")
                risk_score += 10 * shared_officers
        
        # Check for obfuscation patterns
        if len(chain) >= 3:
            obfuscation_patterns.append("Deep ownership structure (3+ layers)")
            risk_score += 25
        
        if len(chain) >= 5:
            obfuscation_patterns.append("Very deep ownership structure (5+ layers)")
            risk_score += 40
        
        # Check for circular ownership patterns
        if self._has_circular_ownership(chain):
            obfuscation_patterns.append("Circular ownership detected")
            risk_score += 50
        
        # Normalize risk score (0-100)
        risk_score = min(risk_score, 100)
        
        return OwnershipChain(
            root_entity=chain[0],
            chain=chain,
            depth=len(chain),
            shell_indicators=shell_indicators,
            risk_score=risk_score,
            obfuscation_patterns=obfuscation_patterns
        )
    
    def _count_shared_officers_in_chain(self, entity: Entity, chain: List[Entity]) -> int:
        """Count how many officers this entity shares with others in the chain."""
        shared_count = 0
        
        for other_entity in chain:
            if other_entity.filing_id != entity.filing_id:
                if self._has_shared_officer(entity, other_entity):
                    shared_count += 1
        
        return shared_count
    
    def _has_circular_ownership(self, chain: List[Entity]) -> bool:
        """Check if the ownership chain has circular references."""
        # Simple check - look for entity appearing twice in chain
        entity_ids = [entity.filing_id for entity in chain]
        return len(entity_ids) != len(set(entity_ids))
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    async def _rate_limit(self):
        """Implement rate limiting for API requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()

    async def get_shell_company_report(self, entity_name: str) -> Dict:
        """Generate a comprehensive shell company analysis report."""
        logger.info(f"Generating shell company report for: {entity_name}")
        
        ownership_chains = await self.trace_ownership_chain(entity_name)
        
        if not ownership_chains:
            return {
                'entity_name': entity_name,
                'analysis_date': datetime.now().isoformat(),
                'risk_assessment': 'LOW',
                'shell_company_probability': 0.0,
                'ownership_chains': [],
                'summary': 'No complex ownership structures detected'
            }
        
        # Calculate overall risk
        max_risk_score = max(chain.risk_score for chain in ownership_chains)
        avg_risk_score = sum(chain.risk_score for chain in ownership_chains) / len(ownership_chains)
        
        # Determine risk level
        if max_risk_score >= 70:
            risk_level = 'CRITICAL'
        elif max_risk_score >= 50:
            risk_level = 'HIGH'
        elif max_risk_score >= 30:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Count total shell indicators
        total_indicators = sum(len(chain.shell_indicators) for chain in ownership_chains)
        total_obfuscation = sum(len(chain.obfuscation_patterns) for chain in ownership_chains)
        
        report = {
            'entity_name': entity_name,
            'analysis_date': datetime.now().isoformat(),
            'risk_assessment': risk_level,
            'shell_company_probability': max_risk_score / 100.0,
            'ownership_chains_found': len(ownership_chains),
            'deepest_chain_depth': max(chain.depth for chain in ownership_chains),
            'total_shell_indicators': total_indicators,
            'total_obfuscation_patterns': total_obfuscation,
            'max_risk_score': max_risk_score,
            'avg_risk_score': avg_risk_score,
            'ownership_chains': [
                {
                    'chain_id': i,
                    'depth': chain.depth,
                    'risk_score': chain.risk_score,
                    'entities': [
                        {
                            'filing_id': entity.filing_id,
                            'name': entity.name,
                            'entity_type': entity.entity_type,
                            'status': entity.status,
                            'date_filed': entity.date_filed.isoformat(),
                            'officers_count': len(entity.officers),
                            'officers': [
                                {
                                    'name': officer.name,
                                    'title': officer.title,
                                    'address': officer.address
                                }
                                for officer in entity.officers
                            ]
                        }
                        for entity in chain.chain
                    ],
                    'shell_indicators': chain.shell_indicators,
                    'obfuscation_patterns': chain.obfuscation_patterns
                }
                for i, chain in enumerate(ownership_chains)
            ]
        }
        
        # Generate summary
        if risk_level == 'CRITICAL':
            summary = f"CRITICAL: {entity_name} exhibits strong shell company characteristics with {len(ownership_chains)} complex ownership chains and {total_indicators} shell indicators."
        elif risk_level == 'HIGH':
            summary = f"HIGH RISK: {entity_name} shows significant ownership obfuscation with {len(ownership_chains)} layered structures."
        elif risk_level == 'MEDIUM':
            summary = f"MEDIUM RISK: {entity_name} has some concerning ownership patterns requiring further investigation."
        else:
            summary = f"LOW RISK: {entity_name} shows minimal shell company indicators."
        
        report['summary'] = summary
        
        logger.info(f"Shell company analysis complete: {risk_level} risk level")
        return report