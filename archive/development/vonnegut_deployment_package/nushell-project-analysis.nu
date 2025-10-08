#!/usr/bin/env nu

# MSP SSL Chaos Tamer - Nushell Project Analysis
# Demonstrates mathematical operations on project data

def main [] {
    print "🔍 MSP SSL Chaos Tamer - Mathematical Project Analysis"
    "=" | fill -c "=" -w 60 | print
    print ""
    
    # Project structure analysis
    print "📁 Project Structure:"
    let components = ls src/msp_ssl_chaos_tamer | where type == dir
    $components | select name | each { |row| $"  - ($row.name | path basename)" } | str join "\n" | print
    print ""
    
    # Code statistics
    print "📊 Code Statistics:"
    let python_files = ls src/msp_ssl_chaos_tamer/**/*.py
    let total_files = $python_files | length
    let total_size = $python_files | get size | math sum
    let avg_size = $python_files | get size | math avg
    let largest_file = $python_files | sort-by size | last
    
    print $"  Total Python files: ($total_files)"
    print $"  Total code size: ($total_size)"
    print $"  Average file size: ($avg_size)"
    print $"  Largest file: ($largest_file.name) (($largest_file.size))"
    print ""
    
    # Task completion analysis
    print "✅ Task Completion Status:"
    if (".make-tasks" | path exists) {
        let completed_tasks = ls .make-tasks | get name | each { |file| 
            $file | path basename | str replace '.done' '' | str replace 'task-' ''
        }
        let task_count = $completed_tasks | length
        print $"  Completed tasks: ($task_count)"
        
        # Group by phase
        let phases = $completed_tasks | each { |task| $task | split row '.' | first } | uniq
        for phase in $phases {
            let phase_tasks = $completed_tasks | where ($it | str starts-with $phase)
            print $"  Phase ($phase): ($phase_tasks | length) tasks completed"
        }
    } else {
        print "  No task tracking found"
    }
    print ""
    
    # Configuration files analysis
    print "⚙️  Configuration Files:"
    let config_files = ls | where name =~ '\.(yml|yaml|json|toml|ini)$'
    if ($config_files | length) > 0 {
        $config_files | select name size | each { |row| 
            print $"  ($row.name): ($row.size)"
        }
    } else {
        print "  No configuration files found in root"
    }
    print ""
    
    # Documentation analysis
    print "📚 Documentation:"
    let docs = ls | where name =~ '\.md$' | where name !~ '^[A-Z_]+\.md$'
    let reports = ls | where name =~ '^[A-Z_]+.*\.md$'
    
    print $"  Documentation files: ($docs | length)"
    print $"  Report files: ($reports | length)"
    
    if ($reports | length) > 0 {
        print "  Recent reports:"
        $reports | sort-by modified | last 5 | each { |row|
            print $"    - ($row.name) (($row.modified))"
        }
    }
    print ""
    
    # Dependency analysis (basic)
    print "🔗 Dependencies:"
    if ("requirements.txt" | path exists) {
        let deps = open requirements.txt | lines | where ($it | str trim | str length) > 0 | where not ($it | str starts-with '#')
        print $"  Python dependencies: ($deps | length)"
        print "  Key dependencies:"
        $deps | first 10 | each { |dep| print $"    - ($dep)" }
    }
    
    if ("package.json" | path exists) {
        let pkg = open package.json
        if ($pkg | get dependencies? | is-not-empty) {
            let js_deps = $pkg.dependencies | columns | length
            print $"  JavaScript dependencies: ($js_deps)"
        }
    }
    print ""
    
    print "🎯 Mathematical Analysis Complete!"
}

# Helper function to analyze component dependencies
def analyze-dependencies [] {
    print "🔍 Analyzing Python import dependencies..."
    
    let python_files = ls src/**/*.py
    for file in $python_files {
        let imports = open $file.name | lines | where ($it | str starts-with 'import ' or ($it | str starts-with 'from '))
        if ($imports | length) > 0 {
            print $"($file.name):"
            $imports | each { |imp| print $"  ($imp)" }
        }
    }
}

# Run the analysis
main