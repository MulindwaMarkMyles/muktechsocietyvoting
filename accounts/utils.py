import pandas as pd

from .models import ApprovedStudent


# Path to your uploaded file
excel_file = "classReps.xlsx"

def add_student_numbers():

    # Read the Excel file
    df = pd.read_excel(excel_file)

    # Assuming student numbers are in a column named 'Student Number'
    column_name = "Student Number"  # Change this if your column name is different

    if column_name in df.columns:
        for student_number in df[column_name].dropna().astype(str):  # Ensure values are strings
            if not ApprovedStudent.objects.filter(student_number=student_number).exists():
                ApprovedStudent.objects.create(student_number=student_number)
                print(f"Added: {student_number}")
            else:
                print(f"Skipped (already exists): {student_number}")
    else:
        print(f"Column '{column_name}' not found in the Excel file.")
