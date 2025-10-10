#!/usr/bin/env python3
"""
Simple System Discovery Tool

A straightforward way to understand what's running in your Beast Mode system.
"""

import requests
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any

def check_service(name: str, url: str) -> Dict[str, Any]:
    """Check if a service is accessible"""
    try:
        response = requests.get(url, timeout=5)
        return {
            "name": name,
            "url": url,
            "status": "✅ HEALTHY" if response.status_code == 200 else f"⚠️  HTTP {response.status_code}",
            "accessible": True,
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        return {
            "name": name,
            "url": url,
            "status": f"❌ ERROR: {str(e)[:50]}",
            "accessible": False,
            "response_time": None
        }

def check_docker_containers() -> List[Dict[str, Any]]:
    """Check running Docker containers"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                container = json.loads(line)
                containers.append({
                    "name": container.get("Names", "Unknown"),
                    "image": container.get("Image", "Unknown"),
                    "status": container.get("Status", "Unknown"),
                    "ports": container.get("Ports", "No ports")
                })
        return containers
    except Exception as e:
        return [{"error": f"Docker check failed: {e}"}]

def count_specs() -> Dict[str, int]:
    """Count specifications"""
    specs_dir = Path(".kiro/specs")
    if not specs_dir.exists():
        return {"error": "No .kiro/specs directory found"}
    
    spec_dirs = [d for d in specs_dir.iterdir() if d.is_dir()]
    
    counts = {
        "total_specs": len(spec_dirs),
        "with_requirements": 0,
        "with_design": 0,
        "with_tasks": 0,
        "complete_specs": 0
    }
    
    for spec_dir in spec_dirs:
        has_req = (spec_dir / "requirements.md").exists()
        has_design = (spec_dir / "design.md").exists()
        has_tasks = (spec_dir / "tasks.md").exists()
        
        if has_req:
            counts["with_requirements"] += 1
        if has_design:
            counts["with_design"] += 1
        if has_tasks:
            counts["with_tasks"] += 1
        if has_req and has_design and has_tasks:
            counts["complete_specs"] += 1
    
    return counts

def count_source_files() -> Dict[str, int]:
    """Count source files"""
    src_dir = Path("src")
    if not src_dir.exists():
        return {"error": "No src directory found"}
    
    counts = {
        "python_files": len(list(src_dir.rglob("*.py"))),
        "javascript_files": len(list(src_dir.rglob("*.js"))),
        "html_files": len(list(src_dir.rglob("*.html"))),
        "css_files": len(list(src_dir.rglob("*.css")))
    }
    
    # Count Beast Mode components
    beast_mode_dir = src_dir / "beast_mode"
    if beast_mode_dir.exists():
        counts["beast_mode_modules"] = len(list(beast_mode_dir.rglob("*.py")))
        counts["beast_mode_subdirs"] = len([d for d in beast_mode_dir.iterdir() if d.is_dir()])
    
    return counts

def main():
    """Run system discovery"""
    print("🔍 Beast Mode System Discovery")
    print("=" * 50)
    
    # Check core services
    print("\n📡 Core Services Status:")
    services = [
        ("Observatory", "http://localhost:8888/health"),
        ("Jaeger Tracing", "http://localhost:16686/api/services"),
        ("Prometheus", "http://localhost:9090/-/healthy"),
        ("Grafana", "http://localhost:3000/api/health"),
        ("Google Calendar MCP", "http://localhost:3001/health"),
        ("Google Workspace MCP", "http://localhost:8000/health")
    ]
    
    for name, url in services:
        result = check_service(name, url)
        print(f"  {result['status']} {name} ({url})")
        if result['accessible'] and result['response_time']:
            print(f"    Response time: {result['response_time']:.3f}s")
    
    # Check Docker containers
    print("\n🐳 Docker Containers:")
    containers = check_docker_containers()
    if containers and "error" not in containers[0]:
        for container in containers:
            print(f"  ✅ {container['name']} ({container['image']})")
            print(f"    Status: {container['status']}")
            if container['ports'] != "No ports":
                print(f"    Ports: {container['ports']}")
    else:
        print("  ❌ No Docker containers or Docker not accessible")
    
    # Check specifications
    print("\n📋 Specifications:")
    spec_counts = count_specs()
    if "error" not in spec_counts:
        print(f"  📁 Total specs: {spec_counts['total_specs']}")
        print(f"  📝 With requirements: {spec_counts['with_requirements']}")
        print(f"  🎨 With design: {spec_counts['with_design']}")
        print(f"  ✅ With tasks: {spec_counts['with_tasks']}")
        print(f"  🎯 Complete specs: {spec_counts['complete_specs']}")
        
        completion_rate = (spec_counts['complete_specs'] / spec_counts['total_specs']) * 100
        print(f"  📊 Completion rate: {completion_rate:.1f}%")
    else:
        print(f"  ❌ {spec_counts['error']}")
    
    # Check source code
    print("\n💻 Source Code:")
    source_counts = count_source_files()
    if "error" not in source_counts:
        print(f"  🐍 Python files: {source_counts['python_files']}")
        print(f"  🟨 JavaScript files: {source_counts['javascript_files']}")
        print(f"  🌐 HTML files: {source_counts['html_files']}")
        print(f"  🎨 CSS files: {source_counts['css_files']}")
        
        if "beast_mode_modules" in source_counts:
            print(f"  🦾 Beast Mode modules: {source_counts['beast_mode_modules']}")
            print(f"  📂 Beast Mode subdirs: {source_counts['beast_mode_subdirs']}")
    else:
        print(f"  ❌ {source_counts['error']}")
    
    # Quick health summary
    print("\n🏥 System Health Summary:")
    
    # Check if Observatory is healthy
    obs_health = check_service("Observatory", "http://localhost:8888/health")
    if obs_health['accessible']:
        print("  ✅ Observatory system is running and healthy")
    else:
        print("  ❌ Observatory system is not accessible")
    
    # Check if tracing is available
    jaeger_health = check_service("Jaeger", "http://localhost:16686/api/services")
    if jaeger_health['accessible']:
        print("  ✅ Distributed tracing is available")
    else:
        print("  ❌ Distributed tracing is not accessible")
    
    # Check if specs are well-structured
    if "error" not in spec_counts and spec_counts['complete_specs'] > 50:
        print("  ✅ Comprehensive specification system")
    else:
        print("  ⚠️  Specification system needs attention")
    
    print("\n🎯 Quick Start Recommendations:")
    print("  1. Visit http://localhost:8888 for Observatory dashboard")
    print("  2. Visit http://localhost:16686 for Jaeger tracing UI")
    print("  3. Check .kiro/specs/ for available specifications")
    print("  4. Run 'python scripts/start_observatory_production.py' if Observatory is down")
    print("  5. Run 'python scripts/start_jaeger.py' if Jaeger is down")
    
    print("\n📚 Documentation:")
    print("  - Repository Discovery Report: REPOSITORY_DISCOVERY_REPORT.md")
    print("  - Specifications: .kiro/specs/")
    print("  - Source Code: src/beast_mode/")
    print("  - Scripts: scripts/")

if __name__ == "__main__":
    main()