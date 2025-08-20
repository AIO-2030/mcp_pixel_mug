#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Executable Builder for PixelMug MCP
Builds optimized executables with comprehensive error handling
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import tempfile


class ExecutableBuilder:
    """Advanced executable builder with optimization"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
    def ensure_pyinstaller(self):
        """Ensure PyInstaller is installed"""
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__} is available")
            return True
        except ImportError:
            print("📦 Installing PyInstaller...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pyinstaller==6.3.0"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("✅ PyInstaller installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install PyInstaller: {e}")
                return False
    
    def clean_build_dirs(self):
        """Clean build directories"""
        print("🧹 Cleaning build directories...")
        
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
        
        # Remove PyInstaller spec files
        for spec_file in self.project_root.glob("*.spec"):
            if spec_file.name != "pixelmug.spec":  # Keep our custom spec
                spec_file.unlink()
                print(f"   Removed: {spec_file}")
    
    def build_executable(self, script_name: str, output_name: str, description: str):
        """Build a single executable"""
        print(f"\n🔧 Building {description}...")
        print(f"   Script: {script_name}")
        print(f"   Output: {output_name}")
        
        # Prepare PyInstaller command
        cmd = [
            "pyinstaller",
            "--onefile",                           # Single executable file
            "--name", output_name,                 # Output name
            "--distpath", str(self.dist_dir),      # Distribution directory
            "--workpath", str(self.build_dir),     # Work directory
            "--specpath", str(self.build_dir),     # Spec file location
            "--console",                           # Console application
            "--clean",                             # Clean build
            "--noconfirm",                         # Don't ask for confirmation
            
            # Include required modules
            "--hidden-import", "asyncio",
            "--hidden-import", "asyncio_mqtt",
            "--hidden-import", "paho.mqtt.client",
            "--hidden-import", "ssl",
            "--hidden-import", "json",
            "--hidden-import", "uuid",
            "--hidden-import", "datetime",
            "--hidden-import", "logging",
            "--hidden-import", "typing",
            
            # Include data files
            "--add-data", "requirements.txt:.",
            "--add-data", "README.md:.",
            "--add-data", "LICENSE:.",
            
            # Exclude unnecessary modules to reduce size
            "--exclude-module", "tkinter",
            "--exclude-module", "matplotlib",
            "--exclude-module", "numpy",
            "--exclude-module", "pandas",
            "--exclude-module", "scipy",
            "--exclude-module", "PIL",
            "--exclude-module", "PyQt5",
            "--exclude-module", "PyQt6",
            "--exclude-module", "PySide2",
            "--exclude-module", "PySide6",
            
            script_name
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check if executable was created
            exe_path = self.dist_dir / output_name
            exe_path_exe = self.dist_dir / f"{output_name}.exe"
            
            if exe_path.exists() or exe_path_exe.exists():
                actual_path = exe_path if exe_path.exists() else exe_path_exe
                
                # Make executable on Unix systems
                if exe_path.exists():
                    exe_path.chmod(0o755)
                
                # Get file size
                size_mb = actual_path.stat().st_size / (1024 * 1024)
                
                print(f"   ✅ Build successful!")
                print(f"   📦 File: {actual_path.name}")
                print(f"   📊 Size: {size_mb:.2f} MB")
                
                return True
            else:
                print(f"   ❌ Executable not found at expected location")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Build failed: {e}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            return False
    
    def create_launcher_scripts(self):
        """Create convenient launcher scripts"""
        print("\n📝 Creating launcher scripts...")
        
        # Windows batch file
        bat_content = """@echo off
echo PixelMug MCP Server Launcher
echo ============================
echo.
echo Choose server mode:
echo 1. Standard I/O mode (for integration)
echo 2. Interactive mode (for testing)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo Starting Standard I/O server...
    pixelmug_mcp_stdio.exe
) else if "%choice%"=="2" (
    echo Starting Interactive server...
    pixelmug_mcp_interactive.exe
) else (
    echo Invalid choice. Starting Standard I/O server...
    pixelmug_mcp_stdio.exe
)
pause
"""
        
        # Unix shell script
        sh_content = """#!/bin/bash
echo "PixelMug MCP Server Launcher"
echo "============================"
echo
echo "Choose server mode:"
echo "1. Standard I/O mode (for integration)"
echo "2. Interactive mode (for testing)"
echo
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "Starting Standard I/O server..."
        ./pixelmug_mcp_stdio
        ;;
    2)
        echo "Starting Interactive server..."
        ./pixelmug_mcp_interactive
        ;;
    *)
        echo "Invalid choice. Starting Standard I/O server..."
        ./pixelmug_mcp_stdio
        ;;
esac
"""
        
        # Write launcher scripts
        (self.dist_dir / "launch.bat").write_text(bat_content)
        (self.dist_dir / "launch.sh").write_text(sh_content)
        (self.dist_dir / "launch.sh").chmod(0o755)
        
        print("   ✅ Created launch.bat (Windows)")
        print("   ✅ Created launch.sh (Unix/Linux/Mac)")
    
    def create_readme(self):
        """Create executable-specific README"""
        readme_content = """# PixelMug MCP Executables

## Quick Start

### Windows
Double-click `launch.bat` or run one of:
- `pixelmug_mcp_stdio.exe` - Standard I/O mode
- `pixelmug_mcp_interactive.exe` - Interactive mode

### Linux/Mac
Run `./launch.sh` or run one of:
- `./pixelmug_mcp_stdio` - Standard I/O mode
- `./pixelmug_mcp_interactive` - Interactive mode

## Usage Examples

### Standard I/O Mode (Integration)
```bash
echo '{"jsonrpc":"2.0","method":"help","id":1}' | ./pixelmug_mcp_stdio
```

### Interactive Mode (Testing)
```bash
./pixelmug_mcp_interactive
# Follow the prompts to send commands
```

## Supported Commands

All executables support the same JSON-RPC methods:
- `help` - Get service information
- `prepare_mqtt_connection` - Get device connection parameters
- `publish_action` - Send device commands

## For Developers

These executables are built from the PixelMug MCP project.
For source code and development instructions, visit:
https://github.com/AIO-2030/mcp_pixel_mug
"""
        
        (self.dist_dir / "README_EXECUTABLES.md").write_text(readme_content)
        print("   ✅ Created README_EXECUTABLES.md")
    
    def build_all(self):
        """Build all executables"""
        print("🚀 PixelMug MCP Executable Builder")
        print("=" * 50)
        
        # Step 1: Ensure PyInstaller
        if not self.ensure_pyinstaller():
            return False
        
        # Step 2: Clean build directories
        self.clean_build_dirs()
        
        # Step 3: Create directories
        self.dist_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        
        # Step 4: Build executables
        builds = [
            ("stdio_server.py", "pixelmug_mcp_stdio", "Standard I/O Server"),
            ("mcp_server.py", "pixelmug_mcp_interactive", "Interactive MCP Server")
        ]
        
        success_count = 0
        for script, output, description in builds:
            if self.build_executable(script, output, description):
                success_count += 1
        
        # Step 5: Create additional files
        if success_count > 0:
            self.create_launcher_scripts()
            self.create_readme()
        
        # Step 6: Summary
        print(f"\n{'=' * 50}")
        if success_count == len(builds):
            print("🎉 All executables built successfully!")
            print(f"📦 Location: {self.dist_dir}")
            print("\nTo run:")
            print("   Windows: double-click launch.bat")
            print("   Unix/Linux/Mac: ./launch.sh")
        else:
            print(f"⚠️  {success_count}/{len(builds)} executables built successfully")
            
        return success_count == len(builds)


def main():
    """Main function"""
    builder = ExecutableBuilder()
    
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("PixelMug MCP Executable Builder")
        print("Usage: python build_all_executables.py")
        print("Builds standalone executables for PixelMug MCP server")
        return
    
    success = builder.build_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
