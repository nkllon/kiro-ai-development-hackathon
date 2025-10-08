#!/usr/bin/env nu

# MSP SSL Chaos Tamer - OSS License Analysis
# "Give us your tired, your poor, your huddled masses of OSS licenses yearning to be free"
# Mathematical analysis of license compatibility and compliance

def main [] {
    print "📜 OSS License Analysis - Liberation Through Mathematics"
    print (seq 1 70 | each { "=" } | str join)
    print ""
    
    # Analyze Python package licenses
    analyze-python-licenses
    
    # Analyze JavaScript package licenses  
    analyze-js-licenses
    
    # Scan for license files in dependencies
    scan-license-files
    
    # Check for license compatibility issues
    check-license-compatibility
    
    # Generate license compliance report
    generate-compliance-report
}

def analyze-python-licenses [] {
    print "🐍 Python Package License Analysis:"
    
    if ("requirements.txt" | path exists) {
        let requirements = open requirements.txt | lines | where ($it | str trim | str length) > 0 | where not ($it | str starts-with '#')
        let package_count = $requirements | length
        
        print $"  Total Python packages: ($package_count)"
        print "  Attempting to identify licenses..."
        
        # Common license patterns in package names/versions
        let license_hints = $requirements | each { |req|
            let pkg_name = $req | str replace '>=.*' '' | str replace '==.*' '' | str replace '>.*' '' | str replace '<.*' '' | str replace '~=.*' ''
            {
                package: $pkg_name,
                requirement: $req,
                likely_license: (guess-license-from-name $pkg_name)
            }
        }
        
        # Group by likely license
        let license_groups = $license_hints | group-by likely_license | transpose license packages
        
        print "  License Distribution (estimated):"
        $license_groups | each { |group|
            let count = $group.packages | length
            print $"    ($group.license): ($count) packages"
        }
        
        print ""
        print "  High-Risk Packages (potential license issues):"
        let risky = $license_hints | where likely_license =~ "(GPL|AGPL|Unknown)"
        if ($risky | length) > 0 {
            $risky | each { |pkg|
                print $"    ⚠️  ($pkg.package) - ($pkg.likely_license)"
            }
        } else {
            print "    ✅ No obvious high-risk licenses detected"
        }
    } else {
        print "  No requirements.txt found"
    }
    print ""
}

def analyze-js-licenses [] {
    print "📦 JavaScript Package License Analysis:"
    
    if ("package.json" | path exists) {
        let pkg_json = open package.json
        
        if ($pkg_json | get dependencies? | is-not-empty) {
            let deps = $pkg_json.dependencies | columns
            let dep_count = $deps | length
            
            print $"  Total JavaScript packages: ($dep_count)"
            print "  Dependencies:"
            $deps | each { |dep|
                let version = $pkg_json.dependencies | get $dep
                print $"    ($dep): ($version)"
            }
            
            # Check if package-lock.json exists for more detailed analysis
            if ("package-lock.json" | path exists) {
                print "  📋 package-lock.json found - detailed analysis possible"
                # Note: Full npm license analysis would require npm ls --json
            }
        } else {
            print "  No JavaScript dependencies found"
        }
        
        if ("node_modules" | path exists) {
            let node_modules_size = ls node_modules | get size | math sum
            print $"  node_modules size: ($node_modules_size)"
            
            # Look for LICENSE files in node_modules
            let license_files = ls node_modules/**/LICENSE* | length
            print $"  License files in node_modules: ($license_files)"
        }
    } else {
        print "  No package.json found"
    }
    print ""
}

def scan-license-files [] {
    print "📄 License File Discovery:"
    
    # Find all license-related files
    let license_patterns = ["LICENSE*", "COPYING*", "COPYRIGHT*", "NOTICE*", "LEGAL*"]
    mut license_files = []
    
    for pattern in $license_patterns {
        let found = ls $pattern | default []
        $license_files = ($license_files | append $found)
    }
    
    if ($license_files | length) > 0 {
        print "  Found license files:"
        $license_files | each { |file|
            let size = $file.size
            let content_preview = open $file.name | lines | first 3 | str join " " | str substring 0..100
            print $"    📜 ($file.name) (($size)) - ($content_preview)..."
        }
    } else {
        print "  ⚠️  No license files found in project root"
    }
    print ""
    
    # Check for license headers in source files
    print "  License Headers in Source Files:"
    let source_files = ls src/**/*.py | first 10  # Sample first 10 files
    let files_with_headers = $source_files | each { |file|
        let first_lines = open $file.name | lines | first 10 | str join "\n"
        let has_license = $first_lines | str contains -i "license" or ($first_lines | str contains -i "copyright")
        {
            file: $file.name,
            has_license_header: $has_license
        }
    }
    
    let header_count = $files_with_headers | where has_license_header | length
    let total_sampled = $files_with_headers | length
    print $"    Files with license headers: ($header_count)/($total_sampled) sampled"
    
    if $header_count == 0 {
        print "    ⚠️  No license headers found in source files"
    }
    print ""
}

def check-license-compatibility [] {
    print "⚖️  License Compatibility Analysis:"
    
    # Define license compatibility matrix
    let permissive_licenses = ["MIT", "BSD", "Apache", "ISC", "Unlicense"]
    let copyleft_licenses = ["GPL", "LGPL", "AGPL", "MPL"]
    let restrictive_licenses = ["SSPL", "Commons Clause", "Proprietary"]
    
    print "  License Categories:"
    print $"    ✅ Permissive: ($permissive_licenses | str join ', ')"
    print $"    ⚠️  Copyleft: ($copyleft_licenses | str join ', ')"
    print $"    ❌ Restrictive: ($restrictive_licenses | str join ', ')"
    print ""
    
    # Check our project license
    if ("LICENSE" | path exists) {
        let our_license = open LICENSE | lines | first 5 | str join " "
        let license_type = identify-license-type $our_license
        print $"  Our Project License: ($license_type)"
        
        if $license_type in $copyleft_licenses {
            print "    ⚠️  Copyleft license - all dependencies must be compatible"
        } else if $license_type in $permissive_licenses {
            print "    ✅ Permissive license - most dependencies will be compatible"
        }
    } else {
        print "  ❌ No LICENSE file found for this project!"
        print "    This is a compliance risk - project needs a license"
    }
    print ""
}

def generate-compliance-report [] {
    print "📊 License Compliance Report:"
    
    # Calculate compliance score
    let has_license_file = ("LICENSE" | path exists)
    let has_requirements = ("requirements.txt" | path exists)
    let has_package_json = ("package.json" | path exists)
    
    let compliance_score = (
        ($has_license_file | into int) * 40 +
        ($has_requirements | into int) * 20 +
        ($has_package_json | into int) * 10 +
        30  # Base score for having some structure
    )
    
    print $"  Compliance Score: ($compliance_score)/100"
    
    if $compliance_score >= 80 {
        print "  ✅ Good compliance posture"
    } else if $compliance_score >= 60 {
        print "  ⚠️  Moderate compliance - improvements needed"
    } else {
        print "  ❌ Poor compliance - immediate action required"
    }
    print ""
    
    print "  Recommendations:"
    if not $has_license_file {
        print "    📜 Add LICENSE file to project root"
    }
    
    print "    🔍 Run detailed license audit: pip-licenses, npm-license-checker"
    print "    📋 Create NOTICE file with third-party attributions"
    print "    🤖 Set up automated license scanning in CI/CD"
    print "    📚 Document license policy for contributors"
    print ""
    
    print "  Suggested Tools:"
    print "    Python: pip-licenses, licensecheck, license-expression"
    print "    JavaScript: license-checker, nlf, license-report"
    print "    Multi-language: FOSSA, WhiteSource, Snyk"
    print "    GitHub: Dependency insights, Security advisories"
    print ""
    
    print "🗽 'Give us your tired, your poor, your huddled masses of OSS licenses yearning to be free!'"
    print "   Mathematical license analysis complete - may your dependencies be forever compatible! 📜✨"
}

# Helper functions
def guess-license-from-name [package_name] {
    # Common patterns for guessing licenses from package names
    # This is heuristic-based, not definitive
    if ($package_name | str contains -i "gpl") {
        "GPL (likely)"
    } else if ($package_name in ["requests", "urllib3", "certifi", "charset-normalizer"]) {
        "Apache-2.0 (common)"
    } else if ($package_name in ["click", "flask", "jinja2", "werkzeug"]) {
        "BSD (common)"
    } else if ($package_name in ["pydantic", "fastapi", "starlette"]) {
        "MIT (common)"
    } else if ($package_name | str contains -i "crypto") {
        "Mixed (crypto packages vary)"
    } else {
        "Unknown (audit required)"
    }
}

def identify-license-type [license_text] {
    if ($license_text | str contains -i "MIT License") {
        "MIT"
    } else if ($license_text | str contains -i "Apache License") {
        "Apache-2.0"
    } else if ($license_text | str contains -i "GNU General Public License") {
        "GPL"
    } else if ($license_text | str contains -i "BSD License") {
        "BSD"
    } else if ($license_text | str contains -i "Mozilla Public License") {
        "MPL"
    } else {
        "Unknown/Custom"
    }
}

# Run the analysis
main