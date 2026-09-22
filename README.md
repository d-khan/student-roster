# Student Roster

**Student Roster** is a desktop application for authorized SDCCD faculty that automates the creation of student roster CSV files using information available through **MyPortal** and **DSPS**.

**Current Version: 1.4.2**

## Download

Choose the installer that matches your computer.

| Platform | Processor | Download |
|---|---|---|
| macOS | Apple Silicon (M1, M2, M3, M4, M5, etc.) | **macOS ARM64** |
| macOS | Intel processor | **macOS Intel** |
| Windows | Intel or AMD 64-bit processor | **Windows x64** |
| Windows | ARM processor | **Windows ARM64** |

> **Not sure which version to download?**
>
> **macOS:** Select **Apple menu → About This Mac**. If your Mac shows an Apple M-series chip, use **macOS ARM64**. If it shows an Intel processor, use **macOS Intel**.
>
> **Windows:** Open **Settings → System → About** and check **System type**. Most Windows computers with Intel or AMD processors should use **Windows x64**. Windows computers with an ARM-based processor should use **Windows ARM64**.

## macOS Installation

1. Download the `.pkg` file that matches your Mac.
2. Open the downloaded package.
3. Follow the installer instructions.
4. Launch **Student Roster**.

### If macOS Blocks the App

Student Roster is distributed outside the Mac App Store. Depending on your macOS security settings, macOS may block the application the first time you try to open it.

If this happens:

1. Try to open **Student Roster** once.
2. Open **System Settings**.
3. Select **Privacy & Security**.
4. Scroll down to the **Security** section.
5. Locate the message indicating that Student Roster was blocked.
6. Click **Open Anyway**.
7. Confirm that you want to open the application.

You should normally need to approve the application only the first time.

> Only install Student Roster from a release source you trust.

## Windows Installation

1. Download the installer that matches your Windows computer.
2. Run the `.exe` installer.
3. Follow the installation instructions.
4. Launch **Student Roster** from the Start menu or desktop shortcut.

For most Windows computers with an Intel or AMD processor, use the **Windows x64** installer.

## Using Student Roster

1. Launch **Student Roster**.
2. Enter the academic term, for example:

   `Fall 2026`

3. Enter one or more section numbers. Separate multiple sections with commas, for example:

   `43422, 43378, 43445`

4. Click **Fetch Roster**.
5. Choose where you want to save the CSV file.
6. Complete the SDCCD sign-in and MFA process in the browser if requested.
7. Student Roster processes the selected sections and creates the CSV file.

## CSV Output

The generated CSV contains the following fields:

- Section
- Course
- Student ID
- Name
- Personal Email
- Student Email
- Honors
- DSPS

## Authentication and Privacy

Student Roster does **not** store your SDCCD username, password, or MFA code. Authentication is completed directly through the institution's browser-based sign-in process.

Browser authentication state may be retained locally on your computer so that you do not have to sign in on every run.

Student Roster is intended for **authorized SDCCD faculty use**. Users are responsible for protecting exported student information and handling it in accordance with applicable institutional privacy and data-security requirements.

## Supported Platforms

- macOS — Apple Silicon (ARM64)
- macOS — Intel (x86-64)
- Windows — Intel/AMD 64-bit (x64)
- Windows — ARM64

## Version

**Student Roster 1.4.2**

## Author

**Danish Khan**  
Computer Science  
San Diego Miramar College
