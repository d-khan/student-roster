#!/bin/bash
cd "$(dirname "$0")"
chmod +x build_mac_app.sh build_pkg.sh
./build_mac_app.sh
STATUS=$?
if [ $STATUS -ne 0 ]; then
  echo
  echo "APP BUILD FAILED"
  read -p "Press RETURN to close..."
  exit $STATUS
fi
echo
echo "The app build succeeded."
echo "Test dist/Student Roster.app first."
echo "After it works, run build_pkg.sh to create the installer."
read -p "Press RETURN to close..."
