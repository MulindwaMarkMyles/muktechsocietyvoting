import os
import pandas as pd
import PyPDF2
from django.core.management.base import BaseCommand
from accounts.models import ApprovedStudent  # Replace 'your_app' with your actual app name

class Command(BaseCommand):
    help = 'Extracts student numbers from files and adds them to ApprovedStudent model'

    def handle(self, *args, **kwargs):
        # List of files to process (update paths as needed)
        files_to_process = [
            {'path': 'resources/CHM 2220 REGISTRATION FORM.pdf', 'type': 'pdf'},
            {'path': 'resources/CHEMISTRY CLASS LIST 2024.xlsx', 'type': 'excel'},
            {'path': 'resources/4_5979012565328467215.pdf', 'type': 'pdf'}
        ]

        student_numbers = set()

        for file_info in files_to_process:
            file_path = file_info['path']
            file_type = file_info['type']

            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f"File not found: {file_path}"))
                continue

            try:
                if file_type == 'pdf':
                    self.extract_from_pdf(file_path, student_numbers)
                elif file_type == 'excel':
                    self.extract_from_excel(file_path, student_numbers)
                
                self.stdout.write(self.style.SUCCESS(f"Processed {file_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {file_path}: {str(e)}"))

        # Add to database
        added_count = 0
        duplicate_count = 0
        
        for number in student_numbers:
            # Clean the number (remove any whitespace or non-digit characters)
            clean_number = ''.join(filter(str.isdigit, str(number)))
            
            if not clean_number:
                continue
                
            try:
                ApprovedStudent.objects.get_or_create(student_number=clean_number)
                added_count += 1
            except Exception as e:
                duplicate_count += 1
                self.stdout.write(self.style.WARNING(f"Duplicate or invalid student number: {clean_number}"))

        self.stdout.write(self.style.SUCCESS(
            f"Successfully added {added_count} student numbers. {duplicate_count} duplicates skipped."
        ))

    def extract_from_pdf(self, file_path, student_numbers):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            for page in reader.pages:
                text = page.extract_text()
                if not text:
                    continue
                    
                # Process each line looking for student numbers
                for line in text.split('\n'):
                    # For CHM 2220 REGISTRATION FORM.pdf format
                    if 'CHM 2220 REGISTRATION FORM' in text:
                        parts = line.split()
                        if len(parts) >= 5 and parts[-2].isdigit() and len(parts[-2]) >= 8:
                            student_numbers.add(parts[-2])
                    
                    # For 4_5979012565328467215.pdf format
                    elif 'REG NO.' in text and 'STUDENT NO.' in text:
                        parts = line.split()
                        if len(parts) >= 3 and parts[-1].isdigit() and len(parts[-1]) >= 8:
                            student_numbers.add(parts[-1])

    def extract_from_excel(self, file_path, student_numbers):
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Check for 'STUDENT NO' column (case insensitive)
        student_col = None
        for col in df.columns:
            if 'student no' in str(col).lower():
                student_col = col
                break
                
        if student_col:
            for num in df[student_col]:
                if pd.notna(num):
                    # Convert to string and remove decimal if it's a float
                    num_str = str(int(num) if isinstance(num, float) else num)
                    student_numbers.add(num_str)