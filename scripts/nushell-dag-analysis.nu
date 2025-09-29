#!/usr/bin/env nu

# MSP SSL Chaos Tamer - DAG Analysis with Nushell
# Mathematical dependency analysis using structured data

def main [] {
    print "🔍 DAG Analysis - Mathematical Dependency Validation"
    print ("=" | str repeat 60)
    print ""
    
    # Analyze Python imports
    analyze-python-imports
    
    # Analyze task dependencies
    analyze-task-dependencies
    
    # Validate DAG properties
    validate-dag-properties
}

def analyze-python-imports [] {
    print "🐍 Python Import Analysis:"
    
    let python_files = ls src/**/*.py
    let import_data = $python_files | each { |file|
        let content = open $file.name | lines
        let imports = $content | where ($it | str starts-with 'import ' or ($it | str starts-with 'from '))
        {
            file: $file.name,
            imports: $imports,
            import_count: ($imports | length)
        }
    }
    
    let total_imports = $import_data | get import_count | math sum
    let avg_imports = $import_data | get import_count | math avg
    let max_imports = $import_data | sort-by import_count | last
    
    print $"  Total import statements: ($total_imports)"
    print $"  Average imports per file: ($avg_imports | math round)"
    print $"  Most imports: ($max_imports.file) (($max_imports.import_count) imports)"
    print ""
    
    # Find potential circular dependencies
    print "🔄 Potential Circular Dependencies:"
    let internal_imports = $import_data | each { |file|
        let internal = $file.imports | where ($it | str contains 'msp_ssl_chaos_tamer')
        {
            file: $file.file,
            internal_imports: $internal
        }
    } | where ($it.internal_imports | length) > 0
    
    if ($internal_imports | length) > 0 {
        $internal_imports | each { |item|
            print $"  ($item.file):"
            $item.internal_imports | each { |imp| print $"    ($imp)" }
        }
    } else {
        print "  ✅ No obvious circular dependencies detected"
    }
    print ""
}

def analyze-task-dependencies [] {
    print "📋 Task Dependency Analysis:"
    
    if ("Makefile" | path exists) {
        let makefile_content = open Makefile | lines
        let task_lines = $makefile_content | where ($it | str contains 'task-') | where ($it | str contains ':')
        
        let dependencies = $task_lines | each { |line|
            let parts = $line | str replace '#.*' '' | str trim | split row ':'
            if ($parts | length) >= 2 {
                let task = $parts.0 | str trim
                let deps = $parts.1 | str trim | split row ' ' | where ($it | str length) > 0
                {
                    task: $task,
                    dependencies: $deps,
                    dep_count: ($deps | length)
                }
            }
        } | where ($it | is-not-empty)
        
        if ($dependencies | length) > 0 {
            let total_deps = $dependencies | get dep_count | math sum
            let avg_deps = $dependencies | get dep_count | math avg
            let max_deps = $dependencies | sort-by dep_count | last
            
            print $"  Total task dependencies: ($total_deps)"
            print $"  Average dependencies per task: ($avg_deps | math round)"
            print $"  Most dependencies: ($max_deps.task) (($max_deps.dep_count) deps)"
            print ""
            
            print "  Task Dependency Graph:"
            $dependencies | each { |item|
                if ($item.dep_count) > 0 {
                    print $"    ($item.task) depends on: ($item.dependencies | str join ', ')"
                }
            }
        } else {
            print "  No task dependencies found in Makefile"
        }
    } else {
        print "  No Makefile found"
    }
    print ""
}

def validate-dag-properties [] {
    print "✅ DAG Validation:"
    
    # Check completed tasks
    if (".make-tasks" | path exists) {
        let completed = ls .make-tasks | get name | each { |file| 
            $file | path basename | str replace '.done' '' | str replace 'task-' ''
        }
        
        # Group by phase
        let phases = $completed | each { |task| $task | split row '.' | first } | uniq | sort
        
        print "  Phase Completion Status:"
        for phase in $phases {
            let phase_tasks = $completed | where ($it | str starts-with $phase)
            let phase_count = $phase_tasks | length
            print $"    Phase ($phase): ($phase_count) tasks ✅"
        }
        print ""
        
        # Check for gaps in task sequence
        print "  Task Sequence Validation:"
        let task_numbers = $completed | each { |task| 
            let parts = $task | split row '.'
            {
                phase: ($parts.0 | into int),
                task: ($parts.1 | into int),
                full: $task
            }
        } | sort-by phase task
        
        let phases_with_gaps = $task_numbers | group-by phase | transpose phase tasks | each { |phase_group|
            let tasks = $phase_group.tasks | get task | sort
            let expected = 1..($tasks | length) | each { |i| $i }
            let missing = $expected | where ($it not-in $tasks)
            {
                phase: $phase_group.phase,
                completed: $tasks,
                missing: $missing,
                has_gaps: ($missing | length) > 0
            }
        }
        
        let gaps_found = $phases_with_gaps | where has_gaps | length
        if $gaps_found > 0 {
            print "  ⚠️  Task sequence gaps detected:"
            $phases_with_gaps | where has_gaps | each { |phase|
                print $"    Phase ($phase.phase): Missing tasks ($phase.missing | str join ', ')"
            }
        } else {
            print "  ✅ No task sequence gaps detected"
        }
        
    } else {
        print "  No task completion data found"
    }
    print ""
    
    print "🎯 DAG Analysis Complete!"
}

# Run the analysis
main