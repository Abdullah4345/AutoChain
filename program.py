import os
import subprocess
import hashlib
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import threading
import re

# Configuration
OUTPUT_DIR = "forensic_evidence"
EVIDENCE_LOG = os.path.join(OUTPUT_DIR, "chain_of_custody.log")
HASH_ALGORITHM = "sha256"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Chain of Custody Log Functions


def log_chain_of_custody(action, details):
    """Log actions to maintain the chain of custody."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action}: {details}\n"
    with open(EVIDENCE_LOG, "a") as log_file:
        log_file.write(log_entry)


def read_chain_of_custody():
    """Read the chain of custody log."""
    if not os.path.exists(EVIDENCE_LOG):
        return "No log entries found."
    with open(EVIDENCE_LOG, "r") as log_file:
        return log_file.read()

# Disk Imaging Functions


def get_disk_size(disk_device):
    """Get the total size of the disk in bytes."""
    try:
        if os.name == "posix":  # macOS or Linux
            output = subprocess.check_output(
                ["diskutil", "info", disk_device]).decode("utf-8")
            for line in output.split("\n"):
                if "Total Size" in line:
                    size_str = line.split("(")[1].split(" ")[0]
                    # Convert from 512-byte blocks to bytes
                    return int(size_str) * 512
        return 0
    except Exception as e:
        print(f"Error getting disk size: {e}")
        return 0


def create_disk_image(disk_device, output_image, progress_callback, progress_bar, percentage_label, time_label):
    """Create a forensic disk image using dd."""
    try:
        log_chain_of_custody("Disk Imaging Started",
                             f"Device: {disk_device}, Output: {output_image}")
        total_bytes = get_disk_size(disk_device)
        command = ["sudo", "dd", f"if={disk_device}",
                   f"of={output_image}", "bs=4M", "status=progress"]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        start_time = datetime.now()

        # Read output and update progress
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Extract progress information from dd output
                match = re.search(r"(\d+) bytes", output)
                if match:
                    copied_bytes = int(match.group(1))
                    if total_bytes > 0:
                        progress = (copied_bytes / total_bytes) * 100
                        progress_bar["value"] = progress
                        percentage_label.config(text=f"{progress:.2f}%")

                        # Calculate estimated time remaining
                        elapsed_time = datetime.now() - start_time
                        if progress > 0:
                            total_time = elapsed_time * (100 / progress)
                            remaining_time = total_time - elapsed_time
                            time_label.config(
                                text=f"Estimated Time Remaining: {str(remaining_time).split('.')[0]}")

                progress_callback(output.strip())

        log_chain_of_custody("Disk Imaging Completed",
                             f"Output: {output_image}")
        progress_callback("Disk imaging completed successfully.")
    except Exception as e:
        log_chain_of_custody("Disk Imaging Failed", f"Error: {str(e)}")
        progress_callback(f"Disk imaging failed: {str(e)}")

# Integrity Verification Functions


def calculate_hash(file_path, algorithm=HASH_ALGORITHM):
    """Calculate the cryptographic hash of a file."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

# PDF Export Functions


def export_to_pdf():
    """Export the chain of custody log to a PDF."""
    log_content = read_chain_of_custody()
    if log_content == "No log entries found.":
        messagebox.showwarning(
            "No Log Entries", "No chain of custody entries found to export.")
        return

    pdf_path = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if not pdf_path:
        return

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph("Chain of Custody Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # Log Content
    log_lines = log_content.split("\n")
    data = [[line] for line in log_lines if line.strip()]
    table = Table(data, colWidths=[500])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)

    doc.build(story)
    messagebox.showinfo("Export Successful",
                        f"Chain of custody exported to {pdf_path}")

# Drive Detection Functions


def get_connected_drives():
    """Get a list of connected drives."""
    drives = []
    if os.name == "posix":  # Linux or macOS
        try:
            output = subprocess.check_output(
                ["diskutil", "list"]).decode("utf-8")
            lines = output.split("\n")
            for line in lines:
                if "/dev/disk" in line:
                    drives.append(line.split()[0])
        except Exception as e:
            print(f"Error detecting drives: {e}")
    elif os.name == "nt":  # Windows
        import string
        from ctypes import windll
        bitmask = windll.kernel32.GetLogicalDrives()
        drives = [f"{letter}:\\" for letter in string.ascii_uppercase if bitmask & 1 << ord(
            letter) - ord('A')]
    return drives

# GUI Application


class ForensicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Forensic Evidence Acquisition Tool")
        self.geometry("800x600")

        # Create Tabs
        self.tab_control = ttk.Notebook(self)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text="Disk Imaging")
        self.tab_control.add(self.tab2, text="Chain of Custody")
        self.tab_control.add(self.tab3, text="Integrity Verification")
        self.tab_control.pack(expand=1, fill="both")

        # Disk Imaging Tab
        self.setup_disk_imaging_tab()

        # Chain of Custody Tab
        self.setup_chain_of_custody_tab()

        # Integrity Verification Tab
        self.setup_integrity_verification_tab()

    def setup_disk_imaging_tab(self):
        """Setup the Disk Imaging tab."""
        frame = ttk.LabelFrame(self.tab1, text="Disk Imaging")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Select Flash Drive:").grid(
            row=0, column=0, padx=5, pady=5)
        self.drive_var = tk.StringVar()
        self.drive_dropdown = ttk.Combobox(
            frame, textvariable=self.drive_var, state="readonly")
        self.drive_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.refresh_drives()

        ttk.Button(frame, text="Refresh Drives", command=self.refresh_drives).grid(
            row=0, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Output Image:").grid(
            row=1, column=0, padx=5, pady=5)
        self.output_image_entry = ttk.Entry(frame, width=50)
        self.output_image_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Browse", command=self.browse_output_image).grid(
            row=1, column=2, padx=5, pady=5)

        self.progress_label = ttk.Label(frame, text="")
        self.progress_label.grid(row=2, column=0, columnspan=3, pady=10)

        self.progress_bar = ttk.Progressbar(
            frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=3, column=0, columnspan=3, pady=10)

        # Style the progress bar to be green
        style = ttk.Style()
        style.configure("green.Horizontal.TProgressbar", background="green")
        self.progress_bar.config(style="green.Horizontal.TProgressbar")

        self.percentage_label = ttk.Label(frame, text="0%")
        self.percentage_label.grid(row=4, column=0, columnspan=3, pady=5)

        self.time_label = ttk.Label(
            frame, text="Estimated Time Remaining: --:--:--")
        self.time_label.grid(row=5, column=0, columnspan=3, pady=5)

        ttk.Button(frame, text="Create Disk Image", command=self.start_disk_imaging).grid(
            row=6, column=0, columnspan=3, pady=10)

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
        """Browse for the output image file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".img", filetypes=[("Image Files", "*.img")])
        if file_path:
            self.output_image_entry.delete(0, tk.END)
            self.output_image_entry.insert(0, file_path)

    def start_disk_imaging(self):
        """Start the disk imaging process in a background thread."""
        disk_device = self.drive_var.get()
        output_image = self.output_image_entry.get()

        if not disk_device or not output_image:
            messagebox.showerror(
                "Error", "Please select a flash drive and provide an output image path.")
            return

        self.progress_label.config(text="Starting disk imaging...")
        self.progress_bar["value"] = 0
        self.percentage_label.config(text="0%")
        self.time_label.config(text="Estimated Time Remaining: --:--:--")

        # Start the disk imaging process in a background thread
        imaging_thread = threading.Thread(
            target=create_disk_image,
            args=(disk_device, output_image, self.update_progress,
                  self.progress_bar, self.percentage_label, self.time_label),
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


# Run the Application
if __name__ == "__main__":
    app = ForensicApp()
    app.mainloop()
