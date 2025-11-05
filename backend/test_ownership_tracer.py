"""
Test suite for ownership tracing functionality
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from app.ownership_tracer import OwnershipTracer, Entity, Officer, OwnershipChain
from datetime import datetime

@pytest.fixture
def sample_officer():
    """Create a sample officer for testing."""
    return Officer(
        name="John Smith",
        title="President",
        address="123 Main St, Miami, FL 33101"
    )

@pytest.fixture
def sample_entity():
    """Create a sample entity for testing."""
    officer = Officer("John Smith", "President", "123 Main St, Miami, FL")
    return Entity(
        filing_id="P12345678",
        name="Test Corporation",
        status="ACTIVE",
        entity_type="CORPORATION",
        date_filed=datetime(2020, 1, 15),
        officers=[officer]
    )

@pytest.fixture
def ownership_tracer():
    """Create an OwnershipTracer instance for testing."""
    return OwnershipTracer()

class TestOwnershipTracer:
    """Test cases for OwnershipTracer functionality."""
    
    def test_officer_normalization(self, sample_officer):
        """Test officer name and address normalization."""
        assert sample_officer.normalized_name == "john smith"
        assert "123 main st" in sample_officer.normalized_address
    
    def test_entity_creation(self, sample_entity):
        """Test entity creation and initialization."""
        assert sample_entity.filing_id == "P12345678"
        assert sample_entity.name == "Test Corporation"
        assert len(sample_entity.officers) == 1
        assert sample_entity.ownership_depth == 0
        assert sample_entity.shell_company_score == 0.0
    
    def test_similarity_calculation(self, ownership_tracer):
        """Test text similarity calculation."""
        similarity = ownership_tracer._calculate_similarity("John Smith", "Jon Smith")
        assert similarity > 0.8  # Should be high similarity
        
        similarity = ownership_tracer._calculate_similarity("John Smith", "Jane Doe")
        assert similarity < 0.5  # Should be low similarity
    
    def test_shared_officers_detection(self, ownership_tracer):
        """Test detection of shared officers between entities."""
        officer1 = Officer("John Smith", "President", "123 Main St")
        officer2 = Officer("John A Smith", "CEO", "456 Oak Ave")  # Similar name
        
        entity1 = Entity("P1", "Corp A", "ACTIVE", "CORP", datetime.now(), [officer1])
        entity2 = Entity("P2", "Corp B", "ACTIVE", "LLC", datetime.now(), [officer2])
        
        has_shared = ownership_tracer._has_shared_officer(entity1, entity2)
        assert has_shared  # Should detect similarity
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, ownership_tracer):
        """Test rate limiting functionality."""
        # Mock the time to test rate limiting
        with patch('app.ownership_tracer.time.time', side_effect=[0, 1, 2, 3]):
            with patch('asyncio.sleep') as mock_sleep:
                ownership_tracer.last_request_time = 0
                await ownership_tracer._rate_limit()
                
                # Should sleep if requests are too close
                ownership_tracer.last_request_time = 1
                await ownership_tracer._rate_limit()
                mock_sleep.assert_called()
    
    def test_ownership_relationship_detection(self, ownership_tracer):
        """Test detection of ownership relationships."""
        managing_officer = Officer("John Smith", "Managing Member", "123 Main St")
        regular_officer = Officer("Jane Doe", "Secretary", "456 Oak Ave")
        
        entity1 = Entity("P1", "Manager LLC", "ACTIVE", "LLC", datetime.now(), [managing_officer])
        entity2 = Entity("P2", "Owned Corp", "ACTIVE", "CORP", datetime.now(), [regular_officer])
        
        # Mock shared officer detection - the method checks for both shared officers AND ownership titles
        with patch.object(ownership_tracer, '_has_shared_officer', return_value=True):
            # Need to also ensure officer names match for ownership detection logic
            with patch.object(ownership_tracer, '_calculate_similarity', return_value=0.9):
                is_ownership = ownership_tracer._is_ownership_relationship(entity1, entity2)
                assert is_ownership
    
    def test_shell_company_scoring(self, ownership_tracer):
        """Test shell company indicator scoring."""
        # Test recent formation indicator
        recent_entity = Entity(
            "P1", "Recent Corp", "ACTIVE", "CORP",
            datetime.now(),  # Very recent
            [Officer("John Doe", "President", "123 Main St")]
        )
        
        # Test minimal officer structure
        minimal_officers_entity = Entity(
            "P2", "Minimal Corp", "ACTIVE", "CORP",
            datetime(2020, 1, 1),
            [Officer("John Doe", "President", "123 Main St")]  # Only 1 officer
        )
        
        chain = [recent_entity, minimal_officers_entity]
        
        # Mock the analyze method
        ownership_chain = asyncio.run(ownership_tracer._analyze_ownership_chain(chain))
        
        # Should have shell indicators
        assert len(ownership_chain.shell_indicators) > 0
        assert ownership_chain.risk_score > 0
    
    def test_circular_ownership_detection(self, ownership_tracer):
        """Test detection of circular ownership patterns."""
        entity1 = Entity("P1", "Entity A", "ACTIVE", "CORP", datetime.now(), [])
        entity2 = Entity("P2", "Entity B", "ACTIVE", "CORP", datetime.now(), [])
        entity3 = Entity("P1", "Entity A", "ACTIVE", "CORP", datetime.now(), [])  # Same ID as entity1
        
        circular_chain = [entity1, entity2, entity3]
        has_circular = ownership_tracer._has_circular_ownership(circular_chain)
        assert has_circular
        
        # Test non-circular chain
        non_circular_chain = [entity1, entity2]
        has_circular = ownership_tracer._has_circular_ownership(non_circular_chain)
        assert not has_circular
    
    @pytest.mark.asyncio
    async def test_ownership_chain_tracing_mock(self, ownership_tracer):
        """Test ownership chain tracing with mocked data."""
        # Mock the search methods
        mock_entity = Entity(
            "P12345", "Test Corp", "ACTIVE", "CORPORATION",
            datetime(2020, 1, 1),
            [Officer("John Smith", "President", "123 Main St")]
        )
        
        with patch.object(ownership_tracer, '_search_sunbiz_entity', return_value=mock_entity):
            with patch.object(ownership_tracer, '_build_ownership_network', return_value={"P12345": mock_entity}):
                with patch.object(ownership_tracer, '_detect_ownership_chains', return_value=[[mock_entity]]):
                    
                    # Test tracing
                    chains = await ownership_tracer.trace_ownership_chain("Test Corp", max_depth=3)
                    
                    # Should return analyzed chains
                    assert len(chains) > 0
                    assert isinstance(chains[0], OwnershipChain)
    
    @pytest.mark.asyncio
    async def test_shell_company_report_generation(self, ownership_tracer):
        """Test generation of comprehensive shell company reports."""
        # Mock ownership chain tracing
        mock_chain = OwnershipChain(
            root_entity=Entity("P1", "Test Corp", "ACTIVE", "CORP", datetime.now(), []),
            chain=[],
            depth=3,
            shell_indicators=["Recent formation", "Minimal officers"],
            risk_score=75.0,
            obfuscation_patterns=["Deep ownership structure"]
        )
        
        with patch.object(ownership_tracer, 'trace_ownership_chain', return_value=[mock_chain]):
            report = await ownership_tracer.get_shell_company_report("Test Corp")
            
            # Verify report structure
            assert report["entity_name"] == "Test Corp"
            assert report["risk_assessment"] == "CRITICAL"  # Should be CRITICAL for 75.0 score (>=70)
            assert report["ownership_chains_found"] == 1
            assert report["deepest_chain_depth"] == 3
            assert "shell_indicators" in str(report)

class TestOwnershipIntegration:
    """Integration tests for ownership analysis."""
    
    @pytest.mark.asyncio
    async def test_full_ownership_analysis_flow(self):
        """Test the complete ownership analysis workflow."""
        # This would be run with actual Sunbiz data in a real test
        tracer = OwnershipTracer()
        
        # Mock async context manager
        tracer.session = AsyncMock()
        
        # Test with a known entity that should have no complex ownership
        with patch.object(tracer, '_search_sunbiz_entity', return_value=None):
            chains = await tracer.trace_ownership_chain("Nonexistent Corp")
            assert len(chains) == 0
    
    def test_ownership_data_model_conversion(self):
        """Test conversion between ownership tracer and data models."""
        from app.analyzer import convert_ownership_report_to_data
        
        # Mock ownership report
        mock_report = {
            "entity_name": "Test Corp",
            "analysis_date": "2024-12-19T10:00:00Z",
            "risk_assessment": "HIGH",
            "shell_company_probability": 0.75,
            "ownership_chains_found": 1,
            "deepest_chain_depth": 3,
            "total_shell_indicators": 2,
            "total_obfuscation_patterns": 1,
            "max_risk_score": 75.0,
            "avg_risk_score": 75.0,
            "ownership_chains": [
                {
                    "chain_id": 0,
                    "depth": 3,
                    "risk_score": 75.0,
                    "entities": [
                        {
                            "filing_id": "P12345",
                            "name": "Test Corp",
                            "status": "ACTIVE",
                            "entity_type": "CORPORATION",
                            "date_filed": "2020-01-01T00:00:00",
                            "officers_count": 1,
                            "officers": [
                                {
                                    "name": "John Smith",
                                    "title": "President",
                                    "address": "123 Main St"
                                }
                            ]
                        }
                    ],
                    "shell_indicators": ["Recent formation"],
                    "obfuscation_patterns": ["Deep structure"]
                }
            ]
        }
        
        # Convert and verify
        ownership_data = convert_ownership_report_to_data(mock_report)
        
        assert ownership_data.shell_company_score == 0.75
        assert ownership_data.obfuscation_detected is True
        assert len(ownership_data.ownership_chains) == 1
        assert len(ownership_data.risk_indicators) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main(["-v", __file__])