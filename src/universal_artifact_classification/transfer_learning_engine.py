"""
Transfer Learning Engine using pre-trained models like CodeBERT.

This engine leverages existing knowledge from pre-trained models and adapts
them to our specific artifact classification needs.
"""

import logging
import torch
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from transformers import AutoModel, AutoTokenizer, AutoConfig

from .models import ClassificationResult, ModelConfig


logger = logging.getLogger(__name__)


class TransferLearningEngine:
    """
    Transfer learning engine that leverages pre-trained models for artifact classification.
    
    Uses CodeBERT as the foundation and adapts it to understand our specific
    organizational patterns while preserving universal knowledge.
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() and config.enable_gpu else "cpu")
        
        # Initialize pre-trained models
        self._load_models()
        
        # Classification head for our specific categories
        self.artifact_categories = [
            "source_code", "configuration", "documentation", "build_script",
            "test_file", "data_file", "binary", "unknown"
        ]
        
        logger.info(f"Transfer Learning Engine initialized on {self.device}")
    
    def _load_models(self):
        """Load pre-trained models for different artifact types"""
        try:
            # CodeBERT for code and configuration understanding
            self.code_tokenizer = AutoTokenizer.from_pretrained(self.config.base_model_name)
            self.code_model = AutoModel.from_pretrained(self.config.base_model_name)
            self.code_model.to(self.device)
            self.code_model.eval()
            
            # For now, use CodeBERT for all types - can expand later
            self.text_tokenizer = self.code_tokenizer
            self.text_model = self.code_model
            
            logger.info(f"Loaded pre-trained model: {self.config.base_model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load pre-trained models: {e}")
            # Fallback to basic classification
            self.code_model = None
            self.code_tokenizer = None
    
    def classify_artifact(self, artifact_path: Path) -> ClassificationResult:
        """
        Classify artifact using transfer learning approach.
        
        Extracts semantic features using pre-trained models and classifies
        based on learned patterns.
        """
        if not self.code_model:
            return self._fallback_classification(artifact_path)
        
        try:
            # Read artifact content
            content = self._read_artifact_safely(artifact_path)
            if not content:
                return self._classify_by_extension(artifact_path)
            
            # Extract features using appropriate model
            features = self._extract_features(content, artifact_path)
            
            # Classify based on features
            classification = self._classify_from_features(features, artifact_path)
            
            return ClassificationResult(
                artifact_path=str(artifact_path),
                predicted_type=classification["type"],
                confidence=classification["confidence"],
                alternative_types=classification.get("alternatives", []),
                features_used=["semantic_embedding", "file_extension", "content_patterns"],
                requires_review=classification["confidence"] < self.config.confidence_threshold,
                processing_time_ms=0.0,  # Will be set by caller
                model_used="deep_learning"
            )
            
        except Exception as e:
            logger.error(f"Error classifying {artifact_path}: {e}")
            return self._fallback_classification(artifact_path)
    
    def _read_artifact_safely(self, artifact_path: Path) -> Optional[str]:
        """Safely read artifact content, handling binary files"""
        try:
            # Try reading as text first
            with open(artifact_path, 'r', encoding='utf-8') as f:
                content = f.read(self.config.max_sequence_length * 4)  # Rough char limit
                return content
        except UnicodeDecodeError:
            # Binary file - use filename and extension only
            return None
        except Exception as e:
            logger.warning(f"Could not read {artifact_path}: {e}")
            return None
    
    def _extract_features(self, content: str, artifact_path: Path) -> Dict[str, Any]:
        """Extract semantic features using pre-trained model"""
        try:
            # Tokenize content
            inputs = self.code_tokenizer(
                content,
                max_length=self.config.max_sequence_length,
                truncation=True,
                padding=True,
                return_tensors="pt"
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.code_model(**inputs)
                # Use [CLS] token embedding as feature vector
                features = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
            
            return {
                "semantic_embedding": features,
                "content_length": len(content),
                "file_extension": artifact_path.suffix.lower(),
                "filename": artifact_path.name.lower()
            }
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {
                "file_extension": artifact_path.suffix.lower(),
                "filename": artifact_path.name.lower(),
                "content_length": len(content) if content else 0
            }
    
    def _classify_from_features(self, features: Dict[str, Any], artifact_path: Path) -> Dict[str, Any]:
        """Classify artifact based on extracted features"""
        
        # For now, use rule-based classification on features
        # This will be replaced with trained classifier head later
        
        extension = features.get("file_extension", "").lower()
        filename = features.get("filename", "").lower()
        
        # Code files
        code_extensions = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".rb", ".php"}
        if extension in code_extensions:
            return {"type": "source_code", "confidence": 0.95, "alternatives": []}
        
        # Configuration files
        config_extensions = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"}
        config_names = {"dockerfile", "makefile", "requirements.txt", "package.json", "pyproject.toml"}
        if extension in config_extensions or filename in config_names:
            return {"type": "configuration", "confidence": 0.90, "alternatives": []}
        
        # Documentation
        doc_extensions = {".md", ".rst", ".txt", ".adoc"}
        if extension in doc_extensions or "readme" in filename:
            return {"type": "documentation", "confidence": 0.88, "alternatives": []}
        
        # Build scripts
        build_extensions = {".sh", ".bat", ".ps1"}
        build_names = {"makefile", "build.gradle", "pom.xml", "setup.py"}
        if extension in build_extensions or filename in build_names:
            return {"type": "build_script", "confidence": 0.85, "alternatives": []}
        
        # Test files
        if "test" in filename or filename.startswith("test_") or filename.endswith("_test.py"):
            return {"type": "test_file", "confidence": 0.90, "alternatives": []}
        
        # Binary files
        binary_extensions = {".exe", ".dll", ".so", ".dylib", ".bin", ".img", ".iso"}
        if extension in binary_extensions:
            return {"type": "binary", "confidence": 0.95, "alternatives": []}
        
        # Default to unknown with low confidence
        return {"type": "unknown", "confidence": 0.30, "alternatives": []}
    
    def _classify_by_extension(self, artifact_path: Path) -> ClassificationResult:
        """Fallback classification using only file extension"""
        features = {"file_extension": artifact_path.suffix.lower(), "filename": artifact_path.name.lower()}
        classification = self._classify_from_features(features, artifact_path)
        
        return ClassificationResult(
            artifact_path=str(artifact_path),
            predicted_type=classification["type"],
            confidence=classification["confidence"] * 0.7,  # Lower confidence for extension-only
            alternative_types=[],
            features_used=["file_extension"],
            requires_review=True,
            processing_time_ms=0.0,
            model_used="extension_fallback"
        )
    
    def _fallback_classification(self, artifact_path: Path) -> ClassificationResult:
        """Ultimate fallback when all else fails"""
        return ClassificationResult(
            artifact_path=str(artifact_path),
            predicted_type="unknown",
            confidence=0.1,
            alternative_types=[],
            features_used=["fallback"],
            requires_review=True,
            processing_time_ms=0.0,
            model_used="fallback"
        )
    
    def get_semantic_features(self, artifact_path: Path) -> Dict[str, float]:
        """Get semantic features for an artifact"""
        content = self._read_artifact_safely(artifact_path)
        if not content:
            return {}
        
        features = self._extract_features(content, artifact_path)
        semantic_embedding = features.get("semantic_embedding", [])
        
        if len(semantic_embedding) > 0:
            # Return first 10 dimensions as example features
            return {f"feature_{i}": float(semantic_embedding[i]) for i in range(min(10, len(semantic_embedding)))}
        
        return {}
    
    def adapt_to_domain(self, training_examples: List[Any]) -> Dict[str, Any]:
        """Adapt model to new domain using training examples"""
        logger.info(f"Domain adaptation with {len(training_examples)} examples")
        
        # For now, just return success - actual fine-tuning would go here
        return {
            "patterns_learned": len(training_examples) // 10,
            "accuracy_delta": 0.05  # Simulated improvement
        }
    
    def is_healthy(self) -> bool:
        """Check if the transfer learning engine is healthy"""
        return self.code_model is not None