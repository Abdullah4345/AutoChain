from tkinter import filedialog
import os
import subprocess
import hashlib
from datetime import datetime, timedelta
import getpass
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import re
from fpdf import FPDF
from PIL import Image, ImageTk

import csv
import hashlib
import psutil
import win32api
import win32file
import win32security
import ctypes
import wmi
import struct

OUTPUT_DIR = "forensic_evidence"
EVIDENCE_LOG = os.path.join(OUTPUT_DIR, "chain_of_custody.log")
HASH_ALGORITHM = "sha256"


os.makedirs(OUTPUT_DIR, exist_ok=True)


OUTPUT_DIR = "forensic_evidence"
EVIDENCE_LOG = os.path.join(OUTPUT_DIR, "chain_of_custody.log")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COUNTRIES = [
    "United States", "Canada", "United Kingdom", "Australia",
    "Saudi Arabia", "United Arab Emirates", "Egypt", "Turkey", "Iran",
    "Iraq", "Jordan", "Kuwait", "Lebanon", "Oman", "Qatar",
    "Bahrain", "Syria", "Yemen", "Palestine"
]

STATES = {
    "United States": [
        "California", "Texas", "New York", "Florida", "Illinois", "Pennsylvania",
        "Ohio", "Georgia", "North Carolina", "Michigan"
    ],
    "Canada": [
        "Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba", "Saskatchewan",
        "Nova Scotia", "New Brunswick", "Newfoundland and Labrador", "Prince Edward Island"
    ],
    "United Kingdom": ["England", "Scotland", "Wales", "Northern Ireland"],
    "Australia": [
        "New South Wales", "Victoria", "Queensland", "Western Australia",
        "South Australia", "Tasmania", "Northern Territory", "Australian Capital Territory"
    ],
    "Saudi Arabia": ["Riyadh", "Makkah", "Madinah", "Eastern Province", "Jizan"],
    "United Arab Emirates": ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Fujairah"],
    "Egypt": ["Cairo", "Giza", "Alexandria", "Dakahlia", "Aswan"],
    "Turkey": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"],
    "Iran": ["Tehran", "Isfahan", "Mashhad", "Shiraz", "Tabriz"],
    "Iraq": ["Baghdad", "Basra", "Mosul", "Najaf", "Erbil"],
    "Jordan": ["Amman", "Irbid", "Zarqa", "Aqaba", "Mafraq"],
    "Kuwait": ["Al Asimah", "Hawalli", "Farwaniya", "Ahmadi", "Jahra"],
    "Lebanon": ["Beirut", "Mount Lebanon", "North Lebanon", "South Lebanon", "Bekaa"],
    "Oman": ["Muscat", "Dhofar", "Al Batinah", "Al Sharqiyah", "Ad Dakhiliyah"],
    "Qatar": ["Doha", "Al Rayyan", "Al Wakrah", "Umm Salal", "Al Khor"],
    "Bahrain": ["Manama", "Muharraq", "Riffa", "Isa Town", "Hamad Town"],
    "Syria": ["Damascus", "Aleppo", "Homs", "Latakia", "Hama"],
    "Yemen": ["Sana'a", "Aden", "Taiz", "Al Hudaydah", "Hadramaut"],
    "Palestine": ["West Bank", "Gaza Strip"]
}

ZIP_CODES = {
    # United States
    "California": ["90001", "90210", "94016", "92101", "90650"],
    "Texas": ["75001", "77001", "78201", "73301", "79936"],
    "New York": ["10001", "10025", "11201", "12207", "14604"],
    "Florida": ["32003", "33101", "33401", "32801", "33601"],
    "Illinois": ["60007", "60601", "62701", "61820", "60411"],
    "Pennsylvania": ["19104", "15213", "17101", "16801", "18501"],
    "Ohio": ["44101", "43210", "45201", "45502", "43601"],
    "Georgia": ["30301", "31401", "31901", "31701", "39801"],
    "North Carolina": ["27513", "28201", "27701", "28401", "28601"],
    "Michigan": ["48201", "49501", "48901", "49007", "48502"],

    # Canada
    "Ontario": ["M5A 1A1", "M4B 1B3", "L3R 5Z6", "N2L 3G1", "P7B 6G1"],
    "Quebec": ["G1A 0A2", "H2X 1Y9", "J7V 5W1", "J4K 2T1", "G3J 1R5"],
    "British Columbia": ["V5K 0A1", "V6B 4Y1", "V8W 1A3", "V9T 6P1", "V3H 2L9"],
    "Alberta": ["T2P 1M4", "T3K 0L3", "T5J 0Y2", "T6G 2R3", "T8N 1M1"],
    "Manitoba": ["R3B 0X3", "R2C 5N1", "R0G 0A1", "R1A 3P3", "R7A 2H7"],
    "Saskatchewan": ["S4P 3Y2", "S7N 3R2", "S9H 1Y3", "S0G 3K0", "S0E 1E0"],
    "Nova Scotia": ["B3H 1W2", "B4N 3V7", "B0T 1K0", "B2N 5G7", "B9A 2K5"],
    "New Brunswick": ["E2L 4G3", "E3B 6A4", "E1C 1H5", "E7M 2H6", "E5N 4A3"],
    "Newfoundland and Labrador": ["A1B 3S6", "A2V 2R1", "A0P 1E0", "A1N 3K7", "A5A 1B3"],
    "Prince Edward Island": ["C1A 7N8", "C0A 1H7", "C0B 3G4", "C1E 1M5", "C1N 4J5"],

    # United Kingdom
    "England": ["E1 6AN", "SW1A 1AA", "M1 1AE", "B1 1BB", "LS1 3AA"],
    "Scotland": ["EH1 1BB", "G1 2FF", "IV3 8LJ", "AB10 1AN", "DD1 4HN"],
    "Wales": ["CF10 1DD", "LL55 4UR", "SA1 3SN", "NP20 1FS", "LD1 5HG"],
    "Northern Ireland": ["BT1 1AA", "BT48 6HJ", "BT71 4QU", "BT28 3PP", "BT61 7DL"],

    # Australia
    "New South Wales": ["2000", "2150", "2280", "2500", "2747"],
    "Victoria": ["3000", "3122", "3805", "3550", "3977"],
    "Queensland": ["4000", "4217", "4810", "4113", "4870"],
    "Western Australia": ["6000", "6151", "6722", "6530", "6210"],
    "South Australia": ["5000", "5152", "5290", "5114", "5700"],
    "Tasmania": ["7000", "7250", "7310", "7468", "7054"],
    "Northern Territory": ["0800", "0830", "0870", "0822", "0850"],
    "Australian Capital Territory": ["2600", "2617", "2620", "2612", "2913"],
    "Riyadh": ["11564", "12271", "13312", "14231"],
    "Makkah": ["21955", "24321", "22345", "21961"],
    "Madinah": ["42311", "42523", "41311", "41541"],
    "Eastern Province": ["31952", "31512", "31911", "32445"],
    "Jizan": ["82611", "82722", "82843", "82555"],
    "Abu Dhabi": ["51133", "51222", "51311", "51444"],
    "Dubai": ["00000", "11222", "22333", "33444"],
    "Sharjah": ["61111", "61222", "61333", "61444"],
    "Ajman": ["71511", "71622", "71733", "71844"],
    "Fujairah": ["81911", "82022", "82133", "82244"],
    "Cairo": ["11511", "11331", "11865", "11936"],
    "Giza": ["12511", "12611", "12736", "12845"],
    "Alexandria": ["21511", "21611", "21745", "21852"],
    "Dakahlia": ["35511", "35622", "35733", "35844"],
    "Aswan": ["81511", "81622", "81733", "81844"],
    "Istanbul": ["34000", "34110", "34220", "34330"],
    "Ankara": ["06000", "06120", "06230", "06340"],
    "Izmir": ["35000", "35110", "35220", "35330"],
    "Bursa": ["16000", "16110", "16220", "16330"],
    "Antalya": ["07000", "07110", "07220", "07330"],
    "Tehran": ["11369", "11479", "11589", "11699"],
    "Isfahan": ["81746", "81856", "81966", "82076"],
    "Mashhad": ["91999", "92012", "92123", "92234"],
    "Shiraz": ["71364", "71474", "71584", "71694"],
    "Tabriz": ["51699", "51712", "51823", "51934"],
    "Baghdad": ["10001", "10025", "10136", "10247"],
    "Basra": ["61001", "61015", "61126", "61237"],
    "Mosul": ["41001", "41025", "41136", "41247"],
    "Najaf": ["54001", "54025", "54136", "54247"],
    "Erbil": ["44001", "44025", "44136", "44247"],
    "Amman": ["11110", "11220", "11330", "11440"],
    "Irbid": ["22110", "22220", "22330", "22440"],
    "Zarqa": ["13110", "13220", "13330", "13440"],
    "Aqaba": ["77110", "77220", "77330", "77440"],
    "Mafraq": ["26110", "26220", "26330", "26440"],
    "Al Asimah": ["13001", "13102", "13203", "13304"],
    "Hawalli": ["20001", "20112", "20223", "20334"],
    "Farwaniya": ["40001", "40112", "40223", "40334"],
    "Ahmadi": ["60001", "60112", "60223", "60334"],
    "Jahra": ["50001", "50112", "50223", "50334"],
    "Beirut": ["11001", "11102", "11203", "11304"],
    "Mount Lebanon": ["20001", "20112", "20223", "20334"],
    "North Lebanon": ["30001", "30112", "30223", "30334"],
    "South Lebanon": ["40001", "40112", "40223", "40334"],
    "Bekaa": ["50001", "50112", "50223", "50334"],
    "Muscat": ["100", "101", "102", "103"],
    "Dhofar": ["211", "212", "213", "214"],
    "Al Batinah": ["311", "312", "313", "314"],
    "Al Sharqiyah": ["411", "412", "413", "414"],
    "Ad Dakhiliyah": ["511", "512", "513", "514"],
    "Doha": ["00000", "11111", "22222", "33333"],
    "Al Rayyan": ["45000", "45111", "45222", "45333"],
    "Al Wakrah": ["55000", "55111", "55222", "55333"],
    "Umm Salal": ["65000", "65111", "65222", "65333"],
    "Al Khor": ["75000", "75111", "75222", "75333"],
    "Manama": ["1000", "2000", "3000", "4000"],
    "Muharraq": ["5000", "5100", "5200", "5300"],
    "Riffa": ["6000", "6100", "6200", "6300"],
    "Isa Town": ["7000", "7100", "7200", "7300"],
    "Hamad Town": ["8000", "8100", "8200", "8300"],
    "Damascus": ["0000", "1111", "2222", "3333"],
    "Aleppo": ["4000", "4111", "4222", "4333"],
    "Homs": ["5000", "5111", "5222", "5333"],
    "Latakia": ["6000", "6111", "6222", "6333"],
    "Hama": ["7000", "7111", "7222", "7333"],
    "Sana'a": ["0000", "1111", "2222", "3333"],
    "Aden": ["2000", "2011", "2022", "2033"],
    "Taiz": ["3000", "3011", "3022", "3033"],
    "Al Hudaydah": ["4000", "4011", "4022", "4033"],
    "Hadramaut": ["5000", "5011", "5022", "5033"],
    "West Bank": ["1000", "2000", "3000", "4000"],
    "Gaza Strip": ["1000", "2000", "3000", "4000"]
}


class ChainOfCustodyTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """Setup the Chain of Custody tab UI."""

        self.title_bg_image = Image.open("Background.png")
        self.title_bg_image = self.title_bg_image.resize(
            (1200, 290))
        self.title_bg_photo = ImageTk.PhotoImage(self.title_bg_image)

        frame = ttk.LabelFrame(self, padding=(20, 10))
        frame.pack(fill="both", expand=True, padx=0, pady=(
            280, 0))

        title_label = tk.Label(self, image=self.title_bg_photo, text="",
                               compound="center", font=("Arial", 14, "bold"),
                               fg="white", bd=0, relief="flat")
        title_label.place(x=0, y=0)

        ttk.Label(frame, text="Case ID:").place(x=10, y=0)
        self.case_id_entry = ttk.Entry(frame, width=42)
        self.case_id_entry.place(x=120, y=0)

        ttk.Label(frame, text="Full Name:").place(x=10, y=30)
        self.name_entry = ttk.Entry(frame, width=42)
        self.name_entry.place(x=120, y=30)

        ttk.Label(frame, text="Country:").place(x=10, y=60)
        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(
            frame, textvariable=self.country_var, values=COUNTRIES, state="readonly", width=39)
        self.country_dropdown.place(x=120, y=60)
        self.country_dropdown.bind("<<ComboboxSelected>>", self.update_states)

        ttk.Label(frame, text="State:").place(x=10, y=90)
        self.state_var = tk.StringVar()
        self.state_dropdown = ttk.Combobox(
            frame, textvariable=self.state_var, state="readonly", width=39)
        self.state_dropdown.place(x=120, y=90)
        self.state_dropdown.bind(
            "<<ComboboxSelected>>", self.update_zip_codes)

        ttk.Label(frame, text="Zip Code:", style="TLabel").place(x=10, y=120)
        self.zip_var = tk.StringVar()
        self.zip_dropdown = ttk.Combobox(
            frame, textvariable=self.zip_var, state="readonly", width=39, style="TCombobox")
        self.zip_dropdown.place(x=120, y=120)

        ttk.Label(frame, text="Signature:").place(x=10, y=150)
        self.signature_entry = ttk.Entry(frame, width=42)
        self.signature_entry.place(x=120, y=150)

        ttk.Label(frame, text="Image File:").place(x=10, y=180)
        self.image_file_entry = ttk.Entry(frame, width=42, state="readonly")
        self.image_file_entry.place(x=120, y=180)
        ttk.Button(frame, text="   Browse  ",
                   command=self.browse_image_file).place(x=390, y=180)

        ttk.Label(frame, text="Image Size:").place(x=10, y=210)
        self.image_size_label = ttk.Label(frame, text="0 MB")
        self.image_size_label.place(x=120, y=210)

        large_font = ("Arial", 10)

        ttk.Label(frame, text="MD5 Hash:").place(x=10, y=240)
        self.md5_hash_label = ttk.Label(
            frame, text="00000000000000000000000000000000", font=large_font)
        self.md5_hash_label.place(x=120, y=240)

        ttk.Label(frame, text="SHA-256 Hash:").place(x=10, y=270)
        self.sha256_hash_label = ttk.Label(
            frame, text="0000000000000000000000000000000000000000000000000000000000000000", font=large_font)
        self.sha256_hash_label.place(x=120, y=270)

        ttk.Label(frame, text="Additional Feedback:").place(x=600, y=-10)
        self.additional_feedback = tk.Text(
            frame, width=70, height=20, wrap=tk.WORD)
        self.additional_feedback.place(x=590, y=10)

        ttk.Button(frame, text="                Submit              ",
                   command=self.submit_form).place(x=120, y=290)

        ttk.Button(frame, text="          Export to PDF        ",
                   command=self.export_to_pdf).place(x=310, y=290)

    def update_states(self, event):
        """Update the states dropdown based on the selected country."""
        selected_country = self.country_var.get()
        if (selected_country in STATES):
            self.state_dropdown["values"] = STATES[selected_country]
            self.state_dropdown.current(0)
            self.update_zip_codes()

    def update_zip_codes(self, event=None):
        """Update the ZIP codes dropdown based on the selected state."""
        selected_state = self.state_var.get()
        if selected_state in ZIP_CODES:
            self.zip_dropdown["values"] = ZIP_CODES[selected_state]

            self.zip_dropdown.current()

    def browse_image_file(self):
        """Open a file dialog to select an image file and update the entry field."""
        file_path = filedialog.askopenfilename(
            title="Select an Image File",
            filetypes=[("Image Files", "*.img *.jpg *.png *.bmp *.tiff")]
        )
        if file_path:

            self.image_file_entry.config(state="normal")
            self.image_file_entry.delete(0, tk.END)

            self.image_file_entry.insert(0, file_path)
            self.image_file_entry.config(
                state="readonly")

            self.update_image_size(file_path)

            self.calculate_hashes(file_path)

    def update_image_size(self, file_path):
        """Update the image size label with the size of the selected file."""
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            self.image_size_label.config(text=f"{file_size_mb:.2f} MB")
        except Exception as e:
            self.image_size_label.config(text="0 MB")
            print(f"Error updating image size: {e}")

    def calculate_hashes(self, file_path):
        """Calculate and display the MD5 and SHA-256 hashes of the selected file."""
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
                md5_hash = hashlib.md5(file_data).hexdigest()
                sha256_hash = hashlib.sha256(file_data).hexdigest()
                self.md5_hash_label.config(text=md5_hash)
                self.sha256_hash_label.config(text=sha256_hash)
        except Exception as e:
            self.md5_hash_label.config(text="")
            self.sha256_hash_label.config(text="")
            print(f"Error calculating hashes: {e}")

    def submit_form(self):
        """Submit the form and log the chain of custody."""
        case_id = self.case_id_entry.get()
        name = self.name_entry.get()
        country = self.country_var.get()
        state = self.state_var.get()
        zip_code = self.zip_dropdown.get()
        signature = self.signature_entry.get()
        image_file = self.image_file_entry.get()
        image_size = self.image_size_label.cget("text")
        md5_hash = self.md5_hash_label.cget("text")
        sha256_hash = self.sha256_hash_label.cget("text")
        additional_feedback = self.additional_feedback.get(
            "1.0", tk.END).strip()

        if not all([case_id, name, country, state, zip_code, signature, image_file, md5_hash, sha256_hash]):
            messagebox.showerror(
                "Error", "Please fill out all fields and select an image file.")
            return

        if self.case_id_exists(case_id):
            messagebox.showerror(
                "Error", f"Case ID {case_id} already exists. Please use a unique Case ID.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"Date & Time: {timestamp} | "
            f"Case ID: {case_id} | "
            f"Name: {name} | "
            f"Country: {country} | "
            f"State: {state} | "
            f"Zip Code: {zip_code} | "
            f"Signature: {signature} | "
            f"Image File: {os.path.basename(image_file)} | "
            f"Image Size: {image_size} | "
            f"MD5: {md5_hash} | "
            f"SHA-256: {sha256_hash} | "
            f"Additional Feedback: {additional_feedback}\n"
        )
        with open(EVIDENCE_LOG, "a") as log_file:
            log_file.write(log_entry)

        with open("case_log.csv", "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([case_id, md5_hash, sha256_hash])

        messagebox.showinfo("Success", "Chain of custody logged successfully.")

    def case_id_exists(self, case_id):
        """Check if the case ID already exists in case_log.csv."""
        if not os.path.exists("case_log.csv"):
            return False

        with open("case_log.csv", "r") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:

                if row and row[0] == case_id:
                    return True
        return False

    def export_to_pdf(self):
        """Exports the chain of custody log to a professional-looking PDF and clears the log."""

        pdf_filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save PDF Report"
        )
        if not pdf_filename:
            return

        if not os.path.exists(EVIDENCE_LOG):
            messagebox.showerror("Error", "No log entries found.")
            return

        try:
            with open(EVIDENCE_LOG, "r") as log_file:
                log_entries = log_file.readlines()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to read the log file: {str(e)}")
            return

        try:
            with open(EVIDENCE_LOG, "w") as log_file:
                log_file.write("")
            print("Log file cleared successfully.")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to clear the log file: {str(e)}")
            return

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_left_margin(20)
        pdf.set_right_margin(20)

        pdf.set_font("Arial", style="B", size=24)
        pdf.set_fill_color(128, 0, 0)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, "Chain of Custody Report",
                 ln=True, align="C", fill=True)

        if log_entries:
            try:
                case_id = log_entries[0].split(" | ")[1].split(
                    ": ")[1]
            except IndexError:
                case_id = "N/A"
            pdf.set_font("Arial", style="B", size=16)
            pdf.cell(0, 10, f"Case ID: {case_id}",
                     ln=True, align="C", fill=True)

        pdf.set_font("Arial", size=12)
        pdf.cell(
            0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C", fill=True)
        pdf.ln(5)

        pdf.set_font("Arial", style="B", size=14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "Agent Information", ln=True, align="L")
        pdf.ln(5)

        pdf.set_font("Arial", style="B", size=12)
        pdf.set_fill_color(0, 128, 0)
        pdf.set_text_color(255, 255, 255)
        col_widths = [40, 40, 35, 30, 25]
        headers = ["Date & Time", "Name", "Country", "State", "Zip Code"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        for i, line in enumerate(log_entries):
            row_color = (240, 240, 240) if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*row_color)
            columns = line.strip().split(" | ")
            data = {}
            for column in columns:
                if ": " in column:
                    key, value = column.split(": ", 1)
                    data[key.strip()] = value.strip()

            date_time = data.get("Date & Time", "N/A")
            name = data.get("Name", "N/A")
            country = data.get("Country", "N/A")
            state = data.get("State", "N/A")
            zip_code = data.get("Zip Code", "N/A")

            pdf.cell(col_widths[0], 10, date_time,
                     border=1, align="C", fill=True)
            pdf.cell(col_widths[1], 10, name, border=1, align="C", fill=True)
            pdf.cell(col_widths[2], 10, country,
                     border=1, align="C", fill=True)
            pdf.cell(col_widths[3], 10, state, border=1, align="C", fill=True)
            pdf.cell(col_widths[4], 10, zip_code,
                     border=1, align="C", fill=True)
            pdf.ln()

        pdf.ln(10)

        pdf.set_font("Arial", style="B", size=14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "Image Information", ln=True, align="L")
        pdf.ln(5)

        pdf.set_font("Arial", style="B", size=12)
        pdf.set_fill_color(0, 128, 0)
        pdf.set_text_color(255, 255, 255)
        col_widths = [50, 70, 50]
        headers = ["Date & Time", "Image File", "Image Size"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        for i, line in enumerate(log_entries):
            row_color = (240, 240, 240) if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*row_color)
            columns = line.strip().split(" | ")
            data = {}
            for column in columns:
                if ": " in column:
                    key, value = column.split(": ", 1)
                    data[key.strip()] = value.strip()

            date_time = data.get("Date & Time", "N/A")
            image_file = data.get("Image File", "N/A")
            image_size = data.get("Image Size", "N/A")

            pdf.cell(col_widths[0], 10, date_time,
                     border=1, align="C", fill=True)
            pdf.cell(col_widths[1], 10, image_file,
                     border=1, align="C", fill=True)
            pdf.cell(col_widths[2], 10, image_size,
                     border=1, align="C", fill=True)
            pdf.ln()

        pdf.ln(10)

        pdf.set_font("Arial", style="B", size=14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "Hash Information", ln=True, align="L")
        pdf.ln(5)

        pdf.set_font("Arial", style="B", size=12)
        pdf.set_fill_color(0, 128, 0)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(35, 10, "Hash Type", border=1, align="C", fill=True)
        pdf.cell(135, 10, "Hash Value", border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        for i, line in enumerate(log_entries):
            columns = line.strip().split(" | ")
            data = {}
            for column in columns:
                if ": " in column:
                    key, value = column.split(": ", 1)
                    data[key.strip()] = value.strip()

            md5_hash = data.get("MD5", "N/A")
            sha256_hash = data.get("SHA-256", "N/A")

            pdf.set_fill_color(
                240, 240, 240) if i % 2 == 0 else (255, 255, 255)
            pdf.cell(35, 10, "MD5", border=1, align="C", fill=True)
            pdf.cell(135, 10, md5_hash, border=1, align="L", fill=True)
            pdf.ln()

            pdf.set_fill_color(
                240, 240, 240) if i % 2 == 0 else (255, 255, 255)
            pdf.cell(35, 10, "SHA-256", border=1, align="C", fill=True)
            pdf.cell(135, 10, sha256_hash, border=1, align="L", fill=True)
            pdf.ln()

        pdf.ln(10)

        pdf.set_font("Arial", style="B", size=14)
        pdf.set_fill_color(0, 0, 0)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, "Additional Info", ln=True, align="L", fill=True)
        pdf.ln(5)

        pdf.set_font("Arial", style="B", size=14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "Signature", ln=True, align="L")
        pdf.ln(5)

        pdf.set_font("Arial", size=12)
        for line in log_entries:
            columns = line.strip().split(" | ")
            data = {}
            for column in columns:
                if ": " in column:
                    key, value = column.split(": ", 1)
                    data[key.strip()] = value.strip()

            signature = data.get("Signature", "N/A")
            pdf.cell(
                0, 10, f"Mr./Ms. {signature}", ln=True, align="L")

        pdf.output(pdf_filename)
        messagebox.showinfo(
            "Success", f"Chain of custody exported to {pdf_filename}")


def log_chain_of_custody(filename, details=""):
    """Log the creation of a disk image with optional details, ensuring .img filenames are included."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = getpass.getuser()
    log_entry = f"{timestamp} | User: {user} | File/Action: {filename}"

    if filename.endswith(".img"):

        img_filename = os.path.basename(filename)
        log_entry += f" | Disk Image: {img_filename}"
    elif "Output: " in details:

        output_image = details.split("Output: ")[1].split(",")[0]
        img_filename = os.path.basename(output_image)
        log_entry += f" | Disk Image: {img_filename}"

    if details:
        log_entry += f" | Details: {details}"

    log_entry += "\n"

    with open(EVIDENCE_LOG, "a") as log_file:
        log_file.write(log_entry)


def read_chain_of_custody():
    """Read the chain of custody log."""
    if not os.path.exists(EVIDENCE_LOG):
        return "No log entries found."
    with open(EVIDENCE_LOG, "r") as log_file:
        return log_file.read()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_connected_drives():
    """Get a list of connected storage devices with their details."""
    devices = []
    try:
        wmi_obj = wmi.WMI()
        for disk in wmi_obj.Win32_DiskDrive():
            if disk.InterfaceType in ["USB", "SCSI", "IDE"]:
                devices.append({
                    'name': f"\\\\.\\{disk.DeviceID}",
                    'display': f"{disk.DeviceID} - {disk.Model} ({float(disk.Size) / (1024**3):.1f} GB)",
                    'size': float(disk.Size)
                })
    except Exception as e:
        print(f"Error getting drives: {e}")
    return devices

def create_disk_image(source_path, output_image, disk_size_gb, progress_callback, progress_bar, mb_label, speed_label, time_label, app):
    """Create a forensic disk image using direct Windows API access."""
    try:
        desired_access = win32file.GENERIC_READ
        share_mode = win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE
        security_attributes = win32security.SECURITY_ATTRIBUTES()
        security_attributes.Initialize()

        source_handle = win32file.CreateFile(
            source_path,
            desired_access,
            share_mode,
            security_attributes,
            win32file.OPEN_EXISTING,
            win32file.FILE_ATTRIBUTE_NORMAL | win32file.FILE_FLAG_NO_BUFFERING | win32file.FILE_FLAG_SEQUENTIAL_SCAN,
            None
        )

        with open(output_image, 'wb') as dest_file:
            buffer_size = 512 * 1024  # 512KB buffer
            total_bytes = 0
            start_time = datetime.now()

            while True:
                try:
                    rc, buffer = win32file.ReadFile(source_handle, buffer_size)
                    if not buffer:
                        break

                    dest_file.write(buffer)
                    total_bytes += len(buffer)
                    
                    # Calculate progress values
                    progress = (total_bytes / (disk_size_gb * 1024**3)) * 100
                    elapsed_time = (datetime.now() - start_time).total_seconds()
                    speed = total_bytes / (1024**2 * elapsed_time) if elapsed_time > 0 else 0
                    
                    # Update UI in thread-safe way
                    app.after(1, app.update_progress_ui, 
                        progress, 
                        total_bytes / (1024**2), 
                        disk_size_gb * 1024, 
                        speed,
                        elapsed_time,
                        progress_bar,
                        mb_label,
                        speed_label,
                        time_label
                    )

                except Exception as e:
                    raise Exception(f"Read/Write error: {str(e)}")

        win32file.CloseHandle(source_handle)
        app.after(1, progress_callback, "Disk imaging completed successfully!")
        
    except Exception as e:
        error_msg = f"Imaging error: {str(e)} (Error code: {ctypes.get_last_error()})"
        app.after(1, progress_callback, error_msg)
        raise Exception(error_msg)

def calculate_hash(file_path, algorithm=HASH_ALGORITHM):
    """Calculate the cryptographic hash of a file."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def export_to_pdf(self):
    """Exports the chain of custody log to a professional-looking PDF and clears the log."""

    pdf_filename = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")],
        title="Save PDF Report"
    )
    if not pdf_filename:
        return

    if not os.path.exists(EVIDENCE_LOG):
        messagebox.showerror("Error", "No log entries found.")
        return

    try:
        with open(EVIDENCE_LOG, "r") as log_file:
            log_entries = log_file.readlines()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read the log file: {str(e)}")
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", style="B", size=24)
    pdf.set_fill_color(0, 128, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(200, 20, "Chain of Custody Report", ln=True, align="C", fill=True)

    if log_entries:
        case_id = log_entries[0].split(" | ")[1].split(
            ": ")[1]
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, f"Case ID: {case_id}", ln=True, align="C", fill=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(
        200, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C", fill=True)
    pdf.ln(20)

    pdf.set_font("Arial", style="B", size=14)
    pdf.set_fill_color(0, 128, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(200, 10, "Agent Information", ln=True, align="L", fill=True)
    pdf.ln(5)

    pdf.set_font("Arial", style="B", size=12)
    pdf.set_fill_color(0, 128, 0)
    pdf.set_text_color(255, 255, 255)
    col_widths = [40, 40, 40, 40, 40]
    headers = ["Date & Time", "Name", "Country", "State", "Zip Code"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    for i, line in enumerate(log_entries):
        row_color = (240, 240, 240) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*row_color)
        columns = line.strip().split(" | ")
        for j, col in enumerate(columns[:5]):
            pdf.cell(col_widths[j], 10, col.split(": ")[
                     1], border=1, align="C", fill=True)
        pdf.ln()

    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=14)
    pdf.set_fill_color(0, 128, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(200, 10, "Image Information", ln=True, align="L", fill=True)
    pdf.ln(5)

    pdf.set_font("Arial", style="B", size=12)
    pdf.set_fill_color(0, 128, 0)
    pdf.set_text_color(255, 255, 255)
    col_widths = [60, 80, 60]
    headers = ["Date & Time", "Image File", "Image Size"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    for i, line in enumerate(log_entries):
        row_color = (240, 240, 240) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*row_color)
        columns = line.strip().split(" | ")
        pdf.cell(col_widths[0], 10, columns[0], border=1, align="C", fill=True)
        pdf.cell(col_widths[1], 10, columns[7].split(
            ": ")[1], border=1, align="C", fill=True)
        pdf.cell(col_widths[2], 10, columns[8].split(
            ": ")[1], border=1, align="C", fill=True)
        pdf.ln()

    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=14)
    pdf.set_fill_color(0, 128, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(200, 10, "Hash Information", ln=True, align="L", fill=True)
    pdf.ln(5)

    pdf.set_font("Arial", style="B", size=12)
    pdf.set_fill_color(0, 128, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(50, 10, "Hash Type", border=1, align="C", fill=True)
    pdf.cell(140, 10, "Hash Value", border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    for i, line in enumerate(log_entries):
        columns = line.strip().split(" | ")
        md5_hash = columns[9].split(": ")[1]
        sha256_hash = columns[10].split(": ")[1]

        pdf.set_fill_color(240, 240, 240) if i % 2 == 0 else (255, 255, 255)
        pdf.cell(50, 10, "MD5", border=1, align="C", fill=True)
        pdf.cell(140, 10, md5_hash, border=1, align="L", fill=True)
        pdf.ln()

        pdf.set_fill_color(240, 240, 240) if i % 2 == 0 else (255, 255, 255)
        pdf.cell(50, 10, "SHA-256", border=1, align="C", fill=True)
        pdf.cell(140, 10, sha256_hash, border=1, align="L", fill=True)
        pdf.ln()

    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=14)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, "Additional Info", ln=True, align="L", fill=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.set_fill_color(240, 240, 240)
    pdf.multi_cell(200, 10, "This is additional information about the case. It can include notes, comments, or any other relevant details.",
                   border=1, align="L", fill=True)

    pdf.output(pdf_filename)
    messagebox.showinfo(
        "Success", f"Chain of custody exported to {pdf_filename}")

    try:
        with open(EVIDENCE_LOG, "w") as log_file:
            log_file.write("")
        print("Log file cleared successfully.")
    except Exception as e:
        messagebox.showerror(
            "Error", f"Failed to clear the log file: {str(e)}")


class ForensicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Forensic Evidence Acquisition Tool")
        self.geometry("1200x700")
        self.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure('TNotebook.Tab', font=(
            'Comic Sans MS', '12', 'bold'))

        self.tab_control = ttk.Notebook(self)

        self.tab1 = tk.Frame(self.tab_control, bg="#530a0a")
        self.tab2 = ChainOfCustodyTab(self.tab_control)

        self.tab3 = tk.Frame(self.tab_control, bg="#530a0a")

        self.tab_control.add(self.tab1, text="Disk Imaging")
        self.tab_control.add(self.tab2, text="Chain of Custody")
        self.tab_control.add(self.tab3, text="Integrity Verification")

        self.tab_control.pack(expand=1, fill="both")

        self.setup_disk_imaging_tab()
        self.setup_integrity_verification_tab()

    def setup_disk_imaging_tab(self):
        """Setup the Disk Imaging tab."""
        if not is_admin():
            messagebox.showerror("Error", "This application requires administrative privileges")
            self.quit()
            return

        label_font = ('Courier', 13)
        button_font = ('Courier', 13, 'bold')
        label_color = "#cb1717"
        button_bg = "#530a0a"
        button_fg = "#cb1717"
        button_relief = "flat"
        button_cursor = "hand2"
        button_width = 20
        button_height = 2
        label1 = tk.Label(self.tab1, text="ジ",
                          fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        label1.place(x=70, y=50)

        label2 = tk.Label(self.tab1, text="ン",
                          fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        label2.place(x=300, y=150)

        label3 = tk.Label(self.tab1, text="ク",
                          fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        label3.place(x=600, y=250)

        label4 = tk.Label(self.tab1, text="ス",
                          fg="#cb1717", bg="#530a0a", font=("Arial", 17))
        label4.place(x=100, y=150)

        label5 = tk.Label(self.tab1, text="ジ",
                          fg="#cb1717", bg="#530a0a", font=("Arial", 19))
        label5.place(x=650, y=100)

        label6 = tk.Label(self.tab1, text="ン",
                          fg="#cb1717", bg="#530a0a", font=("Arial", 21))
        label6.place(x=200, y=500)

        label7 = tk.Label(self.tab1, text="ク",
                          fg="#cb1717", bg="#530a0a", font=("Arial", 16))
        label7.place(x=550, y=50)

        label8 = tk.Label(self.tab1, text="ス",
                          fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        label8.place(x=700, y=400)

        label9 = tk.Label(self.tab1, text="ク",
                          fg="#cb1717", bg="#530a0a", font=("Arial", 15))
        label9.place(x=50, y=450)

        label10 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 13))
        label10.place(x=150, y=300)

        label11 = tk.Label(self.tab1, text="ク",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 17))
        label11.place(x=600, y=400)

        label12 = tk.Label(self.tab1, text="ク",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        label12.place(x=50, y=100)

        label13 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 21))
        label13.place(x=700, y=250)

        label16 = tk.Label(self.tab1, text="ン",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        label16.place(x=100, y=500)

        label17 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 13))
        label17.place(x=650, y=350)

        label19 = tk.Label(self.tab1, text="ク",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 11))
        label19.place(x=300, y=400)

        label20 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 12))
        label20.place(x=850, y=550)

        label21 = tk.Label(self.tab1, text="ン",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 13))
        label21.place(x=900, y=250)

        label22 = tk.Label(self.tab1, text="ク",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 15))
        label22.place(x=800, y=150)

        label23 = tk.Label(self.tab1, text="ン",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 16))
        label23.place(x=950, y=300)

        label24 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 17))
        label24.place(x=850, y=200)

        label25 = tk.Label(self.tab1, text="ク",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 18))
        label25.place(x=900, y=500)

        label26 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 13))
        label26.place(x=850, y=100)

        label27 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        label27.place(x=720, y=250)

        label28 = tk.Label(self.tab1, text="ク",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 19))
        label28.place(x=1030, y=180)

        label29 = tk.Label(self.tab1, text="ン",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 12))
        label29.place(x=880, y=450)

        label30 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 16))
        label30.place(x=920, y=380)

        label31 = tk.Label(self.tab1, text="ク",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 20))
        label31.place(x=1100, y=320)

        label32 = tk.Label(self.tab1, text="ジ",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 15))
        label32.place(x=780, y=220)

        # label33 = tk.Label(self.tab1, text="ジ",
        #                    fg="#cb1717", bg="#530a0a", font=("Arial", 18))
        # label33.place(x=960, y=270)

        # label34 = tk.Label(self.tab1, text="ス",
        #                    fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        # label34.place(x=830, y=160)

        # label35 = tk.Label(self.tab1, text="ク",
        #                    fg="#cb1717", bg="#530a0a", font=("Arial", 17))
        # label35.place(x=1010, y=400)

        label36 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 12))
        label36.place(x=700, y=350)

        label37 = tk.Label(self.tab1, text="ジ",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        label37.place(x=720, y=600)

        # label38 = tk.Label(self.tab1, text="ク",
        #                    fg="#cb1717", bg="#530a0a", font=("Arial", 16))
        # label38.place(x=1030, y=650)

        # label39 = tk.Label(self.tab1, text="ス",
        #                    fg="#cb1717", bg="#530a0a", font=("Arial", 18))
        # label39.place(x=880, y=700)

        label40 = tk.Label(self.tab1, text="ジ",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 12))
        label40.place(x=920, y=750)

        label41 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 20))
        label41.place(x=1100, y=620)

        label42 = tk.Label(self.tab1, text="ク",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 15))
        label42.place(x=780, y=670)

        label43 = tk.Label(self.tab1, text="ジ",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 18))
        label43.place(x=960, y=720)

        label44 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 14))
        label44.place(x=830, y=770)

        label45 = tk.Label(self.tab1, text="ク",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 17))
        label45.place(x=1010, y=780)

        label46 = tk.Label(self.tab1, text="ス",
                           fg="#cb1717", bg="#530a0a", font=("Arial", 12))
        label46.place(x=700, y=790)

        welcome_label = tk.Label(
            self.tab1,
            text='AutoChain',
            fg="#cb1717",
            bg="#530a0a",
            font=("Courier", 90, "bold")
        )
        welcome_label.place(x=330, y=50)

        tk.Label(self.tab1, text="Select Drive:",
                 font=label_font, width=button_width, height=button_height, bg="#530a0a", fg=label_color).place(x=300, y=300)

        self.drive_var = tk.StringVar()
        self.drive_dropdown = ttk.Combobox(
            self.tab1, 
            textvariable=self.drive_var,
            state="readonly", 
            font=('Courier', 13), 
            width=18
        )
        self.drive_dropdown.place(x=480, y=300)
        self.drives_info = []  # Store drive information
        self.refresh_drives()

        refresh_btn = tk.Button(self.tab1,
                                text="🔄",
                                command=self.refresh_drives,
                                font=button_font,
                                bg=button_bg,
                                fg=button_fg,

                                relief=button_relief,
                                cursor=button_cursor,
                                bd=0, width=2, height=2,
                                highlightthickness=0)
        refresh_btn.place(x=700, y=300)

        tk.Label(self.tab1, text="Output Image:",
                 font=label_font, bg="#530a0a", fg=label_color).place(x=335, y=350)

        self.output_image_entry = tk.Entry(
            self.tab1, width=20, font=label_font)
        self.output_image_entry.place(x=480, y=350)

        browse_btn = tk.Button(self.tab1,
                               text="📂",
                               command=self.browse_output_image,
                               font=button_font,
                               bg=button_bg,
                               fg=button_fg,
                               relief=button_relief,
                               cursor=button_cursor,
                               bd=0, width=2, height=2,
                               highlightthickness=0)
        browse_btn.place(x=700, y=350)

        tk.Label(self.tab1, text="Disk Size (GB):",
                 font=label_font, bg="#530a0a", fg=label_color).place(x=315, y=400)

        self.disk_size_entry = tk.Entry(self.tab1, width=20, font=label_font)
        self.disk_size_entry.place(x=480, y=400)

        self.progress_label = tk.Label(self.tab1, text="",
                                       font=label_font, bg="#530a0a", fg=label_color)
        self.progress_label.place(x=510, y=580)

        self.progress_bar = ttk.Progressbar(
            self.tab1, orient="horizontal", length=1200, mode="determinate")
        self.progress_bar.place(x=0, y=650)

        self.mb_label = tk.Label(self.tab1, text="MB Copied: 0.00 / 0.00",
                                 font=label_font, bg="#530a0a", fg=label_color)
        self.speed_label = tk.Label(self.tab1, text="Speed: 0.00 MB/sec",
                                    font=label_font, bg="#530a0a", fg=label_color)
        self.time_label = tk.Label(self.tab1, text="Estimated Time Remaining: --:--:--",
                                   font=label_font, bg="#530a0a", fg=label_color)

        create_btn = tk.Button(self.tab1,
                               text="💾 Create Disk Image",
                               command=self.start_disk_imaging,
                               font=button_font,
                               bg=button_bg,
                               fg=button_fg,
                               width=button_width,
                               height=button_height,
                               relief=button_relief,
                               cursor=button_cursor,
                               bd=0,
                               highlightthickness=0)
        create_btn.place(x=480, y=530)

        for button in (refresh_btn, browse_btn, create_btn):
            button.bind("<Enter>", lambda e, btn=button: btn.configure(
                bg="#6b2e85"))
            button.bind("<Leave>", lambda e, btn=button: btn.configure(
                bg=button_bg))

    def start_disk_imaging(self):
        """Start the disk imaging process in a background thread."""
        selected_drive = None
        for drive in self.drives_info:
            if drive['display'] == self.drive_var.get():
                selected_drive = drive['name']
                break
                
        if not selected_drive:
            messagebox.showerror("Error", "Please select a valid drive")
            return
            
        output_image = self.output_image_entry.get()
        disk_size_gb = self.disk_size_entry.get()

        if not output_image or not disk_size_gb:
            messagebox.showerror(
                "Error", "Please provide an output image path and enter the disk size.")
            return

        try:
            disk_size_gb = float(disk_size_gb)
        except ValueError:
            messagebox.showerror("Error", "Disk size must be a valid number.")
            return

        self.mb_label.place(x=460, y=450)
        self.speed_label.place(x=500, y=470)
        self.time_label.place(x=450, y=490)

        self.progress_bar["value"] = 0
        self.progress_label.config(text="Starting disk imaging...")
        self.mb_label.config(text="MB Copied: 0.00 / 0.00")
        self.speed_label.config(text="Speed: 0.00 MB/sec")
        self.time_label.config(text="Estimated Time Remaining: --:--:--")

        # Create an instance method to handle the disk imaging
        def imaging_task():
            try:
                create_disk_image(
                    selected_drive, 
                    output_image, 
                    disk_size_gb, 
                    self.update_progress,
                    self.progress_bar, 
                    self.mb_label, 
                    self.speed_label, 
                    self.time_label,
                    self  # Pass the app instance
                )
            except Exception as e:
                self.after(1, self.update_progress, f"Error: {str(e)}")
                self.after(1, messagebox.showerror, "Error", f"Imaging failed: {str(e)}")

        imaging_thread = threading.Thread(
            target=imaging_task,
            daemon=True
        )
        imaging_thread.start()

    def update_progress_ui(self, progress, mb_copied, total_mb, speed, elapsed_time, progress_bar, mb_label, speed_label, time_label):
        """Update the progress UI elements in a thread-safe way."""
        progress_bar["value"] = progress
        mb_label.config(text=f"MB Copied: {mb_copied:.2f} / {total_mb:.2f}")
        speed_label.config(text=f"Speed: {speed:.2f} MB/sec")
        
        if speed > 0:
            remaining_mb = total_mb - mb_copied
            estimated_seconds = remaining_mb / speed
            time_label.config(text=f"Estimated Time Remaining: {str(timedelta(seconds=int(estimated_seconds)))}")

    def setup_chain_of_custody_tab(self):
        """Setup the Chain of Custody tab."""
        frame = ttk.LabelFrame(self.tab2, text="Chain of Custody")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_text = tk.Text(frame, wrap=tk.WORD,
                                width=80, height=20, state=tk.DISABLED)
        self.log_text.pack(padx=10, pady=10)

        ttk.Button(frame, text="Refresh Log",
                   command=self.refresh_log).pack(pady=5)
        ttk.Button(frame, text="Export to PDF",
                   command=export_to_pdf).pack(pady=5)

    def setup_integrity_verification_tab(self):
        """Setup the Integrity Verification tab with tk widgets."""

        label_font = ('Courier', 13)
        button_font = ('Courier', 13, 'bold')
        entry_font = ('Courier', 12)
        label_color = "#cb1717"
        button_bg = "#530a0a"
        button_fg = "#cb1717"
        entry_bg = "#1f1e1e"
        entry_fg = "#ffffff"

        self.tab3.configure(bg="#530a0a")

        welcome_label = tk.Label(
            self.tab3,
            text='Integrity Verification',
            fg="#cb1717",
            bg="#530a0a",
            font=("Courier", 40, "bold")
        )
        welcome_label.pack(pady=(20, 40))

        tk.Label(
            self.tab3,
            text="Case ID:",
            font=label_font,
            bg="#530a0a",
            fg=label_color
        ).place(x=300, y=150)

        self.case_id_entry = tk.Entry(
            self.tab3,
            width=39,
            font=entry_font,
            bg=entry_bg,
            fg=entry_fg,
            relief="flat"
        )
        self.case_id_entry.place(x=400, y=150)

        tk.Label(
            self.tab3,
            text="Image File:",
            font=label_font,
            bg="#530a0a",
            fg=label_color
        ).place(x=275, y=200)

        self.image_file_entry = tk.Entry(
            self.tab3,
            width=23,
            font=entry_font,
            bg=entry_bg,
            fg=entry_fg,
            relief="flat"
        )
        self.image_file_entry.place(x=400, y=200)

        browse_btn = tk.Button(
            self.tab3,
            text="📂 Browse",
            command=self.browse_image_file,
            font=button_font,
            bg=button_bg,
            fg=button_fg,
            relief="flat",
            cursor="hand2",
            bd=0,
            width=15,
            height=2
        )
        browse_btn.place(x=640, y=190)

        self.results_label = tk.Label(
            self.tab3,
            text="Verification Results will appear here",
            font=label_font,
            bg="#530a0a",
            fg=label_color,
            wraplength=800,
            justify="left"
        )
        self.results_label.place(x=430, y=300)

        verify_btn = tk.Button(
            self.tab3,
            text="🔍 Verify Integrity",
            command=self.verify_integrity,
            font=button_font,
            bg=button_bg,
            fg=button_fg,
            relief="flat",
            cursor="hand2",
            bd=0,
            width=20,
            height=2
        )
        verify_btn.place(x=500, y=575)

        for button in (browse_btn, verify_btn):
            button.bind("<Enter>", lambda e,
                        btn=button: btn.configure(bg="#6b2e85"))
            button.bind("<Leave>", lambda e,
                        btn=button: btn.configure(bg=button_bg))

        self.add_decorative_elements(self.tab3)

    def add_decorative_elements(self, parent):
        """Add decorative symbols to the integrity verification tab."""
        symbols = ["ス", "ク", "ク", "ス", "ジ", "ン",
                   "ス", "ス", "ジ", "ン", "ジ", "ク", "ス", "ン", "ジ"]
        positions = [
            (70, 50), (120, 150), (600, 250), (100, 150), (650, 100),
            (200, 500), (550, 70), (700, 400), (50, 450), (150, 300),
            (600, 400), (50, 100), (700, 250), (800, 150), (950, 300)
        ]

        for symbol, (x, y) in zip(symbols, positions):
            tk.Label(
                parent,
                text=symbol,
                fg="#cb1717",
                bg="#530a0a",
                font=("Arial", 14)
            ).place(x=x, y=y)

    def refresh_drives(self):
        """Refresh the list of connected drives."""
        self.drives_info = get_connected_drives()
        self.drive_dropdown["values"] = [drive['display'] for drive in self.drives_info]
        if self.drives_info:
            self.drive_dropdown.current(0)

    def browse_output_image(self):
        """Browse for the output image file and enforce .img extension."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".img",
            filetypes=[("Image Files", "*.img")]
        )
        if file_path:

            file_path = os.path.splitext(file_path)[0] + ".img"
            self.output_image_entry.delete(0, tk.END)
            self.output_image_entry.insert(0, file_path)

    def update_progress(self, message):
        """Update the progress label."""
        self.progress_label.config(text=message)
        self.update()

    def refresh_log(self):
        """Refresh the chain of custody log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, read_chain_of_custody())
        self.log_text.config(state=tk.DISABLED)

    def browse_image_file(self):
        """Browse for an image file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.img")])
        if file_path:
            self.image_file_entry.delete(0, tk.END)
            self.image_file_entry.insert(0, file_path)

    def verify_integrity(self):
        """Verify the integrity of the disk image against case_log.csv records."""
        case_id = self.case_id_entry.get()
        image_file = self.image_file_entry.get()

        if not case_id or not image_file:
            messagebox.showerror(
                "Error", "Please enter both Case ID and select an image file.")
            return

        try:

            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()

            with open(image_file, 'rb') as f:
                while chunk := f.read(8192):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)

            current_md5 = md5_hash.hexdigest()
            current_sha256 = sha256_hash.hexdigest()

            found = False
            with open('case_log.csv', 'r') as csv_file:
                for line in csv_file:
                    stored_case_id, stored_md5, stored_sha256 = line.strip().split(',')
                    if stored_case_id == case_id:
                        found = True
                        break

            if not found:
                self.results_label.config(
                    text=f"❌ Case ID {case_id} not found in records.",
                    fg="#ff0000"
                )
                return

            results = []
            results.append(f"Case ID: {case_id}\n")
            results.append(
                f"MD5 Match: {'✅' if current_md5 == stored_md5 else '❌'}")
            results.append(
                f"SHA256 Match: {'✅' if current_sha256 == stored_sha256 else '❌'}\n")
            results.append("Current Hashes:")
            results.append(f"MD5: {current_md5}")
            results.append(f"SHA256: {current_sha256}\n")
            results.append("Stored Hashes:")
            results.append(f"MD5: {stored_md5}")
            results.append(f"SHA256: {stored_sha256}")

            self.results_label.config(
                text="\n".join(results),
                fg="#00ff00" if (
                    current_md5 == stored_md5 and current_sha256 == stored_sha256) else "#ff0000"
            )
            self.results_label.place(x=275, y=300)  # Adjust 'x' to move it to the left

        except FileNotFoundError:
            messagebox.showerror(
                "Error", "Case log file or image file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Verification failed: {str(e)}")


if __name__ == "__main__":
    app = ForensicApp()
    app.mainloop()