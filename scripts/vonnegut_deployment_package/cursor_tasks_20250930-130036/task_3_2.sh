#!/bin/bash
# Individual Task Script: 3.2 - Observatory-Specific Sequence Diagrams
# Generated: 2025-09-30T13:00:36.995743

set -e

echo "🔧 Task 3.2: Observatory-Specific Sequence Diagrams"
echo "Dependencies: 2.2, 2.3"
echo "Priority: 5"
echo "Estimated Duration: 50 minutes"
echo ""

# Check dependencies (basic validation)

if [ ! -f "logs/cursor-parallel-execution/20250930-130036/task-2.2-*.log" ]; then
    echo "❌ Dependency 2.2 not completed - missing log file"
    exit 1
fi

if [ ! -f "logs/cursor-parallel-execution/20250930-130036/task-2.3-*.log" ]; then
    echo "❌ Dependency 2.3 not completed - missing log file"
    exit 1
fi

# Execute task
echo "Executing: cursor --task 'Implement Observatory-specific sequence diagrams (Task 3.2)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md"
cursor --task 'Implement Observatory-specific sequence diagrams (Task 3.2)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md 2>&1 | tee logs/cursor-parallel-execution/20250930-130036/task-3.2-observatory-sequence-diagrams.log

echo "✅ Task 3.2 completed successfully"
