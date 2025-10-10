#!/usr/bin/env python3
"""
New Prompt Identifier - Find and Process Latest Prompt Files

This script identifies the most recently created or modified prompt files
in the staging directory and processes them systematically.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rm_ddd.core.unified_reflective_module import ReflectiveModule


class NewPromptIdentifier(ReflectiveModule):
    """Identifies and processes new prompt files systematically."""
    
    def __init__(self):
        super().__init__()
        self.base_dir = Path.cwd()
        self.staging_dir = self.base_dir / "prompts" / "staging"
    
    def get_module_info(self) -> dict:
        """Get module information."""
        return {
            'module_name': 'NewPromptIdentifier',
            'version': '1.0.0',
            'description': 'Identifies and processes new prompt files systematically'
        }
    
    def get_capabilities(self) -> list:
        """Get module capabilities."""
        return ['file_analysis', 'priority_scoring', 'recommendation_engine']
    
    async def get_health_status(self) -> dict:
        """Get health status."""
        return {
            'status': 'healthy',
            'staging_dir_exists': self.staging_dir.exists(),
            'staging_files_count': len(list(self.staging_dir.glob('*.md'))) if self.staging_dir.exists() else 0
        }
    
    async def graceful_degradation(self, error: Exception = None) -> dict:
        """Handle graceful degradation."""
        return {
            'success': True,
            'degraded_capabilities': [],
            'remaining_capabilities': self.get_capabilities(),
            'error_message': str(error) if error else None
        }
        
    def get_file_stats(self, file_path: Path) -> Tuple[float, float, int]:
        """Get file modification time, creation time, and size."""
        stat = file_path.stat()
        return stat.st_mtime, stat.st_ctime, stat.st_size
    
    def identify_newest_files(self, limit: int = 5) -> List[Tuple[Path, dict]]:
        """Identify the newest files in staging directory."""
        if not self.staging_dir.exists():
            return []
        
        files_with_stats = []
        
        for file_path in self.staging_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.md', '.txt']:
                mtime, ctime, size = self.get_file_stats(file_path)
                
                files_with_stats.append((file_path, {
                    'mtime': mtime,
                    'ctime': ctime,
                    'size': size,
                    'mtime_str': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'ctime_str': datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')
                }))
        
        # Sort by modification time (newest first)
        files_with_stats.sort(key=lambda x: x[1]['mtime'], reverse=True)
        
        return files_with_stats[:limit]
    
    def identify_priority_files(self) -> List[Tuple[Path, str]]:
        """Identify high-priority files based on naming patterns."""
        if not self.staging_dir.exists():
            return []
        
        priority_patterns = [
            ('EXECUTION', 'execution'),
            ('QUICK-START', 'quick_start'),
            ('PARALLEL', 'parallel'),
            ('OPTIMIZATION', 'optimization'),
            ('COMPLETE', 'completion'),
            ('master-', 'master'),
            ('phase-1', 'phase_1'),
            ('constellation', 'constellation')
        ]
        
        priority_files = []
        
        for file_path in self.staging_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.md', '.txt']:
                filename = file_path.name.upper()
                
                for pattern, category in priority_patterns:
                    if pattern in filename:
                        priority_files.append((file_path, category))
                        break
        
        return priority_files
    
    def analyze_file_content(self, file_path: Path) -> dict:
        """Analyze file content to determine task type and urgency."""
        try:
            content = file_path.read_text(encoding='utf-8')
            content_lower = content.lower()
            
            analysis = {
                'file': file_path.name,
                'size': len(content),
                'lines': len(content.split('\n')),
                'task_type': 'unknown',
                'urgency': 'normal',
                'keywords': [],
                'has_instructions': False,
                'has_code': False
            }
            
            # Determine task type
            if 'constellation' in content_lower and 'elaboration' in content_lower:
                analysis['task_type'] = 'constellation_elaboration'
            elif 'cms' in content_lower and ('architecture' in content_lower or 'integration' in content_lower):
                analysis['task_type'] = 'cms_integration'
            elif 'dag' in content_lower and 'orchestration' in content_lower:
                analysis['task_type'] = 'dag_orchestration'
            elif 'parallel' in content_lower and 'execution' in content_lower:
                analysis['task_type'] = 'parallel_execution'
            elif 'optimization' in content_lower:
                analysis['task_type'] = 'optimization'
            elif 'quick' in content_lower and 'start' in content_lower:
                analysis['task_type'] = 'quick_start'
            
            # Determine urgency
            urgency_keywords = ['urgent', 'critical', 'immediate', 'asap', 'priority']
            completion_keywords = ['complete', 'finished', 'done', 'ready']
            
            if any(keyword in content_lower for keyword in urgency_keywords):
                analysis['urgency'] = 'high'
            elif any(keyword in content_lower for keyword in completion_keywords):
                analysis['urgency'] = 'low'  # Already complete
            
            # Check for instructions
            instruction_patterns = ['usage:', 'how to', 'steps:', 'execute:', 'run:']
            analysis['has_instructions'] = any(pattern in content_lower for pattern in instruction_patterns)
            
            # Check for code
            code_patterns = ['```', 'python', 'bash', 'scripts/', 'def ', 'class ']
            analysis['has_code'] = any(pattern in content_lower for pattern in code_patterns)
            
            # Extract keywords
            important_keywords = [
                'execution', 'parallel', 'constellation', 'cms', 'dag', 
                'optimization', 'complete', 'ready', 'system', 'architecture'
            ]
            
            for keyword in important_keywords:
                if keyword in content_lower:
                    analysis['keywords'].append(keyword)
            
            return analysis
            
        except Exception as e:
            return {
                'file': file_path.name,
                'error': str(e),
                'task_type': 'error',
                'urgency': 'unknown'
            }
    
    def recommend_processing_order(self) -> List[Tuple[Path, dict]]:
        """Recommend the order for processing files based on analysis."""
        newest_files = self.identify_newest_files(10)
        priority_files = self.identify_priority_files()
        
        # Create a comprehensive analysis
        file_analyses = []
        
        for file_path, stats in newest_files:
            content_analysis = self.analyze_file_content(file_path)
            
            # Calculate priority score
            priority_score = 0
            
            # Recency bonus (newer files get higher score)
            hours_old = (time.time() - stats['mtime']) / 3600
            if hours_old < 1:
                priority_score += 10
            elif hours_old < 24:
                priority_score += 5
            elif hours_old < 168:  # 1 week
                priority_score += 2
            
            # Task type bonus
            task_type_scores = {
                'quick_start': 15,
                'execution': 12,
                'parallel_execution': 10,
                'optimization': 8,
                'constellation_elaboration': 6,
                'cms_integration': 5,
                'dag_orchestration': 4
            }
            priority_score += task_type_scores.get(content_analysis['task_type'], 1)
            
            # Urgency bonus
            urgency_scores = {'high': 20, 'normal': 5, 'low': 1}
            priority_score += urgency_scores.get(content_analysis['urgency'], 1)
            
            # Instructions bonus (actionable files)
            if content_analysis.get('has_instructions', False):
                priority_score += 5
            
            # Size penalty (very large files are harder to process)
            if content_analysis.get('size', 0) > 50000:  # 50KB
                priority_score -= 3
            
            combined_analysis = {
                **stats,
                **content_analysis,
                'priority_score': priority_score
            }
            
            file_analyses.append((file_path, combined_analysis))
        
        # Sort by priority score (highest first)
        file_analyses.sort(key=lambda x: x[1]['priority_score'], reverse=True)
        
        return file_analyses
    
    def display_recommendations(self, recommendations: List[Tuple[Path, dict]]):
        """Display processing recommendations to the user."""
        print("🔍 Prompt File Analysis and Recommendations")
        print("=" * 60)
        
        if not recommendations:
            print("ℹ️  No prompt files found in staging directory")
            return
        
        print(f"Found {len(recommendations)} prompt files in staging directory\n")
        
        for i, (file_path, analysis) in enumerate(recommendations[:5], 1):
            print(f"#{i} {file_path.name}")
            print(f"   📊 Priority Score: {analysis['priority_score']}")
            print(f"   📝 Task Type: {analysis['task_type']}")
            print(f"   ⚡ Urgency: {analysis['urgency']}")
            print(f"   📅 Modified: {analysis['mtime_str']}")
            print(f"   📏 Size: {analysis['size']:,} bytes ({analysis['lines']} lines)")
            
            if analysis.get('keywords'):
                print(f"   🏷️  Keywords: {', '.join(analysis['keywords'])}")
            
            if analysis.get('has_instructions'):
                print(f"   📋 Has Instructions: Yes")
            
            if analysis.get('has_code'):
                print(f"   💻 Contains Code: Yes")
            
            print()
        
        if len(recommendations) > 5:
            print(f"... and {len(recommendations) - 5} more files")
    
    def get_top_recommendation(self) -> Optional[Path]:
        """Get the top recommended file for processing."""
        recommendations = self.recommend_processing_order()
        
        if recommendations:
            return recommendations[0][0]
        
        return None


def main():
    """Main entry point."""
    identifier = NewPromptIdentifier()
    
    print("🚀 New Prompt File Identifier")
    print("=" * 40)
    
    # Get recommendations
    recommendations = identifier.recommend_processing_order()
    
    # Display recommendations
    identifier.display_recommendations(recommendations)
    
    # Get top recommendation
    top_file = identifier.get_top_recommendation()
    
    if top_file:
        print(f"🎯 Top Recommendation: {top_file.name}")
        print(f"📁 Full Path: {top_file}")
        
        # Ask user if they want to process it
        response = input("\n❓ Process this file? (y/n): ").strip().lower()
        
        if response in ['y', 'yes']:
            print(f"\n🔄 Processing {top_file.name}...")
            
            # Import and use the prompt processor
            from prompt_processor import PromptProcessor
            
            processor = PromptProcessor()
            completed_file = processor.process_file(top_file)
            
            print(f"✅ Completed: {completed_file.name}")
        else:
            print("ℹ️  Processing cancelled by user")
    else:
        print("ℹ️  No files found to process")


if __name__ == "__main__":
    main()