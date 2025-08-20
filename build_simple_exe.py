#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Executable Builder for PixelMug MCP
Focus on core functionality without data files
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def build_simple_executable(script_name: str, output_name: str):
    """Build a simple executable without data files"""
    print(f"🔧 Building {output_name} from {script_name}...")
    
    # Simple PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", output_name,
        "--console",
        "--clean", 
        "--noconfirm",
        script_name
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check if executable was created
        exe_path = Path("dist") / output_name
        exe_path_exe = Path("dist") / f"{output_name}.exe"
        
        if exe_path.exists() or exe_path_exe.exists():
            actual_path = exe_path if exe_path.exists() else exe_path_exe
            
            # Make executable on Unix systems
            if exe_path.exists():
                exe_path.chmod(0o755)
            
            size_mb = actual_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ Success! File: {actual_path.name} ({size_mb:.2f} MB)")
            return True
        else:
            print(f"   ❌ Executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Build failed: {e}")
        return False


def main():
    """Main function"""
    print("🚀 PixelMug MCP Simple Executable Builder")
    print("=" * 50)
    
    # Ensure PyInstaller is available
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} available")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} installed")
    
    # Clean and create directories
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    
    Path("dist").mkdir(exist_ok=True)
    
    # Build executables
    builds = [
        ("stdio_server.py", "pixelmug_stdio"),
        ("mcp_server.py", "pixelmug_interactive"),
    ]
    
    success_count = 0
    for script, output in builds:
        if build_simple_executable(script, output):
            success_count += 1
    
    print(f"\n{'=' * 50}")
    if success_count == len(builds):
        print("🎉 All executables built successfully!")
        print("\nUsage:")
        print("  ./dist/pixelmug_stdio              # Standard I/O mode")
        print("  ./dist/pixelmug_interactive        # Interactive mode")
        print("\nTest with:")
        print('  echo \'{"jsonrpc":"2.0","method":"help","id":1}\' | ./dist/pixelmug_stdio')
    else:
        print(f"⚠️  {success_count}/{len(builds)} executables built")
    
    return success_count == len(builds)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
