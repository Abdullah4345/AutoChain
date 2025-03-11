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
import csv
import hashlib

OUTPUT_DIR = "forensic_evidence"
EVIDENCE_LOG = os.path.join(OUTPUT_DIR, "chain_of_custody.log")
HASH_ALGORITHM = "sha256"


os.makedirs(OUTPUT_DIR, exist_ok=True)


# Constants
OUTPUT_DIR = "forensic_evidence"
EVIDENCE_LOG = os.path.join(OUTPUT_DIR, "chain_of_custody.log")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sample data for dropdowns
COUNTRIES = ["United States", "Canada", "United Kingdom", "Australia"]
STATES = {
    "United States": ["California", "Texas", "New York", "Florida"],
    "Canada": ["Ontario", "Quebec", "British Columbia", "Alberta"],
    "United Kingdom": ["England", "Scotland", "Wales", "Northern Ireland"],
    "Australia": ["New South Wales", "Victoria", "Queensland", "Western Australia"],
}
ZIP_CODES = {
    "California": ["90001", "90210", "94016"],
    "Texas": ["75001", "77001", "78201"],
    "New York": ["10001", "10025", "11201"],
    "Florida": ["32003", "33101", "33401"],
    # Add more as needed
}


class ChainOfCustodyTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """Setup the Chain of Custody tab UI."""
        # Main frame
        frame = ttk.LabelFrame(self, text="Chain of Custody Form")
        frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Form fields
        ttk.Label(frame, text="Case ID:").place(x=10, y=270)
        self.case_id_entry = ttk.Entry(frame, width=40)
        self.case_id_entry.place(x=120, y=270)

        ttk.Label(frame, text="Full Name:").place(x=10, y=300)
        self.name_entry = ttk.Entry(frame, width=40)
        self.name_entry.place(x=120, y=300)

        ttk.Label(frame, text="Country:").place(x=10, y=330)
        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(
            frame, textvariable=self.country_var, values=COUNTRIES, state="readonly", width=39)
        self.country_dropdown.place(x=120, y=330)
        self.country_dropdown.bind("<<ComboboxSelected>>", self.update_states)

        ttk.Label(frame, text="State:").place(x=10, y=360)
        self.state_var = tk.StringVar()
        self.state_dropdown = ttk.Combobox(
            frame, textvariable=self.state_var, state="readonly", width=39)
        self.state_dropdown.place(x=120, y=360)
        self.state_dropdown.bind("<<ComboboxSelected>>", self.update_zip_codes)

        ttk.Label(frame, text="Zip Code:").place(x=10, y=390)
        self.zip_entry = ttk.Entry(frame, width=40)
        self.zip_entry.place(x=120, y=390)

        ttk.Label(frame, text="Signature:").place(x=10, y=420)
        self.signature_entry = ttk.Entry(frame, width=40)
        self.signature_entry.place(x=120, y=420)

        ttk.Label(frame, text="Image File:").place(x=10, y=450)
        self.image_file_entry = ttk.Entry(frame, width=28, state="readonly")
        self.image_file_entry.place(x=120, y=450)
        ttk.Button(frame, text="   Browse  ",
                   command=self.browse_image_file).place(x=390, y=450)

        ttk.Label(frame, text="Image Size:").place(x=10, y=480)
        self.image_size_label = ttk.Label(frame, text="0 MB")
        self.image_size_label.place(x=120, y=480)

        # Define a larger font
        # You can adjust the font name and size as needed
        large_font = ("Arial", 10)

        # MD5 Hash Label
        ttk.Label(frame, text="MD5 Hash:").place(x=10, y=510)
        self.md5_hash_label = ttk.Label(
            frame, text="00000000000000000000000000000000", font=large_font)
        self.md5_hash_label.place(x=120, y=510)

        # SHA-256 Hash Label
        ttk.Label(frame, text="SHA-256 Hash:").place(x=10, y=540)
        self.sha256_hash_label = ttk.Label(
            frame, text="0000000000000000000000000000000000000000000000000000000000000000", font=large_font)
        self.sha256_hash_label.place(x=120, y=540)

        # Additional Feedback Input Field
        ttk.Label(frame, text="Additional Feedback:").place(x=600, y=265)
        self.additional_feedback = tk.Text(
            frame, width=74, height=24, wrap=tk.WORD)
        self.additional_feedback.place(x=600, y=285)

        # Submit button
        ttk.Button(frame, text="                Submit              ",
                   command=self.submit_form).place(x=120, y=570)

        # Export to PDF button
        ttk.Button(frame, text="          Export to PDF        ",
                   command=self.export_to_pdf).place(x=310, y=570)

    def update_states(self, event=None):
        """Update the state dropdown based on the selected country."""
        selected_country = self.country_var.get()
        if selected_country in STATES:
            self.state_dropdown["values"] = STATES[selected_country]
            self.state_dropdown.current(0)
            self.update_zip_codes()

    def update_zip_codes(self, event=None):
        """Update the zip code dropdown based on the selected state."""
        selected_state = self.state_var.get()
        if selected_state in ZIP_CODES:
            # If you want to auto-fill the zip code, you can do something like this:
            self.zip_entry.delete(0, tk.END)
            # Insert the first zip code for the selected state
            self.zip_entry.insert(0, ZIP_CODES[selected_state][0])

    def browse_image_file(self):
        """Open a file dialog to select an image file and update the entry field."""
        file_path = filedialog.askopenfilename(
            title="Select an Image File",
            filetypes=[("Image Files", "*.img *.jpg *.png *.bmp *.tiff")]
        )
        if file_path:  # If a file was selected
            # Temporarily enable the entry to update it
            self.image_file_entry.config(state="normal")
            self.image_file_entry.delete(0, tk.END)  # Clear any existing text
            # Insert the selected file path
            self.image_file_entry.insert(0, file_path)
            self.image_file_entry.config(
                state="readonly")  # Set it back to readonly

            # Update the image size label
            self.update_image_size(file_path)

            # Calculate and display the MD5 and SHA-256 hashes
            self.calculate_hashes(file_path)

    def update_image_size(self, file_path):
        """Update the image size label with the size of the selected file."""
        try:
            file_size = os.path.getsize(file_path)  # Get file size in bytes
            file_size_mb = file_size / (1024 * 1024)  # Convert to MB
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
        zip_code = self.zip_entry.get()
        signature = self.signature_entry.get()
        image_file = self.image_file_entry.get()
        image_size = self.image_size_label.cget("text")
        md5_hash = self.md5_hash_label.cget("text")
        sha256_hash = self.sha256_hash_label.cget("text")
        additional_feedback = self.additional_feedback.get(
            "1.0", tk.END).strip()

        # Validate zip code (must be 5 digits)
        if not zip_code.isdigit() or len(zip_code) != 5:
            messagebox.showerror("Error", "Zip Code must be a 5-digit number.")
            return

        if not all([case_id, name, country, state, zip_code, signature, image_file, md5_hash, sha256_hash]):
            messagebox.showerror(
                "Error", "Please fill out all fields and select an image file.")
            return

        # Log the chain of custody
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

        # Log case ID and hashes to case_log.csv
        with open("case_log.csv", "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([case_id, md5_hash, sha256_hash])

        messagebox.showinfo("Success", "Chain of custody logged successfully.")

    def export_to_pdf(self):
        """Exports the chain of custody log to a professional-looking PDF and clears the log."""
        # Ask the user for the PDF file path
        pdf_filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save PDF Report"
        )
        if not pdf_filename:
            return  # User cancelled the save dialog

        # Read the log file
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

        # Clear the log file before exporting
        try:
            with open(EVIDENCE_LOG, "w") as log_file:
                log_file.write("")
            print("Log file cleared successfully.")  # Debugging statement
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to clear the log file: {str(e)}")
            return

        # Create the PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Set margins for the entire PDF
        pdf.set_left_margin(20)
        pdf.set_right_margin(20)

        # Title Section (Centered with Green Background)
        pdf.set_font("Arial", style="B", size=24)
        pdf.set_fill_color(128, 0, 0)  # Green background
        pdf.set_text_color(255, 255, 255)  # White text
        pdf.cell(0, 20, "Chain of Custody Report",
                 ln=True, align="C", fill=True)

        # Case ID (Centered with Green Background)
        if log_entries:
            try:
                case_id = log_entries[0].split(" | ")[1].split(
                    ": ")[1]  # Extract Case ID from the first log entry
            except IndexError:
                case_id = "N/A"  # Handle missing Case ID
            pdf.set_font("Arial", style="B", size=16)
            pdf.cell(0, 10, f"Case ID: {case_id}",
                     ln=True, align="C", fill=True)

        # Generated On (Centered with Green Background)
        pdf.set_font("Arial", size=12)
        pdf.cell(
            0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C", fill=True)
        pdf.ln(5)  # Add some space after the title section

        # Agent Information Section
        pdf.set_font("Arial", style="B", size=14)
        pdf.set_text_color(0, 0, 0)  # Black text
        pdf.cell(0, 10, "Agent Information", ln=True, align="L")
        pdf.ln(5)

        # Table for Agent Information (Stretched to PDF width with margins)
        pdf.set_font("Arial", style="B", size=12)
        pdf.set_fill_color(0, 128, 0)  # Green color for headers
        pdf.set_text_color(255, 255, 255)  # White text for headers
        col_widths = [40, 40, 30, 30, 30]  # Equal column widths
        headers = ["Date & Time", "Name", "Country", "State", "Zip Code"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)  # Black text for data
        for i, line in enumerate(log_entries):
            row_color = (240, 240, 240) if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*row_color)
            columns = line.strip().split(" | ")
            data = {}
            for column in columns:
                if ": " in column:
                    key, value = column.split(": ", 1)
                    data[key.strip()] = value.strip()

            # Extract values from the log entry
            date_time = data.get("Date & Time", "N/A")
            name = data.get("Name", "N/A")
            country = data.get("Country", "N/A")
            state = data.get("State", "N/A")
            zip_code = data.get("Zip Code", "N/A")

            # Add values to the table
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

        # Image Information Section
        pdf.set_font("Arial", style="B", size=14)
        pdf.set_text_color(0, 0, 0)  # Black text
        pdf.cell(0, 10, "Image Information", ln=True, align="L")
        pdf.ln(5)

        # Table for Image Information (Stretched to PDF width with margins)
        pdf.set_font("Arial", style="B", size=12)
        pdf.set_fill_color(0, 128, 0)  # Green color for headers
        pdf.set_text_color(255, 255, 255)  # White text for headers
        col_widths = [50, 70, 50]  # Adjusted column widths
        headers = ["Date & Time", "Image File", "Image Size"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)  # Black text for data
        for i, line in enumerate(log_entries):
            row_color = (240, 240, 240) if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*row_color)
            columns = line.strip().split(" | ")
            data = {}
            for column in columns:
                if ": " in column:
                    key, value = column.split(": ", 1)
                    data[key.strip()] = value.strip()

            # Extract values from the log entry
            date_time = data.get("Date & Time", "N/A")
            image_file = data.get("Image File", "N/A")
            image_size = data.get("Image Size", "N/A")

            # Add values to the table
            pdf.cell(col_widths[0], 10, date_time,
                     border=1, align="C", fill=True)
            pdf.cell(col_widths[1], 10, image_file,
                     border=1, align="C", fill=True)
            pdf.cell(col_widths[2], 10, image_size,
                     border=1, align="C", fill=True)
            pdf.ln()

        pdf.ln(10)

        # Hash Information Section
        pdf.set_font("Arial", style="B", size=14)
        pdf.set_text_color(0, 0, 0)  # Black text
        pdf.cell(0, 10, "Hash Information", ln=True, align="L")
        pdf.ln(5)

        # Display MD5 and SHA-256 hashes on top of each other
        pdf.set_font("Arial", style="B", size=12)
        pdf.set_fill_color(0, 128, 0)  # Green color for headers
        pdf.set_text_color(255, 255, 255)  # White text for headers
        pdf.cell(35, 10, "Hash Type", border=1, align="C", fill=True)
        pdf.cell(135, 10, "Hash Value", border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)  # Black text for data
        for i, line in enumerate(log_entries):
            columns = line.strip().split(" | ")
            data = {}
            for column in columns:
                if ": " in column:
                    key, value = column.split(": ", 1)
                    data[key.strip()] = value.strip()

            # Extract values from the log entry
            md5_hash = data.get("MD5", "N/A")
            sha256_hash = data.get("SHA-256", "N/A")

            # MD5 Hash Row
            pdf.set_fill_color(
                240, 240, 240) if i % 2 == 0 else (255, 255, 255)
            pdf.cell(35, 10, "MD5", border=1, align="C", fill=True)
            pdf.cell(135, 10, md5_hash, border=1, align="L", fill=True)
            pdf.ln()

            # SHA-256 Hash Row
            pdf.set_fill_color(
                240, 240, 240) if i % 2 == 0 else (255, 255, 255)
            pdf.cell(35, 10, "SHA-256", border=1, align="C", fill=True)
            pdf.cell(135, 10, sha256_hash, border=1, align="L", fill=True)
            pdf.ln()

        pdf.ln(10)
        # Additional Info Section (Black Background for Header, White Text)
        pdf.set_font("Arial", style="B", size=14)
        pdf.set_fill_color(0, 0, 0)  # Black background for the header
        pdf.set_text_color(255, 255, 255)  # White text for the header
        pdf.cell(0, 10, "Additional Info", ln=True, align="L", fill=True)
        pdf.ln(5)

        # Feedback Text (Light Gray Background, Black Text)
        pdf.set_font("Arial", size=12)
        # Light gray background for the feedback text
        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(0, 0, 0)  # Black text for the feedback text
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
        # Signature Section (Moved to the bottom of the page)
        pdf.ln(10)
        pdf.set_font("Arial", style="B", size=14)
        pdf.set_text_color(0, 0, 0)  # Black text
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

        # Save the PDF
        pdf.output(pdf_filename)
        messagebox.showinfo(
            "Success", f"Chain of custody exported to {pdf_filename}")


def log_chain_of_custody(filename, details=""):
    """Log the creation of a disk image with optional details, ensuring .img filenames are included."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = getpass.getuser()  # Get the current username
    log_entry = f"{timestamp} | User: {user} | File/Action: {filename}"

    # Ensure .img file names are recorded in the log
    if filename.endswith(".img"):
        # Extract just the filename from the full path
        img_filename = os.path.basename(filename)
        log_entry += f" | Disk Image: {img_filename}"
    elif "Output: " in details:
        # Extract the output image filename from the details
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
    try:
        # Log the start of the disk imaging process with the output image filename
        log_chain_of_custody("Disk Imaging Started",
                             f"Device: {disk_device}, Output: {output_image}")
        command = ["sudo", "dd", f"if={disk_device}",
                   f"of={output_image}", "bs=4M", "status=progress"]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        start_time = datetime.now()
        total_size_bytes = disk_size_gb * 1024 * 1024 * 1024  # Convert GB to bytes
        total_size_mb = disk_size_gb * 1024  # Convert GB to MB

        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break

            match = re.search(r"(\d+) bytes", output)
            if match:
                copied_bytes = int(match.group(1))
                copied_mb = copied_bytes / (1024 * 1024)  # Convert bytes to MB

                progress = (copied_bytes / total_size_bytes) * 100
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
                    remaining_time = (elapsed_time.total_seconds(
                    ) / copied_bytes) * (total_size_bytes - copied_bytes)
                    time_label.config(
                        text=f"Estimated Time Remaining: {str(timedelta(seconds=int(remaining_time)))}")
                else:
                    time_label.config(
                        text="Estimated Time Remaining: Calculating...")

            progress_callback(f"Progress: {progress:.2f}%")

        # Log the completion of the disk imaging process with the output image filename
        log_chain_of_custody("Disk Imaging Completed",
                             f"Output: {output_image}")
        progress_callback("Disk imaging completed successfully.")
    except Exception as e:
        log_chain_of_custody("Disk Imaging Failed", f"Error: {str(e)}")
        progress_callback(f"Disk imaging failed: {str(e)}")


def calculate_hash(file_path, algorithm=HASH_ALGORITHM):
    """Calculate the cryptographic hash of a file."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def export_to_pdf(self):
    """Exports the chain of custody log to a professional-looking PDF and clears the log."""
    # Ask the user for the PDF file path
    pdf_filename = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")],
        title="Save PDF Report"
    )
    if not pdf_filename:
        return  # User cancelled the save dialog

    # Read the log file
    if not os.path.exists(EVIDENCE_LOG):
        messagebox.showerror("Error", "No log entries found.")
        return

    try:
        with open(EVIDENCE_LOG, "r") as log_file:
            log_entries = log_file.readlines()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read the log file: {str(e)}")
        return

    # Create the PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title Section (Centered)
    pdf.set_font("Arial", style="B", size=24)  # Big font for the title
    pdf.set_fill_color(0, 128, 0)  # Green background
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.cell(200, 20, "Chain of Custody Report", ln=True, align="C", fill=True)

    # Case ID (Centered, Medium Font)
    if log_entries:
        case_id = log_entries[0].split(" | ")[1].split(
            ": ")[1]  # Extract Case ID from the first log entry
        pdf.set_font("Arial", style="B", size=16)  # Medium font for Case ID
        pdf.cell(200, 10, f"Case ID: {case_id}", ln=True, align="C", fill=True)

    # Generated On (Centered, Small Font)
    pdf.set_font("Arial", size=12)  # Small font for the timestamp
    pdf.cell(
        200, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C", fill=True)
    pdf.ln(20)  # Add some space after the title section

    # Agent Information Section
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_fill_color(0, 128, 0)  # Green background
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.cell(200, 10, "Agent Information", ln=True, align="L", fill=True)
    pdf.ln(5)

    # Table for Agent Information (Stretched to PDF width)
    pdf.set_font("Arial", style="B", size=12)
    pdf.set_fill_color(0, 128, 0)  # Green color for headers
    pdf.set_text_color(255, 255, 255)  # White text for headers
    col_widths = [40, 40, 40, 40, 40]  # Equal column widths
    headers = ["Date & Time", "Name", "Country", "State", "Zip Code"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)  # Black text for data
    for i, line in enumerate(log_entries):
        row_color = (240, 240, 240) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*row_color)
        columns = line.strip().split(" | ")
        for j, col in enumerate(columns[:5]):  # First 5 columns
            pdf.cell(col_widths[j], 10, col.split(": ")[
                     1], border=1, align="C", fill=True)
        pdf.ln()

    pdf.ln(10)

    # Image Information Section
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_fill_color(0, 128, 0)  # Green background
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.cell(200, 10, "Image Information", ln=True, align="L", fill=True)
    pdf.ln(5)

    # Table for Image Information (Stretched to PDF width)
    pdf.set_font("Arial", style="B", size=12)
    pdf.set_fill_color(0, 128, 0)  # Green color for headers
    pdf.set_text_color(255, 255, 255)  # White text for headers
    col_widths = [60, 80, 60]  # Adjusted column widths
    headers = ["Date & Time", "Image File", "Image Size"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)  # Black text for data
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

    # Hash Information Section
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_fill_color(0, 128, 0)  # Green background
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.cell(200, 10, "Hash Information", ln=True, align="L", fill=True)
    pdf.ln(5)

    # Display MD5 and SHA-256 hashes on top of each other
    pdf.set_font("Arial", style="B", size=12)
    pdf.set_fill_color(0, 128, 0)  # Green color for headers
    pdf.set_text_color(255, 255, 255)  # White text for headers
    pdf.cell(50, 10, "Hash Type", border=1, align="C", fill=True)
    pdf.cell(140, 10, "Hash Value", border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)  # Black text for data
    for i, line in enumerate(log_entries):
        columns = line.strip().split(" | ")
        md5_hash = columns[9].split(": ")[1]
        sha256_hash = columns[10].split(": ")[1]

        # MD5 Hash Row
        pdf.set_fill_color(240, 240, 240) if i % 2 == 0 else (255, 255, 255)
        pdf.cell(50, 10, "MD5", border=1, align="C", fill=True)
        pdf.cell(140, 10, md5_hash, border=1, align="L", fill=True)
        pdf.ln()

        # SHA-256 Hash Row
        pdf.set_fill_color(240, 240, 240) if i % 2 == 0 else (255, 255, 255)
        pdf.cell(50, 10, "SHA-256", border=1, align="C", fill=True)
        pdf.cell(140, 10, sha256_hash, border=1, align="L", fill=True)
        pdf.ln()

    pdf.ln(10)

    # Additional Info Section (Gray Box)
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_fill_color(240, 240, 240)  # Gray background
    pdf.set_text_color(0, 0, 0)  # Black text
    pdf.cell(200, 10, "Additional Info", ln=True, align="L", fill=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.set_fill_color(240, 240, 240)  # Gray background
    pdf.multi_cell(200, 10, "This is additional information about the case. It can include notes, comments, or any other relevant details.",
                   border=1, align="L", fill=True)

    # Save the PDF
    pdf.output(pdf_filename)
    messagebox.showinfo(
        "Success", f"Chain of custody exported to {pdf_filename}")

    # Clear the log file after exporting
    try:
        with open(EVIDENCE_LOG, "w") as log_file:
            log_file.write("")
        print("Log file cleared successfully.")  # Debugging statement
    except Exception as e:
        messagebox.showerror(
            "Error", f"Failed to clear the log file: {str(e)}")


def get_connected_drives():
    """Get a list of connected drives."""
    drives = []
    if os.name == "posix":
        try:
            output = subprocess.check_output(
                ["diskutil", "list"]).decode("utf-8")
            lines = output.split("\n")
            for line in lines:
                if "/dev/disk" in line:
                    drives.append(line.split()[0])
        except Exception as e:
            print(f"Error detecting drives: {e}")
    elif os.name == "nt":
        import string
        from ctypes import windll
        bitmask = windll.kernel32.GetLogicalDrives()
        drives = [f"{letter}:\\" for letter in string.ascii_uppercase if bitmask & 1 << ord(
            letter) - ord('A')]
    return drives


# ...existing code...

class ForensicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Forensic Evidence Acquisition Tool")
        self.geometry("1200x700")
        self.resizable(False, False)

        # Configure the style for the notebook tabs
        self.style = ttk.Style()
        self.style.configure('TNotebook.Tab', font=(
            'Comic Sans MS', '12', 'bold'))

        # Create the notebook (tab control)
        self.tab_control = ttk.Notebook(self)

        # Create the tabs
        # Disk Imaging tab
        self.tab1 = tk.Frame(self.tab_control, bg="#c71585")
        self.tab2 = ChainOfCustodyTab(self.tab_control)  # Chain of Custody tab
        # Integrity Verification tab
        self.tab3 = tk.Frame(self.tab_control, bg="#b6d0e2")

        # Add the tabs to the notebook
        self.tab_control.add(self.tab1, text="Disk Imaging")
        self.tab_control.add(self.tab2, text="Chain of Custody")
        self.tab_control.add(self.tab3, text="Integrity Verification")

        # Pack the notebook to make it visible
        self.tab_control.pack(expand=1, fill="both")

        # Set up the contents of each tab
        self.setup_disk_imaging_tab()
        self.setup_integrity_verification_tab()

    def setup_disk_imaging_tab(self):
        """Setup the Disk Imaging tab."""
        frame = ttk.LabelFrame(self.tab1, text="Disk Imaging")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        label_font = ('Arial', 13)  # Change font and size here

        # Define a custom style for the buttons
        self.style.configure('Custom.TButton', font=label_font)

        ttk.Label(frame, text="Select Flash Drive:", font=label_font).grid(
            row=1, column=0, padx=5, pady=5)
        self.drive_var = tk.StringVar()
        self.drive_dropdown = ttk.Combobox(
            frame, textvariable=self.drive_var, state="readonly", font=label_font)
        self.drive_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.refresh_drives()

        ttk.Button(frame, text="Refresh Drives", command=self.refresh_drives, style='Custom.TButton').grid(
            row=1, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Output Image:", font=label_font).grid(
            row=2, column=0, padx=5, pady=5)
        self.output_image_entry = ttk.Entry(frame, width=20, font=label_font)
        self.output_image_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(frame, text="      Browse     ", command=self.browse_output_image, style='Custom.TButton').grid(
            row=2, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Disk Size (GB):", font=label_font).grid(
            row=3, column=0, padx=5, pady=5)
        self.disk_size_entry = ttk.Entry(frame, width=20, font=label_font)
        self.disk_size_entry.grid(row=3, column=1, padx=5, pady=5)

        self.progress_label = ttk.Label(frame, text="", font=label_font)
        self.progress_label.grid(row=4, column=0, columnspan=3, pady=10)

        self.progress_bar = ttk.Progressbar(
            frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=5, column=0, columnspan=3, pady=10)

        self.mb_label = ttk.Label(
            frame, text="MB Copied: 0.00 / 0.00", font=label_font)
        self.mb_label.grid(row=6, column=0, columnspan=3, pady=5)

        self.speed_label = ttk.Label(
            frame, text="Speed: 0.00 MB/sec", font=label_font)
        self.speed_label.grid(row=7, column=0, columnspan=3, pady=5)

        self.time_label = ttk.Label(
            frame, text="Estimated Time Remaining: --:--:--", font=label_font)
        self.time_label.grid(row=8, column=0, columnspan=3, pady=5)

        ttk.Button(frame, text="Create Disk Image", command=self.start_disk_imaging, style='Custom.TButton').grid(
            row=9, column=0, columnspan=3, pady=10)

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
        """Setup the Integrity Verification tab."""
        frame = ttk.LabelFrame(self.tab3, text="Integrity Verification")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Image File:").grid(
            row=0, column=0, padx=5, pady=5)
        self.image_file_entry = ttk.Entry(frame, width=50)
        self.image_file_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Browse", command=self.browse_image_file).grid(
            row=0, column=2, padx=5, pady=5)

        self.hash_label = ttk.Label(frame, text="Hash: ")
        self.hash_label.grid(row=1, column=0, columnspan=3, pady=10)

        ttk.Button(frame, text="Verify Integrity", command=self.verify_integrity).grid(
            row=2, column=0, columnspan=3, pady=10)

    def refresh_drives(self):
        """Refresh the list of connected drives."""
        drives = get_connected_drives()
        self.drive_dropdown["values"] = drives
        if drives:
            self.drive_var.set(drives[0])

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

    def start_disk_imaging(self):
        """Start the disk imaging process in a background thread."""
        disk_device = self.drive_var.get()
        output_image = self.output_image_entry.get()
        disk_size_gb = self.disk_size_entry.get()

        if not disk_device or not output_image or not disk_size_gb:
            messagebox.showerror(
                "Error", "Please select a flash drive, provide an output image path, and enter the disk size.")
            return

        try:
            disk_size_gb = float(disk_size_gb)
        except ValueError:
            messagebox.showerror("Error", "Disk size must be a valid number.")
            return

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
        """Verify the integrity of the disk image."""
        image_file = self.image_file_entry.get()
        if not image_file:
            messagebox.showerror("Error", "Please select an image file.")
            return

        try:
            image_hash = calculate_hash(image_file)
            self.hash_label.config(text=f"Hash: {image_hash}")
            messagebox.showinfo("Success", "Integrity verification completed.")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Integrity verification failed: {str(e)}")


# Run
if __name__ == "__main__":
    app = ForensicApp()
    app.mainloop()
