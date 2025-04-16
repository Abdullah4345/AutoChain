from tkinter import filedialog
import os
import subprocess
import hashlib
from datetime import datetime, timedelta
import getpass
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import threading
import re
from fpdf import FPDF
from PIL import Image, ImageTk
import csv
import hashlib
import sys
import psutil
import time

# Conditionally import Windows-specific modules
if os.name == "nt":
    try:
        import win32api
        import win32file
    except ImportError:
        print("Warning: pywin32 package not installed. Some Windows-specific features may not work.")
        # Provide dummy values for Windows constants if needed
        class win32file:
            DRIVE_REMOVABLE = 2
            DRIVE_FIXED = 3

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
        # Apply the style for black background
        super().__init__(parent, style='Black.TFrame') 
        self.parent = parent
        # Remove the direct configure call for bg
        # self.configure(bg="black") 
        self.setup_ui()

    def setup_ui(self):
        """Setup the Chain of Custody tab UI with a resizable grid layout."""

        # --- Style Definitions ---
        label_font = ('Courier', 12) # Slightly smaller font for this tab
        entry_font = ('Courier', 11)
        hash_font = ('Courier', 10)
        button_font = ('Courier', 11, 'bold')
        label_fg = "white"
        page_bg = "black"
        # Use ttk styles for themed widgets where possible
        style = ttk.Style()
        # Define the style for the black frame background
        style.configure('Black.TFrame', background=page_bg)
        style.configure("TLabel", background=page_bg, foreground=label_fg, font=label_font)
        style.configure("TButton", font=button_font)
        style.configure("TEntry")
        style.configure("TCombobox")
        style.configure("TProgressbar")

        # --- Title Image (Remains placed at top of self.tab2) ---
        self.title_bg_image = Image.open("Background.png")
        self.title_bg_image = self.title_bg_image.resize((1200, 290))
        self.title_bg_photo = ImageTk.PhotoImage(self.title_bg_image)
        title_label = tk.Label(self, image=self.title_bg_photo, bd=0)
        title_label.place(x=0, y=0) # Title image stays fixed

        # --- Main Content Frame (Resizable) ---
        # Use tk.Frame for easier background setting
        content_frame = tk.Frame(self, bg=page_bg)
        # Pack below the title image, filling the rest
        content_frame.pack(fill="both", expand=True, padx=10, pady=(295, 10))

        # Configure grid columns: 0 for labels/entries, 1 for feedback text
        content_frame.grid_columnconfigure(0, weight=1, minsize=450) # Left side forms
        content_frame.grid_columnconfigure(1, weight=2) # Right side feedback expands more
        # Configure grid rows
        content_frame.grid_rowconfigure(0, weight=1) # Let the main content area expand vertically
        content_frame.grid_rowconfigure(1, weight=0) # Buttons/Progress at bottom

        # --- Left Column Frame (Inputs & Hashes) ---
        left_frame = tk.Frame(content_frame, bg=page_bg)
        left_frame.grid(row=0, column=0, padx=(10, 20), pady=10, sticky="nsew")

        # Configure grid within left_frame
        left_frame.grid_columnconfigure(1, weight=1) # Allow entries/combos to expand a bit

        # Input Fields using grid
        row_num = 0
        ttk.Label(left_frame, text="Case ID:").grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
        self.case_id_entry = ttk.Entry(left_frame, width=40, font=entry_font)
        self.case_id_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        row_num += 1

        ttk.Label(left_frame, text="Full Name:").grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(left_frame, width=40, font=entry_font)
        self.name_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        row_num += 1

        # (Continuing from previous edit in left_frame setup)
        row_num = 2 # Start after Case ID and Full Name

        ttk.Label(left_frame, text="Country:").grid(row=row_num, column=0, padx=5, pady=3, sticky="w") # Apply pady=3
        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(left_frame, textvariable=self.country_var, values=COUNTRIES, state="readonly", width=38, font=entry_font)
        self.country_dropdown.grid(row=row_num, column=1, padx=5, pady=3, sticky="ew") # Apply pady=3
        self.country_dropdown.bind("<<ComboboxSelected>>", self.update_states)
        row_num += 1

        ttk.Label(left_frame, text="State:").grid(row=row_num, column=0, padx=5, pady=3, sticky="w") # Apply pady=3
        self.state_var = tk.StringVar()
        self.state_dropdown = ttk.Combobox(left_frame, textvariable=self.state_var, state="readonly", width=38, font=entry_font)
        self.state_dropdown.grid(row=row_num, column=1, padx=5, pady=3, sticky="ew") # Apply pady=3
        self.state_dropdown.bind("<<ComboboxSelected>>", self.update_zip_codes)
        row_num += 1

        ttk.Label(left_frame, text="Zip Code:").grid(row=row_num, column=0, padx=5, pady=3, sticky="w") # Apply pady=3
        self.zip_var = tk.StringVar()
        self.zip_dropdown = ttk.Combobox(left_frame, textvariable=self.zip_var, state="readonly", width=38, font=entry_font)
        self.zip_dropdown.grid(row=row_num, column=1, padx=5, pady=3, sticky="ew") # Apply pady=3
        row_num += 1

        ttk.Label(left_frame, text="Signature:").grid(row=row_num, column=0, padx=5, pady=3, sticky="w") # Apply pady=3
        self.signature_entry = ttk.Entry(left_frame, width=40, font=entry_font)
        self.signature_entry.grid(row=row_num, column=1, padx=5, pady=3, sticky="ew") # Apply pady=3
        row_num += 1

        # Image File Entry & Button Frame
        image_frame = tk.Frame(left_frame, bg=page_bg)
        image_frame.grid(row=row_num, column=0, columnspan=2, sticky="ew", pady=3) # Apply pady=3
        image_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(image_frame, text="Image File:").grid(row=0, column=0, padx=5, sticky="w") # Inner padding okay
        self.image_file_entry = ttk.Entry(image_frame, width=28, state="readonly", font=entry_font)
        self.image_file_entry.grid(row=0, column=1, padx=5, sticky="ew") # Inner padding okay
        ttk.Button(image_frame, text="Browse", style="TButton", command=self.browse_image_file).grid(row=0, column=2, padx=5) # Inner padding okay
        row_num += 1

        # Image Size
        ttk.Label(left_frame, text="Image Size:").grid(row=row_num, column=0, padx=5, pady=3, sticky="w") # Apply pady=3
        self.image_size_label = ttk.Label(left_frame, text="0 MB")
        self.image_size_label.grid(row=row_num, column=1, padx=5, pady=3, sticky="w") # Apply pady=3
        row_num += 1

        # Hash Labels (Keep slightly larger padding for separation)
        ttk.Label(left_frame, text="MD5 Hash:").grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
        self.md5_hash_label = ttk.Label(left_frame, text="-" * 32, font=hash_font, wraplength=300, justify="left")
        self.md5_hash_label.grid(row=row_num, column=1, padx=5, pady=2, sticky="w")
        row_num += 1

        ttk.Label(left_frame, text="SHA-256 Hash:").grid(row=row_num, column=0, padx=5, pady=5, sticky="w")
        self.sha256_hash_label = ttk.Label(left_frame, text="-" * 64, font=hash_font, wraplength=300, justify="left")
        self.sha256_hash_label.grid(row=row_num, column=1, padx=5, pady=2, sticky="w")
        row_num += 1

        # --- Right Column Frame (Feedback Text) ---
        right_frame = tk.Frame(content_frame, bg=page_bg)
        right_frame.grid(row=0, column=1, padx=(10, 10), pady=10, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1) # Text area row expands
        right_frame.grid_columnconfigure(0, weight=1) # Text area column expands

        ttk.Label(right_frame, text="Additional Feedback:").grid(row=0, column=0, padx=5, pady=5, sticky="sw")
        self.additional_feedback = tk.Text(
            right_frame, wrap=tk.WORD, background="#202020", foreground="white", font=entry_font,
            insertbackground='white', relief="solid", bd=1)
        self.additional_feedback.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # --- Bottom Frame (Buttons & Progress) ---
        bottom_frame = tk.Frame(content_frame, bg=page_bg)
        bottom_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        # Center buttons
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=0)
        bottom_frame.grid_columnconfigure(2, weight=0)
        bottom_frame.grid_columnconfigure(3, weight=1)

        # Buttons
        button_inner_frame = tk.Frame(bottom_frame, bg=page_bg)
        button_inner_frame.grid(row=0, column=1, columnspan=2) # Place in center cols

        submit_btn = ttk.Button(button_inner_frame, text="Submit", style="TButton", command=self.submit_form)
        submit_btn.pack(side="left", padx=10, pady=5)
        export_btn = ttk.Button(button_inner_frame, text="Export to PDF", style="TButton", command=self.export_to_pdf)
        export_btn.pack(side="left", padx=10, pady=5)

        # Progress Bar
        progress_frame = tk.Frame(bottom_frame, bg=page_bg)
        progress_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        progress_frame.grid_columnconfigure(1, weight=1)

        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.grid(row=0, column=0, padx=(0, 10))
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=0, column=1, sticky="ew")

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
            print(f"\n=== Calculating hashes for {file_path} ===")
            
            # Initialize hash objects
            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()
            
            # Get file size for progress calculation
            file_size = os.path.getsize(file_path)
            total_chunks = file_size // (4 * 1024 * 1024)  # Number of 4MB chunks
            processed_chunks = 0
            
            # Use a much larger chunk size for better performance
            chunk_size = 4 * 1024 * 1024  # 4MB chunks
            
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    # Update hashes
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)
                    
                    # Update progress
                    processed_chunks += 1
                    progress = (processed_chunks / total_chunks) * 100
                    
                    # Update progress bar and label if they exist
                    if hasattr(self, 'progress_bar') and hasattr(self, 'progress_label'):
                        self.progress_bar["value"] = progress
                        self.progress_label.config(text=f"Calculating hashes: {progress:.1f}%")
                        self.update()
            
            # Get hex digests
            md5_digest = md5_hash.hexdigest()
            sha256_digest = sha256_hash.hexdigest()
            
            print(f"MD5 Hash: {md5_digest}")
            print(f"SHA-256 Hash: {sha256_digest}")
            
            # Update the labels
            self.md5_hash_label.config(text=md5_digest)
            self.sha256_hash_label.config(text=sha256_digest)
            
            # Reset progress bar and label if they exist
            if hasattr(self, 'progress_bar') and hasattr(self, 'progress_label'):
                self.progress_bar["value"] = 0
                self.progress_label.config(text="")
            
        except Exception as e:
            error_msg = f"Error calculating hashes: {str(e)}"
            print(f"Error: {error_msg}")
            self.md5_hash_label.config(text="Error calculating hash")
            self.sha256_hash_label.config(text="Error calculating hash")
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text="Error occurred")
            messagebox.showerror("Error", error_msg)

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
        
        # Write to evidence log
        with open(EVIDENCE_LOG, "a") as log_file:
            log_file.write(log_entry)

        # Create or update case_log.csv
        try:
            # Check if case_log.csv exists, if not create it with headers
            if not os.path.exists("case_log.csv"):
                with open("case_log.csv", "w", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["Case ID", "MD5 Hash", "SHA-256 Hash"])
            
            # Append the new case data
            with open("case_log.csv", "a", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([case_id, md5_hash, sha256_hash])
                
            print(f"Case {case_id} logged successfully in case_log.csv")
        except Exception as error:
            print(f"Error writing to case_log.csv: {error}")
            messagebox.showerror("Error", f"Failed to update case log: {str(error)}")
            return

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

        pdf.set_font("Arial", size=9)

        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(0, 0, 0)
        for line in log_entries:
            columns = line.strip().split(" | ")
            data = {}
            for column in columns:
                if ": " in column:
                    key, value = column.split(": ", 1)
                    data[key.strip()] = value.strip()

            additional_feedback = data.get(
                "Additional Feedback", "No additional feedback provided.")
            pdf.multi_cell(0, 10, additional_feedback,
                           border=1, align="L", fill=True)

        pdf.ln(10)
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


def create_disk_image(disk_device, output_image, disk_size_gb, progress_callback, progress_bar, mb_label, speed_label, time_label):
    """Create a forensic disk image using dd."""
    process = None
    try:
        print(f"\n=== Starting Disk Imaging ===")
        print(f"Source device: {disk_device}")
        print(f"Output image: {output_image}")
        print(f"Disk size: {disk_size_gb} GB")

        # Check if source device exists
        if not os.path.exists(disk_device):
            error_msg = f"Source device {disk_device} does not exist"
            print(f"Error: {error_msg}")
            progress_callback(error_msg)
            return

        # Check if we have write permission for output directory
        output_dir = os.path.dirname(output_image)
        if not os.access(output_dir, os.W_OK):
            error_msg = f"No write permission for output directory: {output_dir}"
            print(f"Error: {error_msg}")
            progress_callback(error_msg)
            return

        # Log the start of imaging
        log_chain_of_custody("Disk Imaging Started",
                             f"Device: {disk_device}, Output: {output_image}")
        
        # Create the dd command with conv=fsync to ensure data is written to disk
        command = ["sudo", "dd", f"if={disk_device}",
                  f"of={output_image}", "bs=4M", "status=progress", "conv=fsync"]
        print(f"Running command: {' '.join(command)}")

        # Start the dd process with shell=True to ensure proper process handling
        process = subprocess.Popen(
            ' '.join(command),  # Join command into a single string
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )

        start_time = datetime.now()
        total_size_bytes = disk_size_gb * 1024 * 1024 * 1024
        total_size_mb = disk_size_gb * 1024

        progress = 0
        last_progress = 0
        no_progress_count = 0
        max_no_progress = 20  # Maximum number of iterations with no progress
        max_runtime = 3600  # Maximum runtime in seconds (1 hour)

        print("Starting to monitor process...")

        while True:
            # Check if process has finished
            if process.poll() is not None:
                print("Process has finished")
                break

            # Check if we've exceeded maximum runtime
            elapsed_time = datetime.now() - start_time
            if elapsed_time.total_seconds() > max_runtime:
                print("Maximum runtime exceeded, terminating process...")
                process.terminate()
                error_msg = "Disk imaging exceeded maximum runtime"
                progress_callback(error_msg)
                return

            # Read output without blocking
            try:
                output = process.stderr.readline()
                if not output:
                    # If no output for a while, check if process is still running
                    if process.poll() is not None:
                        print("Process finished with no more output")
                        break
                    time.sleep(0.1)  # Small delay to prevent CPU hogging
                    continue

                print(f"Process output: {output.strip()}")  # Debug output

                match = re.search(r"(\d+) bytes", output)
                if match:
                    copied_bytes = int(match.group(1))
                    copied_mb = copied_bytes / (1024 * 1024)

                    progress = (copied_bytes / total_size_bytes) * 100
                    print(f"Progress: {progress:.2f}%")  # Debug output
                    
                    # Check for progress
                    if progress == last_progress:
                        no_progress_count += 1
                        if no_progress_count > max_no_progress:
                            error_msg = "Disk imaging appears to be stuck"
                            print(f"Error: {error_msg}")
                            process.terminate()
                            progress_callback(error_msg)
                            return
                    else:
                        no_progress_count = 0
                        last_progress = progress

                    progress_bar["value"] = progress

                    elapsed_time = datetime.now() - start_time
                    if elapsed_time.total_seconds() > 0:
                        mb_per_sec = copied_mb / elapsed_time.total_seconds()
                    else:
                        mb_per_sec = 0

                    mb_label.config(
                        text=f"MB Copied: {copied_mb:.2f} / {total_size_mb:.2f}")
                    speed_label.config(text=f"Speed: {mb_per_sec:.2f} MB/sec")

                    if copied_bytes > 0 and elapsed_time.total_seconds() > 0:
                        remaining_time = (elapsed_time.total_seconds() / copied_bytes) * (total_size_bytes - copied_bytes)
                        time_label.config(
                            text=f"Estimated Time Remaining: {str(timedelta(seconds=int(remaining_time)))}")
                    else:
                        time_label.config(
                            text="Estimated Time Remaining: Calculating...")

                progress_callback(f"Progress: {progress:.2f}%")
            except Exception as error:
                print(f"Error reading process output: {error}")
                continue

        print("Waiting for process to complete...")
        # Wait for process to complete with timeout
        try:
            process.wait(timeout=30)  # Wait up to 30 seconds for process to finish
            print("Process completed successfully")
        except subprocess.TimeoutExpired:
            print("Process did not finish in time, terminating...")
            process.terminate()
            error_msg = "Disk imaging process timed out"
            progress_callback(error_msg)
            return

        # Force process termination if it's still running
        if process.poll() is None:
            print("Forcing process termination...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

        # Check if the process completed successfully
        if process.returncode != 0:
            error_msg = f"dd command failed with return code {process.returncode}"
            print(f"Error: {error_msg}")
            progress_callback(error_msg)
            return

        print("Verifying output file...")
        # Verify the output file was created and has the expected size
        if not os.path.exists(output_image):
            error_msg = f"Output image {output_image} was not created"
            print(f"Error: {error_msg}")
            progress_callback(error_msg)
            return

        # Check if the file size matches the expected size
        actual_size = os.path.getsize(output_image)
        expected_size = total_size_bytes
        if abs(actual_size - expected_size) > 1024:  # Allow 1KB difference
            error_msg = f"Output image size ({actual_size} bytes) does not match expected size ({expected_size} bytes)"
            print(f"Error: {error_msg}")
            progress_callback(error_msg)
            return

        print("Calculating image hash...")
        # Calculate and log the hash of the created image
        try:
            image_hash = calculate_hash(output_image)
            print(f"Image hash: {image_hash}")
        except Exception as e:
            print(f"Warning: Could not calculate image hash: {e}")

        # Update UI to show completion
        progress_bar["value"] = 100
        mb_label.config(text=f"MB Copied: {total_size_mb:.2f} / {total_size_mb:.2f}")
        speed_label.config(text="Speed: Completed")
        time_label.config(text="Estimated Time Remaining: Completed")
        
        # Show completion message
        completion_msg = "✅ Disk imaging completed successfully!"
        progress_callback(completion_msg)
        print("=== Disk Imaging Completed Successfully ===")

        # Log completion
        log_chain_of_custody("Disk Imaging Completed",
                             f"Output: {output_image}")

    except Exception as e:
        error_msg = f"Disk imaging failed: {str(e)}"
        print(f"Error: {error_msg}")
        log_chain_of_custody("Disk Imaging Failed", f"Error: {str(e)}")
        progress_callback(error_msg)
    finally:
        # Ensure process is terminated
        if process and process.poll() is None:
            print("Ensuring process is terminated...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            # Reset progress bar and labels
            progress_bar["value"] = 0
            mb_label.config(text="MB Copied: 0.00 / 0.00")
            speed_label.config(text="Speed: 0.00 MB/sec")
            time_label.config(text="Estimated Time Remaining: --:--:--")


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


def get_removable_drives():
    """Get a list of removable drives using a simple approach."""
    removable = []
    
    print("\n=== Debug: Checking for USB drives ===")
    
    # First check if we have necessary permissions
    try:
        # Try to read /dev directory
        os.listdir('/dev')
        print("Have access to /dev directory")
    except PermissionError:
        print("WARNING: No permission to access /dev directory. Try running with sudo.")
        return removable
    
    # Simple method: Check for sd* devices in /dev
    try:
        print("Checking /dev for storage devices...")
        for device in os.listdir('/dev'):
            if device.startswith('sd'):
                dev_path = f"/dev/{device}"
                print(f"Found device: {dev_path}")
                
                # Try to get mount point
                mountpoint = 'Not Mounted'
                try:
                    result = subprocess.run(['mount'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if result.returncode == 0:
                        for line in result.stdout.decode().splitlines():
                            if dev_path in line:
                                mountpoint = line.split()[2]
                                break
                except:
                    pass
                
                # Add to list
                removable.append((dev_path, mountpoint))
                print(f"Added device: {dev_path} mounted at {mountpoint}")
    except Exception as e:
        print(f"Error checking devices: {e}")
    
    # If no devices found, try running lsblk
    if not removable:
        print("\nTrying lsblk command...")
        try:
            result = subprocess.run(['lsblk', '-o', 'NAME,MOUNTPOINT'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print("lsblk output:")
                print(result.stdout.decode())
                
                lines = result.stdout.decode().splitlines()[1:]  # skip header
                for line in lines:
                    parts = line.split()
                    if parts and parts[0].startswith('sd'):
                        dev_path = f"/dev/{parts[0]}"
                        mountpoint = parts[1] if len(parts) > 1 else 'Not Mounted'
                        if not any(dev_path == dev for dev, _ in removable):
                            removable.append((dev_path, mountpoint))
                            print(f"Added device via lsblk: {dev_path} mounted at {mountpoint}")
        except Exception as e:
            print(f"Error running lsblk: {e}")
    
    print("\n=== Debug: Final drives list ===")
    print(f"Found {len(removable)} drives:")
    for dev, mnt in removable:
        print(f"{dev} mounted at {mnt}")
    
    return removable


def get_connected_drives(self):
    """Get a list of connected drives and their partitions."""
    print("--- get_connected_drives ENTERED ---")  # Debug print
    drives = []
    try:
        if sys.platform == "win32":
            if 'win32api' in sys.modules:
                drive_letters = win32api.GetLogicalDriveStrings().split('\000')[:-1]
                for letter in drive_letters:
                    try:
                        drive_type = win32file.GetDriveType(letter)
                        if drive_type == win32file.DRIVE_REMOVABLE:
                            drives.append(letter)
                    except Exception:
                        continue  # Ignore drives that cause errors (like floppy drives)
            else:
                print("win32api not loaded, cannot get Windows drives.")
        else:  # POSIX (Linux/macOS)
            print("--- Detecting POSIX drives ---")
            try:
                output = subprocess.check_output(["lsblk", "-dpno", "NAME,TYPE"], text=True)
                print(f"lsblk output:\n{output}\n---")  # Debug print
                for line in output.splitlines():
                    line = line.strip()
                    print(f"Processing line: '{line}'")  # Debug each line
                    try:
                        name, type = line.split()
                        if type == 'disk':  # Include all disk types
                            drives.append(name)
                            print(f"Added drive: {name}")
                    except ValueError:
                        print("Skipping line (could not split into 2 parts)")
                        continue
            except FileNotFoundError:
                print("ERROR: lsblk command not found. Cannot list drives.")
            except subprocess.CalledProcessError as e:
                print(f"ERROR: lsblk command failed: {e}")
            except Exception as error:
                print(f"ERROR: Unexpected error during POSIX drive detection: {error}")
    except Exception as error:
        print(f"ERROR: General error in get_connected_drives: {error}")

    # Remove duplicates and sort
    drives = sorted(list(set(drives)))
    print(f"--- Final drive list: {drives} ---")
    return drives


class ForensicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        print("--- ForensicApp Initializing ---") # Add print here
        self.title("Forensic Evidence Acquisition Tool")
        self.geometry("1200x700")
        # Allow resizing
        self.resizable(True, True) # Changed to True

        self.style = ttk.Style()
        self.style.configure('TNotebook.Tab', font=(
            'Comic Sans MS', '12', 'bold'))

        self.tab_control = ttk.Notebook(self)

        self.tab1 = tk.Frame(self.tab_control) # Use tk.Frame for tab1 background control
        self.tab2 = ChainOfCustodyTab(self.tab_control)
        self.tab3 = tk.Frame(self.tab_control) # Use tk.Frame for tab3 background control

        self.tab_control.add(self.tab1, text="Disk Imaging")
        self.tab_control.add(self.tab2, text="Chain of Custody")
        self.tab_control.add(self.tab3, text="Integrity Verification")

        self.tab_control.pack(expand=1, fill="both")

        self.setup_disk_imaging_tab()
        # setup_chain_of_custody_tab is called within ChainOfCustodyTab.__init__
        self.setup_integrity_verification_tab()
        print("--- ForensicApp Initialization Complete ---") # Add print here

    def setup_disk_imaging_tab(self):
        """Setup the Disk Imaging tab with a resizable layout."""

        # Configure tab background
        self.tab1.configure(bg="#530a0a")

        # --- Style Definitions ---
        label_font = ('Courier', 13)
        button_font = ('Courier', 13, 'bold')
        title_font = ("Courier", 50, "bold") # Match other tabs
        label_color = "#cb1717"
        button_bg = "#404040" # Match other tabs' button style
        button_fg = "#ffffff"
        button_hover_bg = "#606060"
        page_bg = "#530a0a"
        button_relief = "flat"
        button_cursor = "hand2"

        # --- Decorative Elements Removed ---

        # --- Main Content Frame (Resizable) ---
        content_frame = tk.Frame(self.tab1, bg=page_bg)
        content_frame.pack(fill="both", expand=True, padx=50, pady=20)

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1) # Title space
        content_frame.grid_rowconfigure(1, weight=0) # Input controls
        content_frame.grid_rowconfigure(2, weight=0) # Action button
        content_frame.grid_rowconfigure(3, weight=0) # Progress Info
        content_frame.grid_rowconfigure(4, weight=1) # Spacer

        # --- Title ---
        title_label = tk.Label(content_frame, text='AutoChain', fg=label_color, bg=page_bg, font=title_font)
        # Add more padding below title
        title_label.grid(row=0, column=0, pady=(30, 50), sticky="s")

        # --- Input Controls Frame ---
        input_controls_frame = tk.Frame(content_frame, bg=page_bg)
        # Add consistent padding around this frame
        input_controls_frame.grid(row=1, column=0, pady=15)

        tk.Label(input_controls_frame, text="Select Drive:", font=label_font, bg=page_bg, fg=label_color).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.drive_var = tk.StringVar()
        self.drive_dropdown = ttk.Combobox(input_controls_frame, textvariable=self.drive_var, state="readonly", font=label_font, width=20)
        self.drive_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.refresh_drives()

        refresh_btn = tk.Button(input_controls_frame,
                                text="[↻]", # Changed icon
                                command=self.refresh_drives,
                                font=button_font,
                                bg=button_bg, # Use new button style
                                fg=button_fg,
                                relief=button_relief,
                                cursor=button_cursor,
                                bd=0, width=3,
                                highlightthickness=0)
        refresh_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Output Image
        tk.Label(input_controls_frame, text="Output Image:", font=label_font, bg=page_bg, fg=label_color).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.output_image_entry = tk.Entry(input_controls_frame, width=22, font=label_font, relief="solid", bd=1)
        self.output_image_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        browse_btn = tk.Button(input_controls_frame,
                               text="[📁]", # Changed icon
                               command=self.browse_output_image,
                               font=button_font,
                               bg=button_bg, # Use new button style
                               fg=button_fg,
                               relief=button_relief,
                               cursor=button_cursor,
                               bd=0, width=3,
                               highlightthickness=0)
        browse_btn.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        tk.Label(input_controls_frame, text="Disk Size (GB):", font=label_font, bg=page_bg, fg=label_color).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.disk_size_entry = tk.Entry(input_controls_frame, width=22, font=label_font, relief="solid", bd=1)
        self.disk_size_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # --- Action Button Frame ---
        action_button_frame = tk.Frame(content_frame, bg=page_bg)
        # Add consistent padding around this frame
        action_button_frame.grid(row=2, column=0, pady=25)

        create_btn = tk.Button(action_button_frame, text="💾 Create Disk Image", command=self.start_disk_imaging, font=button_font, bg=button_bg, fg=button_fg, width=20, height=2, relief=button_relief, cursor=button_cursor, bd=0, highlightthickness=0)
        create_btn.pack()

        # --- Progress Info Frame ---
        self.progress_info_frame = tk.Frame(content_frame, bg=page_bg)
        # Add consistent padding around this frame
        self.progress_info_frame.grid(row=3, column=0, pady=15)

        self.mb_label = tk.Label(self.progress_info_frame, text="MB Copied: 0.00 / 0.00", font=label_font, bg=page_bg, fg=label_color)
        self.speed_label = tk.Label(self.progress_info_frame, text="Speed: 0.00 MB/sec", font=label_font, bg=page_bg, fg=label_color)
        self.time_label = tk.Label(self.progress_info_frame, text="Estimated Time Remaining: --:--:--", font=label_font, bg=page_bg, fg=label_color)

        self.mb_label.pack()
        self.speed_label.pack()
        self.time_label.pack()
        self.progress_info_frame.grid_remove() # Keep hidden initially

        # --- Progress Bar Section (Bottom of Tab1) ---
        progress_bar_frame = tk.Frame(self.tab1, bg=page_bg)
        progress_bar_frame.pack(side="bottom", fill="x", pady=(10, 10), padx=10) # Adjusted padding

        self.progress_label = tk.Label(progress_bar_frame, text="", font=label_font, bg=page_bg, fg=label_color)
        self.progress_label.pack(pady=(0, 2))

        self.progress_bar = ttk.Progressbar(progress_bar_frame, orient="horizontal", length=1148, mode="determinate")
        self.progress_bar.pack(fill="x", expand=True, padx=20, pady=(0, 10)) # Adjusted padding

        # --- Add hover effects ---
        for button in (refresh_btn, browse_btn, create_btn):
            button.bind("<Enter>", lambda e, btn=button: btn.configure(bg=button_hover_bg))
            button.bind("<Leave>", lambda e, btn=button: btn.configure(bg=button_bg))

    def start_disk_imaging(self):
        """Start the disk imaging process in a background thread."""
        print("\n=== Starting Disk Imaging Process ===")
        selected_device = self.drive_var.get()
        output_image = self.output_image_entry.get()
        disk_size_str = self.disk_size_entry.get()
        disk_device = selected_device.split(' (')[0] if ' (' in selected_device else selected_device
        print(f"Selected device: {selected_device}")
        print(f"Extracted device path: {disk_device}")
        print(f"Output image path: {output_image}")
        print(f"Disk size: {disk_size_str}")

        if not disk_device: error_msg = "Please select a drive"; print(f"Error: {error_msg}"); messagebox.showerror("Error", error_msg); return
        if not output_image: error_msg = "Please specify an output image path"; print(f"Error: {error_msg}"); messagebox.showerror("Error", error_msg); return
        if not disk_size_str: error_msg = "Please enter the disk size"; print(f"Error: {error_msg}"); messagebox.showerror("Error", error_msg); return

        try:
            disk_size_gb = float(disk_size_str)
            if disk_size_gb <= 0: raise ValueError("Disk size must be positive")
        except ValueError as e: error_msg = f"Invalid disk size: {str(e)}"; print(f"Error: {error_msg}"); messagebox.showerror("Error", error_msg); return

        output_dir = os.path.dirname(output_image)
        if not os.path.exists(output_dir):
            try: os.makedirs(output_dir); print(f"Created output directory: {output_dir}")
            except Exception as e: error_msg = f"Cannot create output directory: {str(e)}"; print(f"Error: {error_msg}"); messagebox.showerror("Error", error_msg); return
        if not os.access(output_dir, os.W_OK): error_msg = f"No write permission for output directory: {output_dir}"; print(f"Error: {error_msg}"); messagebox.showerror("Error", error_msg); return

        self.progress_info_frame.grid()
        self.progress_bar["value"] = 0
        self.progress_label.config(text="Starting disk imaging...")
        self.mb_label.config(text="MB Copied: 0.00 / 0.00")
        self.speed_label.config(text="Speed: 0.00 MB/sec")
        self.time_label.config(text="Estimated Time Remaining: --:--:--")

        imaging_thread = threading.Thread(
            target=create_disk_image,
            args=(disk_device, output_image, disk_size_gb, self.update_progress,
                  self.progress_bar, self.mb_label, self.speed_label, self.time_label),
            daemon=True
        )
        imaging_thread.start()
        print("Disk imaging thread started")

    def setup_integrity_verification_tab(self):
        """Setup the Integrity Verification tab with a structured layout."""
        self.tab3.configure(bg="#530a0a")
        label_font = ('Courier', 13)
        button_font = ('Courier', 13, 'bold')
        title_font = ("Courier", 50, "bold")
        label_color = "#cb1717"
        button_bg = "#404040"
        button_fg = "#ffffff"
        button_hover_bg = "#606060"
        page_bg = "#530a0a"
        button_relief = "flat"
        button_cursor = "hand2"

        content_frame = tk.Frame(self.tab3, bg=page_bg)
        content_frame.pack(fill="both", expand=True, padx=50, pady=(20, 0))

        title_label = tk.Label(content_frame, text='Integrity Verification', fg=label_color, bg=page_bg, font=title_font)
        # Add more padding below title
        title_label.pack(pady=(30, 50))

        input_frame = tk.Frame(content_frame, bg=page_bg)
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="Case ID:", font=label_font, bg=page_bg, fg=label_color).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.case_id_entry = tk.Entry(input_frame, width=35, font=label_font, relief="solid", bd=1)
        self.case_id_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(input_frame, text="Image File:", font=label_font, bg=page_bg, fg=label_color).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.image_file_entry = tk.Entry(input_frame, width=35, font=label_font, relief="solid", bd=1)
        self.image_file_entry.grid(row=1, column=1, padx=10, pady=10)

        browse_btn = tk.Button(input_frame, text="📂 Browse", command=self.browse_image_file, font=button_font, bg=button_bg, fg=button_fg, relief=button_relief, cursor=button_cursor, bd=0, width=10, highlightthickness=0)
        browse_btn.grid(row=1, column=2, padx=10, pady=10)

        results_frame = tk.Frame(content_frame, bg=page_bg)
        results_frame.pack(pady=15, fill="x", padx=20)

        self.results_label = tk.Label(results_frame, text="Verification Results will appear here", font=label_font, bg=page_bg, fg=label_color, wraplength=1000, justify="center")
        self.results_label.pack(pady=10)

        button_frame = tk.Frame(content_frame, bg=page_bg)
        button_frame.pack(pady=25)

        verify_btn = tk.Button(button_frame, text="🔍 Verify Integrity", command=self.verify_integrity, font=button_font, bg=button_bg, fg=button_fg, width=20, height=2, relief=button_relief, cursor=button_cursor, bd=0, highlightthickness=0)
        verify_btn.pack(side="left", padx=20)

        clear_btn = tk.Button(button_frame, text="🧹 Clear", command=self.clear_verification_results, font=button_font, bg=button_bg, fg=button_fg, width=20, height=2, relief=button_relief, cursor=button_cursor, bd=0, highlightthickness=0)
        clear_btn.pack(side="left", padx=20)

        progress_frame_bottom = tk.Frame(self.tab3, bg=page_bg)
        progress_frame_bottom.pack(side="bottom", fill="x", pady=(10, 10), padx=10) # Adjusted padding

        self.verification_progress_label = tk.Label(progress_frame_bottom, text="", font=label_font, bg=page_bg, fg=label_color)
        self.verification_progress_label.pack()

        self.verification_progress_bar = ttk.Progressbar(progress_frame_bottom, orient="horizontal", length=1148, mode="determinate")
        self.verification_progress_bar.pack(fill="x", padx=20, pady=(5, 10)) # Adjusted padding

        for button in (browse_btn, verify_btn, clear_btn):
            button.bind("<Enter>", lambda e, btn=button: btn.configure(bg=button_hover_bg))
            button.bind("<Leave>", lambda e, btn=button: btn.configure(bg=button_bg))

        # --- Decorative Elements Removed ---
        # No call to self.add_decorative_elements needed

    def refresh_drives(self):
        """Refresh the list of connected drives"""
        print("--- refresh_drives CALLED ---") # Add print here
        try:
            # Add print before calling get_connected_drives
            print("--- Calling get_connected_drives from refresh_drives ---") 
            drives = self.get_connected_drives()
            print(f"--- refresh_drives: Found {len(drives)} drives ---")
            self.drive_dropdown["values"] = drives
            if drives:
                self.drive_var.set(drives[0])
            else:
                 self.drive_var.set("")
        except Exception as error:
            # Add print inside the except block too
            print(f"--- ERROR in refresh_drives: {error} ---") 
            self.drive_dropdown["values"] = []
            self.drive_var.set("")

    def get_connected_drives(self):
        """Get list of connected drives and their partitions"""
        print("--- get_connected_drives ENTERED ---") # Add print here
        drives = []
        try:
            if sys.platform == "win32":
                if 'win32api' in sys.modules:
                    drive_letters = win32api.GetLogicalDriveStrings().split('\000')[:-1]
                    for letter in drive_letters:
                        try:
                            drive_type = win32file.GetDriveType(letter)
                            if drive_type == win32file.DRIVE_REMOVABLE:
                                drives.append(letter)
                        except Exception:
                            continue # Ignore drives that cause errors (like floppy drives)
                else:
                    print("win32api not loaded, cannot get Windows drives.")
            else: # POSIX (Linux/macOS)
                print("--- Detecting POSIX drives ---")
                try:
                    output = subprocess.check_output(["lsblk", "-dpno", "NAME,TYPE"], text=True)
                    print(f"lsblk output:\n{output}\n---") # Debug print
                    for line in output.splitlines():
                        line = line.strip()
                        print(f"Processing line: '{line}'") # Debug each line
                        try:
                            name, type = line.split()
                            if type == 'disk': # Include all disk types
                                drives.append(name)
                                print(f"Added drive: {name}")
                        except ValueError:
                            print("Skipping line (could not split into 2 parts)")
                            continue
                except FileNotFoundError:
                    print("ERROR: lsblk command not found. Cannot list drives.")
                except subprocess.CalledProcessError as e:
                     print(f"ERROR: lsblk command failed: {e}")
                except Exception as error:
                    print(f"ERROR: Unexpected error during POSIX drive detection: {error}")
        except Exception as error:
            print(f"ERROR: General error in get_connected_drives: {error}")
        
        # Remove duplicates and sort
        drives = sorted(list(set(drives)))
        print(f"--- Final drive list: {drives} ---")
        return drives

    def browse_output_image(self):
        """Browse for the output image file and enforce .img extension."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".img",
            filetypes=[("Image Files", "*.img")])
        if file_path:
            if not file_path.lower().endswith(".img"):
                file_path += ".img"
            self.output_image_entry.delete(0, tk.END)
            self.output_image_entry.insert(0, file_path)

    def update_progress(self, message):
        """Update the progress label (thread-safe via Tkinter)."""
        # Check if widgets exist before configuring
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text=message)
        self.update_idletasks() # Process pending UI events

    def browse_image_file(self):
        """Browse for an image file (for verification)."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.img")])
        if file_path:
            # Use the correct entry widget for this tab
            if hasattr(self, 'image_file_entry'): # Ensure it exists
                self.image_file_entry.delete(0, tk.END)
                self.image_file_entry.insert(0, file_path)
            else:
                 print("Error: image_file_entry widget not found in setup_integrity_verification_tab")

    def verify_integrity(self):
        """Verify the integrity of the disk image against case_log.csv records."""
        case_id = self.case_id_entry.get()
        image_file = self.image_file_entry.get()

        if not case_id or not image_file:
            messagebox.showerror("Error", "Please enter both Case ID and select an image file.")
            return

        try:
            self.verification_progress_bar["value"] = 0
            self.verification_progress_label.config(text="Starting verification...")
            self.results_label.config(text="Verification in progress...", fg="#cb1717")
            self.update_idletasks()

            if not os.path.exists("case_log.csv"): self.results_label.config(text="❌ No case records found.", fg="#ff0000"); return
            if not os.path.exists(image_file): self.results_label.config(text="❌ Image file not found.", fg="#ff0000"); return

            print("\n=== Calculating current hashes ===")
            self.verification_progress_label.config(text="Calculating hashes...")
            self.update_idletasks()
            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()
            file_size = os.path.getsize(image_file)
            chunk_size = 4 * 1024 * 1024
            processed_bytes = 0
            with open(image_file, 'rb') as f:
                while chunk := f.read(chunk_size):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)
                    processed_bytes += len(chunk)
                    progress = (processed_bytes / file_size) * 100 if file_size > 0 else 0
                    self.verification_progress_bar["value"] = progress
                    self.verification_progress_label.config(text=f"Calculating hashes: {progress:.1f}%")
                    self.update_idletasks()
            current_md5 = md5_hash.hexdigest()
            current_sha256 = sha256_hash.hexdigest()
            print(f"Current MD5: {current_md5}")
            print(f"Current SHA-256: {current_sha256}")

            self.verification_progress_label.config(text="Searching case records...")
            self.update_idletasks()
            found, stored_md5, stored_sha256 = False, "", ""
            print("\n=== Searching case records ===")
            with open('case_log.csv', 'r', newline='') as csv_file:
                reader = csv.reader(csv_file)
                try: next(reader) # Skip header
                except StopIteration: pass # Handle empty file
                for row in reader:
                    if len(row) >= 3 and row[0] == case_id: found, stored_md5, stored_sha256 = True, row[1], row[2]; break
            print(f"Found case {case_id}: {found}")

            if not found: self.results_label.config(text=f"❌ Case ID {case_id} not found.", fg="#ff0000"); self.verification_progress_label.config(text="Verification failed"); return

            self.verification_progress_label.config(text="Comparing hashes...")
            self.update_idletasks()
            md5_match = current_md5 == stored_md5
            sha256_match = current_sha256 == stored_sha256

            results = [
                f"Case ID: {case_id}",
                f"MD5 Match: {'✅' if md5_match else '❌'}",
                f"SHA256 Match: {'✅' if sha256_match else '❌'}\n",
                "Current Hashes:", f"  MD5: {current_md5}", f"  SHA256: {current_sha256}\n",
                "Stored Hashes:", f"  MD5: {stored_md5}", f"  SHA256: {stored_sha256}"
            ]
            self.verification_progress_label.config(text="Verification complete")
            self.verification_progress_bar["value"] = 100
            result_color = "#00ff00" if md5_match and sha256_match else "#ff0000"
            self.results_label.config(text="\n".join(results), fg=result_color)
            print("\n=== Verification complete ===")
            print(f"MD5 Match: {md5_match}, SHA256 Match: {sha256_match}")

        except FileNotFoundError:
            self.results_label.config(text="❌ Error: File not found.", fg="#ff0000")
            self.verification_progress_label.config(text="Verification failed")
            messagebox.showerror("Error", "Case log file or image file not found.")
        except Exception as e:
            self.results_label.config(text=f"❌ Error: {str(e)}", fg="#ff0000")
            self.verification_progress_label.config(text="Verification failed")
            print(f"Error during verification: {e}")
            messagebox.showerror("Error", f"Verification failed: {str(e)}")
        finally:
            self.after(3000, lambda: self.verification_progress_bar.config(value=0) if hasattr(self, 'verification_progress_bar') else None)
            self.after(3000, lambda: self.verification_progress_label.config(text="") if hasattr(self, 'verification_progress_label') else None)

    def clear_verification_results(self):
        """Clear the verification input fields, results, and reset the progress bar."""
        if hasattr(self, 'case_id_entry'): self.case_id_entry.delete(0, tk.END)
        if hasattr(self, 'image_file_entry'): self.image_file_entry.delete(0, tk.END)
        if hasattr(self, 'verification_progress_bar'): self.verification_progress_bar["value"] = 0
        if hasattr(self, 'verification_progress_label'): self.verification_progress_label.config(text="")
        if hasattr(self, 'results_label'): self.results_label.config(text="Verification Results will appear here", fg="#cb1717")
        print("Verification fields and results cleared.")


if __name__ == "__main__":
    app = ForensicApp()
    app.mainloop()
