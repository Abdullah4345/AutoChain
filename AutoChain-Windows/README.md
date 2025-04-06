# Forensic Disk Imager

A Python-based forensic disk imaging tool with a graphical user interface for Windows. This tool allows for secure disk imaging with integrity verification and reporting capabilities.

## Features

- User-friendly GUI interface
- Support for multiple disk imaging formats (DD and E01)
- Hash verification (MD5 and SHA-256)
- Real-time progress monitoring
- Detailed logging and reporting
- Support for both fixed and removable drives
- Read-only operations to maintain evidence integrity

## Requirements

- Windows operating system
- Python 3.7 or higher
- Required Python packages (install using requirements.txt)

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python forensic_utils.py
   ```

2. Select the source drive from the dropdown menu
3. Choose a destination folder for the image
4. Select the desired image format (DD or E01)
5. Choose hash verification methods
6. Click "Start Imaging" to begin the process

## Safety Notes

- The tool operates in read-only mode to prevent modification of source media
- Always verify hash values to ensure image integrity
- Keep detailed logs of all imaging operations
- Use write blockers when possible for additional security

## License

MIT License
