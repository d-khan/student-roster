# Student Roster

**Student Roster** is a desktop application for authorized SDCCD faculty that automates the creation of student roster CSV files using information available through **MyPortal** and **DSPS**.

**Current Version: 1.4.2**

## Download

Choose the installer that matches your computer.

| Platform | Processor | Download |
|---|---|---|
| macOS | Apple Silicon (M1, M2, M3, M4, M5, etc.) | [Download macOS Apple Silicon](https://github.com/d-khan/student-roster/releases/latest/download/StudentRoster-1.4.2-macOS-ARM64.pkg) |
| macOS | Intel processor | [Download macOS Intel](https://github.com/d-khan/student-roster/releases/latest/download/StudentRoster-1.4.2-macOS-Intel.pkg) |
| Windows | Intel or AMD 64-bit processor | [Download Windows x64](https://github.com/d-khan/student-roster/releases/latest/download/StudentRoster-Setup-1.4.2-x64.exe) |
| Windows | ARM processor | [Download Windows ARM64](https://github.com/d-khan/student-roster/releases/latest/download/StudentRoster-Setup-1.4.2-ARM64.exe) |

### Which version do I need?

**Mac:** Select **Apple menu → About This Mac**.

- If you see an Apple M-series chip (M1, M2, M3, M4, M5, etc.), download **macOS Apple Silicon**.
- If you see an Intel processor, download **macOS Intel**.

**Windows:** Open **Settings → System → About** and check **System type**.

- Intel or AMD 64-bit processor → download **Windows x64**.
- ARM-based processor → download **Windows ARM64**.

## macOS Installation

1. Download the `.pkg` file for your Mac.
2. Open the downloaded package.
3. Follow the installation instructions.
4. Launch **Student Roster**.

### macOS Security

Student Roster is distributed outside the Mac App Store. macOS may therefore block the application the first time you try to open it.

If Student Roster is blocked:

1. Try to open **Student Roster** once.
2. Open **System Settings → Privacy & Security**.
3. Scroll down to the **Security** section.
4. Find the message indicating that Student Roster was blocked.
5. Click **Open Anyway**.
6. Confirm that you want to open the application.

You should normally need to do this only once.

## Windows Installation

1. Download the appropriate `.exe` installer.
2. Run the installer.
3. Follow the installation instructions.
4. Launch **Student Roster** from the Start menu or desktop shortcut.

Most Windows computers with Intel or AMD processors should use the **Windows x64** version.

## How to Use Student Roster

1. Launch **Student Roster**.
2. Enter the academic term, for example: `Fall 2026`
3. Enter one or more section numbers. Separate multiple sections with commas, for example: `43422, 43378, 43445`
4. Click **Fetch Roster**.
5. Choose where you want to save the CSV file.
6. Complete the SDCCD sign-in and MFA process in the browser if requested.
7. Student Roster will process the selected sections and create the CSV file.

## CSV Output

The generated CSV includes:

- Section
- Course
- Student ID
- Name
- Personal Email
- Student Email
- Honors
- DSPS

## Authentication and Privacy

Student Roster does **not** store your SDCCD username, password, or MFA code. Authentication is completed through the institution's browser-based sign-in process.

Browser authentication state may be retained locally on your computer so that you do not have to sign in every time you run the application.

Student Roster is intended for **authorized SDCCD faculty use**. Users are responsible for protecting exported student information and handling it in accordance with applicable institutional privacy and data-security requirements.

## All Releases

Previous versions and all available installers can be found on the [GitHub Releases](https://github.com/d-khan/student-roster/releases) page.

## Author

**Danish Khan**  
Computer Science  
San Diego Miramar College
