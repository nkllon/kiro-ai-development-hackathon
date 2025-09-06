#!/usr/bin/env python3
"""
Script to run implementation migration to consolidated specs
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run migration
try:
    from spec_reconciliation.migration import ImplementationMigrator
    
    print("Starting implementation migration to consolidated specs...")
    migrator = ImplementationMigrator('.')
    result = migrator.execute_implementation_migration()
    
    print("\n" + "="*60)
    print("MIGRATION RESULTS")
    print("="*60)
    
    if result['success']:
        print("✅ Migration completed successfully!")
    else:
        print(f"❌ Migration failed: {result.get('error', 'Unknown error')}")
    
    print(f"\n📊 Summary:")
    print(f"   Migrations performed: {len(result['migrations_performed'])}")
    print(f"   Compatibility layers created: {len(result['compatibility_layers_created'])}")
    print(f"   Documentation updates: {len(result['documentation_updates'])}")
    
    if result['migrations_performed']:
        print(f"\n📝 Code Migrations:")
        for migration in result['migrations_performed'][:5]:  # Show first 5
            print(f"   - {migration['file']}: {migration['type']}")
            if migration.get('changes'):
                for change in migration['changes'][:2]:  # Show first 2 changes
                    print(f"     • {change}")
    
    if result['compatibility_layers_created']:
        print(f"\n🔄 Compatibility Layers:")
        for layer in result['compatibility_layers_created']:
            print(f"   - {layer['consolidated_spec']}")
            print(f"     File: {layer['compatibility_file']}")
            print(f"     Supports: {', '.join(layer['original_specs_supported'])}")
    
    if result['documentation_updates']:
        print(f"\n📚 Documentation Updates:")
        for doc_update in result['documentation_updates']:
            print(f"   - {doc_update['file']}: {doc_update['type']}")
    
    print(f"\n🎯 Migration ID: {result['migration_id']}")
    print(f"⏰ Started: {result['started_at']}")
    if 'completed_at' in result:
        print(f"⏰ Completed: {result['completed_at']}")
    
except Exception as e:
    print(f"❌ Error running migration: {e}")
    import traceback
    traceback.print_exc()