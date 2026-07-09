# AGENTS.md

## Cursor Cloud specific instructions

Umi-OCR is a **free, offline OCR desktop application** (PySide2 / Qt5 + QML, Python).
This repository (`UmiOCR-data/`) contains **only the application source**. The Python
runtime and the OCR engine plugins live in *separate* upstream repositories and are
**not** committed here — they are provisioned during environment setup and persist in
the VM snapshot. There are **no automated tests, no linter, and no build step** in this
repo (packaging/build is delegated to the external `Umi-OCR_runtime_*` repos).

### What was provisioned (persists in the VM snapshot, not tracked by git)

- `UmiOCR-data/.venv/` — Python **3.10** virtualenv with the runtime deps
  (`PySide2>=5.15`, `PyMuPDF`, `fonttools`, `pillow`, `psutil`, `pynput`, `zxing-cpp`).
  PySide2 5.15 only supports CPython 3.8–3.10, so the system `python3` (3.12) cannot be
  used — always use Python 3.10 for the venv.
- `UmiOCR-data/plugins/linux_x64_PaddleOCR-json_v141/` — the PaddleOCR-json OCR engine
  (from `Umi-OCR_plugins`). Requires a CPU with the **AVX** instruction set.
- `umi-ocr.sh`, `requirements.txt`, `UmiOCR-data/main_linux.py` — the Linux launcher
  files (copied from `Umi-OCR_runtime_linux`). These are intentionally **untracked /
  gitignored**.
- System packages (baked into the snapshot): Python 3.10 (deadsnakes PPA), Qt/xcb
  runtime libs (`libxcb-*`, `libxkbcommon-x11-0`, `libgl1`, `libegl1`, etc.), CJK fonts,
  and `xvfb`.

### Running the app

The launcher `./umi-ocr.sh` activates `UmiOCR-data/.venv` and runs
`UmiOCR-data/main_linux.py`. Run it from the repo root.

- GUI on the existing desktop: `DISPLAY=:1 ./umi-ocr.sh`
- Headless (no desktop): `HEADLESS=true ./umi-ocr.sh` — this starts its own `Xvfb :99`.

It is a long-running foreground process (starts the Qt event loop); run it in a
dedicated terminal/tmux session.

### HTTP API and CLI

- The app runs a **local HTTP server on `http://127.0.0.1:1224`** by default
  (enabled out of the box). OCR endpoint: `POST /api/ocr` with a JSON body
  `{"base64": "<img>", "options": {"data.format": "text"}}`. See `docs/http/`.
- CLI control goes *through* that HTTP server, e.g. `./umi-ocr.sh --screenshot`,
  `./umi-ocr.sh --path "img.png"`. Start the main process first, then send CLI commands
  from a second shell (see `docs/README_CLI.md`).

### Non-obvious gotchas

- On startup you will see non-fatal warnings that are safe to ignore in headless/minimal
  environments: `SystemTrayIcon`/`Menu` "requires Qt Widgets", and
  "system does not support OpenGLES" (it falls back to software OpenGL).
- Screenshot OCR needs an X (not Wayland) session; on `:1` it works, but the batch-image
  and HTTP OCR paths are the most reliable way to verify the engine.
- Config is stored in `UmiOCR-data/.settings` (INI). Use `--reload` to re-read it.
