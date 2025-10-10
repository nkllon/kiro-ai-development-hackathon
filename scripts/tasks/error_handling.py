#!/usr/bin/env python3
"""
Task 7.1: Enhance Error Handling and Diagnostics
================================================

Adds comprehensive error handling and custom exception classes.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

class ErrorHandlingImplementation:
    """Implements enhanced error handling for vocabulary projector."""
    
    def __init__(self):
        self.project_root = project_root
        self.main_file = self.project_root / "src/multi_dimensional_vocabulary_projector.py"
    
    def add_custom_exceptions(self) -> bool:
        """Add custom exception classes."""
        print("🔧 Adding custom exception classes...")
        
        try:
            content = self.main_file.read_text()
            
            # Check if exceptions already exist
            if "VocabularyProjectorError" in content:
                print("✅ Custom exceptions already exist")
                return True
            
            # Add custom exception classes
            exception_code = '''
import logging
import traceback
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vocabulary_projector.log')
    ]
)

class VocabularyProjectorError(Exception):
    """Base exception for vocabulary projector errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
        
        # Log the error
        logger = logging.getLogger(__name__)
        logger.error(f"VocabularyProjectorError: {message}")
        if details:
            logger.error(f"Error details: {details}")
        if cause:
            logger.error(f"Caused by: {cause}")

class ValidationError(VocabularyProjectorError):
    """Raised when vocabulary validation fails."""
    pass

class ProjectionError(VocabularyProjectorError):
    """Raised when projection generation fails."""
    pass

class OutputError(VocabularyProjectorError):
    """Raised when output operations fail."""
    pass

class ConfigurationError(VocabularyProjectorError):
    """Raised when configuration is invalid."""
    pass

class ErrorHandler:
    """Centralized error handling and diagnostics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_file_error(self, file_path: str, operation: str, error: Exception) -> VocabularyProjectorError:
        """Handle file operation errors."""
        details = {
            "file_path": file_path,
            "operation": operation,
            "error_type": type(error).__name__,
            "exists": Path(file_path).exists() if file_path else False
        }
        
        if isinstance(error, FileNotFoundError):
            message = f"File not found during {operation}: {file_path}"
            suggestions = self._get_file_not_found_suggestions(file_path)
            details["suggestions"] = suggestions
        elif isinstance(error, PermissionError):
            message = f"Permission denied during {operation}: {file_path}"
            details["suggestions"] = ["Check file permissions", "Run with appropriate privileges"]
        else:
            message = f"File operation failed during {operation}: {file_path}"
            details["suggestions"] = ["Check file path", "Verify file is not corrupted"]
        
        return OutputError(message, details, error)
    
    def handle_validation_error(self, item: str, issue: str, error: Exception) -> ValidationError:
        """Handle validation errors."""
        details = {
            "item": item,
            "issue": issue,
            "error_type": type(error).__name__
        }
        
        suggestions = []
        if "json" in issue.lower():
            suggestions.extend([
                "Check JSON syntax",
                "Validate JSON structure",
                "Ensure proper encoding"
            ])
        elif "vocabulary" in issue.lower():
            suggestions.extend([
                "Check vocabulary file format",
                "Verify required fields are present",
                "Ensure data types are correct"
            ])
        
        details["suggestions"] = suggestions
        message = f"Validation failed for {item}: {issue}"
        
        return ValidationError(message, details, error)
    
    def handle_projection_error(self, dimension: str, error: Exception) -> ProjectionError:
        """Handle projection generation errors."""
        details = {
            "dimension": dimension,
            "error_type": type(error).__name__,
            "suggestions": [
                f"Check {dimension} projection algorithm",
                "Verify vocabulary data completeness",
                "Check for circular references"
            ]
        }
        
        message = f"Projection generation failed for dimension '{dimension}'"
        return ProjectionError(message, details, error)
    
    def _get_file_not_found_suggestions(self, file_path: str) -> list:
        """Get suggestions for file not found errors."""
        suggestions = []
        
        if "vocabulary" in file_path.lower():
            suggestions.extend([
                "Run vocabulary conversion task (5.1) first",
                "Check if vocabulary file exists in docs/ directory",
                "Verify file path is correct"
            ])
        elif "projection" in file_path.lower():
            suggestions.extend([
                "Ensure output directory exists",
                "Check write permissions",
                "Verify projection was generated successfully"
            ])
        else:
            suggestions.extend([
                "Check file path spelling",
                "Verify file exists",
                "Check current working directory"
            ])
        
        return suggestions
    
    def log_recovery_attempt(self, error: VocabularyProjectorError, recovery_action: str):
        """Log recovery attempt."""
        self.logger.info(f"Attempting recovery for {type(error).__name__}: {recovery_action}")
    
    def log_recovery_success(self, error: VocabularyProjectorError, recovery_action: str):
        """Log successful recovery."""
        self.logger.info(f"Recovery successful for {type(error).__name__}: {recovery_action}")
    
    def log_recovery_failure(self, error: VocabularyProjectorError, recovery_action: str):
        """Log failed recovery."""
        self.logger.error(f"Recovery failed for {type(error).__name__}: {recovery_action}")

# Global error handler instance
error_handler = ErrorHandler()
'''
            
            # Add exception code at the beginning after imports
            import_end = content.find('\n\n@dataclass')
            if import_end == -1:
                import_end = content.find('\n\nclass')
            if import_end == -1:
                import_end = content.find('\n\ndef')
            
            if import_end != -1:
                content = content[:import_end] + exception_code + content[import_end:]
            else:
                # Add after imports
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        insert_pos = i + 1
                
                lines.insert(insert_pos, exception_code)
                content = '\n'.join(lines)
            
            self.main_file.write_text(content)
            print("✅ Custom exception classes added")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add custom exceptions: {e}")
            return False
    
    def enhance_error_handling_in_methods(self) -> bool:
        """Enhance error handling in existing methods."""
        print("🔧 Enhancing error handling in existing methods...")
        
        try:
            content = self.main_file.read_text()
            
            # Enhance load_vocabulary method
            old_load_method = '''def load_vocabulary(self) -> None:
        """Load vocabulary from JSON file."""
        if not self.vocabulary_file.exists():
            print(f"❌ Vocabulary file not found: {self.vocabulary_file}")
            return
            
        with open(self.vocabulary_file, 'r') as f:
            data = json.load(f)'''
            
            new_load_method = '''def load_vocabulary(self) -> None:
        """Load vocabulary from JSON file with enhanced error handling."""
        try:
            if not self.vocabulary_file.exists():
                raise error_handler.handle_file_error(
                    str(self.vocabulary_file), 
                    "vocabulary loading", 
                    FileNotFoundError(f"Vocabulary file not found: {self.vocabulary_file}")
                )
            
            with open(self.vocabulary_file, 'r') as f:
                data = json.load(f)
                
        except json.JSONDecodeError as e:
            raise error_handler.handle_validation_error(
                str(self.vocabulary_file),
                f"Invalid JSON format: {e}",
                e
            )
        except Exception as e:
            if isinstance(e, VocabularyProjectorError):
                raise
            raise error_handler.handle_file_error(
                str(self.vocabulary_file),
                "vocabulary loading",
                e
            )'''
            
            if old_load_method in content:
                content = content.replace(old_load_method, new_load_method)
                print("✅ Enhanced load_vocabulary method")
            
            # Enhance generate_all_projections method
            old_generate = '''def generate_all_projections(self) -> None:
        """Generate all vocabulary projections."""
        print("🔍 Generating multi-dimensional vocabulary projections...")
        
        projections = {'''
            
            new_generate = '''def generate_all_projections(self) -> None:
        """Generate all vocabulary projections with enhanced error handling."""
        print("🔍 Generating multi-dimensional vocabulary projections...")
        
        failed_projections = []
        
        try:
            projections = {'''
            
            if old_generate in content:
                content = content.replace(old_generate, new_generate)
                
                # Add error handling to the projection generation loop
                old_loop = '''for dimension, content in projections.items():
            filename = f"vocabulary_{dimension}.md"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"✅ Generated: {filepath}")'''
                
                new_loop = '''for dimension, projection_content in projections.items():
            try:
                filename = f"vocabulary_{dimension}.md"
                filepath = self.output_dir / filename
                
                # Ensure output directory exists
                self.output_dir.mkdir(parents=True, exist_ok=True)
                
                with open(filepath, 'w') as f:
                    f.write(projection_content)
                
                print(f"✅ Generated: {filepath}")
                
            except Exception as e:
                error = error_handler.handle_projection_error(dimension, e)
                failed_projections.append((dimension, error))
                print(f"❌ Failed to generate {dimension}: {error.message}")
                
                # Log suggestions
                if error.details.get("suggestions"):
                    for suggestion in error.details["suggestions"]:
                        print(f"   💡 {suggestion}")
        
        # Report any failures
        if failed_projections:
            print(f"\\n⚠️  {len(failed_projections)} projections failed:")
            for dimension, error in failed_projections:
                print(f"   • {dimension}: {error.message}")
        
        except Exception as e:
            raise error_handler.handle_projection_error("all_projections", e)'''
                
                if old_loop in content:
                    content = content.replace(old_loop, new_loop)
                    print("✅ Enhanced projection generation loop")
            
            self.main_file.write_text(content)
            print("✅ Enhanced error handling in existing methods")
            return True
            
        except Exception as e:
            print(f"❌ Failed to enhance error handling: {e}")
            return False
    
    def add_diagnostic_methods(self) -> bool:
        """Add diagnostic methods to the main class."""
        print("🔧 Adding diagnostic methods...")
        
        try:
            content = self.main_file.read_text()
            
            # Check if diagnostics already exist
            if "run_diagnostics" in content:
                print("✅ Diagnostic methods already exist")
                return True
            
            # Add diagnostic methods before the main function
            diagnostic_code = '''
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics."""
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "vocabulary_file": {
                "path": str(self.vocabulary_file),
                "exists": self.vocabulary_file.exists(),
                "size": self.vocabulary_file.stat().st_size if self.vocabulary_file.exists() else 0,
                "readable": os.access(self.vocabulary_file, os.R_OK) if self.vocabulary_file.exists() else False
            },
            "output_directory": {
                "path": str(self.output_dir),
                "exists": self.output_dir.exists(),
                "writable": os.access(self.output_dir, os.W_OK) if self.output_dir.exists() else False
            },
            "vocabulary_data": {
                "loaded": len(self.vocabulary) > 0,
                "term_count": len(self.vocabulary),
                "categories": list(set(term.category for term in self.vocabulary.values())) if self.vocabulary else []
            },
            "system": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd()
            }
        }
        
        return diagnostics
    
    def print_diagnostics(self):
        """Print diagnostic information."""
        diagnostics = self.run_diagnostics()
        
        print("🔍 Vocabulary Projector Diagnostics")
        print("=" * 40)
        
        # Vocabulary file info
        vocab_info = diagnostics["vocabulary_file"]
        print(f"📄 Vocabulary File:")
        print(f"   Path: {vocab_info['path']}")
        print(f"   Exists: {'✅' if vocab_info['exists'] else '❌'}")
        if vocab_info['exists']:
            print(f"   Size: {vocab_info['size']} bytes")
            print(f"   Readable: {'✅' if vocab_info['readable'] else '❌'}")
        
        # Output directory info
        output_info = diagnostics["output_directory"]
        print(f"\\n📁 Output Directory:")
        print(f"   Path: {output_info['path']}")
        print(f"   Exists: {'✅' if output_info['exists'] else '❌'}")
        if output_info['exists']:
            print(f"   Writable: {'✅' if output_info['writable'] else '❌'}")
        
        # Vocabulary data info
        vocab_data = diagnostics["vocabulary_data"]
        print(f"\\n📚 Vocabulary Data:")
        print(f"   Loaded: {'✅' if vocab_data['loaded'] else '❌'}")
        print(f"   Terms: {vocab_data['term_count']}")
        if vocab_data['categories']:
            print(f"   Categories: {', '.join(vocab_data['categories'])}")
        
        # System info
        system_info = diagnostics["system"]
        print(f"\\n🖥️  System:")
        print(f"   Python: {system_info['python_version'].split()[0]}")
        print(f"   Platform: {system_info['platform']}")
        print(f"   Working Dir: {system_info['working_directory']}")
    
    def validate_system_health(self) -> bool:
        """Validate system health and readiness."""
        print("🏥 Checking system health...")
        
        issues = []
        
        try:
            # Check vocabulary file
            if not self.vocabulary_file.exists():
                issues.append(f"Vocabulary file not found: {self.vocabulary_file}")
            elif not os.access(self.vocabulary_file, os.R_OK):
                issues.append(f"Cannot read vocabulary file: {self.vocabulary_file}")
            
            # Check output directory
            if not self.output_dir.exists():
                try:
                    self.output_dir.mkdir(parents=True, exist_ok=True)
                    print("✅ Created output directory")
                except Exception as e:
                    issues.append(f"Cannot create output directory: {e}")
            elif not os.access(self.output_dir, os.W_OK):
                issues.append(f"Cannot write to output directory: {self.output_dir}")
            
            # Check vocabulary loading
            if not self.vocabulary:
                try:
                    self.load_vocabulary()
                    if not self.vocabulary:
                        issues.append("No vocabulary terms loaded")
                except Exception as e:
                    issues.append(f"Cannot load vocabulary: {e}")
            
            if issues:
                print("❌ System health check failed:")
                for issue in issues:
                    print(f"   • {issue}")
                return False
            else:
                print("✅ System health check passed")
                return True
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
'''
            
            # Add imports for diagnostics
            if "import os" not in content:
                content = content.replace("import json", "import json\nimport os")
            if "from datetime import datetime" not in content:
                content = content.replace("import os", "import os\nfrom datetime import datetime")
            
            # Find insertion point (before main function)
            main_pos = content.find('\ndef main():')
            if main_pos != -1:
                content = content[:main_pos] + diagnostic_code + content[main_pos:]
            else:
                # Add at end of class
                class_end = content.rfind('        return markdown')
                if class_end != -1:
                    # Find end of method
                    next_method = content.find('\n    def ', class_end)
                    if next_method == -1:
                        next_method = content.find('\ndef ', class_end)
                    if next_method != -1:
                        content = content[:next_method] + diagnostic_code + content[next_method:]
                    else:
                        content += diagnostic_code
            
            self.main_file.write_text(content)
            print("✅ Diagnostic methods added")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add diagnostic methods: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test the error handling implementation."""
        print("🧪 Testing error handling...")
        
        try:
            # Test import
            import multi_dimensional_vocabulary_projector as mvp
            
            # Check if custom exceptions exist
            if hasattr(mvp, 'VocabularyProjectorError'):
                print("✅ Custom exceptions imported successfully")
            else:
                print("❌ Custom exceptions not found")
                return False
            
            # Check if error handler exists
            if hasattr(mvp, 'error_handler'):
                print("✅ Error handler available")
            else:
                print("❌ Error handler not found")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
    
    def run_implementation(self) -> bool:
        """Run the complete error handling implementation."""
        print("🚀 Starting error handling implementation (Task 7.1)")
        print("=" * 50)
        
        try:
            # Add custom exceptions
            if not self.add_custom_exceptions():
                return False
            
            # Enhance existing methods
            if not self.enhance_error_handling_in_methods():
                return False
            
            # Add diagnostic methods
            if not self.add_diagnostic_methods():
                return False
            
            # Test implementation
            if not self.test_error_handling():
                return False
            
            print("\\n✅ Task 7.1 completed successfully!")
            print("🎯 Enhanced error handling and diagnostics implemented")
            return True
            
        except Exception as e:
            print(f"\\n❌ Task 7.1 failed: {e}")
            return False

def main():
    """Main execution."""
    implementation = ErrorHandlingImplementation()
    success = implementation.run_implementation()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()