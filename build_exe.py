# -*- coding: utf-8 -*-
"""
Milk Pet Build & Installer Tool

Usage:
    python build_exe.py              # Default build EXE
    python build_exe.py --simple     # Single file mode
    python build_exe.py --test       # Test mode
    python build_exe.py --installer  # Build installer (requires EXE first)
    python build_exe.py --all        # Build EXE + Installer (one click)
"""

import sys
import os
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SPEC_MAP = {
    "default": ("MilkPet.spec", "MilkPet"),
    "--simple": ("MilkPet_Simple.spec", "MilkPet"),
    "--test": ("MilkPet_Test.spec", "MilkPet_Test"),
}

DATA_DIR_NAME = "_internal"
ISS_FILE = "MilkPet.iss"
INSTALLER_DIR = "installer"


def clean_build():
    build_dir = os.path.join(SCRIPT_DIR, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print("[OK] Cleaned build directory")


def run_build(spec_name: str, dist_name: str):
    spec_path = os.path.join(SCRIPT_DIR, spec_name)
    if not os.path.exists(spec_path):
        print(f"[ERROR] Spec file not found: {spec_path}")
        return False

    print(f"=" * 50)
    print(f"  Milk Pet Build Tool")
    print(f"  Spec: {spec_name}")
    print(f"  Output: dist/{dist_name}/")
    print(f"  Data Dir: {DATA_DIR_NAME}")
    print(f"=" * 50)

    clean_build()

    cmd = [sys.executable, "-m", "PyInstaller", spec_path, "--clean", "--noconfirm"]
    result = subprocess.run(cmd, cwd=SCRIPT_DIR,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    dist_path = os.path.join(SCRIPT_DIR, "dist", dist_name)
    
    if os.path.exists(dist_path) and os.path.exists(os.path.join(dist_path, f"{dist_name}.exe")):
        print()
        print(f"{'=' * 50}")
        print(f"  Build successful!")
        print(f"  Output: {dist_path}")

        exe_path = os.path.join(dist_path, f"{dist_name}.exe")
        if not os.path.exists(exe_path):
            exe_path = os.path.join(SCRIPT_DIR, 'dist', f"{dist_name}.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"  EXE Size: {size_mb:.1f} MB")

        data_path = os.path.join(dist_path, DATA_DIR_NAME)
        if os.path.exists(data_path):
            file_count = sum(len(files) for _, _, files in os.walk(data_path))
            print(f"  Data Dir: {DATA_DIR_NAME}/ ({file_count} files)")
        print(f"{'=' * 50}")
        return True
    else:
        print(f"\n[ERROR] Build failed, exit code: {result.returncode}")
        return False


def find_inno_setup():
    """Find Inno Setup compiler (ISCC.exe)"""
    candidates = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup\ISCC.exe",
        r"C:\Program Files\Inno Setup\ISCC.exe",
    ]
    
    for path in candidates:
        if os.path.exists(path):
            return path
    
    try:
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1")
            path, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            iscc_path = os.path.join(path, "ISCC.exe")
            if os.path.exists(iscc_path):
                return iscc_path
        except Exception:
            pass
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1")
            path, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            iscc_path = os.path.join(path, "ISCC.exe")
            if os.path.exists(iscc_path):
                return iscc_path
        except Exception:
            pass
            
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 5_is1")
            path, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            iscc_path = os.path.join(path, "ISCC.exe")
            if os.path.exists(iscc_path):
                return iscc_path
        except Exception:
            pass
    except Exception:
        pass
    
    try:
        result = subprocess.run(["where", "ISCC"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0].strip()
    except Exception:
        pass
    
    return None


def build_installer():
    """Build installer using Inno Setup"""
    iss_path = os.path.join(SCRIPT_DIR, ISS_FILE)
    dist_path = os.path.join(SCRIPT_DIR, "dist", "MilkPet")
    exe_path = os.path.join(dist_path, "MilkPet.exe")
    data_path = os.path.join(dist_path, DATA_DIR_NAME)

    print()
    print(f"=" * 50)
    print(f"  Installer Builder")
    print(f"=" * 50)

    if not os.path.isfile(exe_path):
        print("[ERROR] MilkPet.exe not found, run build first:")
        print("        python build_exe.py")
        return False

    if not os.path.isdir(data_path):
        print(f"[ERROR] Data directory not found: {data_path}")
        return False

    iscc_path = find_inno_setup()
    if not iscc_path:
        print("[ERROR] Inno Setup compiler (ISCC.exe) not found")
        print()
        print("  Please download and install Inno Setup:")
        print("  https://jrsoftware.org/isdl.php")
        print()
        print("  Re-run this script after installation.")
        return False

    print(f"  Inno Setup: {iscc_path}")
    print(f"  Script: {ISS_FILE}")
    print(f"  Source: dist/MilkPet/")
    print(f"  Output: {INSTALLER_DIR}/")
    print()

    installer_output_dir = os.path.join(SCRIPT_DIR, INSTALLER_DIR)
    if not os.path.exists(installer_output_dir):
        os.makedirs(installer_output_dir)

    cmd = [iscc_path, iss_path]
    print(f"  Executing: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, cwd=SCRIPT_DIR,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding='utf-8', errors='replace')
    
    if result.stdout:
        print("  --- Inno Setup Output ---")
        print(result.stdout)
        print("  --- End Output ---")

    output_files = []
    if os.path.exists(installer_output_dir):
        for f in os.listdir(installer_output_dir):
            if f.endswith(".exe"):
                full_path = os.path.join(installer_output_dir, f)
                size_mb = os.path.getsize(full_path) / (1024 * 1024)
                output_files.append((f, size_mb))

    if output_files:
        print()
        print(f"{'=' * 50}")
        print(f"  Installer build successful!")
        for name, size in output_files:
            print(f"  File: {INSTALLER_DIR}/{name} ({size:.1f} MB)")
        print(f"{'=' * 50}")
        return True
    else:
        print(f"\n[ERROR] Installer build failed")
        return False


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "default"

    if arg in ("-h", "--help"):
        print(__doc__)
        return

    if arg == "--installer":
        success = build_installer()
        sys.exit(0 if success else 1)
        return

    if arg == "--all":
        print("[Step 1/2] Building EXE...")
        spec_name, dist_name = SPEC_MAP["default"]
        build_ok = run_build(spec_name, dist_name)
        
        if build_ok:
            print("\n[Step 2/2] Building installer...")
            installer_ok = build_installer()
            sys.exit(0 if installer_ok else 1)
        else:
            sys.exit(1)
        return

    if arg not in SPEC_MAP:
        print(f"[ERROR] Unknown argument: {arg}")
        print(__doc__)
        sys.exit(1)

    spec_name, dist_name = SPEC_MAP[arg]
    success = run_build(spec_name, dist_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()