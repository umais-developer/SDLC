#!/usr/bin/env python3
"""
Machine Capability Detector

Detects which tech stacks are available on the current machine.
Used by the SDLC architecture stage to make informed stack recommendations.

Output: JSON file with available capabilities and versions
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Force UTF-8 stdio so emoji prints survive Windows cp1252.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "_shared"))
from console import setup as setup_console  # noqa: E402
setup_console()

class CapabilityDetector:
    """Detects installed runtimes, frameworks, and tools"""

    def __init__(self):
        self.capabilities = {
            "timestamp": self._get_timestamp(),
            "os": self._detect_os(),
            "runtimes": {},
            "package_managers": {},
            "frameworks": {},
            "databases": {},
            "build_tools": {},
            "recommendations": []
        }

    @staticmethod
    def _get_timestamp() -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _detect_os() -> str:
        import platform
        return platform.system()

    def _run_command(self, cmd: List[str]) -> Tuple[bool, Optional[str]]:
        """Run command and return (success, output)"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, None

    def detect_all(self) -> Dict:
        """Run all detections"""
        self._detect_runtimes()
        self._detect_package_managers()
        self._detect_frameworks()
        self._detect_databases()
        self._detect_build_tools()
        self._make_recommendations()
        return self.capabilities

    # Runtime Detection
    def _detect_runtimes(self):
        """Detect Node.js, Python, Java, .NET, Go, Rust"""
        self.capabilities["runtimes"] = {
            "nodejs": self._detect_nodejs(),
            "python": self._detect_python(),
            "java": self._detect_java(),
            "dotnet": self._detect_dotnet(),
            "go": self._detect_go(),
            "rust": self._detect_rust(),
        }

    def _detect_nodejs(self) -> Optional[Dict]:
        success, version = self._run_command(["node", "--version"])
        if success:
            npm_success, npm_version = self._run_command(["npm", "--version"])
            return {
                "available": True,
                "node_version": version,
                "npm_version": npm_version if npm_success else None,
                "pnpm": self._check_pnpm(),
                "yarn": self._check_yarn()
            }
        return {"available": False}

    def _check_pnpm(self) -> Optional[str]:
        _, version = self._run_command(["pnpm", "--version"])
        return version

    def _check_yarn(self) -> Optional[str]:
        _, version = self._run_command(["yarn", "--version"])
        return version

    def _detect_python(self) -> Optional[Dict]:
        success, version = self._run_command(["python3", "--version"])
        if not success:
            success, version = self._run_command(["python", "--version"])
        
        if success:
            pip_success, pip_version = self._run_command(["pip3", "--version"])
            if not pip_success:
                pip_success, pip_version = self._run_command(["pip", "--version"])
            
            return {
                "available": True,
                "version": version,
                "pip_available": pip_success,
                "venv_available": self._check_venv(),
            }
        return {"available": False}

    @staticmethod
    def _check_venv() -> bool:
        """Check if venv module is available"""
        import sys
        return sys.version_info >= (3, 3)

    def _detect_java(self) -> Optional[Dict]:
        success, version = self._run_command(["java", "--version"])
        if success:
            mvn_success, mvn_version = self._run_command(["mvn", "--version"])
            gradle_success, gradle_version = self._run_command(["gradle", "--version"])
            
            return {
                "available": True,
                "version": version.split('\n')[0],
                "maven": mvn_version.split('\n')[0] if mvn_success else None,
                "gradle": gradle_version if gradle_success else None,
            }
        return {"available": False}

    def _detect_dotnet(self) -> Optional[Dict]:
        success, version = self._run_command(["dotnet", "--version"])
        if success:
            sdk_success, sdk_list = self._run_command(["dotnet", "--list-sdks"])
            
            return {
                "available": True,
                "version": version,
                "sdks": sdk_list if sdk_success else None,
                "runtimes": self._get_dotnet_runtimes()
            }
        return {"available": False}

    def _get_dotnet_runtimes(self) -> Optional[str]:
        _, output = self._run_command(["dotnet", "--list-runtimes"])
        return output

    def _detect_go(self) -> Optional[Dict]:
        success, version = self._run_command(["go", "version"])
        if success:
            return {
                "available": True,
                "version": version
            }
        return {"available": False}

    def _detect_rust(self) -> Optional[Dict]:
        success, version = self._run_command(["rustc", "--version"])
        if success:
            cargo_success, cargo_version = self._run_command(["cargo", "--version"])
            return {
                "available": True,
                "rustc": version,
                "cargo": cargo_version if cargo_success else None
            }
        return {"available": False}

    # Package Manager Detection
    def _detect_package_managers(self):
        """Detect npm, pip, nuget, maven, gradle, cargo"""
        self.capabilities["package_managers"] = {
            "npm": self._check_command(["npm", "--version"]),
            "pnpm": self._check_command(["pnpm", "--version"]),
            "yarn": self._check_command(["yarn", "--version"]),
            "pip": self._check_command(["pip3", "--version"]) or self._check_command(["pip", "--version"]),
            "maven": self._check_command(["mvn", "--version"]),
            "gradle": self._check_command(["gradle", "--version"]),
            "cargo": self._check_command(["cargo", "--version"]),
            "nuget": self._check_command(["nuget"]),
        }

    def _check_command(self, cmd: List[str]) -> Optional[str]:
        """Check if command exists and return version"""
        success, output = self._run_command(cmd)
        return output if success else None

    # Framework Detection
    def _detect_frameworks(self):
        """Detect popular frameworks by checking for common packages"""
        self.capabilities["frameworks"] = {
            "spa": self._detect_spa_frameworks(),
            "backend": self._detect_backend_frameworks(),
        }

    def _detect_spa_frameworks(self) -> Dict:
        """Detect React, Vue, Angular, Svelte"""
        return {
            "react": self._check_npm_package("react"),
            "vue": self._check_npm_package("vue"),
            "angular": self._check_npm_package("@angular/core"),
            "svelte": self._check_npm_package("svelte"),
            "vite": self._check_npm_package("vite"),
            "webpack": self._check_npm_package("webpack"),
            "typescript": self._check_npm_package("typescript"),
        }

    def _detect_backend_frameworks(self) -> Dict:
        """Detect FastAPI, Django, Spring Boot, ASP.NET Core"""
        return {
            "fastapi": self._check_pip_package("fastapi"),
            "django": self._check_pip_package("django"),
            "flask": self._check_pip_package("flask"),
            "express": self._check_npm_package("express"),
            "spring_boot": self._check_java_dependency("org.springframework.boot"),
            "asp_net_core": self.capabilities["runtimes"].get("dotnet", {}).get("available", False),
        }

    def _check_npm_package(self, package: str) -> bool:
        """Check if npm package is installed globally or locally"""
        success, _ = self._run_command(["npm", "list", "-g", "--depth=0", package])
        return success

    def _check_pip_package(self, package: str) -> bool:
        """Check if pip package is installed"""
        try:
            import importlib.util
            return importlib.util.find_spec(package) is not None
        except (ImportError, ModuleNotFoundError):
            return False

    @staticmethod
    def _check_java_dependency(dependency: str) -> bool:
        """Check if Java dependency is available (simplified check)"""
        # This would require Maven or Gradle, simplified for now
        return False

    # Database Detection
    def _detect_databases(self):
        """Detect PostgreSQL, MySQL, SQLite, MongoDB, Redis"""
        self.capabilities["databases"] = {
            "postgresql": self._check_command(["psql", "--version"]),
            "mysql": self._check_command(["mysql", "--version"]),
            "sqlite": self._check_command(["sqlite3", "--version"]),
            "mongodb": self._check_command(["mongod", "--version"]),
            "redis": self._check_command(["redis-cli", "--version"]),
        }

    # Build Tools Detection
    def _detect_build_tools(self):
        """Detect Docker, Git, CI/CD tools"""
        self.capabilities["build_tools"] = {
            "docker": self._check_command(["docker", "--version"]),
            "docker_compose": self._check_command(["docker-compose", "--version"]),
            "git": self._check_command(["git", "--version"]),
            "gh_cli": self._check_command(["gh", "--version"]),
        }

    # Recommendations
    def _make_recommendations(self):
        """Generate recommendations based on available capabilities"""
        runtimes = self.capabilities["runtimes"]
        frameworks = self.capabilities["frameworks"]
        
        recommendations = []

        # SPA Recommendation
        if runtimes["nodejs"]["available"] if runtimes.get("nodejs") else False:
            recommendations.append({
                "stack": "SPA (React/Vue/Svelte)",
                "reason": "Node.js and npm are available",
                "opinion_file": "spa-opinion.md",
                "ready": True
            })
        
        # .NET Recommendation
        if runtimes.get("dotnet", {}).get("available", False):
            recommendations.append({
                "stack": ".NET 8+",
                "reason": ".NET runtime detected",
                "opinion_file": "dotnet-opinion.md",
                "ready": True
            })
        
        # Python Recommendation
        if runtimes.get("python", {}).get("available", False):
            recommendations.append({
                "stack": "Python (FastAPI/Django)",
                "reason": "Python 3.11+ detected",
                "opinion_file": "python-opinion.md",
                "ready": True
            })
        
        # Java Recommendation
        if runtimes.get("java", {}).get("available", False):
            recommendations.append({
                "stack": "Java (Spring Boot)",
                "reason": "Java 21 LTS detected",
                "opinion_file": "java-opinion.md",
                "ready": True
            })

        # Warnings
        if not runtimes.get("nodejs", {}).get("available", False):
            recommendations.append({
                "stack": "SPA (React/Vue/Svelte)",
                "reason": "Node.js not found - install to use",
                "ready": False,
                "install": "https://nodejs.org/en/download"
            })

        if not runtimes.get("python", {}).get("available", False):
            recommendations.append({
                "stack": "Python (FastAPI/Django)",
                "reason": "Python 3.11+ not found - install to use",
                "ready": False,
                "install": "https://www.python.org/downloads"
            })

        if not runtimes.get("dotnet", {}).get("available", False):
            recommendations.append({
                "stack": ".NET 8+",
                "reason": ".NET runtime not found - install to use",
                "ready": False,
                "install": "https://dotnet.microsoft.com/en-us/download"
            })

        if not runtimes.get("java", {}).get("available", False):
            recommendations.append({
                "stack": "Java (Spring Boot)",
                "reason": "Java 21+ not found - install to use",
                "ready": False,
                "install": "https://www.oracle.com/java/technologies/downloads/"
            })

        self.capabilities["recommendations"] = recommendations


def main():
    """Main entry point"""
    detector = CapabilityDetector()
    capabilities = detector.detect_all()
    
    # Output JSON
    output = json.dumps(capabilities, indent=2)
    print(output)
    
    # Optionally save to file
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        Path(output_file).write_text(output)
        print(f"\n✅ Capabilities saved to: {output_file}", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
