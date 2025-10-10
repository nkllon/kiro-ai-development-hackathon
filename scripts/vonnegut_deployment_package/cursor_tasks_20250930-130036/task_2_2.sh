#!/bin/bash
# Individual Task Script: 2.2 - Comprehensive Data Flow Mapping
# Generated: 2025-09-30T13:00:36.995731

set -e

echo "🔧 Task 2.2: Comprehensive Data Flow Mapping"
echo "Dependencies: 1.4, 1.6"
echo "Priority: 8"
echo "Estimated Duration: 55 minutes"
echo ""

# Check dependencies (basic validation)

if [ ! -f "logs/cursor-parallel-execution/20250930-130036/task-1.4-*.log" ]; then
    echo "❌ Dependency 1.4 not completed - missing log file"
    exit 1
fi

if [ ! -f "logs/cursor-parallel-execution/20250930-130036/task-1.6-*.log" ]; then
    echo "❌ Dependency 1.6 not completed - missing log file"
    exit 1
fi

# Execute task
echo "Executing: cursor --task 'Implement comprehensive data flow mapping (Task 2.2)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md"
cursor --task 'Implement comprehensive data flow mapping (Task 2.2)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md 2>&1 | tee logs/cursor-parallel-execution/20250930-130036/task-2.2-data-flow-mapping.log

echo "✅ Task 2.2 completed successfully"
