#!/usr/bin/env python3
"""
Beast Mode Task List Converter CLI
=================================

Command-line tool to convert legacy task lists to Beast Mode format.

Usage:
    python scripts/convert_to_beast_mode.py <input_file> [output_file]
    python scripts/convert_to_beast_mode.py --scan-specs  # Scan all specs
    python scripts/convert_to_beast_mode.py --help

Author: Beast Mode Framework
Date: 2025-01-16
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.beast_mode.task_dag.beast_mode_converter import BeastModeConverter


def convert_single_file(input_file: str, output_file: str = None, backup: bool = True):
    """Convert a single task file to Beast Mode format"""
    converter = BeastModeConverter()
    
    print(f"Converting {input_file} to Beast Mode format...")
    
    # Create backup if requested
    if backup and not output_file:
        input_path = Path(input_file)
        backup_path = input_path.with_suffix('.backup.md')
        backup_path.write_text(input_path.read_text())
        print(f"Created backup: {backup_path}")
    
    # Perform conversion
    result = converter.convert_task_file(input_file, output_file)
    
    if result.success:
        print(f"✅ Conversion successful!")
        print(f"   Original tasks: {result.original_tasks}")
        print(f"   Converted tasks: {result.converted_tasks}")
        print(f"   Parallel phases: {result.parallel_phases}")
        print(f"   Estimated time reduction: {result.time_reduction_estimate:.1%}")
        
        # Write to original file if no output specified
        if not output_file:
            Path(input_file).write_text(result.beast_mode_content)
            print(f"   Updated: {input_file}")
        else:
            print(f"   Output: {output_file}")
        
        # Print conversion report
        report = result.conversion_report
        if 'parallel_opportunities' in report:
            parallel_info = report['parallel_opportunities']
            print(f"   Max parallel tasks in one phase: {parallel_info['max_parallel_tasks']}")
            print(f"   Total parallel tasks: {parallel_info['total_parallel_tasks']}")
            print(f"   Parallelization ratio: {parallel_info['parallelization_ratio']:.1%}")
    
    else:
        print(f"❌ Conversion failed: {result.error_message}")
        return False
    
    return True


def scan_and_convert_specs(specs_dir: str = ".kiro/specs", dry_run: bool = False):
    """Scan all specs and convert legacy task lists"""
    specs_path = Path(specs_dir)
    
    if not specs_path.exists():
        print(f"❌ Specs directory not found: {specs_dir}")
        return
    
    print(f"Scanning for task files in {specs_dir}...")
    
    task_files = list(specs_path.glob("*/tasks.md"))
    legacy_files = []
    
    # Check which files need conversion
    for task_file in task_files:
        content = task_file.read_text()
        
        # Check if it's already Beast Mode format (has hierarchical numbering)
        if "1.1" in content or "2.1" in content:
            print(f"✅ Already Beast Mode: {task_file}")
        else:
            # Check if it has legacy format (sequential numbering)
            if "- [ ] 1." in content or "- [-] 1." in content or "- [x] 1." in content:
                legacy_files.append(task_file)
                print(f"🔄 Needs conversion: {task_file}")
    
    if not legacy_files:
        print("✅ All task files are already in Beast Mode format!")
        return
    
    print(f"\nFound {len(legacy_files)} files that need conversion:")
    for file in legacy_files:
        print(f"  - {file}")
    
    if dry_run:
        print("\n🔍 Dry run complete. Use --convert to perform actual conversion.")
        return
    
    # Perform conversions
    print(f"\nConverting {len(legacy_files)} files...")
    successful = 0
    
    for task_file in legacy_files:
        print(f"\n📝 Converting {task_file}...")
        if convert_single_file(str(task_file), backup=True):
            successful += 1
    
    print(f"\n🎉 Conversion complete!")
    print(f"   Successfully converted: {successful}/{len(legacy_files)} files")
    
    if successful < len(legacy_files):
        print(f"   Failed conversions: {len(legacy_files) - successful}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert legacy task lists to Beast Mode hierarchical format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file
  python scripts/convert_to_beast_mode.py .kiro/specs/my-spec/tasks.md
  
  # Convert with custom output
  python scripts/convert_to_beast_mode.py input.md output.md
  
  # Scan all specs (dry run)
  python scripts/convert_to_beast_mode.py --scan-specs --dry-run
  
  # Convert all legacy specs
  python scripts/convert_to_beast_mode.py --scan-specs --convert
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='Input task file to convert')
    parser.add_argument('output_file', nargs='?', help='Output file (optional)')
    parser.add_argument('--scan-specs', action='store_true', help='Scan all specs for conversion')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be converted without making changes')
    parser.add_argument('--convert', action='store_true', help='Actually perform conversions when scanning')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup files')
    
    args = parser.parse_args()
    
    if args.scan_specs:
        scan_and_convert_specs(dry_run=args.dry_run and not args.convert)
    elif args.input_file:
        if not Path(args.input_file).exists():
            print(f"❌ Input file not found: {args.input_file}")
            sys.exit(1)
        
        convert_single_file(
            args.input_file, 
            args.output_file, 
            backup=not args.no_backup
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()