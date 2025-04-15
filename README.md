<div align="center">
  <img height="200" src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExY2gwMjVjcHdyMHJudTFpeGRzOWhuZ2Z0d2hsdndjdGJudGl4eDl5biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/AiuAHkuyccTnG1l21k/giphy.gif" style="width: 100vw; height: 200px; object-fit: fill;" />
</div>

###

<p align="left">AutoChain - Automated Chain of Custody & Image Validation<br><br>Overview:<br>

Overview
AutoChain is a forensic tool designed to automate the chain of custody process while ensuring integrity and authenticity of forensic images. The tool facilitates the creation of forensic disk images, validates them using cryptographic hashes (MD5 and SHA-256), and generates a detailed chain of custody report in PDF format.

Features
- Forensic Image Creation: Supports creating forensic disk images in .img format.
- Image Validation: Computes and verifies MD5 and SHA-256 hashes to ensure image integrity.
- Automated Chain of Custody: Generates a PDF report documenting acquisition details, timestamps, and hash values.
- User-Friendly Interface: GUI-based workflow for easy interaction and evidence management.


<h2>Main Program Interface</h2>
<img src="https://media-hosting.imagekit.io/d901a14c7f5445bf/Screenshot%202025-04-15%20at%202.18.40%E2%80%AFPM.png?Expires=1839327597&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=ihn6JF7LMlKzJ1R6NJHVIbin3SvfbWpF7mzUlpHWxQtTvh8TAJJCncUq8uPodQ0NptAokxLKAdraQhnwwKer6x-EmBrRjfpkRwzmQEnX07fUdnzm-kfeqdG6Oor26i14nvXxLuqaDzjpolbLN54eEnXWdjDfZRH0QLk-YEBOcf3P-wL63j8QEJMxuh83APMYVvTzsMuhmCbwGJChS4fiQ~1rybM-Jkgu6stuv7mNch1mXypJUT3ML-2YrJnu~sYjsZ2YZGtt0NOKIlH1gYNgev4v~jxXJkHT1x2uDUB7FvqfcH9IiiP09BSPdU5I08qt6Yv4nOSPJCH2EFpLjIQXWA__" alt="Main Program Image">

<h2>Chain Of Custody</h2>
<img src="https://media-hosting.imagekit.io/8d5ed700f3eb4799/Picture2.png?Expires=1839326822&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=l3PKJQp6TkKhHZa6ND4ew8phldGnMcxF7~11D1s-5EXKpp2FEpYDleGFHuisizPfktqj~CO7TVaZGyD3cq~BfOsFF6zXNdcr5PDsfUkOaFe0jkWcsRwJkHe12OQc26GejZtUuYm~higbFmPLVvv4sEQgr1PwgHpA-C9PCtgQiW3fjplC5iFVUy67LTSE7EwaQgXHzEXOjhZ~AzM3PwQrfx-YHPb8OD~12hPpOzIWrERByC1xyUrbFsudQxkv-SjRS3lLg3Z1Fqh4IW5~2e5ztRzMi8hzyf0Lnng7nqEZ5aVinX7m-oStNqdCzoSiLx88kFAz6liS6g4HzHdg03cOCA__" alt="Chain Of Custody" style="width: 60%; margin-top: 10px;">

<p>The user is supposed to fill in all the fields so that the program can handle the rest by generating a chain of custody report as well as maintaining copies of the hash values and store them for comparison later on. The program uses the unique ID and links it to the generated hash values and stores them. The values are automatically generated when the user enters the image file.</p>

<div style="text-align: center; margin-bottom: 30px;">
  <h2>Integrity verification</h2>
  <img src="https://media-hosting.imagekit.io/a16ad66dc43048f7/Picture3.png?Expires=1839326822&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=GH9Aj2pDIkQJBcR4Wx~HQxFqUHU6jTZEtLfEt9I5a6~ob8k0uFdKBk2nZ~HJkAoNfJH8GVDqp8NUghiYVF3HZu9NJJaxNfNW-MrjYUs2mfaei7jX5NFGA~N1EbsGufyyE5HmoUJ5ruYrppwJA9sCmJ3H9pcDnAN9yrnCubOCTosULD54AaeC0KPh25c08yoqsuu7-p5DBCbVgkNEnrMRdNDtSit2JfXCh3n7Lwhh3lbYbdKrK581H9tCJLaWo8-eXadPuVfnHlfAf0-EIrQXCnwHxqlzlDaLLQH0BaImhj5g4hO7VAdWFRyPoDs8lPJ0LBoQsSvpB3KqE84jWV6Uzw__" alt="Integrity verification" style="width: 60%; margin-top: 10px;">
</div>

<p>This tab’s purpose is to verify the image integrity by creating both hash values again and comparing them with the stored values. If both are identical, then it shows a green confirmation message, and if not, it shows a red message, which means the images are tampered with.</p>



