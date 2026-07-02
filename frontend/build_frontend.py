#!/usr/bin/env python3
"""
One-command build script for the Internal Rating Survey Vue 3 frontend.
Runs npm install then npm run build from the frontend/ directory.

Usage:
    python build_frontend.py
"""

import subprocess
import sys
from pathlib import Path

APP_NAME = "internal_rating_survey"

def main():
    frontend_dir = Path(__file__).parent.absolute()
    app_root = frontend_dir.parent.absolute()
    output_dir = app_root / APP_NAME / "public" / "frontend"

    print(f"🔨  Building frontend for: {APP_NAME}")
    print(f"📁  Output directory:      {output_dir}\n")

    # Install dependencies
    print("[1/2] Installing npm dependencies...")
    result = subprocess.run(["npm", "install"], cwd=frontend_dir)
    if result.returncode != 0:
        print("❌  npm install failed")
        sys.exit(1)

    # Build
    print("\n[2/2] Building Vue app...")
    result = subprocess.run(["npm", "run", "build"], cwd=frontend_dir)
    if result.returncode != 0:
        print("❌  npm run build failed")
        sys.exit(1)

    print(f"\n✅  Build complete! Assets written to:\n    {output_dir}")


if __name__ == "__main__":
    main()
