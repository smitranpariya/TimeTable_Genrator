import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt

class TimeTableGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Timetable Generator")
        self.setGeometry(100, 100, 800, 400)

        # Data
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.time_slots = ["9:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "1:00 - 2:00", "2:00 - 3:00"]
        self.courses = ["Math", "Physics", "Chemistry", "Biology", "English"]
        self.faculty = ["Dr. Smith", "Prof. Johnson", "Dr. Lee", "Prof. Brown", "Dr. Taylor"]

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout(self.central_widget)

        # Table Widget
        self.table = QTableWidget(len(self.time_slots), len(self.days))
        self.table.setHorizontalHeaderLabels(self.days)
        self.table.setVerticalHeaderLabels(self.time_slots)
        self.layout.addWidget(self.table)

        # Generate Button
        self.generate_button = QPushButton("Generate Timetable")
        self.generate_button.clicked.connect(self.generate_timetable)
        self.layout.addWidget(self.generate_button)

    def generate_timetable(self):
        """Generates a timetable ensuring no subject repeats on the same day."""
        self.table.clearContents()
        
        for col in range(len(self.days)):  # Iterate over days (columns)
            used_courses = set()  # Keep track of courses already assigned to this day
            for row in range(len(self.time_slots)):  # Iterate over time slots (rows)
                # Filter courses not already used on this day
                available_courses = [course for course in self.courses if course not in used_courses]
                if not available_courses:
                    QMessageBox.warning(self, "Conflict", "Not enough unique courses to fill the timetable.")
                    return
                
                # Randomly select a course and a faculty
                course = random.choice(available_courses)
                teacher = random.choice(self.faculty)
                
                # Add course and teacher to the timetable
                timetable_entry = f"{course}\n{teacher}"
                self.table.setItem(row, col, QTableWidgetItem(timetable_entry))
                
                # Mark this course as used for the day
                used_courses.add(course)

        QMessageBox.information(self, "Timetable Generated", "The timetable has been successfully generated!")

# Run Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeTableGenerator()
    window.show()
    sys.exit(app.exec())
