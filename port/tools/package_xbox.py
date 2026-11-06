#!/usr/bin/env python3
"""Build and package Downhill Revived into a signed UWP .appx package for Xbox Dev Mode.

Creates the Appx package directory, copies dhd64.exe, dxcompiler.dll, dxil.dll, assets,
generates AppxManifest.xml, runs makeappx.exe, and signs the package using signtool.exe.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
DEVCACHES = Path(os.environ.get('DHD_DEVCACHES') or Path.home() / 'DevCaches')
SDK_BIN = Path('C:/Program Files (x86)/Windows Kits/10/bin/10.0.26100.0/x64')
D3D_REDIST = Path('C:/Program Files (x86)/Windows Kits/10/Redist/D3D/x64')
MAKEAPPX = SDK_BIN / 'makeappx.exe'
SIGNTOOL = SDK_BIN / 'signtool.exe'
CERT_THUMBPRINT = 'FB4EE4DB81A7F10C710F9BC1C969FC318E69D4A1'

MANIFEST_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<Package
  xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
  xmlns:mp="http://schemas.microsoft.com/appx/2014/phone/manifest"
  xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
  xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
  IgnorableNamespaces="uap mp rescap">

  <Identity
    Name="DownhillRevived.Xbox"
    Publisher="CN=DownhillRevived"
    Version="1.0.0.0"
    ProcessorArchitecture="x64" />

  <Properties>
    <DisplayName>Downhill Revived</DisplayName>
    <PublisherDisplayName>Downhill Revived Team</PublisherDisplayName>
    <Logo>Assets\\StoreLogo.png</Logo>
  </Properties>

  <Dependencies>
    <TargetDeviceFamily Name="Windows.Universal" MinVersion="10.0.10240.0" MaxVersionTested="10.0.26100.0" />
    <TargetDeviceFamily Name="Windows.Xbox" MinVersion="10.0.10240.0" MaxVersionTested="10.0.26100.0" />
  </Dependencies>

  <Resources>
    <Resource Language="x-generate" />
  </Resources>

  <Applications>
    <Application Id="App"
      Executable="dhd64.exe"
      EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements
        DisplayName="Downhill Revived"
        Square150x150Logo="Assets\\Square150x150Logo.png"
        Square44x44Logo="Assets\\Square44x44Logo.png"
        Description="Downhill Revived on Xbox One Dev Mode"
        BackgroundColor="transparent">
        <uap:DefaultTile Wide310x150Logo="Assets\\Wide310x150Logo.png"/>
        <uap:SplashScreen Image="Assets\\SplashScreen.png" />
      </uap:VisualElements>
    </Application>
  </Applications>

  <Capabilities>
    <Capability Name="internetClient" />
    <rescap:Capability Name="runFullTrust" />
  </Capabilities>
</Package>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe', type=Path, default=ROOT / 'build/xbox-x64/dhd64.exe', help='Host executable')
    p.add_argument('--out', type=Path, default=ROOT / 'build/xbox-x64/DownhillRevived-xbox.appx',
                   help='Output .appx file')
    p.add_argument('--staging', type=Path, default=ROOT / 'build/xbox-x64/package',
                   help='Staging directory for packaging')
    a = p.parse_args()

    if not a.exe.exists():
        p.error(f'Executable not found: {a.exe}. Run build_host64.py --target xbox-x64 first.')

    staging = a.staging.resolve()
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)

    # 1. Copy executable
    dest_exe = staging / 'dhd64.exe'
    shutil.copyfile(a.exe, dest_exe)
    print(f'Staged executable: {dest_exe} ({dest_exe.stat().st_size / 1048576:.1f} MB)')

    # 2. Copy DX12 DXC DLLs
    for dll_name in ('dxcompiler.dll', 'dxil.dll'):
        src_dll = D3D_REDIST / dll_name
        if src_dll.exists():
            shutil.copyfile(src_dll, staging / dll_name)
            print(f'Staged DXC library: {dll_name}')
        else:
            print(f'WARNING: {src_dll} not found')

    # 3. Copy visual assets
    assets_dir = staging / 'Assets'
    assets_dir.mkdir(parents=True, exist_ok=True)
    src_assets = DEVCACHES / 'hello-xbox/package/Assets'
    if src_assets.exists():
        for asset in src_assets.glob('*.png'):
            shutil.copyfile(asset, assets_dir / asset.name)
            # Also copy unscaled base name so makeappx finds either naming
            base_name = asset.name.replace('.scale-200', '')
            if base_name != asset.name:
                shutil.copyfile(asset, assets_dir / base_name)
        print(f'Staged visual assets from {src_assets}')
    else:
        p.error(f'Visual assets not found at {src_assets}')

    # 4. Generate AppxManifest.xml
    manifest = staging / 'AppxManifest.xml'
    manifest.write_text(MANIFEST_TEMPLATE, encoding='utf-8')
    print('Generated AppxManifest.xml')

    # 5. Pack with makeappx.exe
    a.out.parent.mkdir(parents=True, exist_ok=True)
    if a.out.exists():
        a.out.unlink()

    cmd_pack = [str(MAKEAPPX), 'pack', '/d', str(staging), '/p', str(a.out), '/o']
    print('Running makeappx...')
    res = subprocess.run(cmd_pack, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        p.error('makeappx failed')
    print(f'Packaged Appx: {a.out} ({a.out.stat().st_size / 1048576:.1f} MB)')

    # 6. Sign package
    cmd_sign = [str(SIGNTOOL), 'sign', '/fd', 'SHA256', '/sha1', CERT_THUMBPRINT, str(a.out)]
    print('Signing package...')
    res = subprocess.run(cmd_sign, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        p.error('signtool failed')
    print('Package successfully signed!')
    print(f'\nSUCCESS: {a.out} is ready for Xbox Dev Mode deployment.')


if __name__ == '__main__':
    main()
