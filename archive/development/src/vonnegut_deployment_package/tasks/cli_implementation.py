#!/usr/bin/env python3
"""
Task 6.1: Implement CLI Entry Point and Argument Parsing
========================================================

Enhances the vocabulary projector with comprehensive CLI interface.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

class CLIImplementation:
    """Implements CLI enhancements for vocabulary projector."""
    
    def __init__(self):
        self.project_root = project_root
        self.main_file = self.project_root / "src/multi_dimensional_vocabulary_projector.py"
    
    def add_cli_interface(self) -> bool:
        """Add CLI interface to the main projector file."""
        print("🔧 Adding CLI interface to vocabulary projector...")
        
        try:
            # Read current content
            content = self.main_file.read_text()
            
            # Check if CLI already exists
            if "argparse" in content and "ArgumentParser" in content:
                print("✅ CLI interface already exists")
                return True
            
            # Add CLI implementation
            cli_code = '''
import argparse
import sys
from typing import Optional, List

class VocabularyProjectorCLI:
    """Command-line interface for Multi-Dimensional Vocabulary Projector."""
    
    def __init__(self):
        self.projector = None
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="Multi-Dimensional Vocabulary Projector",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s                                    # Generate all projections
  %(prog)s --vocabulary custom_vocab.json    # Use custom vocabulary
  %(prog)s --output-dir custom_output/       # Custom output directory
  %(prog)s --dimensions category context     # Generate specific projections
  %(prog)s --validate-only                   # Validate vocabulary without generating
  %(prog)s --batch vocab1.json vocab2.json  # Process multiple vocabularies
  %(prog)s --watch                           # Watch for changes and regenerate
            """
        )
        
        # Input options
        parser.add_argument(
            "--vocabulary", "-v",
            type=str,
            default="docs/ubiquitous_language_vocabulary.json",
            help="Path to vocabulary JSON file (default: docs/ubiquitous_language_vocabulary.json)"
        )
        
        parser.add_argument(
            "--output-dir", "-o",
            type=str,
            default="docs/vocabulary_projections",
            help="Output directory for projections (default: docs/vocabulary_projections)"
        )
        
        # Projection selection
        parser.add_argument(
            "--dimensions", "-d",
            nargs="+",
            choices=["category", "context", "alphabetical", "relationships", 
                    "complexity", "stakeholder", "implementation_phase", "domain_boundary"],
            help="Specific projection dimensions to generate (default: all)"
        )
        
        # Operation modes
        parser.add_argument(
            "--validate-only",
            action="store_true",
            help="Validate vocabulary file without generating projections"
        )
        
        parser.add_argument(
            "--batch",
            nargs="+",
            help="Process multiple vocabulary files"
        )
        
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Watch vocabulary file for changes and regenerate automatically"
        )
        
        # Output options
        parser.add_argument(
            "--verbose", "-V",
            action="store_true",
            help="Enable verbose output"
        )
        
        parser.add_argument(
            "--quiet", "-q",
            action="store_true",
            help="Suppress non-error output"
        )
        
        parser.add_argument(
            "--format",
            choices=["markdown", "html", "json"],
            default="markdown",
            help="Output format (default: markdown)"
        )
        
        return parser
    
    def validate_vocabulary(self, vocab_file: str) -> bool:
        """Validate vocabulary file."""
        try:
            projector = MultiDimensionalVocabularyProjector(vocab_file)
            projector.load_vocabulary()
            
            if not projector.vocabulary:
                print(f"❌ No vocabulary loaded from {vocab_file}")
                return False
            
            print(f"✅ Vocabulary validation passed: {len(projector.vocabulary)} terms")
            return True
            
        except Exception as e:
            print(f"❌ Vocabulary validation failed: {e}")
            return False
    
    def process_single_vocabulary(self, vocab_file: str, output_dir: str, 
                                dimensions: Optional[List[str]] = None) -> bool:
        """Process a single vocabulary file."""
        try:
            projector = MultiDimensionalVocabularyProjector(vocab_file)
            projector.output_dir = Path(output_dir)
            projector.output_dir.mkdir(parents=True, exist_ok=True)
            
            projector.load_vocabulary()
            
            if not projector.vocabulary:
                print(f"❌ No vocabulary loaded from {vocab_file}")
                return False
            
            if dimensions:
                # Generate specific dimensions
                print(f"📊 Generating {len(dimensions)} specific projections...")
                for dimension in dimensions:
                    method_name = f"project_by_{dimension}"
                    if hasattr(projector, method_name):
                        method = getattr(projector, method_name)
                        content = method()
                        
                        filename = f"vocabulary_by_{dimension}.md"
                        filepath = projector.output_dir / filename
                        
                        with open(filepath, 'w') as f:
                            f.write(content)
                        
                        print(f"✅ Generated: {filepath}")
                    else:
                        print(f"⚠️  Unknown dimension: {dimension}")
            else:
                # Generate all projections
                projector.generate_all_projections()
            
            return True
            
        except Exception as e:
            print(f"❌ Processing failed for {vocab_file}: {e}")
            return False
    
    def watch_mode(self, vocab_file: str, output_dir: str, dimensions: Optional[List[str]] = None):
        """Watch vocabulary file for changes."""
        import time
        import os
        
        print(f"👁️  Watching {vocab_file} for changes...")
        print("Press Ctrl+C to stop")
        
        last_modified = 0
        
        try:
            while True:
                try:
                    current_modified = os.path.getmtime(vocab_file)
                    
                    if current_modified > last_modified:
                        print(f"🔄 Change detected in {vocab_file}")
                        if self.process_single_vocabulary(vocab_file, output_dir, dimensions):
                            print("✅ Projections updated")
                        else:
                            print("❌ Update failed")
                        
                        last_modified = current_modified
                    
                    time.sleep(1)  # Check every second
                    
                except FileNotFoundError:
                    print(f"⚠️  File not found: {vocab_file}")
                    time.sleep(5)  # Wait longer if file doesn't exist
                    
        except KeyboardInterrupt:
            print("\\n👋 Watch mode stopped")
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run CLI interface."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Set up logging level
        if parsed_args.quiet:
            import logging
            logging.getLogger().setLevel(logging.ERROR)
        elif parsed_args.verbose:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        
        try:
            # Validate-only mode
            if parsed_args.validate_only:
                if parsed_args.batch:
                    success = all(self.validate_vocabulary(f) for f in parsed_args.batch)
                else:
                    success = self.validate_vocabulary(parsed_args.vocabulary)
                return 0 if success else 1
            
            # Batch processing mode
            if parsed_args.batch:
                print(f"📦 Processing {len(parsed_args.batch)} vocabulary files...")
                success_count = 0
                
                for vocab_file in parsed_args.batch:
                    print(f"\\n🔄 Processing: {vocab_file}")
                    if self.process_single_vocabulary(vocab_file, parsed_args.output_dir, parsed_args.dimensions):
                        success_count += 1
                
                print(f"\\n📊 Batch processing complete: {success_count}/{len(parsed_args.batch)} successful")
                return 0 if success_count == len(parsed_args.batch) else 1
            
            # Watch mode
            if parsed_args.watch:
                self.watch_mode(parsed_args.vocabulary, parsed_args.output_dir, parsed_args.dimensions)
                return 0
            
            # Standard processing
            return 0 if self.process_single_vocabulary(
                parsed_args.vocabulary, 
                parsed_args.output_dir, 
                parsed_args.dimensions
            ) else 1
            
        except KeyboardInterrupt:
            print("\\n👋 Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return 1

def main_cli():
    """CLI entry point."""
    cli = VocabularyProjectorCLI()
    return cli.run()
'''
            
            # Add CLI code before the existing main function
            if 'def main():' in content:
                content = content.replace('def main():', cli_code + '\n\ndef main():')
            else:
                content += cli_code
            
            # Update the main execution block
            if 'if __name__ == "__main__":' in content:
                content = content.replace(
                    'if __name__ == "__main__":\n    main()',
                    '''if __name__ == "__main__":
    # Check if CLI arguments provided
    if len(sys.argv) > 1:
        sys.exit(main_cli())
    else:
        main()'''
                )
            
            # Write updated content
            self.main_file.write_text(content)
            
            print("✅ CLI interface added successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add CLI interface: {e}")
            return False
    
    def test_cli_interface(self) -> bool:
        """Test the CLI interface."""
        print("🧪 Testing CLI interface...")
        
        try:
            import subprocess
            
            # Test help command
            result = subprocess.run([
                sys.executable, 
                str(self.main_file), 
                "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "Multi-Dimensional Vocabulary Projector" in result.stdout:
                print("✅ CLI help command works")
                return True
            else:
                print(f"❌ CLI help test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ CLI test failed: {e}")
            return False
    
    def run_implementation(self) -> bool:
        """Run the complete CLI implementation."""
        print("🚀 Starting CLI implementation (Task 6.1)")
        print("=" * 50)
        
        try:
            # Add CLI interface
            if not self.add_cli_interface():
                return False
            
            # Test CLI interface
            if not self.test_cli_interface():
                return False
            
            print("\n✅ Task 6.1 completed successfully!")
            print("🎯 CLI interface with comprehensive argument parsing added")
            return True
            
        except Exception as e:
            print(f"\n❌ Task 6.1 failed: {e}")
            return False

def main():
    """Main execution."""
    implementation = CLIImplementation()
    success = implementation.run_implementation()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()