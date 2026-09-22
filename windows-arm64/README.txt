Student Roster v1.4.1 - Windows ARM64

This revision changes only the build verification logic (plus the displayed version).

The build now searches recursively for chrome.exe instead of assuming a
specific Chromium version folder.

Build:
  Double-click Build Student Roster ARM64 v1.4.1.bat

A successful build must end with:
  SUCCESS - Student Roster v1.4.1

Then test:
  dist\Student Roster\Student Roster.exe
