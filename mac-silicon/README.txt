Student Roster v1.4.2 — Modern macOS GUI

This keeps the working macOS roster automation and replaces the old Tkinter
interface with the modern CustomTkinter design used by the Windows app.

FILES YOU SUPPLY FROM YOUR EXISTING MAC FOLDER
- app_icon.png
- AppIcon.icns

FIRST TEST
1. Create/use a folder such as student-roster-mac.
2. Put these new files in it.
3. Copy app_icon.png and AppIcon.icns from your existing Mac project into it.
4. Double-click Build Student Roster.command.
5. Test: dist/Student Roster.app
6. Fetch a real roster and confirm authentication + CSV work.

ONLY AFTER THE APP WORKS
Run in Terminal from this folder:
  chmod +x build_pkg.sh
  ./build_pkg.sh

Final installer:
  StudentRoster-1.4.2.pkg

The end user receives only the .pkg.
