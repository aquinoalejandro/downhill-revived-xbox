#!/usr/bin/env python3
"""Deploy Downhill Revived to an Xbox console running in Developer Mode.

Uses Microsoft's official WinAppDeployCmd utility from the Windows 10/11 SDK.
Supports loose-file deployment (recommended, bypasses certificate checks)
and packaged (.appx) deployment.

Usage:
    python port/tools/deploy_xbox.py --ip 192.168.1.50 [--pin 123456] [--method loose]
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SDK_BIN = Path('C:/Program Files (x86)/Windows Kits/10/bin/10.0.26100.0/x64')
WINAPPDEPLOY = SDK_BIN / 'WinAppDeployCmd.exe'

PACKAGE_DIR = ROOT / 'build' / 'xbox-x64' / 'package'
MANIFEST_PATH = PACKAGE_DIR / 'AppxManifest.xml'
APPX_PATH = ROOT / 'build' / 'xbox-x64' / 'DownhillRevived-xbox.appx'


def main():
    parser = argparse.ArgumentParser(description='Deploy Downhill Revived to Xbox Dev Mode')
    parser.add_argument('--ip', required=True, help='IP address of the Xbox console (shown in Dev Home)')
    parser.add_argument('--pin', help='Pairing PIN generated in Xbox Dev Home (Settings -> Pair with Visual Studio)')
    parser.add_argument('--method', choices=['loose', 'package'], default='loose',
                        help='Deployment method: "loose" (recommended, no cert check) or "package" (.appx)')
    args = parser.parse_args()

    if not WINAPPDEPLOY.exists():
        print(f"Error: WinAppDeployCmd not found at {WINAPPDEPLOY}", file=sys.stderr)
        return 1

    if args.method == 'loose':
        if not MANIFEST_PATH.exists():
            print(f"Error: Manifest not found at {MANIFEST_PATH}. Run package_xbox.py first.", file=sys.stderr)
            return 1

        print(f"[1/2] Deploying loose package layout to Xbox at {args.ip}...")
        cmd_deploy = [
            str(WINAPPDEPLOY),
            'deployfiles',
            '-file', str(MANIFEST_PATH),
            '-remotedeploydir', 'DownhillRevived',
            '-ip', args.ip,
        ]
        if args.pin:
            cmd_deploy.extend(['-pin', args.pin])

        res = subprocess.run(cmd_deploy)
        if res.returncode != 0:
            print("Failed to deploy files to Xbox. Check the IP address and PIN.", file=sys.stderr)
            return res.returncode

        print(f"[2/2] Registering loose package on Xbox at {args.ip}...")
        cmd_reg = [
            str(WINAPPDEPLOY),
            'registerfiles',
            '-remotedeploydir', 'DownhillRevived',
            '-ip', args.ip,
        ]
        res = subprocess.run(cmd_reg)
        if res.returncode != 0:
            print("Failed to register files on Xbox.", file=sys.stderr)
            return res.returncode

        print("\nDeployment successful! Downhill Revived is now installed on your Xbox.")
        print("Note: On your Xbox controller, highlight Downhill Revived in Dev Home,")
        print("press the View button (two overlapping squares) -> Manage app -> set App Type to 'Game'.")
        return 0

    else:
        if not APPX_PATH.exists():
            print(f"Error: Package not found at {APPX_PATH}. Run package_xbox.py first.", file=sys.stderr)
            return 1

        print(f"Installing package {APPX_PATH.name} to Xbox at {args.ip}...")
        cmd_install = [
            str(WINAPPDEPLOY),
            'install',
            '-file', str(APPX_PATH),
            '-ip', args.ip,
        ]
        if args.pin:
            cmd_install.extend(['-pin', args.pin])

        res = subprocess.run(cmd_install)
        return res.returncode


if __name__ == '__main__':
    sys.exit(main())
