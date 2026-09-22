#!/bin/bash
set -e
cd "$(dirname "$0")"

APP="Student Roster"
VERSION="1.4.2"
APP_BUNDLE="dist/${APP}.app"
PKG="StudentRoster-${VERSION}.pkg"
ROOT="pkg-root"

if [ ! -d "$APP_BUNDLE" ]; then
  echo "ERROR: ${APP_BUNDLE} does not exist."
  echo "Run build_mac_app.sh first."
  exit 1
fi

rm -rf "$ROOT" "$PKG"
mkdir -p "$ROOT/Applications"
ditto "$APP_BUNDLE" "$ROOT/Applications/${APP}.app"

pkgbuild \
  --root "$ROOT" \
  --identifier "edu.sdccd.studentroster" \
  --version "$VERSION" \
  --install-location "/" \
  "$PKG"

echo
echo "SUCCESS"
echo "Installer created:"
echo "$(pwd)/$PKG"
echo
echo "Give ONLY this .pkg file to the end user."
