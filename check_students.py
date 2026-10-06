import csv
import os

CSV_FILE = "data/students.csv"
PHOTO_FOLDER = "data/students"

with open(CSV_FILE, "r", encoding="utf-8") as file:
    students = list(csv.DictReader(file))

print("\nRegistered Students:")
print("-" * 50)

for student in students:
    photo_path = os.path.join(
        PHOTO_FOLDER,
        student["photo"]
    )

    if os.path.exists(photo_path):
        status = "Photo found"
    else:
        status = "Photo missing"

    print(
        student["student_id"],
        "|",
        student["roll_number"],
        "|",
        student["name"],
        "|",
        status
    )