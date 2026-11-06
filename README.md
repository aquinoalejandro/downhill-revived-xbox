# Downhill Revived (Xbox Port)

An Xbox One and Xbox Series X|S native port of *Downhill Domination* running via **Retail Developer Mode**.

Downhill Revived is a source port of *Downhill Domination* (PlayStation 2, Incognito Entertainment / SCEA, 2003) built on a matching byte-for-byte decompilation. This repository adds native **UWP (Universal Windows Platform) x64** support, allowing the game to run directly on **Xbox One**, **Xbox One S**, **Xbox One X**, and **Xbox Series X|S** in Developer Mode with native Direct3D 12 rendering and Xbox controller support.

---

## Xbox Features & Compatibility

- **Xbox One Tested & Supported:** Runs natively on original Xbox One hardware (1.75 GHz AMD Jaguar CPU) targeting a locked **60 fps** in Game Mode.
- **DirectX 12 Renderer:** Custom `wgpu-hal` swap chain integration using `CreateSwapChainForCoreWindow` for smooth presentation and minimal input latency.
- **Xbox Controller Integration:** Full gamepad input, analog steering, vibration and button mapping via SDL3 and `Windows.Gaming.Input`.
- **Game Mode Memory Access:** Built for Xbox Game Mode, giving the port access to 5 GB of RAM (well above the 1 GB App Mode limit) and dedicated CPU cores.
- **Automatic Disc Detection:** Drop your clean USA disc image (`SCUS-97177.iso` or `downhill.iso`) into `LocalState` via Xbox Device Portal; the game detects and verifies it automatically on boot.
- **In-Game Settings:** Full PC SETTINGS accessible directly from the in-game OPTIONS menu (resolution scale, widescreen Hor+, audio, controls).

---

## Installation Guide (Xbox Dev Mode)

### Prerequisites

1. An Xbox console (Xbox One, One S, One X, or Series X|S) set to **Developer Mode**.
2. PC on the same local network with a modern web browser.
3. Your own copy of the USA disc image: **Downhill Domination (SCUS-97177)** as an `.iso` file.

### Step 1: Deploy the Package

1. On your Xbox, open **Dev Home** and note the IP address shown for the **Xbox Device Portal** (e.g., `https://192.168.1.XX:11443`).
2. On your PC, navigate to that address in your browser (accept the self-signed certificate warning if prompted).
3. Go to the **Apps** section.
4. Under **Deploy App**, click **Choose File** and select `DownhillRevived-xbox.appx`.
5. If prompted for dependencies or certificates, provide `dev_cert.cer`.
6. Click **Deploy** / **Install** and wait for the upload to complete.

### Step 2: Switch to Game Mode (Crucial!)

On the console:
1. In the Dev Home app list, highlight **Downhill Revived**.
2. Press the **View** button (the two overlapping squares on the Xbox controller).
3. Change the app type from **App** to **Game**.
> [!IMPORTANT]
> This step is required: Game Mode unlocks 5 GB of RAM and dedicated CPU cores instead of the restricted 1 GB App Mode sandbox.

### Step 3: Upload your Disc Image (ISO)

1. In the Xbox Device Portal on your PC, go to **File Explorer**.
2. Navigate to:
   `DevelopmentFiles\WindowsApps\DownhillRevived.Xbox_1.0.0.0_x64__...\LocalState\`
3. Upload your clean PS2 disc image renamed to:
   `SCUS-97177.iso` or `downhill.iso`
4. (Optional) You can also place custom `dhd.ini` configurations or texture packs here.

### Step 4: Play!

Launch **Downhill Revived** from Dev Home. The game will automatically detect the disc, initialize the DX12 renderer at fullscreen, and start playing at 60 fps.

---

## Building from Source

To build the Xbox UWP package yourself on Windows 10/11:

### Requirements
- **LLVM / Clang** (`clang-cl`, `lld-link`, `llvm-rc`)
- **MSVC v143** (Visual Studio 2022 C++ tools with UWP / Windows Store components)
- **Windows 10/11 SDK** (10.0.26100.0 or compatible)
- **Rust** (1.97.1 MSVC toolchain)
- **Python 3.10+** with `ninja` and `splat64`

### Build Steps

1. Extract the original PS2 game executable (`SCUS_971.77`) into `iso/`:
   ```powershell
   python tools/split.py
   ```
2. Build the WebAssembly game core:
   ```powershell
   python port/tools/build_wasm.py
   ```
3. Build the host executable for Xbox UWP:
   ```powershell
   python port/tools/build_host64.py --target xbox-x64 build/wasm/dhd_core.wasm
   ```
4. Package and sign into an `.appx` container:
   ```powershell
   python port/tools/package_xbox.py
   ```
The output package `build/xbox-x64/DownhillRevived-xbox.appx` and `dev_cert.cer` will be ready for deployment.

---

## Legal Notice

- This is an unofficial fan port based on educational clean-room reverse engineering. It is not endorsed by or affiliated with Sony Interactive Entertainment or Incognito Entertainment.
- This repository contains **no copyrighted game assets**: no disc images, game executables, textures, audio, video or BIOS files. The game requires your own legitimate dump of the original PlayStation 2 disc (SCUS-97177).
