<div align="center">
  <img height="200" src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExY2gwMjVjcHdyMHJudTFpeGRzOWhuZ2Z0d2hsdndjdGJudGl4eDl5biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/AiuAHkuyccTnG1l21k/giphy.gif" style="width: 100vw; height: 200px; object-fit: fill;" />
</div>

###
<hr style="width: 100%; border: none; border-top: 2px solid black; margin: 0;">
<p align="left">AutoChain - Automated Chain of Custody & Image Validation<br><br>Overview:<br>


AutoChain is a forensic tool designed to automate the chain of custody process while ensuring integrity and authenticity of forensic images. The tool facilitates the creation of forensic disk images, validates them using cryptographic hashes (MD5 and SHA-256), and generates a detailed chain of custody report in PDF format.

Features
- Forensic Image Creation: Supports creating forensic disk images in .img format.
- Image Validation: Computes and verifies MD5 and SHA-256 hashes to ensure image integrity.
- Automated Chain of Custody: Generates a PDF report documenting acquisition details, timestamps, and hash values.
- User-Friendly Interface: GUI-based workflow for easy interaction and evidence management.


<h2>Main Program Interface</h2>
<img src="https://ik.imagekit.io/jyx7871cz/Screenshot%202025-05-21%20at%209.10.59%E2%80%AFPM.png" alt="Screenshot" style="width: 100%;">

<h2>Chain Of Custody</h2>
<img src="https://ik.imagekit.io/jyx7871cz/Screenshot%202025-05-21%20at%209.12.18%E2%80%AFPM.png" alt="Screenshot" style="width: 100%;">

<p>The user is supposed to fill in all the fields so that the program can handle the rest by generating a chain of custody report as well as maintaining copies of the hash values and store them for comparison later on. The program uses the unique ID and links it to the generated hash values and stores them. The values are automatically generated when the user enters the image file.</p>

<div style="text-align: center; margin-bottom: 30px;">
  <h2>Integrity verification</h2>
<img src="https://ik.imagekit.io/jyx7871cz/Screenshot%202025-05-21%20at%209.12.21%E2%80%AFPM.png" alt="Screenshot" style="width: 100%;">
</div>

<p>This tab’s purpose is to verify the image integrity by creating both hash values again and comparing them with the stored values. If both are identical, then it shows a green confirmation message, and if not, it shows a red message, which means the images are tampered with.</p>
<hr style="width: 100%; border: none; border-top: 2px solid black; margin: 0;">
<pre style="background-color: white; color: black; padding: 10px;">

  Contributors
  
• Abdullah Mohamed 
• Omar Ahmed
• Ehab Reda

Supervised by: <a href="https://www.linkedin.com/in/maryam-adel-4539b8170" style="display: none;">Dr. Maryam Adel</a>
</pre>

