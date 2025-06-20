from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel,
    QDialog, QComboBox, QPushButton, QHBoxLayout, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QFont, QColor, QBrush, QPixmap, QPainter, QPageSize, QPageLayout
from PyQt6.QtCore import Qt, QMarginsF
from PyQt6.QtPrintSupport import QPrinter
import sys
import pymongo

class TimetableSelectionDialog(QDialog):
    """Dialog to select batch, year, semester, and specialization before showing the timetable"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Timetable")
        self.setGeometry(300, 200, 350, 250)

        layout = QVBoxLayout()

        # Batch selection (1 and 2 instead of Batch A & B)
        self.batch_combo = QComboBox()
        self.batch_combo.addItems(["1", "2"])  
        layout.addWidget(QLabel("Select Batch:"))
        layout.addWidget(self.batch_combo)
        
        # Year selection
        self.year_combo = QComboBox()
        self.year_combo.addItems(["First", "Second", "Third", "Final"])
        self.year_combo.currentIndexChanged.connect(self.update_semester_and_specialization_options)
        layout.addWidget(QLabel("Select Year:"))
        layout.addWidget(self.year_combo)

        # Semester selection (auto-updating based on year)
        self.semester_combo = QComboBox()
        layout.addWidget(QLabel("Select Semester:"))
        layout.addWidget(self.semester_combo)

        # Specialization selection (visible only for 3rd and 4th years)
        self.specialization_label = QLabel("Select Specialization:")
        self.specialization_combo = QComboBox()
        self.specialization_combo.addItems(["AI", "CS", "DS", "Cloud Computing"])
        layout.addWidget(self.specialization_label)
        layout.addWidget(self.specialization_combo)

        # Initially hide specialization options (will show for 3rd and 4th years)
        self.specialization_label.setVisible(False)
        self.specialization_combo.setVisible(False)

        self.update_semester_and_specialization_options()  # Initialize semester and specialization options

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)  # Ensure OK button closes the dialog

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def update_semester_and_specialization_options(self):
        """Update semester and specialization dropdowns based on selected year"""
        self.semester_combo.clear()
        year_index = self.year_combo.currentIndex()
        start_semester = year_index * 2 + 1
        self.semester_combo.addItems([str(start_semester), str(start_semester + 1)])

        # Show specialization dropdown only for 3rd and 4th years
        if year_index in [2, 3]:  # Third or Final year
            self.specialization_label.setVisible(True)
            self.specialization_combo.setVisible(True)
        else:
            self.specialization_label.setVisible(False)
            self.specialization_combo.setVisible(False)

    def get_selection(self):
        """Returns selected batch, year, semester, and specialization"""
        batch = int(self.batch_combo.currentText())  # Convert to integer (1 or 2)
        year = self.year_combo.currentText()
        semester = int(self.semester_combo.currentText())  # Convert to integer (1-8)
        # Only include specialization for 3rd and 4th years
        if self.year_combo.currentIndex() in [2, 3]:
            specialization = self.specialization_combo.currentText()
        else:
            specialization = "None"
        return batch, year, semester, specialization


class Timetable(QWidget):
    """Main timetable display window"""

    def __init__(self, batch, year, semester, specialization):
        super().__init__()

        self.batch = batch
        self.year = year
        self.semester = semester
        self.specialization = specialization

        # Update window title to include specialization for 3rd and 4th years
        if self.specialization != "None":
            self.setWindowTitle(f"Timetable for Batch {batch}, {year} Year - Semester {semester} ({specialization})")
        else:
            self.setWindowTitle(f"Timetable for Batch {batch}, {year} Year - Semester {semester}")
        self.setGeometry(100, 100, 1400, 800)

        layout = QVBoxLayout()

        # Title
        if self.specialization != "None":
            title = QLabel(f"Timetable for Batch {batch}, {year} Year - Semester {semester} ({specialization})")
        else:
            title = QLabel(f"Timetable for Batch {batch}, {year} Year - Semester {semester}")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Timetable Table
        self.table = QTableWidget()
        self.table.setRowCount(8)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        self.table.setVerticalHeaderLabels([
            "9:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30", "12:30 - 1:30 (Lunch)", 
            "1:30 - 2:30", "2:30 - 3:30", "3:30 - 4:30", "4:30 - 5:30"
        ])

        # Increase column width
        for col in range(6):
            self.table.setColumnWidth(col, 200)  # Adjust width as needed

        # Increase row height
        for row in range(8):
            self.table.setRowHeight(row, 80)  # Adjust height as needed

        self.populate_table()

        layout.addWidget(self.table)

        # Export Buttons
        export_layout = QHBoxLayout()
        self.export_image_button = QPushButton("Export as Image")
        self.export_image_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: white;
                color: #1E90FF;
                border: 2px solid #1E90FF;
            }
            QPushButton:pressed {
                background-color: #1E90FF;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 8px;
            }
        """)
        self.export_image_button.clicked.connect(self.export_as_image)
        export_layout.addWidget(self.export_image_button)
        layout.addLayout(export_layout)

        self.setLayout(layout)

    def populate_table(self):
        """Fetch and display timetable from MongoDB"""
        try:
            client = pymongo.MongoClient("mongodb://localhost:27017/")
            db = client["timetable_db"]
            collection = db["timetable"]

            YEAR_MAPPING = {"First": 1, "Second": 2, "Third": 3, "Final": 4}
            SEMESTER_MAPPING = {str(i): i for i in range(1, 9)}

            year = YEAR_MAPPING.get(self.year, self.year)  
            semester = SEMESTER_MAPPING.get(str(self.semester), self.semester)
            batch = int(self.batch)  

            # Include specialization in the query for 3rd and 4th years
            query = {"year": year, "semester": semester, "batch": batch}
            if self.specialization != "None":
                query["specialization"] = self.specialization
            else:
                query["specialization"] = "None"

            print(f"Fetching timetable with query: {query}")
            timetable_data = collection.find_one(query)

            if not timetable_data:
                print(f"No timetable found for Year {year}, Semester {semester}, Batch {batch}, Specialization {self.specialization}")
                QMessageBox.warning(self, "No Data", f"No timetable found for Batch {batch}, {self.year} Year - Semester {semester}, Specialization {self.specialization}")
                return

            data = timetable_data.get("data", {})

            self.table.clearContents()

            for day, sessions in data.items():
                col = self.get_day_column(day)
                if col == -1:
                    continue

                for time_slot, session in sessions.items():
                    row = self.get_time_slot_row(time_slot)
                    if row == -1:
                        continue

                    if session:
                        subject = session.get("subject", "N/A")
                        subject_type = session.get("type", "N/A")
                        instructor = session.get("instructor", "N/A")  # Fetch instructor name
                        if subject_type == "Lab":
                            location = session.get("lab", "N/A")
                            location_text = f"Lab: {location}"
                            instructor_text = f"TA: {instructor}"
                        elif subject_type == "Office":
                            location_text = "Office Hour"
                            instructor_text = ""
                        elif subject_type == "Tutorial":
                            location = session.get("room", "N/A")
                            location_text = f"Room: {location}"
                            instructor_text = f"TA: {instructor}"
                        else:  # Theory
                            location = session.get("room", "N/A")
                            location_text = f"Room: {location}"
                            instructor_text = f"Faculty: {instructor}"
                        
                        text = f"{subject} ({subject_type})\n{instructor_text}\n{location_text}"
                    else:
                        text = "Office Hour"

                    self.set_cell(row, col, text, session.get("type", "Office") if session else "Office")

            self.table.repaint()

        except Exception as e:
            print("Error fetching timetable:", str(e))
            QMessageBox.critical(self, "Error", f"Error fetching timetable: {str(e)}")

    def get_day_column(self, day):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        return days.index(day) if day in days else -1

    def get_time_slot_row(self, time_slot):
        TIME_SLOTS = [
            "9:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30", 
            "12:30 - 1:30", "1:30 - 2:30", "2:30 - 3:30", 
            "3:30 - 4:30", "4:30 - 5:30"
        ]
        return TIME_SLOTS.index(time_slot) if time_slot in TIME_SLOTS else -1

    def set_cell(self, row, col, text, session_type):
        if col == -1 or row == -1:
            return
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        if session_type == "Lab":
            item.setBackground(QBrush(QColor("#90EE90")))
        elif session_type == "Office":
            item.setBackground(QBrush(QColor("#FFFFE0")))
        elif session_type == "Tutorial":
            item.setBackground(QBrush(QColor("#C68EFD")))
        else:
            item.setBackground(QBrush(QColor("#ADD8E6")))

        self.table.setItem(row, col, item)

    def export_as_image(self):
        """Export the timetable as an image"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_path:
            pixmap = QPixmap(self.table.size())
            self.table.render(pixmap)
            pixmap.save(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    selection_dialog = TimetableSelectionDialog()
    if selection_dialog.exec():
        batch, year, semester, specialization = selection_dialog.get_selection()
        timetable_window = Timetable(batch, year, semester, specialization)
        timetable_window.show()

    sys.exit(app.exec())