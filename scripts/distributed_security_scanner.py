#!/usr/bin/env python3
"""
Distributed Security Scanner Framework

This script enables running security scans across multiple machines
to distribute CPU load and improve performance.
"""

import asyncio
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import aiohttp
import docker
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


@dataclass
class ScannerConfig:
    """Configuration for a security scanner"""

    name: str
    command: List[str]
    docker_image: Optional[str] = None
    machine: str = "local"
    timeout: int = 300
    memory_limit: str = "2g"
    cpu_limit: str = "1.0"


@dataclass
class ScanResult:
    """Result from a security scan"""

    scanner: str
    machine: str
    success: bool
    output: str
    duration: float
    error: Optional[str] = None


class DistributedSecurityScanner:
    """Distributed security scanning across multiple machines"""

    def __init__(self, config_path: str = "security_scanner_config.json"):
        self.config_path = Path(config_path)
        self.scanners: List[ScannerConfig] = []
        self.results: List[ScanResult] = []
        self.docker_client = None

        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            print(f"⚠️ Docker not available: {e}")

        self.load_config()

    def load_config(self):
        """Load scanner configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config_data = json.load(f)
                self.scanners = [ScannerConfig(**scanner) for scanner in config_data["scanners"]]
        else:
            # Default configuration
            self.scanners = [
                ScannerConfig(
                    name="bandit",
                    command=["bandit", "-r", "src/", "--format", "json"],
                    machine="local",
                ),
                ScannerConfig(
                    name="semgrep",
                    command=["semgrep", "scan", "--config", "auto", "--json"],
                    docker_image="returntocorp/semgrep:latest",
                    machine="docker",
                ),
                ScannerConfig(
                    name="trivy",
                    command=["trivy", "fs", "--format", "json", "."],
                    docker_image="aquasec/trivy:latest",
                    machine="docker",
                ),
                ScannerConfig(
                    name="gitleaks",
                    command=["gitleaks", "detect", "--report-format", "json"],
                    docker_image="zricethezav/gitleaks:latest",
                    machine="docker",
                ),
            ]
            self.save_config()

    def save_config(self):
        """Save scanner configuration"""
        config_data = {
            "scanners": [
                {
                    "name": s.name,
                    "command": s.command,
                    "docker_image": s.docker_image,
                    "machine": s.machine,
                    "timeout": s.timeout,
                    "memory_limit": s.memory_limit,
                    "cpu_limit": s.cpu_limit,
                }
                for s in self.scanners
            ]
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f, indent=2)

    async def run_scanner_local(self, scanner: ScannerConfig, work_dir: str) -> ScanResult:
        """Run scanner locally"""
        start_time = time.time()

        try:
            # Use ThreadPoolExecutor for I/O-bound operations
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    subprocess.run,
                    scanner.command,
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=scanner.timeout,
                )

                result = future.result()

                duration = time.time() - start_time

                return ScanResult(
                    scanner=scanner.name,
                    machine="local",
                    success=result.returncode == 0,
                    output=result.stdout,
                    duration=duration,
                    error=result.stderr if result.returncode != 0 else None,
                )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ScanResult(
                scanner=scanner.name,
                machine="local",
                success=False,
                output="",
                duration=duration,
                error="Timeout exceeded",
            )
        except Exception as e:
            duration = time.time() - start_time
            return ScanResult(
                scanner=scanner.name,
                machine="local",
                success=False,
                output="",
                duration=duration,
                error=str(e),
            )

    async def run_scanner_docker(self, scanner: ScannerConfig, work_dir: str) -> ScanResult:
        """Run scanner in Docker container"""
        if not self.docker_client:
            return ScanResult(
                scanner=scanner.name,
                machine="docker",
                success=False,
                output="",
                duration=0,
                error="Docker not available",
            )

        start_time = time.time()

        try:
            # Run container with resource limits
            container = self.docker_client.containers.run(
                scanner.docker_image,
                command=scanner.command,
                volumes={work_dir: {"bind": "/workspace", "mode": "ro"}},
                working_dir="/workspace",
                mem_limit=scanner.memory_limit,
                cpu_quota=int(float(scanner.cpu_limit) * 100000),
                cpu_period=100000,
                detach=True,
            )

            # Wait for completion
            result = container.wait()
            logs = container.logs().decode("utf-8")
            container.remove()

            duration = time.time() - start_time

            return ScanResult(
                scanner=scanner.name,
                machine="docker",
                success=result["StatusCode"] == 0,
                output=logs,
                duration=duration,
                error=(None if result["StatusCode"] == 0 else f"Exit code: {result['StatusCode']}"),
            )

        except Exception as e:
            duration = time.time() - start_time
            return ScanResult(
                scanner=scanner.name,
                machine="docker",
                success=False,
                output="",
                duration=duration,
                error=str(e),
            )

    async def run_scanner_remote(self, scanner: ScannerConfig, work_dir: str, remote_config: Dict) -> ScanResult:
        """Run scanner on remote machine via SSH"""
        start_time = time.time()

        try:
            # SSH command to run scanner on remote machine
            ssh_cmd = [
                "ssh",
                f"{remote_config['user']}@{remote_config['host']}",
                "cd",
                work_dir,
                "&&",
                *scanner.command,
            ]

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    subprocess.run,
                    ssh_cmd,
                    capture_output=True,
                    text=True,
                    timeout=scanner.timeout,
                )

                result = future.result()

                duration = time.time() - start_time

                return ScanResult(
                    scanner=scanner.name,
                    machine=remote_config["host"],
                    success=result.returncode == 0,
                    output=result.stdout,
                    duration=duration,
                    error=result.stderr if result.returncode != 0 else None,
                )

        except Exception as e:
            duration = time.time() - start_time
            return ScanResult(
                scanner=scanner.name,
                machine=remote_config.get("host", "unknown"),
                success=False,
                output="",
                duration=duration,
                error=str(e),
            )

    async def run_all_scanners(self, work_dir: str, remote_configs: Optional[Dict] = None) -> List[ScanResult]:
        """Run all scanners in parallel"""
        tasks = []

        for scanner in self.scanners:
            if scanner.machine == "local":
                task = self.run_scanner_local(scanner, work_dir)
            elif scanner.machine == "docker":
                task = self.run_scanner_docker(scanner, work_dir)
            elif scanner.machine.startswith("remote-") and remote_configs:
                remote_name = scanner.machine.replace("remote-", "")
                if remote_name in remote_configs:
                    task = self.run_scanner_remote(scanner, work_dir, remote_configs[remote_name])
                else:
                    print(f"⚠️ Remote config not found for {remote_name}")
                    continue
            else:
                print(f"⚠️ Unknown machine type: {scanner.machine}")
                continue

            tasks.append(task)

        # Run all scanners concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.results.append(
                    ScanResult(
                        scanner=self.scanners[i].name,
                        machine="unknown",
                        success=False,
                        output="",
                        duration=0,
                        error=str(result),
                    )
                )
            else:
                self.results.append(result)

        return self.results

    def generate_report(self) -> Dict:
        """Generate comprehensive scan report"""
        total_scanners = len(self.results)
        successful_scans = sum(1 for r in self.results if r.success)
        total_duration = sum(r.duration for r in self.results)

        # Group results by machine
        results_by_machine = {}
        for result in self.results:
            if result.machine not in results_by_machine:
                results_by_machine[result.machine] = []
            results_by_machine[result.machine].append(result)

        report = {
            "summary": {
                "total_scanners": total_scanners,
                "successful_scans": successful_scans,
                "failed_scans": total_scanners - successful_scans,
                "total_duration": total_duration,
                "average_duration": (total_duration / total_scanners if total_scanners > 0 else 0),
            },
            "results_by_machine": results_by_machine,
            "detailed_results": [
                {
                    "scanner": r.scanner,
                    "machine": r.machine,
                    "success": r.success,
                    "duration": r.duration,
                    "error": r.error,
                }
                for r in self.results
            ],
        }

        return report


async def main():
    """Main function"""
    scanner = DistributedSecurityScanner()

    # Example remote configurations
    remote_configs = {
        "scanner-1": {
            "user": "jenkins",
            "host": "192.168.1.100",
            "key_path": "~/.ssh/id_rsa",
        },
        "scanner-2": {
            "user": "jenkins",
            "host": "192.168.1.101",
            "key_path": "~/.ssh/id_rsa",
        },
    }

    print("🚀 Starting distributed security scan...")
    print(f"📊 Running {len(scanner.scanners)} scanners across multiple machines")

    # Run all scanners
    results = await scanner.run_all_scanners(".", remote_configs)

    # Generate report
    report = scanner.generate_report()

    print("\n📋 Scan Report:")
    print(f"✅ Successful: {report['summary']['successful_scans']}")
    print(f"❌ Failed: {report['summary']['failed_scans']}")
    print(f"⏱️ Total Duration: {report['summary']['total_duration']:.2f}s")
    print(f"📊 Average Duration: {report['summary']['average_duration']:.2f}s")

    # Save report
    with open("distributed_security_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Report saved to: distributed_security_report.json")


if __name__ == "__main__":
    asyncio.run(main())
