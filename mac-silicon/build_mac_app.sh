#!/bin/bash
set -e
cd "$(dirname "$0")"

APP="Student Roster"
VERSION="1.4.2"
VENV=".build-venv"

echo "=============================================="
echo "Student Roster ${VERSION} - macOS Builder"
echo "=============================================="

if [ ! -f "app_icon.png" ]; then
  echo "ERROR: app_icon.png is missing."
  exit 1
fi
if [ ! -f "AppIcon.icns" ]; then
  echo "ERROR: AppIcon.icns is missing."
  exit 1
fi

rm -rf "$VENV" build dist "Student Roster.spec" browser-stage pkg-root
python3 -m venv "$VENV"
source "$VENV/bin/activate"

python -m pip install --upgrade pip
python -m pip install pyinstaller playwright customtkinter pillow
python -m playwright install chromium

PW_CACHE="$HOME/Library/Caches/ms-playwright"
if [ ! -d "$PW_CACHE" ]; then
  echo "ERROR: Playwright browser cache not found at $PW_CACHE"
  exit 1
fi

echo "Building modern macOS app..."
python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --onedir \
  --name "$APP" \
  --icon "AppIcon.icns" \
  --add-data "app_icon.png:." \
  --collect-all customtkinter \
  --collect-all playwright \
  roster_gui.py

APP_BUNDLE="dist/${APP}.app"
RESOURCES="${APP_BUNDLE}/Contents/Resources"
mkdir -p "$RESOURCES/ms-playwright"

echo "Bundling Playwright Chromium..."
for d in "$PW_CACHE"/chromium-* "$PW_CACHE"/chromium_headless_shell-* "$PW_CACHE"/ffmpeg-*; do
  if [ -d "$d" ]; then
    echo "  Copying $(basename "$d")"
    ditto "$d" "$RESOURCES/ms-playwright/$(basename "$d")"
  fi
done

# Remove quarantine attributes from locally staged browser files.
xattr -cr "$APP_BUNDLE" 2>/dev/null || true

echo
echo "SUCCESS"
echo "App created:"
echo "$(pwd)/$APP_BUNDLE"
echo
echo "Open it and test a real roster before building the PKG."
