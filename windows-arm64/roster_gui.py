import re
import csv
import unicodedata
import os
import threading
import queue
import traceback
import json
import sys
import shlex
import subprocess
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


# ============================================================
# SETTINGS
# ============================================================

PORTAL = (
    "https://myportal.sdccd.edu/psp/IHPRD/"
    "?cmd=login&languageCd=ENG&"
)

DSPS_URL = (
    "https://mydsps.sdccd.edu/"
    "user/instructor/letters.aspx"
)

APP_NAME = "Student Roster"
APP_VERSION = "1.4.2"

APP_SUPPORT_DIR = os.path.join(
    os.path.expanduser("~"), "Library", "Application Support", "StudentRoster"
) if sys.platform == "darwin" else os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "StudentRoster"
)

PROFILE_DIR = os.path.join(APP_SUPPORT_DIR, "playwright-profile")
SETTINGS_FILE = os.path.join(APP_SUPPORT_DIR, "settings.json")
os.makedirs(APP_SUPPORT_DIR, exist_ok=True)

def resource_path(filename):
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

def configure_bundled_playwright():
    """Point packaged Playwright at Chromium shipped beside the executable."""
    if getattr(sys, "frozen", False):
        bundled = os.path.join(os.path.dirname(sys.executable), "ms-playwright")
        if not os.path.isdir(bundled):
            raise RuntimeError("Bundled Chromium folder not found:\n" + bundled)
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = bundled

def retry_click(
    locator,
    page,
    description,
    attempts=4,
    wait_before_click=1000
):

    for attempt in range(
        1,
        attempts + 1
    ):

        try:

            print(
                f"{description} "
                f"(attempt {attempt}/{attempts})..."
            )

            locator.wait_for(
                state="visible",
                timeout=15000
            )

            page.wait_for_timeout(
                wait_before_click
            )

            locator.click(
                timeout=15000
            )

            print(
                f"{description}: OK"
            )

            return

        except PlaywrightTimeoutError:

            if attempt == attempts:

                print(
                    f"\nUnable to complete: "
                    f"{description}"
                )

                raise

            print(
                "Page refreshed while clicking. "
                "Retrying..."
            )

            page.wait_for_timeout(
                2000
            )


# ============================================================
# NAME NORMALIZATION
# ============================================================

def clean_name_part(text):

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    text = text.casefold()

    text = re.sub(
        r"[^a-z0-9'\-\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def myportal_name_key(name):
    """
    MyPortal example:

        Last,First Middle

    Returns:

        (first, last)
    """

    if "," not in name:
        return None

    last_part, first_part = name.split(
        ",",
        1
    )

    last_part = clean_name_part(
        last_part
    )

    first_part = clean_name_part(
        first_part
    )

    if not last_part or not first_part:
        return None

    first_name = (
        first_part.split()[0]
    )

    return (
        first_name,
        last_part
    )


def dsps_name_key(name):
    """
    DSPS examples:

        First Last
        First Middle Last

    Returns:

        (first, last)
    """

    normalized = clean_name_part(
        name
    )

    parts = normalized.split()

    if len(parts) < 2:
        return None

    return (
        parts[0],
        parts[-1]
    )


# ============================================================
# GET MAIN CONTENT FRAME
# ============================================================

def get_main_frame(page):

    return page.locator(
        'iframe[title="Main Content"]'
    ).content_frame


# ============================================================
# GET COURSE NUMBER
# ============================================================

def get_course_number(
    frame,
    section_number
):
    """
    Extract the CISC course number from the Faculty Schedule.

    Example:

        <td>
            <p>CISC 179-3001</p>
            <p>Miramar - Web</p>
            <p>Fully Online</p>
        </td>

    Returns:

        CISC 179
    """

    print(
        f"Finding course number for "
        f"section {section_number}..."
    )

    # --------------------------------------------------------
    # Find the requested section.
    # --------------------------------------------------------

    section_button = frame.get_by_role(
        "button",
        name=section_number,
        exact=True
    )

    section_button.wait_for(
        state="visible",
        timeout=15000
    )

    # --------------------------------------------------------
    # Find the table row containing THIS section.
    # --------------------------------------------------------

    schedule_row = section_button.locator(
        "xpath=ancestor::tr"
    )

    cells = schedule_row.locator(
        "td"
    )

    # --------------------------------------------------------
    # Search the same row for:
    #
    #     CISC 179-3001
    #
    # and extract:
    #
    #     CISC 179
    # --------------------------------------------------------

    for cell_index in range(
        cells.count()
    ):

        cell = cells.nth(
            cell_index
        )

        paragraphs = cell.locator(
            "p"
        )

        for paragraph_index in range(
            paragraphs.count()
        ):

            text = (
                paragraphs
                .nth(paragraph_index)
                .inner_text()
                .strip()
            )

            match = re.search(
                r"\b(CISC\s+\d+)\b",
                text,
                re.IGNORECASE
            )

            if match:

                course_number = (
                    match
                    .group(1)
                    .upper()
                )

                print(
                    f"Course found: "
                    f"{course_number}"
                )

                return course_number

    # --------------------------------------------------------
    # NOT FOUND
    # --------------------------------------------------------

    print(
        f"WARNING: Could not find the "
        f"CISC course number for section "
        f"{section_number}."
    )

    return ""


# ============================================================
# FIRST SECTION:
# OPEN FACULTY SCHEDULE FROM INITIAL LANDING PAGE
# ============================================================

def open_initial_faculty_schedule(page):

    print(
        "\nOpening College Faculty Dashboard..."
    )

    # --------------------------------------------------------
    # Initial landing page.
    #
    # Use the first College Faculty Dashboard link.
    # This is the navigation used by the working
    # single-section version.
    # --------------------------------------------------------

    dashboard = page.get_by_role(
        "link",
        name="College Faculty Dashboard"
    ).first

    retry_click(
        dashboard,
        page,
        "Opening College Faculty Dashboard",
        attempts=4,
        wait_before_click=1000
    )

    page.wait_for_timeout(
        2000
    )

    # --------------------------------------------------------
    # GET MAIN CONTENT FRAME
    # --------------------------------------------------------

    frame = get_main_frame(
        page
    )

    print(
        "Looking for College Faculty Schedule..."
    )

    faculty_schedule = frame.get_by_text(
        "College Faculty Schedule",
        exact=True
    )

    retry_click(
        faculty_schedule,
        page,
        "Opening College Faculty Schedule",
        attempts=4,
        wait_before_click=1000
    )

    page.wait_for_timeout(
        2000
    )

    return get_main_frame(
        page
    )


# ============================================================
# LATER SECTIONS:
# RETURN TO FACULTY SCHEDULE
# ============================================================

def open_faculty_schedule(
    page,
    frame
):

    print(
        "\nReturning to College Faculty Dashboard..."
    )

    # --------------------------------------------------------
    # PeopleSoft contains two elements named:
    #
    #     College Faculty Dashboard
    #
    # When returning from Follow-Up / Contact List, use the
    # Faculty Self Service dashboard.
    # --------------------------------------------------------

    dashboard = page.locator(
        '[role="link"]'
        '[steplabel="College Faculty Dashboard"]'
        '[onclick*="X_IH_FACULTY_SELF_SERVICE"]'
    )

    try:

        dashboard.wait_for(
            state="visible",
            timeout=15000
        )

        print(
            "Faculty Dashboard return link found."
        )

    except PlaywrightTimeoutError:

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        print(
            "Primary return link not found."
        )

        print(
            "Trying College Faculty Dashboard Step 4..."
        )

        dashboard = page.locator(
            '[role="link"]'
            '[steplabel="College Faculty Dashboard"]'
            '[stepnumber^="Step 4"]'
        )

        dashboard.wait_for(
            state="visible",
            timeout=15000
        )

    retry_click(
        dashboard,
        page,
        "Returning to College Faculty Dashboard",
        attempts=4,
        wait_before_click=1000
    )

    page.wait_for_timeout(
        2000
    )

    # --------------------------------------------------------
    # REFRESH FRAME
    # --------------------------------------------------------

    frame = get_main_frame(
        page
    )

    print(
        "Looking for College Faculty Schedule..."
    )

    faculty_schedule = frame.get_by_text(
        "College Faculty Schedule",
        exact=True
    )

    retry_click(
        faculty_schedule,
        page,
        "Opening College Faculty Schedule",
        attempts=4,
        wait_before_click=1000
    )

    page.wait_for_timeout(
        2000
    )

    return get_main_frame(
        page
    )


# ============================================================
# SELECT MYPORTAL TERM
# ============================================================

def select_myportal_term(
    page,
    frame
):

    print(
        f"\nLooking for {TERM}..."
    )

    term_containers = frame.locator(
        '[id^="ClassTermsUGRDList"]'
    )

    container_count = (
        term_containers.count()
    )

    selected_term = False

    # --------------------------------------------------------
    # SEARCH TERM CONTAINERS
    # --------------------------------------------------------

    for i in range(
        container_count
    ):

        container = (
            term_containers.nth(i)
        )

        try:

            container_text = (
                container
                .inner_text()
                .strip()
            )

        except Exception:

            continue

        # ----------------------------------------------------
        # FULL TERM MATCH
        # ----------------------------------------------------

        if (
            TERM.casefold()
            in container_text.casefold()
        ):

            try:

                term_link = (
                    container.get_by_text(
                        TERM,
                        exact=False
                    )
                )

                retry_click(
                    term_link,
                    page,
                    f"Selecting {TERM}"
                )

                selected_term = True

                break

            except Exception:

                pass

        # ----------------------------------------------------
        # SEASON + YEAR MATCH
        # ----------------------------------------------------

        if (
            TERM_NAME.casefold()
            in container_text.casefold()
            and
            TERM_YEAR in container_text
        ):

            try:

                term_link = (
                    container.get_by_text(
                        TERM_NAME,
                        exact=False
                    )
                )

                retry_click(
                    term_link,
                    page,
                    f"Selecting {TERM}"
                )

                selected_term = True

                break

            except Exception:

                pass

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if not selected_term:

        print(
            f"Trying visible term name: "
            f"{TERM_NAME}"
        )

        visible_term = frame.get_by_text(
            TERM_NAME,
            exact=True
        )

        try:

            retry_click(
                visible_term,
                page,
                f"Selecting {TERM}"
            )

            selected_term = True

        except Exception:

            print(
                f"\nUnable to locate {TERM} "
                "in College Faculty Schedule."
            )

            raise RuntimeError(
                f"Could not select term {TERM}"
            )

    page.wait_for_timeout(
        1500
    )


# ============================================================
# PROCESS ONE SECTION
# ============================================================

def process_section(
    page,
    frame,
    section_number
):

    print(
        "\n========================================"
    )

    print(
        f"PROCESSING SECTION {section_number}"
    )

    print(
        "========================================"
    )

    # ========================================================
    # GET COURSE NUMBER
    #
    # IMPORTANT:
    # Do this while we are still on College Faculty Schedule.
    # ========================================================

    course_number = get_course_number(
        frame,
        section_number
    )

    # ========================================================
    # OPEN SECTION
    # ========================================================

    section_button = frame.get_by_role(
        "button",
        name=section_number,
        exact=True
    )

    retry_click(
        section_button,
        page,
        f"Opening section {section_number}",
        attempts=4,
        wait_before_click=1500
    )

    print(
        "Waiting for section to load..."
    )

    page.wait_for_timeout(
        2500
    )

    # ========================================================
    # FOLLOW-UP
    # ========================================================

    follow_up = frame.get_by_role(
        "link",
        name="Follow-Up",
        exact=True
    )

    retry_click(
        follow_up,
        page,
        "Opening Follow-Up",
        attempts=5,
        wait_before_click=1500
    )

    page.wait_for_timeout(
        2000
    )

    # ========================================================
    # HONORS
    # ========================================================

    print(
        "\nChecking Honors records..."
    )

    honors_ids = set()

    honors_row = 0
    follow_up_rows = 0

    while True:

        student_id_locator = frame.locator(
            f'[id="X_FAC_FOLLOW_UP_EMPLID${honors_row}"]'
        )

        if (
            student_id_locator.count()
            == 0
        ):
            break

        reason_locator = frame.locator(
            f'[id="X_FAC_FOLLOW_UP_X_FAC_FOLLOWUP${honors_row}"]'
        )

        student_id = (
            student_id_locator
            .inner_text()
            .strip()
        )

        reason = ""

        if reason_locator.count() > 0:

            try:

                reason = (
                    reason_locator
                    .input_value()
                    .strip()
                )

            except Exception:

                reason = ""

        follow_up_rows += 1

        # H = Honors
        if reason == "H":

            honors_ids.add(
                student_id
            )

        honors_row += 1

    print(
        f"Follow-Up rows checked: "
        f"{follow_up_rows}"
    )

    print(
        f"Honors records found: "
        f"{len(honors_ids)}"
    )

    # ========================================================
    # CONTACT LIST
    # ========================================================

    contact_list = frame.get_by_role(
        "button",
        name="Contact List",
        exact=True
    )

    retry_click(
        contact_list,
        page,
        "Opening Contact List",
        attempts=4,
        wait_before_click=1000
    )

    print(
        "Contact List opened."
    )

    first_student = frame.locator(
        '[id="X_FCLTY_CNTCT_V_EMPLID$0"]'
    )

    first_student.wait_for(
        state="visible",
        timeout=30000
    )

    print(
        "Roster loaded."
    )

    # ========================================================
    # EXTRACT ROSTER
    # ========================================================

    section_students = []

    row = 0

    total_rows = 0
    enrolled_rows = 0
    excluded_status_note = 0

    while True:

        student_id_locator = frame.locator(
            f'[id="X_FCLTY_CNTCT_V_EMPLID${row}"]'
        )

        if (
            student_id_locator.count()
            == 0
        ):
            break

        # ----------------------------------------------------
        # LOCATORS
        # ----------------------------------------------------

        name_locator = frame.locator(
            f'[id="X_PREFR_NODT_V_NAME${row}"]'
        )

        status_locator = frame.locator(
            f'[id="X_FCLTY_CNTCT_V_STDNT_ENRL_STATUS${row}"]'
        )

        status_note_locator = frame.locator(
            f'[id="X_FCLTY_CNTCT_V_DESCR${row}"]'
        )

        personal_email_locator = frame.locator(
            f'[id="X_FCLTY_CNTCT_V_EMAIL_ADDR2${row}"]'
        )

        student_email_locator = frame.locator(
            f'[id="X_FCLTY_CNTCT_V_EMAIL_ADDR${row}"]'
        )

        # ----------------------------------------------------
        # VALUES
        # ----------------------------------------------------

        student_id = (
            student_id_locator
            .inner_text()
            .strip()
        )

        student_name = (
            name_locator
            .inner_text()
            .strip()
            if name_locator.count() > 0
            else ""
        )

        enrollment_status = (
            status_locator
            .inner_text()
            .strip()
            if status_locator.count() > 0
            else ""
        )

        status_note = (
            status_note_locator
            .inner_text()
            if status_note_locator.count() > 0
            else ""
        )

        personal_email = (
            personal_email_locator
            .inner_text()
            .strip()
            if personal_email_locator.count() > 0
            else ""
        )

        student_email = (
            student_email_locator
            .inner_text()
            .strip()
            if student_email_locator.count() > 0
            else ""
        )

        # ----------------------------------------------------
        # NORMALIZE STATUS NOTE
        # ----------------------------------------------------

        status_note = (
            status_note
            .replace("\u00a0", "")
            .strip()
        )

        total_rows += 1

        # ----------------------------------------------------
        # FILTER
        #
        # Include only:
        #
        # Enrollment Status = Enrolled
        #
        # AND
        #
        # Status Note = blank
        # ----------------------------------------------------

        if (
            enrollment_status.casefold()
            == "enrolled"
        ):

            enrolled_rows += 1

            if status_note == "":

                section_students.append({

                    "section":
                        section_number,

                    "course":
                        course_number,

                    "student_id":
                        student_id,

                    "name":
                        student_name,

                    "personal_email":
                        personal_email,

                    "student_email":
                        student_email,

                    "honors":
                        (
                            "Yes"
                            if student_id
                            in honors_ids
                            else ""
                        ),

                    "dsps":
                        ""
                })

            else:

                excluded_status_note += 1

        row += 1

    # ========================================================
    # SECTION SUMMARY
    # ========================================================

    section_honors = sum(
        1
        for student in section_students
        if student["honors"] == "Yes"
    )

    print(
        "\n----------------------------------------"
    )

    print(
        f"SECTION {section_number} COMPLETE"
    )

    print(
        "----------------------------------------"
    )

    print(
        f"Course: "
        f"{course_number}"
    )

    print(
        f"Total Contact List rows: "
        f"{total_rows}"
    )

    print(
        f"Enrollment Status = Enrolled: "
        f"{enrolled_rows}"
    )

    print(
        f"Excluded by Status Note: "
        f"{excluded_status_note}"
    )

    print(
        f"Final students: "
        f"{len(section_students)}"
    )

    print(
        f"Honors students: "
        f"{section_honors}"
    )

    return section_students



# ============================================================
# GUI APPLICATION
# ============================================================

TERM = ""
TERM_NAME = ""
TERM_YEAR = ""
SECTION_NUMBERS = []


def validate_inputs(term_text, section_text):
    term_text = term_text.strip()
    match = re.fullmatch(r"(Spring|Summer|Fall)\s+(\d{4})", term_text, re.IGNORECASE)
    if not match:
        raise ValueError("Enter the term as Fall 2026, Summer 2026, or Spring 2026.")

    term_name = match.group(1).title()
    term_year = match.group(2)
    term = f"{term_name} {term_year}"

    sections = [s.strip() for s in section_text.split(",") if s.strip()]
    sections = list(dict.fromkeys(sections))
    if not sections:
        raise ValueError("Enter at least one section number.")
    if not all(s.isdigit() for s in sections):
        raise ValueError("Section numbers must contain digits only.")

    return term, term_name, term_year, sections


def wait_for_myportal_authentication(page):
    print("\nWaiting for MyPortal authentication...")
    print("Complete Microsoft/SDCCD login and MFA in the browser if requested.")
    print("The program will continue automatically after login.")

    # The authenticated landing page exposes College Faculty Dashboard.
    dashboard = page.get_by_role("link", name="College Faculty Dashboard").first
    dashboard.wait_for(state="visible", timeout=300000)
    print("Authentication successful. Continuing automatically...")


def run_roster(term_text, section_text, csv_filename):
    global TERM, TERM_NAME, TERM_YEAR, SECTION_NUMBERS
    TERM, TERM_NAME, TERM_YEAR, SECTION_NUMBERS = validate_inputs(term_text, section_text)


    configure_bundled_playwright()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False
        )

        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.set_default_timeout(30000)

            print("\n========================================")
            print("STARTING STUDENT CHECK")
            print("========================================")
            print(f"Term: {TERM}")
            print("Sections: " + ", ".join(SECTION_NUMBERS))
            print(f"Number of sections: {len(SECTION_NUMBERS)}")
            print("========================================")

            print("\nOpening MyPortal...")
            page.goto(PORTAL, wait_until="domcontentloaded")
            print("MyPortal opened.")
            wait_for_myportal_authentication(page)

            students = []
            frame = None

            for section_index, section_number in enumerate(SECTION_NUMBERS, start=1):
                print("\n\n########################################")
                print(f"SECTION {section_index} OF {len(SECTION_NUMBERS)}")
                print("########################################")

                if section_index == 1:
                    frame = open_initial_faculty_schedule(page)
                else:
                    frame = open_faculty_schedule(page, frame)

                select_myportal_term(page, frame)
                section_students = process_section(page, frame, section_number)
                students.extend(section_students)

            print("\n========================================")
            print("ALL MYPORTAL SECTIONS COMPLETE")
            print("========================================")
            print(f"Sections processed: {len(SECTION_NUMBERS)}")
            print(f"Total student/course rows captured: {len(students)}")

            roster_name_index = {}
            duplicate_keys = set()
            for student in students:
                name_key = myportal_name_key(student["name"])
                if name_key is None:
                    continue
                key = (student["section"], name_key)
                if key in roster_name_index:
                    duplicate_keys.add(key)
                else:
                    roster_name_index[key] = student
            for key in duplicate_keys:
                roster_name_index.pop(key, None)

            print("\nOpening DSPS...")
            dsps_page = context.new_page()
            dsps_page.set_default_timeout(30000)
            dsps_page.goto(DSPS_URL, wait_until="domcontentloaded")
            print("DSPS SSO started...")
            dsps_page.wait_for_timeout(4000)
            print("Current DSPS page:")
            print(dsps_page.url)

            if "letters.aspx" not in dsps_page.url.lower():
                print("\nDSPS authentication completed.")
                print("Opening Instructor Accommodation Letters...")
                dsps_page.goto(DSPS_URL, wait_until="domcontentloaded")
                dsps_page.wait_for_timeout(2500)

            print("\nDSPS Accommodation Letters page:")
            print(dsps_page.url)

            term_selector = dsps_page.locator(
                "#placeholder_main_placeholder_content_"
                "CtrlTermChooser1_CtrlTermChooser1_cmb_term"
            )
            print("\nWaiting for DSPS term selector...")
            try:
                term_selector.wait_for(state="visible", timeout=30000)
            except PlaywrightTimeoutError:
                print("Term selector was not found. Reloading Accommodation Letters page...")
                dsps_page.goto(DSPS_URL, wait_until="domcontentloaded")
                dsps_page.wait_for_timeout(3000)
                term_selector.wait_for(state="visible", timeout=30000)

            print("DSPS term selector found.")
            selected_dsps_term = term_selector.locator("option:checked").inner_text().strip()
            print(f"Current DSPS term: {selected_dsps_term}")

            if selected_dsps_term.casefold() != TERM.casefold():
                print(f"Selecting DSPS term: {TERM}")
                term_selector.select_option(label=TERM)
                dsps_page.wait_for_timeout(3500)
                dsps_page.wait_for_load_state("domcontentloaded")
            else:
                print(f"DSPS already showing {TERM}.")

            print("\nChecking DSPS records for sections:")
            print(", ".join(SECTION_NUMBERS))

            dsps_grid = dsps_page.locator(
                "#ctl00_ctl00_placeholder_main_placeholder_content_gv_courses_ctl00"
            )
            dsps_grid.wait_for(state="visible", timeout=30000)
            print("DSPS course table found.")

            dsps_rows = dsps_grid.locator("tbody tr")
            dsps_row_count = dsps_rows.count()
            print(f"DSPS table rows found: {dsps_row_count}")

            dsps_section_rows = 0
            dsps_matches = 0
            dsps_unmatched = 0

            for i in range(dsps_row_count):
                dsps_row = dsps_rows.nth(i)
                cells = dsps_row.locator("td")
                if cells.count() < 2:
                    continue

                course_text = cells.nth(0).inner_text().strip()
                dsps_student_name = cells.nth(1).inner_text().strip()
                section_match = re.search(r"\bsection\s+(\d+)\b", course_text, re.IGNORECASE)
                if not section_match:
                    continue

                dsps_section = section_match.group(1)
                if dsps_section not in SECTION_NUMBERS:
                    continue

                dsps_section_rows += 1
                name_key = dsps_name_key(dsps_student_name)
                if name_key is None:
                    dsps_unmatched += 1
                    continue

                student = roster_name_index.get((dsps_section, name_key))
                if student is not None:
                    student["dsps"] = "Yes"
                    dsps_matches += 1
                else:
                    dsps_unmatched += 1

            honors_students = sum(1 for s in students if s["honors"] == "Yes")
            dsps_students = sum(1 for s in students if s["dsps"] == "Yes")

            print("\n========================================")
            print("STUDENT ROSTER COMPLETE")
            print("========================================")
            print(f"Term: {TERM}")
            print("Sections: " + ", ".join(SECTION_NUMBERS))
            print(f"Sections processed: {len(SECTION_NUMBERS)}")
            print("----------------------------------------")
            print(f"Total student/course rows: {len(students)}")
            print(f"Honors rows: {honors_students}")
            print(f"DSPS rows: {dsps_students}")
            print("----------------------------------------")
            print(f"DSPS requested-section rows found: {dsps_section_rows}")
            print(f"DSPS records matched: {dsps_matches}")
            print(f"DSPS records not automatically matched: {dsps_unmatched}")
            print("========================================")

            print(f"\nSaving roster to: {csv_filename}")

            with open(csv_filename, "w", newline="", encoding="utf-8-sig") as csv_file:
                fieldnames = [
                    "Section", "Course", "Student ID", "Name",
                    "Personal Email", "Student Email", "Honors", "DSPS"
                ]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for student in students:
                    writer.writerow({
                        "Section": student["section"],
                        "Course": student["course"],
                        "Student ID": student["student_id"],
                        "Name": student["name"],
                        "Personal Email": student["personal_email"],
                        "Student Email": student["student_email"],
                        "Honors": student["honors"],
                        "DSPS": student["dsps"],
                    })

            print("\nCSV file created successfully.")
            print(f"File: {csv_filename}")
            print(f"Rows exported: {len(students)}")
            return csv_filename
        finally:
            context.close()


class QueueWriter:
    def __init__(self, q):
        self.q = q

    def write(self, text):
        if text:
            self.q.put(("log", text))
        return len(text)

    def flush(self):
        pass



class StudentRosterGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("900x720")
        self.minsize(800, 640)

        self.log_queue = queue.Queue()
        self.running = False
        self.last_csv = None
        self.selected_csv = None
        self.term_var = tk.StringVar(value="Fall 2026")
        self.sections_var = tk.StringVar()

        self._set_window_icon()
        self._load_settings()
        self._build_ui()
        self.after(100, self._drain_queue)

    def _set_window_icon(self):
        try:
            if os.name == "nt":
                icon = resource_path("app_icon.ico")
                if os.path.exists(icon):
                    self.iconbitmap(icon)
        except Exception:
            pass

    def _load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r", encoding="utf-8") as handle:
                    settings = json.load(handle)
                self.term_var.set(settings.get("term", self.term_var.get()))
                self.sections_var.set(settings.get("sections", ""))
        except Exception:
            pass

    def _save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as handle:
                json.dump({
                    "term": self.term_var.get().strip(),
                    "sections": self.sections_var.get().strip(),
                }, handle, indent=2)
        except Exception:
            pass

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        shell = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "#0f172a"))
        shell.grid(row=0, column=0, sticky="nsew")
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(shell, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=34, pady=(26, 18))
        header.grid_columnconfigure(1, weight=1)

        try:
            image = Image.open(resource_path("app_icon.png"))
            self.logo = ctk.CTkImage(light_image=image, dark_image=image, size=(58, 58))
            ctk.CTkLabel(header, text="", image=self.logo).grid(row=0, column=0, rowspan=2, padx=(0, 16))
        except Exception:
            pass

        ctk.CTkLabel(
            header, text="Student Roster",
            font=ctk.CTkFont(family="Segoe UI", size=27, weight="bold")
        ).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(
            header, text="Faculty roster automation",
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).grid(row=1, column=1, sticky="nw")
        ctk.CTkLabel(
            header, text=f"Version {APP_VERSION}",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        ).grid(row=0, column=2, rowspan=2, sticky="e")

        card = ctk.CTkFrame(shell, corner_radius=14)
        card.grid(row=1, column=0, sticky="ew", padx=34, pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)

        label_font = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        entry_font = ctk.CTkFont(family="Segoe UI", size=14)
        help_font = ctk.CTkFont(family="Segoe UI", size=12)

        ctk.CTkLabel(card, text="Term", font=label_font).grid(
            row=0, column=0, sticky="w", padx=22, pady=(18, 6))
        self.term_entry = ctk.CTkEntry(
            card, textvariable=self.term_var, height=42, font=entry_font)
        self.term_entry.grid(row=1, column=0, sticky="ew", padx=22)
        ctk.CTkLabel(
            card, text="Example: Fall 2026, Spring 2027, or Summer 2027",
            font=help_font
        ).grid(row=2, column=0, sticky="w", padx=24, pady=(5, 14))

        ctk.CTkLabel(card, text="Sections", font=label_font).grid(
            row=3, column=0, sticky="w", padx=22, pady=(0, 6))
        self.sections_entry = ctk.CTkEntry(
            card, textvariable=self.sections_var, height=42,
            placeholder_text="43422, 43378, 43445", font=entry_font)
        self.sections_entry.grid(row=4, column=0, sticky="ew", padx=22)
        ctk.CTkLabel(
            card, text="Example: 43422, 43378, 43445 — separate multiple sections with commas",
            font=help_font
        ).grid(row=5, column=0, sticky="w", padx=24, pady=(5, 18))

        actions = ctk.CTkFrame(shell, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=34, pady=(0, 16))
        actions.grid_columnconfigure(4, weight=1)

        self.run_button = ctk.CTkButton(
            actions, text="Fetch Roster", height=44, width=190,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self.start_run)
        self.run_button.grid(row=0, column=0)

        self.open_csv_button = ctk.CTkButton(
            actions, text="Open CSV", height=40, width=120,
            command=self.open_csv, state="disabled")
        self.open_csv_button.grid(row=0, column=1, padx=(10, 0))

        self.open_button = ctk.CTkButton(
            actions, text="Open Folder", height=40, width=130,
            command=self.open_folder, state="disabled")
        self.open_button.grid(row=0, column=2, padx=(10, 0))

        self.about_button = ctk.CTkButton(
            actions, text="About", height=40, width=100,
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"), command=self.show_about)
        self.about_button.grid(row=0, column=3, padx=(10, 0))

        status_card = ctk.CTkFrame(shell, corner_radius=14)
        status_card.grid(row=3, column=0, sticky="nsew", padx=34, pady=(0, 28))
        status_card.grid_columnconfigure(0, weight=1)
        status_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(status_card, text="Status", font=label_font).grid(
            row=0, column=0, sticky="w", padx=20, pady=(16, 8))

        self.status = ctk.CTkTextbox(
            status_card, corner_radius=10, wrap="word",
            font=ctk.CTkFont(family="Cascadia Mono", size=12))
        self.status.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.status.configure(state="disabled")

        self.progress = ctk.CTkProgressBar(status_card, mode="indeterminate")
        self.progress.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 16))
        self.progress.grid_remove()

        self.append_log("Ready. Enter a term and one or more section numbers.\n")

    def append_log(self, text):
        self.status.configure(state="normal")
        self.status.insert("end", text)
        self.status.see("end")
        self.status.configure(state="disabled")

    def start_run(self):
        if self.running:
            return
        try:
            term, _, _, _ = validate_inputs(
                self.term_var.get(), self.sections_var.get())
        except ValueError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return

        default_name = f"{term.replace(' ', '_')}_Roster.csv"
        destination = filedialog.asksaveasfilename(
            parent=self, title="Save Student Roster",
            initialfile=default_name, defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")])
        if not destination:
            return

        self.selected_csv = destination
        self.last_csv = None
        self._save_settings()
        self.running = True
        self.run_button.configure(state="disabled")
        self.term_entry.configure(state="disabled")
        self.sections_entry.configure(state="disabled")
        self.open_csv_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.progress.grid()
        self.progress.start()

        self.append_log("\nFetching roster...\n")
        self.append_log(f"Roster will be saved to:\n{destination}\n")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        import contextlib
        writer = QueueWriter(self.log_queue)
        try:
            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                result = run_roster(
                    self.term_var.get(),
                    self.sections_var.get(),
                    self.selected_csv)
            self.log_queue.put(("done", result))
        except Exception as exc:
            self.log_queue.put(("error", (str(exc), traceback.format_exc())))

    def _set_idle(self):
        self.running = False
        self.progress.stop()
        self.progress.grid_remove()
        self.run_button.configure(state="normal")
        self.term_entry.configure(state="normal")
        self.sections_entry.configure(state="normal")

    def _friendly_error(self, message):
        msg = message or "An unexpected error occurred."
        lower = msg.lower()
        if "timeout" in lower:
            return ("The site did not respond in time. If a login or MFA window is open, "
                    "complete it and try again. Otherwise, verify your connection and retry.")
        if "permission" in lower:
            return ("Student Roster could not save the CSV at the selected location. "
                    "Choose another location and try again.")
        if "section" in lower and ("locat" in lower or "visible" in lower):
            return ("A requested section could not be located. Verify the section number, "
                    "term, and that the section appears in College Faculty Schedule.")
        return "The roster could not be completed. See the Status box for technical details."

    def _drain_queue(self):
        try:
            while True:
                kind, payload = self.log_queue.get_nowait()
                if kind == "log":
                    self.append_log(payload)
                elif kind == "done":
                    self._set_idle()
                    self.last_csv = payload
                    self.open_csv_button.configure(state="normal")
                    self.open_button.configure(state="normal")
                    self.append_log("\n✓ Roster complete.\n")
                    self.append_log(f"✓ Saved: {payload}\n")
                    messagebox.showinfo(
                        APP_NAME, f"Roster created successfully.\n\nSaved to:\n{payload}")
                elif kind == "error":
                    self._set_idle()
                    short_message, details = payload
                    self.append_log("\nERROR\n" + details + "\n")
                    messagebox.showerror(APP_NAME, self._friendly_error(short_message))
        except queue.Empty:
            pass
        self.after(100, self._drain_queue)

    def open_csv(self):
        if not self.last_csv or not os.path.exists(self.last_csv):
            return
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", self.last_csv], check=False)
            elif os.name == "nt":
                os.startfile(self.last_csv)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not open the CSV.\n\n{exc}")

    def open_folder(self):
        if not self.last_csv:
            return
        folder = os.path.dirname(self.last_csv)
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", folder], check=False)
            elif os.name == "nt":
                os.startfile(folder)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not open the folder.\n\n{exc}")

    def show_about(self):
        messagebox.showinfo(
            f"About {APP_NAME}",
            f"{APP_NAME} {APP_VERSION}\n\n"
            "Generates faculty roster CSV files from the authorized SDCCD "
            "MyPortal and DSPS pages.\n\n"
            "Privacy: Student Roster does not store your username, password, "
            "or MFA code. Authentication is completed directly in the institution's "
            "browser login page. Browser authentication state may be retained locally "
            "on this computer so you do not have to sign in on every run."
        )


if __name__ == "__main__":
    app = StudentRosterGUI()
    app.mainloop()
