#!/usr/bin/env python3
"""
Task 5.1: Convert Vocabulary Markdown to JSON
=============================================

Converts the existing docs/ubiquitous_language_vocabulary.md file to structured JSON format.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class VocabularyTerm:
    """Structured vocabulary term."""
    term: str
    definition: str
    category: str
    context: str
    related_terms: List[str]
    examples: List[str]
    synonyms: List[str]
    antonyms: List[str]

class VocabularyConverter:
    """Converts markdown vocabulary to JSON format."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.markdown_file = self.project_root / "docs/ubiquitous_language_vocabulary.md"
        self.json_file = self.project_root / "docs/ubiquitous_language_vocabulary.json"
        
    def parse_markdown_vocabulary(self) -> Dict[str, VocabularyTerm]:
        """Parse the markdown vocabulary file."""
        print("📖 Parsing vocabulary markdown file...")
        
        if not self.markdown_file.exists():
            raise FileNotFoundError(f"Vocabulary file not found: {self.markdown_file}")
        
        content = self.markdown_file.read_text()
        vocabulary = {}
        
        # Split by main category sections
        category_sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)
        
        current_category = "Unknown"
        
        for i in range(1, len(category_sections), 2):
            if i + 1 < len(category_sections):
                category = category_sections[i].strip()
                section_content = category_sections[i + 1]
                
                # Parse terms within this category
                terms = self._parse_category_terms(section_content, category)
                vocabulary.update(terms)
        
        print(f"✅ Parsed {len(vocabulary)} vocabulary terms")
        return vocabulary
    
    def _parse_category_terms(self, content: str, category: str) -> Dict[str, VocabularyTerm]:
        """Parse terms within a category section."""
        terms = {}
        
        # Split by term headers (### Term Name)
        term_sections = re.split(r'^### (.+)$', content, flags=re.MULTILINE)
        
        for i in range(1, len(term_sections), 2):
            if i + 1 < len(term_sections):
                term_name = term_sections[i].strip()
                term_content = term_sections[i + 1].strip()
                
                if term_content:
                    term = self._parse_term_content(term_name, term_content, category)
                    if term:
                        terms[term_name] = term
        
        return terms
    
    def _parse_term_content(self, term_name: str, content: str, category: str) -> VocabularyTerm:
        """Parse individual term content."""
        lines = content.split('\n')
        
        definition = ""
        context = ""
        related_terms = []
        examples = []
        synonyms = []
        antonyms = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('**Definition:**'):
                definition = line.replace('**Definition:**', '').strip()
                current_section = 'definition'
            elif line.startswith('**Context:**'):
                context = line.replace('**Context:**', '').strip()
                current_section = 'context'
            elif line.startswith('**Related Terms:**'):
                related_text = line.replace('**Related Terms:**', '').strip()
                if related_text:
                    related_terms = [t.strip() for t in related_text.split(',')]
                current_section = 'related'
            elif line.startswith('**Examples:**'):
                current_section = 'examples'
            elif line.startswith('**Synonyms:**'):
                synonyms_text = line.replace('**Synonyms:**', '').strip()
                if synonyms_text:
                    synonyms = [t.strip() for t in synonyms_text.split(',')]
                current_section = 'synonyms'
            elif line.startswith('**Antonyms:**'):
                antonyms_text = line.replace('**Antonyms:**', '').strip()
                if antonyms_text:
                    antonyms = [t.strip() for t in antonyms_text.split(',')]
                current_section = 'antonyms'
            elif line.startswith('- ') and current_section == 'examples':
                examples.append(line[2:].strip())
            elif line and not line.startswith('**') and not line.startswith('---'):
                # Continue previous section
                if current_section == 'definition' and not definition:
                    definition = line
                elif current_section == 'context' and not context:
                    context = line
        
        # Handle cases where definition is on next line
        if not definition and lines:
            for line in lines:
                line = line.strip()
                if line and not line.startswith('**') and not line.startswith('---'):
                    definition = line
                    break
        
        return VocabularyTerm(
            term=term_name,
            definition=definition,
            category=category,
            context=context,
            related_terms=related_terms,
            examples=examples,
            synonyms=synonyms,
            antonyms=antonyms
        )
    
    def convert_to_json(self, vocabulary: Dict[str, VocabularyTerm]) -> None:
        """Convert vocabulary to JSON format."""
        print("🔄 Converting to JSON format...")
        
        # Convert to dictionary format
        json_data = {}
        for term_name, term in vocabulary.items():
            json_data[term_name] = asdict(term)
        
        # Save to JSON file
        with open(self.json_file, 'w') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON vocabulary saved to: {self.json_file}")
    
    def validate_conversion(self) -> bool:
        """Validate the converted JSON file."""
        print("🔍 Validating JSON conversion...")
        
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            
            # Basic validation
            if not isinstance(data, dict):
                print("❌ JSON data is not a dictionary")
                return False
            
            if len(data) == 0:
                print("❌ JSON data is empty")
                return False
            
            # Validate term structure
            required_fields = ['term', 'definition', 'category', 'context', 'related_terms', 'examples', 'synonyms', 'antonyms']
            
            for term_name, term_data in data.items():
                if not isinstance(term_data, dict):
                    print(f"❌ Term {term_name} is not a dictionary")
                    return False
                
                for field in required_fields:
                    if field not in term_data:
                        print(f"❌ Term {term_name} missing field: {field}")
                        return False
            
            print(f"✅ JSON validation passed: {len(data)} terms with complete structure")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    def run_conversion(self) -> bool:
        """Run the complete conversion process."""
        print("🚀 Starting vocabulary conversion (Task 5.1)")
        print("=" * 50)
        
        try:
            # Parse markdown
            vocabulary = self.parse_markdown_vocabulary()
            
            # Convert to JSON
            self.convert_to_json(vocabulary)
            
            # Validate conversion
            if self.validate_conversion():
                print("\n✅ Task 5.1 completed successfully!")
                print(f"📄 Converted {len(vocabulary)} terms to JSON format")
                return True
            else:
                print("\n❌ Task 5.1 failed validation")
                return False
                
        except Exception as e:
            print(f"\n❌ Task 5.1 failed: {e}")
            return False

def main():
    """Main execution."""
    converter = VocabularyConverter()
    success = converter.run_conversion()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()