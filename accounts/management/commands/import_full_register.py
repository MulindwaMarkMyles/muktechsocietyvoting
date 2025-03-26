import os
import re
from django.core.management.base import BaseCommand
from PyPDF2 import PdfReader
from accounts.models import ApprovedStudent  # Replace 'your_app' with your app name

class Command(BaseCommand):
    help = 'Extracts student numbers from voter register PDF and adds to ApprovedStudent model'

    def handle(self, *args, **options):
        pdf_path = "resources/UPDATED VOTER'S REGISTER ,2.pdf"
        
        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f"File not found: {pdf_path}"))
            return

        student_numbers = self.extract_student_numbers(pdf_path)
        added, duplicates = self.save_to_model(student_numbers)
        
        self.stdout.write(self.style.SUCCESS(
            f"\nProcessing complete!\n"
            f"Total numbers extracted: {len(student_numbers)}\n"
            f"New records added: {added}\n"
            f"Duplicate numbers skipped: {duplicates}"
        ))

    def extract_student_numbers(self, pdf_path):
        """Extract student numbers from the PDF file"""
        student_numbers = set()
        
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if not text:
                    self.stdout.write(self.style.WARNING(f"Page {page_num} had no text"))
                    continue
                
                # Find all student numbers in the page (looking for 8+ digit sequences)
                numbers = re.findall(r'\b\d{8,}\b', text)
                for num in numbers:
                    # Clean the number (remove any non-digit characters just in case)
                    clean_num = re.sub(r'\D', '', num)
                    if clean_num:
                        student_numbers.add(clean_num)
                        self.stdout.write(f"Found student number: {clean_num}")
        
        return student_numbers

    def save_to_model(self, student_numbers):
        """Save extracted numbers to the model, handling duplicates"""
        added = 0
        duplicates = 0
        
        for number in sorted(student_numbers):
            try:
                _, created = ApprovedStudent.objects.get_or_create(student_number=number)
                if created:
                    added += 1
                    self.stdout.write(self.style.SUCCESS(f"Added: {number}"))
                else:
                    duplicates += 1
                    self.stdout.write(self.style.WARNING(f"Duplicate skipped: {number}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error saving {number}: {str(e)}"))
        
        return added, duplicates