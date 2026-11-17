"""
Automated Submission Packaging Script
======================================
Course: Cyber Security Lab (7CS4-22 / 7CIT4-22)
Guidelines Deliverable: Report PDF + Source Code (ZIP) named as:
RollNo_Name_ProjectCode (e.g. 23ESKCS814_ShreyansJain_CSL-I11.zip)
"""

import os
import sys
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_zip(roll_no="23ESKCSxxx", student_name="StudentName"):
    project_code = "CSL-I11"
    clean_name = student_name.replace(" ", "")
    zip_filename = f"{roll_no}_{clean_name}_{project_code}.zip"
    zip_filepath = os.path.join(os.path.dirname(BASE_DIR), zip_filename)

    print(f"[*] Packaging project files into: {zip_filename}...")
    
    # Exclude temporary cache directories
    exclude_dirs = {"__pycache__", ".git", ".pytest_cache", ".idea", ".vscode"}
    exclude_extensions = {".pyc", ".pyo"}

    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if any(file.endswith(ext) for ext in exclude_extensions):
                    continue
                file_abs = os.path.join(root, file)
                rel_path = os.path.relpath(file_abs, os.path.dirname(BASE_DIR))
                zipf.write(file_abs, arcname=rel_path)
                print(f"  + Added: {rel_path}")

    print("=" * 65)
    print(f"[+] Submission ZIP created successfully: {zip_filepath}")
    print(f"[+] Total size: {os.path.getsize(zip_filepath):,} bytes")
    print("=" * 65)
    return zip_filepath

if __name__ == "__main__":
    roll = sys.argv[1] if len(sys.argv) > 1 else input("Enter your Roll No (e.g. 23ESKCS814): ").strip()
    name = sys.argv[2] if len(sys.argv) > 2 else input("Enter your Full Name (e.g. Shreyans Jain): ").strip()
    create_zip(roll or "23ESKCSxxx", name or "StudentName")
