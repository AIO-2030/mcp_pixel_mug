#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelMug MCP Project Build Script
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class ProjectBuilder:
    """Project Builder"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
    
    def clean(self):
        """Clean build directories"""
        print("🧹 Cleaning build directories...")
        
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
        
        # Clean Python cache
        for cache_dir in self.project_root.rglob("__pycache__"):
            shutil.rmtree(cache_dir)
            print(f"   Removed cache: {cache_dir}")
        
        for pyc_file in self.project_root.rglob("*.pyc"):
            pyc_file.unlink()
            print(f"   Removed: {pyc_file}")
        
        print("✅ Cleanup completed")
        return True
    
    def check_dependencies(self):
        """Check dependencies"""
        print("📦 Checking dependencies...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt does not exist")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print("✅ Dependencies check passed")
                return True
            else:
                print(f"❌ Dependencies check failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error occurred during dependencies check: {str(e)}")
            return False
    
    def install_dependencies(self):
        """Install dependencies"""
        print("📥 Installing dependencies...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print("✅ Dependencies installation completed")
                return True
            else:
                print("❌ Dependencies installation failed")
                return False
                
        except Exception as e:
            print(f"❌ Error occurred while installing dependencies: {str(e)}")
            return False
    
    def run_tests(self):
        """Run tests"""
        print("🧪 Running tests...")
        
        test_scripts = [
            "test_help.sh",
            "test_prepare.sh", 
            "test_publish.sh"
        ]
        
        all_passed = True
        for script in test_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                try:
                    print(f"   Running: {script}")
                    result = subprocess.run(
                        ["bash", str(script_path)],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        print(f"   ✅ {script} passed")
                    else:
                        print(f"   ❌ {script} failed")
                        print(f"      Output: {result.stdout}")
                        print(f"      Error: {result.stderr}")
                        all_passed = False
                        
                except Exception as e:
                    print(f"   ❌ Error occurred while running {script}: {str(e)}")
                    all_passed = False
            else:
                print(f"   ⚠️  Test script {script} does not exist")
        
        if all_passed:
            print("✅ All tests passed")
        else:
            print("❌ Some tests failed")
        
        return all_passed
    
    def build_package(self):
        """Build package"""
        print("📦 Building package...")
        
        # Create build directory
        self.dist_dir.mkdir(exist_ok=True)
        
        # Copy source code files
        source_files = [
            "mug_service.py",
            "mcp_server.py", 
            "stdio_server.py",
            "requirements.txt",
            "README.md",
            "LICENSE"
        ]
        
        for file_name in source_files:
            src_file = self.project_root / file_name
            if src_file.exists():
                dst_file = self.dist_dir / file_name
                shutil.copy2(src_file, dst_file)
                print(f"   Copied: {file_name}")
            else:
                print(f"   ⚠️  File does not exist: {file_name}")
        
        # Create startup script
        startup_script = self.dist_dir / "start_server.py"
        startup_content = '''#!/usr/bin/env python3
"""PixelMug MCP Server Startup Script"""

import sys
import asyncio
from stdio_server import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nServer stopped")
        sys.exit(0)
'''
        startup_script.write_text(startup_content, encoding='utf-8')
        startup_script.chmod(0o755)
        print("   Created: start_server.py")
        
        print("✅ Package build completed")
        return True
    
    def validate_project(self):
        """Validate project"""
        print("🔍 Validating project...")
        
        required_files = [
            "mug_service.py",
            "mcp_server.py",
            "stdio_server.py",
            "requirements.txt"
        ]
        
        all_valid = True
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                print(f"   ✅ {file_name}")
            else:
                print(f"   ❌ Missing file: {file_name}")
                all_valid = False
        
        # Validate Python syntax
        for py_file in ["mug_service.py", "mcp_server.py", "stdio_server.py"]:
            file_path = self.project_root / py_file
            if file_path.exists():
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(file_path)],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"   ✅ {py_file} syntax correct")
                    else:
                        print(f"   ❌ {py_file} syntax error: {result.stderr}")
                        all_valid = False
                except Exception as e:
                    print(f"   ❌ Error occurred while validating {py_file}: {str(e)}")
                    all_valid = False
        
        if all_valid:
            print("✅ Project validation passed")
        else:
            print("❌ Project validation failed")
        
        return all_valid
    
    def build_all(self):
        """Complete build process"""
        print("🚀 Starting PixelMug MCP Project Build")
        print("=" * 50)
        
        steps = [
            ("Clean", self.clean),
            ("Validate Project", self.validate_project),
            ("Install Dependencies", self.install_dependencies),
            ("Check Dependencies", self.check_dependencies),
            ("Run Tests", self.run_tests),
            ("Build Package", self.build_package)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                if not step_func():
                    print(f"❌ {step_name} failed, build aborted")
                    return False
            except Exception as e:
                print(f"❌ Error occurred during {step_name}: {str(e)}")
                return False
        
        print("\n" + "=" * 50)
        print("🎉 Build completed successfully!")
        print(f"📦 Build artifacts located at: {self.dist_dir}")
        print("\nTo start the server:")
        print(f"   cd {self.dist_dir}")
        print("   python start_server.py")
        
        return True
    
    def build_executable(self, mode: str = "stdio"):
        """Build standalone executable"""
        print(f"🚀 Building executable for {mode} mode...")
        
        try:
            # Check if PyInstaller is available
            result = subprocess.run(
                [sys.executable, "-c", "import PyInstaller"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("📦 Installing PyInstaller...")
                install_result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pyinstaller==6.3.0"],
                    cwd=self.project_root
                )
                if install_result.returncode != 0:
                    print("❌ Failed to install PyInstaller")
                    return False
            
            # Run the build script
            build_script = self.project_root / "build_exec.sh"
            if build_script.exists():
                result = subprocess.run(
                    ["bash", str(build_script), mode],
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    print("✅ Executable build completed")
                    return True
                else:
                    print("❌ Executable build failed")
                    return False
            else:
                print("❌ build_exec.sh not found")
                return False
                
        except Exception as e:
            print(f"❌ Error occurred during executable build: {str(e)}")
            return False


def main():
    """Main function"""
    builder = ProjectBuilder()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "clean":
            builder.clean()
        elif command == "install":
            builder.install_dependencies()
        elif command == "test":
            builder.run_tests()
        elif command == "build":
            builder.build_package()
        elif command == "validate":
            builder.validate_project()
        elif command == "all":
            builder.build_all()
        elif command == "exe" or command == "executable":
            mode = sys.argv[2] if len(sys.argv) > 2 else "stdio"
            builder.build_executable(mode)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: clean, install, test, build, validate, all, exe [stdio|mcp]")
            sys.exit(1)
    else:
        # Default to complete build
        if not builder.build_all():
            sys.exit(1)


if __name__ == "__main__":
    main()
