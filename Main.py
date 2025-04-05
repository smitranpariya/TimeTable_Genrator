from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QTabWidget, 
    QMessageBox, QHeaderView, QHBoxLayout,QComboBox,QRadioButton,QMenuBar,QGridLayout,QFrame
)
from PyQt6.QtGui import QFont, QColor, QPalette,QIntValidator,QAction
from PyQt6.QtCore import Qt,QProcess,pyqtSignal
from pymongo import MongoClient
from timetable_logic import TimetableDialog
from time_table_ui import Timetable

class ClickableFrame(QFrame):
    clicked = pyqtSignal(int, int, int)  # Signal for (year, semester, batch)

    def __init__(self, year, semester, batch, parent=None):
        super().__init__(parent)
        self.year = year
        self.semester = semester
        self.batch = batch

        # Frame styling
        self.setStyleSheet("""
            background-color: #007bff;
            border-radius: 10px;
            padding: 15px;
            color: white;
            font-size: 14px;
        """)
        self.setFixedSize(150, 150)  # Set uniform size for better alignment

        # Label inside frame
        label = QLabel(f"Year {year} - Sem {semester} - Batch {batch}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout for the frame
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        """Emit signal when clicked"""
        self.clicked.emit(self.year, self.semester, self.batch)

class ViewTimetableTab(QWidget):
    timetable_selected = pyqtSignal(int, int, int)  # Signal for (year, semester, batch)

    def __init__(self):
        super().__init__()
        self.time_layout = QVBoxLayout()
        self.setLayout(self.time_layout)
        self.db = self.connectDB()
        self.createTimetableBoxes()  # Changed to use boxes instead of buttons

    def connectDB(self):
        client = MongoClient("mongodb://localhost:27017/")
        return client["timetable_db"]

    def createTimetableBoxes(self):
        grid_layout = QGridLayout()
        timetables = self.db["timetable"].find()
        row, col = 0, 0
        max_cols = 3  # Adjust column count as needed

        for entry in timetables:
            year, semester, batch = entry["year"], entry["semester"], entry["batch"]
            box = ClickableFrame(year, semester, batch)
            box.clicked.connect(self.openTimetable)  # Connect signal to method
            grid_layout.addWidget(box, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        self.time_layout.addLayout(grid_layout)  # Correctly adds to layout

    def openTimetable(self, year, semester, batch):
        """Handles opening timetable on box click"""
        self.timetable_selected.emit(year, semester, batch)
        self.timetable_ui = Timetable(batch, year, semester)
        self.timetable_ui.show()

class TimetableManager(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("College Timetable Management")
        self.setGeometry(200, 200, 600, 500)

        # Connect to MongoDB
        self.connectDB()

        # Main Layout
        main_layout = QVBoxLayout()
   
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { background: #444; color: white; padding: 10px; margin:5px; font-size: 14px; }
            QTabBar::tab:selected { background: #1E90FF; }
        """)

        self.room_tab = QWidget()
        self.lab_tab = QWidget()
        self.strength_management_tab = QWidget()
        self.subject_tab = QWidget()
        self.view_timetable_tab = ViewTimetableTab()
        

        self.tabs.addTab(self.subject_tab, "Subject Management")
        self.tabs.addTab(self.room_tab, "Room Management")
        self.tabs.addTab(self.lab_tab, "Lab Management")
        self.tabs.addTab(self.strength_management_tab, "Strength Management")
        self.tabs.addTab(self.view_timetable_tab,"View Timetables")
        self.generate_timetable_button = QPushButton("Generate Timetable")
        self.generate_timetable_button.setStyleSheet("""
            QPushButton {
                background-color: Green; 
                color: white; 
                padding: 8px; 
                margin-bottom:5px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #87A96B; }
        """)
        self.generate_timetable_button.clicked.connect(self.openTimetableWizard)

        # Insert the button into the tab bar
        self.tabs.setCornerWidget(self.generate_timetable_button)

        
        self.setupRoomTab()
        self.setupLabTab()
        self.setupStrengthTab()
        self.setupSubjectTab()
        
      
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.setStyleSheet("""
            QWidget { background-color: #2E2E2E; color: white; font-size: 14px; }
            QPushButton { background-color: #1E90FF; color: white; padding: 8px; border-radius: 5px; }
            QPushButton:hover { background-color: #4169E1; }
            QLineEdit { background-color: #444; color: white; padding: 5px; border-radius: 3px; }
            QLabel { font-size: 16px; }
        """)

        self.showMaximized()

    def connectDB(self):
        """Connects to MongoDB"""
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["timetable_db"]
        self.room_collection = self.db["rooms"]
        self.lab_collection = self.db["labs"]
        self.strength_collection = self.db["strength_details"]
        self.subject_collection = self.db["Subject_collection"]

    def openTimetableWizard(self):
        """Opens the timetable generation wizard"""
        wizard = TimetableDialog(self)
        wizard.exec()  # Open the wizard dialog

        # Optionally, switch back to another tab after closing
        self.tabs.setCurrentIndex(0)

    def setupSubjectTab(self):
        """UI Setup for Subject Management"""
        layout = QVBoxLayout()

        # --- Mapping for Semesters by Year ---
        self.year_semester_map = {
            "1st Year": ["Semester 1", "Semester 2"],
            "2nd Year": ["Semester 3", "Semester 4"],
            "3rd Year": ["Semester 5", "Semester 6"],
            "4th Year": ["Semester 7", "Semester 8"]
        }

        # --- Input Fields ---
        input_layout = QHBoxLayout()
        self.subject_name = QLineEdit(self)
        self.subject_name.setPlaceholderText("Subject Name")

        self.faculty_input = QLineEdit(self)
        self.faculty_input.setPlaceholderText("Faculty/TA Name")

        self.year_dropdown = QComboBox(self)
        self.year_dropdown.addItems(self.year_semester_map.keys())
        self.year_dropdown.currentTextChanged.connect(self.updateSemesterDropdown)

        self.semester_dropdown = QComboBox(self)
        self.updateSemesterDropdown(self.year_dropdown.currentText())  # Initialize default semesters

        self.theory_radio = QRadioButton("Theory")
        self.lab_radio = QRadioButton("Lab")
        self.theory_radio.setChecked(True)

        add_btn = QPushButton("Add Subject", self)
        add_btn.clicked.connect(self.addSubject)

        # Add widgets to input layout
        input_layout.addWidget(self.subject_name)
        input_layout.addWidget(self.faculty_input)
        input_layout.addWidget(self.year_dropdown)
        input_layout.addWidget(self.semester_dropdown)
        input_layout.addWidget(self.theory_radio)
        input_layout.addWidget(self.lab_radio)
        input_layout.addWidget(add_btn)

        # --- Table to Display Subjects ---
        self.subject_table = QTableWidget(0, 5)
        self.subject_table.setHorizontalHeaderLabels(["Subject", "Faculty", "Year", "Semester", "Type"])
        self.subject_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addLayout(input_layout)
        layout.addWidget(self.subject_table)

        self.subject_tab.setLayout(layout)
        self.loadSubjects()


    def updateSemesterDropdown(self, selected_year):
        """Updates the semester dropdown based on selected year"""
        semesters = self.year_semester_map.get(selected_year, [])
        self.semester_dropdown.clear()
        self.semester_dropdown.addItems(semesters)


    def addSubject(self):
        """Adds a new subject"""
        subject = self.subject_name.text().strip()
        faculty = self.faculty_input.text().strip()
        year = self.year_dropdown.currentText()
        semester = self.semester_dropdown.currentText()
        subject_type = "Theory" if self.theory_radio.isChecked() else "Lab"

        if not subject:
            QMessageBox.warning(self, "Error", "Please enter a subject name.")
            return

        if not faculty:
            QMessageBox.warning(self, "Error", "Faculty name is mandatory.")
            return

        # Check for duplicates
        existing_subject = self.subject_collection.find_one({
            "subject": subject,
            "year": year,
            "semester": semester,
            "type": subject_type
        })

        if existing_subject:
            QMessageBox.warning(self, "Error", f"'{subject}' ({subject_type}) is already assigned in {year} - {semester}.")
            return

        # Insert into the database
        self.subject_collection.insert_one({
            "subject": subject,
            "faculty": faculty,
            "year": year,
            "semester": semester,
            "type": subject_type
        })

        QMessageBox.information(self, "Success", f"Subject '{subject}' ({subject_type}) added successfully!")
        self.subject_name.clear()
        self.faculty_input.clear()
        self.loadSubjects()

    def loadSubjects(self):
        """Loads subjects from database into the table"""
        self.subject_table.setRowCount(0)
        subjects = self.subject_collection.find()
        
        for row, subject in enumerate(subjects):
            self.subject_table.insertRow(row)
            self.subject_table.setItem(row, 0, QTableWidgetItem(subject["subject"]))
            self.subject_table.setItem(row, 1, QTableWidgetItem(subject["faculty"]))  # Display faculty
            self.subject_table.setItem(row, 2, QTableWidgetItem(subject["year"]))
            self.subject_table.setItem(row, 3, QTableWidgetItem(subject["semester"]))
            self.subject_table.setItem(row, 4, QTableWidgetItem(subject["type"]))

    def deleteSubject(self):
        """Deletes a selected subject"""
        row = self.subject_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Error", "Please select a subject to delete.")
            return

        subject_name = self.subject_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Delete Subject", f"Are you sure you want to delete '{subject_name}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.subject_collection.delete_one({"subject": subject_name})
            self.subject_table.removeRow(row)
            QMessageBox.information(self, "Success", "Subject deleted successfully!")


    def updateSubject(self):
        """Updates selected subject"""
        row = self.subject_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Error", "Please select a subject to update.")
            return

        subject_name = self.subject_table.item(row, 0).text()
        new_year = self.year_dropdown.currentText()
        new_semester = self.semester_dropdown.currentText()
        new_faculty = self.faculty_dropdown.currentText()
        new_type = "Theory" if self.theory_radio.isChecked() else "Lab"

        self.subject_collection.update_one(
            {"subject": subject_name},
            {"$set": {
                "year": new_year,
                "semester": new_semester,
                "faculty": new_faculty,
                "type": new_type
            }}
        )
        
        QMessageBox.information(self, "Success", f"Subject '{subject_name}' updated successfully!")
        self.loadSubjects()

    def setupStrengthTab(self):
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.year_input = QLineEdit(self)
        self.year_input.setPlaceholderText("Year (1st, 2nd, 3rd, 4th)")

        self.section_input = QLineEdit(self)
        self.section_input.setPlaceholderText("Number of Sections")

        self.student_count_input = QLineEdit(self)
        self.student_count_input.setPlaceholderText("Total Students")

        add_btn = QPushButton("Add Strength", self)
        add_btn.clicked.connect(self.addStrength)

        input_layout.addWidget(self.year_input)
        input_layout.addWidget(self.section_input)
        input_layout.addWidget(self.student_count_input)
        input_layout.addWidget(add_btn)

        # Table to display strength data
        self.strength_table = QTableWidget(0, 3)
        self.strength_table.setHorizontalHeaderLabels(["Year", "Sections", "Students"])
        self.strength_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addLayout(input_layout)
        layout.addWidget(self.strength_table)

        self.strength_management_tab.setLayout(layout)
        self.loadStrengthData()

    def addStrength(self):
        """Adds strength data"""
        year = self.year_input.text().strip()
        sections = self.section_input.text().strip()
        students = self.student_count_input.text().strip()

        if not year or not sections or not students:
            QMessageBox.warning(self, "Error", "Please fill all fields!")
            return

        # Add to database (MongoDB collection)
        self.strength_collection.insert_one({"year": year, "sections": sections, "students": students})

        QMessageBox.information(self, "Success", f"Strength added for {year} year!")
        self.year_input.clear()
        self.section_input.clear()
        self.student_count_input.clear()
        self.loadStrengthData()

    def loadStrengthData(self):
        """Loads student strength data into the table"""
        self.strength_table.setRowCount(0)
        for row, strength in enumerate(self.strength_collection.find()):
            self.strength_table.insertRow(row)
            self.strength_table.setItem(row, 0, QTableWidgetItem(str(strength["year"])))
            self.strength_table.setItem(row, 1, QTableWidgetItem(str(strength["sections"])))
            self.strength_table.setItem(row, 2, QTableWidgetItem(str(strength["students"])))

    def deleteStrength(self, row):
        """Deletes strength record"""
        year = self.strength_table.item(row, 0).text()

        confirm = QMessageBox.question(self, "Delete", f"Delete record for {year} year?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.strength_collection.delete_one({"year": year})
            self.loadStrengthData()


    def setupRoomTab(self):
        """✅ UI Setup for Room Management with CRUD"""
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        
        self.room_no = QLineEdit(self)
        self.room_no.setPlaceholderText("Room Number")

        self.room_capacity = QLineEdit(self)
        self.room_capacity.setPlaceholderText("Room Capacity")
        self.room_capacity.setValidator(QIntValidator())

        add_btn = QPushButton("Add Room", self)
        add_btn.clicked.connect(self.addRoom)

        input_layout.addWidget(self.room_no)
        input_layout.addWidget(self.room_capacity)
        input_layout.addWidget(add_btn)

        self.room_table = QTableWidget(0, 3)
        self.room_table.setHorizontalHeaderLabels(["Room Number", "Capacity", "Actions"])
        self.room_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        

        layout.addLayout(input_layout)
        layout.addWidget(self.room_table)

        self.room_tab.setLayout(layout)

        self.loadRooms()


    def addRoom(self):
        """✅ Adds a Room"""
        room_no = self.room_no.text().strip()
        capacity = self.room_capacity.text().strip()

        if not room_no or not capacity:
            QMessageBox.warning(self, "Error", "Please enter both Room Number and Capacity.")
            return

        self.room_collection.insert_one({"room_no": room_no, "capacity": int(capacity)})
        QMessageBox.information(self, "Success", f"Room {room_no} added successfully!")

        self.room_no.clear()
        self.room_capacity.clear()
        
        self.loadRooms()


    def loadRooms(self):
        """📌 Loads Rooms into the table"""
        self.room_table.setRowCount(0)

        for row, room in enumerate(self.room_collection.find()):
            self.room_table.insertRow(row)
            self.room_table.setItem(row, 0, QTableWidgetItem(room["room_no"]))
            self.room_table.setItem(row, 1, QTableWidgetItem(str(room["capacity"])))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, r=row: self.deleteRoom(r))
            self.room_table.setCellWidget(row, 2, delete_btn)



    def deleteRoom(self, row):
        """Deletes a selected room."""
        try:
            room_no = self.room_table.item(row, 0).text()
            if not room_no:
                QMessageBox.warning(self, "Error", "No room selected.")
                return

            confirmation = QMessageBox.question(self, "Confirm Deletion",
                                                f"Are you sure you want to delete Room {room_no}?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirmation == QMessageBox.StandardButton.No:
                return

            self.room_collection.delete_one({"room_no": room_no})
            QMessageBox.information(self, "Success", f"Room {room_no} deleted successfully!")
            self.loadRooms()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete room: {str(e)}")


    def setupLabTab(self):
        """✅ UI Setup for Lab Management with CRUD"""
        layout = QVBoxLayout()

        # Input Fields Layout
        input_layout = QHBoxLayout()
        
        # Lab Number Input
        self.lab_no = QLineEdit(self)
        self.lab_no.setPlaceholderText("Lab Number")

        # Lab Capacity Input
        self.lab_strength = QLineEdit(self)
        self.lab_strength.setPlaceholderText("Lab Capacity")
        self.lab_strength.setValidator(QIntValidator())  # Numeric input only

        # Add Lab Button
        add_btn = QPushButton("Add Lab", self)
        add_btn.clicked.connect(self.addLab)

        # Add widgets to input layout
        input_layout.addWidget(self.lab_no)
        input_layout.addWidget(self.lab_strength)
        input_layout.addWidget(add_btn)

        # Lab Table Setup
        self.lab_table = QTableWidget(0, 3)  # Added extra column for actions
        self.lab_table.setHorizontalHeaderLabels(["Lab Number", "Lab Capacity", "Actions"])
        self.lab_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       

        # Add layouts to main layout
        layout.addLayout(input_layout)
        layout.addWidget(self.lab_table)

        # Apply layout to tab
        self.lab_tab.setLayout(layout)

        # Load existing labs
        self.loadLabs()


    def addLab(self):
        """ Adds a lab"""
        lab = self.lab_no.text().strip()
        strength = self.lab_strength.text().strip()

        if not lab or not strength:
            QMessageBox.warning(self, "Error", "Please enter both Lab Number and Capacity.")
            return

        self.lab_collection.insert_one({"lab_no": lab, "strength": int(strength)})
        QMessageBox.information(self, "Success", f"Lab {lab} added successfully!")
        
        self.lab_no.clear()
        self.lab_strength.clear()
        
        self.loadLabs()  # Refresh table


    def loadLabs(self):
        """ Loads labs into the table"""
        self.lab_table.setRowCount(0)  # Clear existing data

        for row, lab in enumerate(self.lab_collection.find()):
            self.lab_table.insertRow(row)
            self.lab_table.setItem(row, 0, QTableWidgetItem(lab["lab_no"]))
            self.lab_table.setItem(row, 1, QTableWidgetItem(str(lab["strength"])))
            

            # Add Delete Button
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, r=row: self.deleteLab(r))
            self.lab_table.setCellWidget(row, 2, delete_btn)


    def deleteLab(self, row):
        """Deletes the selected lab with proper error handling"""
        try:
            if row == -1:
                QMessageBox.warning(self, "Error", "Please select a lab to delete.")
                return

            lab_item = self.lab_table.item(row, 0)
            if lab_item is None:
                QMessageBox.warning(self, "Error", "Invalid selection. Please try again.")
                return

            lab_no = lab_item.text()

            # Confirm before deleting
            confirmation = QMessageBox.question(self, "Confirm Deletion",
                                                f"Are you sure you want to delete Lab {lab_no}?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirmation == QMessageBox.StandardButton.No:
                return

            # Try deleting from MongoDB
            delete_result = self.lab_collection.delete_one({"lab_no": lab_no})

            if delete_result.deleted_count > 0:
                self.lab_table.removeRow(row)  # Remove from UI after DB deletion
                QMessageBox.information(self, "Success", f"Lab {lab_no} deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", f"Lab {lab_no} not found in the database.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{str(e)}")


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = TimetableManager()
    window.show()
    app.exec()
