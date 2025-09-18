"""
Integration tests for RequirementsParser

Tests parsing of actual specification documents from the repository.
"""

import pytest
from pathlib import Path

from src.spec_scrub.parsers.requirements_parser import RequirementsParser


class TestRequirementsParserIntegration:
    """Integration tests for RequirementsParser with real specification documents."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RequirementsParser()
        self.spec_dir = Path(".kiro/specs")
        
    def test_parse_spec_scrub_requirements(self):
        """Test parsing the spec-scrub-rdi-consistency requirements document."""
        requirements_path = self.spec_dir / "spec-scrub-rdi-consistency" / "requirements.md"
        
        if not requirements_path.exists():
            pytest.skip(f"Requirements file not found: {requirements_path}")
            
        requirements = self.parser.parse_requirements(requirements_path)
        
        # Verify we found requirements
        assert len(requirements) > 0, "Should find requirements in the document"
        
        # Verify requirement structure
        for req in requirements:
            assert req.requirement_id, f"Requirement should have ID: {req}"
            assert req.user_story, f"Requirement should have user story: {req}"
            assert req.source_file == requirements_path
            assert req.line_number > 0
            
        # Verify specific requirements exist
        req_ids = [req.requirement_id for req in requirements]
        assert "1" in req_ids, "Should find Requirement 1 (Forward Pass RDI Validation)"
        assert "2" in req_ids, "Should find Requirement 2 (Backward Pass RDI Validation)"
        
        # Test metadata extraction for first requirement
        first_req = requirements[0]
        metadata = self.parser.extract_requirement_metadata(first_req)
        assert metadata.requirement_id == first_req.requirement_id
        
    def test_parse_spec_framework_requirements(self):
        """Test parsing spec-framework requirements if they exist."""
        requirements_path = self.spec_dir / "spec-framework" / "requirements.md"
        
        if not requirements_path.exists():
            pytest.skip(f"Requirements file not found: {requirements_path}")
            
        requirements = self.parser.parse_requirements(requirements_path)
        
        # Verify basic parsing works
        assert isinstance(requirements, list)
        
        # If requirements exist, verify structure
        if requirements:
            for req in requirements:
                assert req.requirement_id
                assert req.source_file == requirements_path
                
    def test_parse_multiple_specifications(self):
        """Test parsing requirements from multiple specifications."""
        if not self.spec_dir.exists():
            pytest.skip(f"Specs directory not found: {self.spec_dir}")
            
        parsed_specs = []
        
        # Find all requirements.md files
        for spec_path in self.spec_dir.iterdir():
            if spec_path.is_dir():
                requirements_path = spec_path / "requirements.md"
                if requirements_path.exists():
                    try:
                        requirements = self.parser.parse_requirements(requirements_path)
                        parsed_specs.append({
                            'spec_name': spec_path.name,
                            'requirements_count': len(requirements),
                            'requirements': requirements
                        })
                    except Exception as e:
                        pytest.fail(f"Failed to parse {requirements_path}: {e}")
                        
        # Verify we found and parsed some specifications
        assert len(parsed_specs) > 0, "Should find at least one specification with requirements"
        
        # Verify all parsed requirements have proper structure
        total_requirements = 0
        for spec in parsed_specs:
            total_requirements += spec['requirements_count']
            for req in spec['requirements']:
                assert req.requirement_id, f"Requirement missing ID in {spec['spec_name']}"
                assert req.user_story, f"Requirement missing user story in {spec['spec_name']}"
                
        print(f"Successfully parsed {len(parsed_specs)} specifications with {total_requirements} total requirements")
        
    def test_requirements_parser_performance(self):
        """Test parser performance with actual specification documents."""
        import time
        
        requirements_path = self.spec_dir / "spec-scrub-rdi-consistency" / "requirements.md"
        
        if not requirements_path.exists():
            pytest.skip(f"Requirements file not found: {requirements_path}")
            
        # Measure parsing time
        start_time = time.time()
        requirements = self.parser.parse_requirements(requirements_path)
        parse_time = time.time() - start_time
        
        # Verify performance is reasonable (should be under 1 second for typical docs)
        assert parse_time < 1.0, f"Parsing took too long: {parse_time:.3f}s"
        
        # Verify we got results
        assert len(requirements) > 0
        
        print(f"Parsed {len(requirements)} requirements in {parse_time:.3f}s")
        
    def test_requirements_traceability_extraction(self):
        """Test extraction of requirement traceability information."""
        requirements_path = self.spec_dir / "spec-scrub-rdi-consistency" / "requirements.md"
        
        if not requirements_path.exists():
            pytest.skip(f"Requirements file not found: {requirements_path}")
            
        requirements = self.parser.parse_requirements(requirements_path)
        
        # Test metadata extraction for all requirements
        for req in requirements:
            metadata = self.parser.extract_requirement_metadata(req)
            
            # Verify metadata structure
            assert metadata.requirement_id == req.requirement_id
            assert isinstance(metadata.dependencies, list)
            assert isinstance(metadata.tags, list)
            assert metadata.priority >= 1
            assert metadata.category
            assert metadata.complexity in ['low', 'medium', 'high']
            
        print(f"Successfully extracted metadata for {len(requirements)} requirements")