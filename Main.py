from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMainWindow,
    QLineEdit, QTableWidget, QTableWidgetItem, QTabWidget, 
    QMessageBox, QHeaderView, QHBoxLayout, QComboBox, QRadioButton, QMenuBar, QGridLayout, QFrame, QSizePolicy, QCheckBox,QAbstractItemView,QMenu,QDialog
)
from PyQt6.QtGui import QFont, QColor, QPalette, QIntValidator, QAction
from PyQt6.QtCore import Qt, QProcess, pyqtSignal
from pymongo import MongoClient
from timetable_logic import TimetableDialog
from time_table_ui import Timetable
from timetable_logic import TimetableGenerator

class ClickableFrame(QFrame):
    clicked = pyqtSignal(int, int, int, str)

    def __init__(self, year, semester, batch, specialization):
        super().__init__()
        self.year = year
        self.semester = semester
        self.batch = batch
        self.specialization = specialization

        self.setStyleSheet("""
            QFrame {
                background-color: #FFF3CD;
                border-radius: 12px;
                color: #333333;
                font-size: 14px;
                font-weight: 500;
                padding: 15px;
                border: none;
            }
            QFrame:hover {
                background-color: #FFE69C;
                border: 2px solid #FF6F61;
                cursor: pointer;
            }
            QFrame:focus {
                outline: none;
            }
        """)

        if self.specialization != "None":
            label = QLabel(f"Year {year} - Semester {semester} - Batch {batch} - Specialization: {specialization}")
        else:
            label = QLabel(f"Year {year} - Semester {semester} - Batch {batch}")

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.year, self.semester, self.batch, self.specialization)
        super().mousePressEvent(event)

class ViewTimetableTab(QWidget):
    timetable_selected = pyqtSignal(int, int, int, str)  # Signal for (year, semester, batch, specialization)

    def __init__(self):
        super().__init__()
        self.time_layout = QVBoxLayout()
        self.setLayout(self.time_layout)
        self.db = self.connectDB()
        self.createTimetableBoxes()

    def connectDB(self):
        client = MongoClient("mongodb://localhost:27017/")
        return client["timetable_db"]

    def createTimetableBoxes(self):
        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)

        timetables = self.db["timetable"].find()

        for entry in timetables:
            year = entry["year"]
            semester = entry["semester"]
            batch = entry["batch"]
            # Fetch specialization, default to "None" if not present
            specialization = entry.get("specialization", "None")

            box = ClickableFrame(year, semester, batch, specialization)

            # Ensure full width
            box.setMinimumHeight(50)
            box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            # Connect the clicked signal (which now emits year, semester, batch, specialization)
            box.clicked.connect(self.openTimetable)

            # Add to layout
            vbox.addWidget(box)

        vbox.addStretch(1)  # Pushes items to the top
        self.time_layout.addLayout(vbox)

    def openTimetable(self, year, semester, batch, specialization):
        # Emit the signal with all parameters including specialization
        self.timetable_selected.emit(year, semester, batch, specialization)
        # Pass specialization to the Timetable constructor
        self.timetable_ui = Timetable(batch, year, semester, specialization)
        self.timetable_ui.show()

    def refreshTimetable(self):
        """Refresh the timetable display."""
        # Clear the current layout
        while self.time_layout.count():
            item = self.time_layout.takeAt(0)
            layout = item.layout()
            if layout is not None:
                # Clear all widgets inside the nested layout
                while layout.count():
                    sub_item = layout.takeAt(0)
                    widget = sub_item.widget()
                    if widget is not None:
                        widget.deleteLater()
                layout.deleteLater()
            else:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        # Recreate the timetable boxes
        self.createTimetableBoxes()

class TimetableManager(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("College Timetable Management")
        self.setGeometry(200, 200, 600, 500)

        self.connectDB()

        # Main layout with sidebar and content area
        main_layout = QHBoxLayout()

        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(15)
        sidebar.setContentsMargins(0, 20, 0, 20)
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(230)
        sidebar_widget.setStyleSheet("""
            QWidget {
                background-color: #1A1A2E;
                border-radius: 12px;
            }
        """)

        # Sidebar title
        title_label = QLabel("Timetable")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 600;
                padding: 10px;
            }
        """)
        sidebar.addWidget(title_label)

        # Sidebar items
        self.tab_buttons = []
        tab_names = ["Subject Management", "Room Management", "Lab Management", "Strength Management", "View Timetables"]
        icons = ["📚", "🏫", "🧪", "👥", "🕒"]
        for i, (name, icon) in enumerate(zip(tab_names, icons)):
            btn = QPushButton(f"{icon}  {name}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    text-align: left;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: 500;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2A2A4E;
                    border-radius: 8px;
                }
                QPushButton:pressed {
                    background-color: #3A3A6E;
                }
                QPushButton:focus {
                    outline: none;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_tab(idx))
            self.tab_buttons.append(btn)
            sidebar.addWidget(btn)

        sidebar.addStretch(1)
        sidebar_widget.setLayout(sidebar)
        main_layout.addWidget(sidebar_widget)

        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # Stacked widget to hold tab contents
        self.tab_stack = QTabWidget()
        self.tab_stack.setStyleSheet("QTabWidget::pane { border: none; } QTabBar::tab { height: 0px; width: 0px; }")

        self.subject_tab = QWidget()
        self.room_tab = QWidget()
        self.lab_tab = QWidget()
        self.strength_management_tab = QWidget()
        self.view_timetable_tab = ViewTimetableTab()

        self.tab_stack.addTab(self.subject_tab, "Subject Management")
        self.tab_stack.addTab(self.room_tab, "Room Management")
        self.tab_stack.addTab(self.lab_tab, "Lab Management")
        self.tab_stack.addTab(self.strength_management_tab, "Strength Management")
        self.tab_stack.addTab(self.view_timetable_tab, "View Timetables")

        self.setupSubjectTab()
        self.setupRoomTab()
        self.setupLabTab()
        self.setupStrengthTab()

        # Generate Timetable button with creative styling
        self.generate_timetable_button = QPushButton("Generate Timetable")
        self.generate_timetable_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF6F61, stop:1 #FF3D00);
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 12px;
                border: none;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF8A80, stop:1 #FF5733);
                box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF4D40, stop:1 #FF2D00);
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }
            QPushButton:focus {
                outline: none;
            }
        """)
        self.generate_timetable_button.clicked.connect(self.openTimetableWizard)

        content_layout.addWidget(self.tab_stack)
        content_layout.addWidget(self.generate_timetable_button, alignment=Qt.AlignmentFlag.AlignRight)
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        self.setLayout(main_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5FA;
                color: #333333;
                font-family: 'Inter', sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #FF6F61;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: 500;
                border: none;
            }
            QPushButton:hover {
                background-color: #FF8A80;
                border: 2px solid #FFFFFF;
            }
            QPushButton:focus {
                outline: none;
            }
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #FF6F61;
                outline: none;
            }
            QComboBox {
                background-color: #FFFFFF;
                color: #333333;
                padding: 8px 32px 8px 8px; /* Extra padding on the right for the arrow */
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
            QComboBox:hover {
                border: 2px solid #FF6F61;
            }
            QComboBox:focus {
                outline: none;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                background: #FF6F61; /* Color the arrow area */
                border-radius: 2px;
            }
            QComboBox::down-arrow:hover {
                background: #FF8A80; /* Lighter shade on hover */
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #FFF3CD;
                selection-color: #333333;
                border: none; /* Remove the border */
                border-radius: 8px;
            }
            QCheckBox {
                color: #333333;
                font-size: 14px;
            }
            QCheckBox:focus {
                outline: none;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: 500;
            }
        """)

        # Set initial tab
        self.switch_tab(0)
        self.showMaximized()

    def switch_tab(self, index):
        self.tab_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.tab_buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2A2A4E;
                        color: white;
                        text-align: left;
                        padding: 12px 20px;
                        font-size: 14px;
                        font-weight: 500;
                        border: none;
                        border-radius: 8px;
                    }
                    QPushButton:focus {
                        outline: none;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: white;
                        text-align: left;
                        padding: 12px 20px;
                        font-size: 14px;
                        font-weight: 500;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2A2A4E;
                        border-radius: 8px;
                    }
                    QPushButton:focus {
                        outline: none;
                    }
                """)

    def connectDB(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["timetable_db"]
        self.room_collection = self.db["rooms"]
        self.lab_collection = self.db["labs"]
        self.strength_collection = self.db["strength_details"]
        self.subject_collection = self.db["Subject_collection"]

    def openTimetableWizard(self):
        wizard = TimetableDialog(self)
        wizard.timetable_generated.connect(self.view_timetable_tab.refreshTimetable)
        wizard.exec()

    def setupSubjectTab(self):
        layout = QVBoxLayout()

        self.year_semester_map = {
            "1st Year": ["Semester 1", "Semester 2"],
            "2nd Year": ["Semester 3", "Semester 4"],
            "3rd Year": ["Semester 5", "Semester 6"],
            "4th Year": ["Semester 7", "Semester 8"]
        }

        input_layout = QHBoxLayout()
        self.subject_name = QLineEdit(self)
        self.subject_name.setPlaceholderText("Subject Name")

        self.faculty_input = QLineEdit(self)
        self.faculty_input.setPlaceholderText("Faculty Name")

        self.ta_input = QLineEdit(self)
        self.ta_input.setPlaceholderText("TA Name")

        self.year_dropdown = QComboBox(self)
        self.year_dropdown.addItems(self.year_semester_map.keys())
        self.year_dropdown.currentTextChanged.connect(self.updateSemesterDropdown)

        self.specialization_dropdown = QComboBox(self)
        self.specialization_dropdown.addItems(["AI", "CS", "DS", "Cloud Computing"])
        self.specialization_dropdown.setVisible(False)

        self.semester_dropdown = QComboBox(self)
        self.updateSemesterDropdown(self.year_dropdown.currentText())

        self.theory_checkbox = QCheckBox("Theory")
        self.lab_checkbox = QCheckBox("Lab")
        self.tutorial_checkbox = QCheckBox("Tutorial")

        self.theory_checkbox.setChecked(True)

        add_btn = QPushButton("Add Subject", self)
        add_btn.clicked.connect(self.addSubject)

        input_layout.addWidget(self.subject_name)
        input_layout.addWidget(self.faculty_input)
        input_layout.addWidget(self.ta_input)
        input_layout.addWidget(self.year_dropdown)
        input_layout.addWidget(self.specialization_dropdown)
        input_layout.addWidget(self.semester_dropdown)
        input_layout.addWidget(self.theory_checkbox)
        input_layout.addWidget(self.tutorial_checkbox)
        input_layout.addWidget(self.lab_checkbox)
        input_layout.addWidget(add_btn)

        self.subject_table = QTableWidget(0, 5)
        self.subject_table.setHorizontalHeaderLabels(["Subject", "Assigned To", "Year", "Semester", "Type"])
        self.subject_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
            }
            QHeaderView::section {
                background-color: #1A1A2E;
                color: white;
                padding: 10px;
                font-weight: 500;
                border: none;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E0E0E0;
                padding: 10px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #FFF3CD;
                color: #333333;
            }
            QTableWidget:focus {
                outline: none;
            }
        """)
        self.subject_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Enable context menu for right-click
        self.subject_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.subject_table.customContextMenuRequested.connect(self.showContextMenu)

        layout.addLayout(input_layout)
        layout.addWidget(self.subject_table)

        self.subject_tab.setLayout(layout)
        self.loadSubjects()

    def showContextMenu(self, pos):
        """Show context menu with Edit and Delete options on right-click"""
        row = self.subject_table.currentRow()
        if row == -1:
            return

        menu = QMenu(self)

        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self.editSubject)
        menu.addAction(edit_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.deleteSubject)
        menu.addAction(delete_action)

        menu.exec(self.subject_table.mapToGlobal(pos))

    def editSubject(self):
        """Open a dialog to edit the selected subject"""
        row = self.subject_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Error", "Please select a subject to edit.")
            return

        # Gather subject data
        subject_name = self.subject_table.item(row, 0).text()
        assigned_to = self.subject_table.item(row, 1).text()
        year_text = self.subject_table.item(row, 2).text()
        semester = self.subject_table.item(row, 3).text()
        types_str = self.subject_table.item(row, 4).text()

        # Extract year and specialization from year_text
        year = year_text
        specialization = ""
        if "(" in year_text:
            year, specialization = year_text.split(" (")
            specialization = specialization.rstrip(")")
            year = year.strip()

        # Fetch all types for this subject
        types_cursor = self.subject_collection.find({
            "subject": subject_name,
            "year": year,
            "semester": semester,
            "specialization": specialization
        })

        theory_types = []
        lab_tut_types = []
        faculty = ""
        ta = ""

        for sub in types_cursor:
            if sub["type"] == "Theory":
                theory_types.append("Theory")
                faculty = sub.get("faculty", "")
            else:
                lab_tut_types.append(sub["type"])
                ta = sub.get("ta", "")

        # Create dialog for editing
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Subject")
        dialog.setGeometry(300, 200, 400, 400)

        layout = QVBoxLayout()

        # Subject Name
        layout.addWidget(QLabel("Subject Name:"))
        subject_input = QLineEdit(subject_name)
        layout.addWidget(subject_input)

        # Faculty Name
        layout.addWidget(QLabel("Faculty Name (for Theory):"))
        faculty_input = QLineEdit(faculty)
        layout.addWidget(faculty_input)

        # TA Name
        layout.addWidget(QLabel("TA Name (for Lab/Tutorial):"))
        ta_input = QLineEdit(ta)
        layout.addWidget(ta_input)

        # Year
        layout.addWidget(QLabel("Year:"))
        year_dropdown = QComboBox()
        year_dropdown.addItems(self.year_semester_map.keys())
        year_dropdown.setCurrentText(year)
        layout.addWidget(year_dropdown)

        # Specialization (for 3rd and 4th years)
        layout.addWidget(QLabel("Specialization:"))
        specialization_dropdown = QComboBox()
        specialization_dropdown.addItems(["AI", "CS", "DS", "Cloud Computing"])
        if specialization:
            specialization_dropdown.setCurrentText(specialization)
        specialization_dropdown.setVisible(year in ["3rd Year", "4th Year"])

        # Update specialization visibility when year changes
        def updateSpecializationVisibility(selected_year):
            specialization_dropdown.setVisible(selected_year in ["3rd Year", "4th Year"])

        year_dropdown.currentTextChanged.connect(updateSpecializationVisibility)
        layout.addWidget(specialization_dropdown)

        # Semester
        layout.addWidget(QLabel("Semester:"))
        semester_dropdown = QComboBox()
        semester_dropdown.addItems(self.year_semester_map[year])
        semester_dropdown.setCurrentText(semester)

        # Update semesters when year changes
        def updateSemesterDropdown(selected_year):
            semesters = self.year_semester_map.get(selected_year, [])
            semester_dropdown.clear()
            semester_dropdown.addItems(semesters)

        year_dropdown.currentTextChanged.connect(updateSemesterDropdown)
        layout.addWidget(semester_dropdown)

        # Types
        layout.addWidget(QLabel("Subject Types:"))
        theory_checkbox = QCheckBox("Theory")
        lab_checkbox = QCheckBox("Lab")
        tutorial_checkbox = QCheckBox("Tutorial")
        theory_checkbox.setChecked("Theory" in types_str)
        lab_checkbox.setChecked("Lab" in types_str)
        tutorial_checkbox.setChecked("Tutorial" in types_str)
        layout.addWidget(theory_checkbox)
        layout.addWidget(lab_checkbox)
        layout.addWidget(tutorial_checkbox)

        # Update Button
        update_btn = QPushButton("Update")
        def updateAction():
            new_subject = subject_input.text().strip()
            new_faculty = faculty_input.text().strip()
            new_ta = ta_input.text().strip()
            new_year = year_dropdown.currentText()
            new_semester = semester_dropdown.currentText()
            new_specialization = specialization_dropdown.currentText() if specialization_dropdown.isVisible() else ""

            new_types = []
            if theory_checkbox.isChecked():
                new_types.append("Theory")
            if lab_checkbox.isChecked():
                new_types.append("Lab")
            if tutorial_checkbox.isChecked():
                new_types.append("Tutorial")

            # Validation
            if not new_subject:
                QMessageBox.warning(dialog, "Error", "Please enter a subject name.")
                return

            if not new_types:
                QMessageBox.warning(dialog, "Error", "Please select at least one type (Theory/Lab/Tutorial).")
                return

            if "Theory" in new_types and not new_faculty:
                QMessageBox.warning(dialog, "Error", "Faculty name is mandatory for Theory subjects.")
                return

            if ("Lab" in new_types or "Tutorial" in new_types) and not new_ta:
                QMessageBox.warning(dialog, "Error", "TA name is mandatory for Lab/Tutorial subjects.")
                return

            # Delete old entries
            self.subject_collection.delete_many({
                "subject": subject_name,
                "year": year,
                "semester": semester,
                "specialization": specialization
            })

            # Insert updated entries
            inserted_count = 0
            for t in new_types:
                existing_subject = self.subject_collection.find_one({
                    "subject": new_subject,
                    "year": new_year,
                    "semester": new_semester,
                    "type": t,
                    "specialization": new_specialization
                })

                if existing_subject:
                    QMessageBox.warning(
                        dialog, "Duplicate Entry",
                        f"'{new_subject}' ({t}) is already assigned in {new_year} - {new_semester} ({new_specialization})."
                    )
                    continue

                subject_doc = {
                    "subject": new_subject,
                    "year": new_year,
                    "semester": new_semester,
                    "type": t,
                    "specialization": new_specialization
                }

                if t == "Theory":
                    subject_doc["faculty"] = new_faculty
                else:
                    subject_doc["ta"] = new_ta

                self.subject_collection.insert_one(subject_doc)
                inserted_count += 1

            if inserted_count:
                QMessageBox.information(dialog, "Success", f"Subject '{new_subject}' updated successfully ({inserted_count} types)!")
                self.loadSubjects()
                dialog.accept()
            else:
                QMessageBox.information(dialog, "Info", "No new subject types were added.")
                self.loadSubjects()

        update_btn.clicked.connect(updateAction)
        layout.addWidget(update_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def updateSemesterDropdown(self, selected_year):
        semesters = self.year_semester_map.get(selected_year, [])
        self.semester_dropdown.clear()
        self.semester_dropdown.addItems(semesters)

        if selected_year in ["3rd Year", "4th Year"]:
            self.specialization_dropdown.setVisible(True)
        else:
            self.specialization_dropdown.setVisible(False)

    def addSubject(self):
        subject = self.subject_name.text().strip()
        faculty = self.faculty_input.text().strip()
        ta = self.ta_input.text().strip()
        year = self.year_dropdown.currentText()
        semester = self.semester_dropdown.currentText()

        types = []
        if self.theory_checkbox.isChecked():
            types.append("Theory")
        if self.lab_checkbox.isChecked():
            types.append("Lab")
        if self.tutorial_checkbox.isChecked():
            types.append("Tutorial")

        if not subject:
            QMessageBox.warning(self, "Error", "Please enter a subject name.")
            return

        if not faculty and "Theory" in types:
            QMessageBox.warning(self, "Error", "Faculty name is mandatory for Theory subjects.")
            return

        if (self.lab_checkbox.isChecked() or self.tutorial_checkbox.isChecked()) and not ta:
            QMessageBox.warning(self, "Error", "TA name is mandatory for Lab/Tutorial subjects.")
            return

        if not types:
            QMessageBox.warning(self, "Error", "Please select at least one type (Theory/Lab/Tutorial).")
            return

        specialization = ""
        if self.specialization_dropdown.isVisible():
            specialization = self.specialization_dropdown.currentText()

        inserted_count = 0

        for t in types:
            existing_subject = self.subject_collection.find_one({
                "subject": subject,
                "year": year,
                "semester": semester,
                "type": t,
                "specialization": specialization
            })

            if existing_subject:
                QMessageBox.warning(
                    self, "Duplicate Entry",
                    f"'{subject}' ({t}) is already assigned in {year} - {semester} ({specialization})."
                )
                continue

            subject_doc = {
                "subject": subject,
                "year": year,
                "semester": semester,
                "type": t,
                "specialization": specialization
            }

            if t == "Theory":
                subject_doc["faculty"] = faculty
            else:
                subject_doc["ta"] = ta

            self.subject_collection.insert_one(subject_doc)
            inserted_count += 1

        if inserted_count:
            QMessageBox.information(self, "Success", f"Subject '{subject}' added successfully ({inserted_count} types)!")
            self.subject_name.clear()
            self.faculty_input.clear()
            self.ta_input.clear()
            self.loadSubjects()
        else:
            QMessageBox.information(self, "Info", "No new subject types were added.")

    def loadSubjects(self):
        self.subject_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.subject_table.setRowCount(0)
        subjects = list(self.subject_collection.find())

        added_keys = set()

        for subject in subjects:
            year = subject["year"]
            semester = subject["semester"]
            specialization = subject.get("specialization", "")
            subject_name = subject["subject"]

            year_text = year
            if specialization:
                year_text += f" ({specialization})"

            key = (subject_name, year, semester, specialization)
            if key in added_keys:
                continue

            types_cursor = self.subject_collection.find({
                "subject": subject_name,
                "year": year,
                "semester": semester,
                "specialization": specialization
            })

            theory_names = []
            lab_tut_names = []
            theory_types = []
            lab_tut_types = []

            for sub in types_cursor:
                if sub["type"] == "Theory":
                    theory_names.append(sub.get("faculty", ""))
                    theory_types.append("Theory")
                else:
                    lab_tut_names.append(sub.get("ta", ""))
                    lab_tut_types.append(sub["type"])

            if theory_types:
                self.subject_table.insertRow(self.subject_table.rowCount())
                values = [
                    subject_name,
                    ", ".join(set(theory_names)),
                    year_text,
                    semester,
                    ", ".join(theory_types)
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.subject_table.setItem(self.subject_table.rowCount() - 1, col, item)

            if lab_tut_types:
                self.subject_table.insertRow(self.subject_table.rowCount())
                values = [
                    subject_name,
                    ", ".join(set(lab_tut_names)),
                    year_text,
                    semester,
                    ", ".join(lab_tut_types)
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.subject_table.setItem(self.subject_table.rowCount() - 1, col, item)

            added_keys.add(key)

    def deleteSubject(self):
        row = self.subject_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Error", "Please select a subject to delete.")
            return

        subject_name = self.subject_table.item(row, 0).text()
        year_text = self.subject_table.item(row, 2).text()
        semester = self.subject_table.item(row, 3).text()

        # Extract year and specialization from year_text
        year = year_text
        specialization = ""
        if "(" in year_text:
            year, specialization = year_text.split(" (")
            specialization = specialization.rstrip(")")
            year = year.strip()

        reply = QMessageBox.question(
            self, "Delete Subject",
            f"Are you sure you want to delete '{subject_name}' for {year} - {semester} ({specialization})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Delete all types of this subject for the given year, semester, and specialization
            self.subject_collection.delete_many({
                "subject": subject_name,
                "year": year,
                "semester": semester,
                "specialization": specialization
            })
            self.loadSubjects()
            QMessageBox.information(self, "Success", "Subject deleted successfully!")

    def setupStrengthTab(self):
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.year_input = QLineEdit(self)
        self.year_input.setPlaceholderText("Year (1st, 2nd, 3rd, 4th)")

        self.section_input = QLineEdit(self)
        self.section_input.setPlaceholderText("Number of Sections")

        self.student_count_input = QLineEdit(self)
        self.student_count_input.setPlaceholderText("Total Students")

        self.spec_label = QLabel("Specialization:")

        self.spec_dropdown = QComboBox(self)
        self.spec_dropdown.addItems(["None", "AI", "CS", "DS", "Cloud Computing"])

        add_btn = QPushButton("Add Strength", self)
        add_btn.clicked.connect(self.addStrength)

        input_layout.addWidget(self.year_input)
        input_layout.addWidget(self.section_input)
        input_layout.addWidget(self.student_count_input)
        input_layout.addWidget(self.spec_label)
        input_layout.addWidget(self.spec_dropdown)
        input_layout.addWidget(add_btn)

        self.strength_table = QTableWidget(0, 4)
        self.strength_table.setHorizontalHeaderLabels(["Year", "Sections", "Students", "Specialization"])
        self.strength_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
            }
            QHeaderView::section {
                background-color: #1A1A2E;
                color: white;
                padding: 10px;
                font-weight: 500;
                border: none;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E0E0E0;
                padding: 10px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #FFF3CD;
                color: #333333;
            }
            QTableWidget:focus {
                outline: none;
            }
        """)
        self.strength_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addLayout(input_layout)
        layout.addWidget(self.strength_table)

        self.strength_management_tab.setLayout(layout)
        self.loadStrengthData()

    def addStrength(self):
        year = self.year_input.text().strip()
        sections = self.section_input.text().strip()
        students = self.student_count_input.text().strip()
        specialization = self.spec_dropdown.currentText()

        if not year or not sections or not students:
            QMessageBox.warning(self, "Error", "Please fill Year, Sections, and Students fields!")
            return

        self.strength_collection.insert_one({
            "year": year,
            "sections": sections,
            "students": students,
            "specialization": None if specialization == "None" else specialization
        })

        QMessageBox.information(self, "Success", f"Strength added for {year} year!")
        self.year_input.clear()
        self.section_input.clear()
        self.student_count_input.clear()
        self.spec_dropdown.setCurrentIndex(0)
        self.loadStrengthData()

    def loadStrengthData(self):
        self.strength_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.strength_table.setRowCount(0)
        for row, strength in enumerate(self.strength_collection.find()):
            self.strength_table.insertRow(row)

            year_item = QTableWidgetItem(str(strength["year"]))
            year_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.strength_table.setItem(row, 0, year_item)

            section_item = QTableWidgetItem(str(strength["sections"]))
            section_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.strength_table.setItem(row, 1, section_item)

            student_item = QTableWidgetItem(str(strength["students"]))
            student_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.strength_table.setItem(row, 2, student_item)

            spec_text = str(strength.get("specialization", ""))
            spec_item = QTableWidgetItem(spec_text)
            spec_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.strength_table.setItem(row, 3, spec_item)

    def deleteStrength(self, row):
        year = self.strength_table.item(row, 0).text()

        confirm = QMessageBox.question(self, "Delete", f"Delete record for {year} year?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.strength_collection.delete_one({"year": year})
            self.loadStrengthData()

    def setupRoomTab(self):
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

        self.room_table = QTableWidget(0, 2)
        self.room_table.setHorizontalHeaderLabels(["Room Number", "Capacity"])
        self.room_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
            }
            QHeaderView::section {
                background-color: #1A1A2E;
                color: white;
                padding: 10px;
                font-weight: 500;
                border: none;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E0E0E0;
                padding: 10px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #FFF3CD;
                color: #333333;
            }
            QTableWidget:focus {
                outline: none;
            }
        """)
        self.room_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addLayout(input_layout)
        layout.addWidget(self.room_table)

        self.room_tab.setLayout(layout)

        self.loadRooms()

    def addRoom(self):
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
        self.room_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.room_table.setRowCount(0)

        for row, room in enumerate(self.room_collection.find()):
            self.room_table.insertRow(row)

            room_item = QTableWidgetItem(room["room_no"])
            room_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.room_table.setItem(row, 0, room_item)

            capacity_item = QTableWidgetItem(str(room["capacity"]))
            capacity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.room_table.setItem(row, 1, capacity_item)

    def deleteRoom(self, row):
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
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        
        self.lab_no = QLineEdit(self)
        self.lab_no.setPlaceholderText("Lab Number")

        self.lab_strength = QLineEdit(self)
        self.lab_strength.setPlaceholderText("Lab Capacity")
        self.lab_strength.setValidator(QIntValidator())

        add_btn = QPushButton("Add Lab", self)
        add_btn.clicked.connect(self.addLab)

        input_layout.addWidget(self.lab_no)
        input_layout.addWidget(self.lab_strength)
        input_layout.addWidget(add_btn)

        self.lab_table = QTableWidget(0, 2)
        self.lab_table.setHorizontalHeaderLabels(["Lab Number", "Lab Capacity"])
        self.lab_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
            }
            QHeaderView::section {
                background-color: #1A1A2E;
                color: white;
                padding: 10px;
                font-weight: 500;
                border: none;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E0E0E0;
                padding: 10px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #FFF3CD;
                color: #333333;
            }
            QTableWidget:focus {
                outline: none;
            }
        """)
        self.lab_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addLayout(input_layout)
        layout.addWidget(self.lab_table)

        self.lab_tab.setLayout(layout)

        self.loadLabs()

    def addLab(self):
        lab = self.lab_no.text().strip()
        strength = self.lab_strength.text().strip()

        if not lab or not strength:
            QMessageBox.warning(self, "Error", "Please enter both Lab Number and Capacity.")
            return

        self.lab_collection.insert_one({"lab_no": lab, "strength": int(strength)})
        QMessageBox.information(self, "Success", f"Lab {lab} added successfully!")
        
        self.lab_no.clear()
        self.lab_strength.clear()
        
        self.loadLabs()

    def loadLabs(self):
        self.lab_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lab_table.setRowCount(0)

        for row, lab in enumerate(self.lab_collection.find()):
            self.lab_table.insertRow(row)

            lab_item = QTableWidgetItem(lab["lab_no"])
            lab_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lab_table.setItem(row, 0, lab_item)

            capacity_item = QTableWidgetItem(str(lab["strength"]))
            capacity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lab_table.setItem(row, 1, capacity_item)

    def deleteLab(self, row):
        try:
            if row == -1:
                QMessageBox.warning(self, "Error", "Please select a lab to delete.")
                return

            lab_item = self.lab_table.item(row, 0)
            if lab_item is None:
                QMessageBox.warning(self, "Error", "Invalid selection. Please try again.")
                return

            lab_no = lab_item.text()

            confirmation = QMessageBox.question(self, "Confirm Deletion",
                                                f"Are you sure you want to delete Lab {lab_no}?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirmation == QMessageBox.StandardButton.No:
                return

            delete_result = self.lab_collection.delete_one({"lab_no": lab_no})

            if delete_result.deleted_count > 0:
                self.lab_table.removeRow(row)
                QMessageBox.information(self, "Success", f"Lab {lab_no} deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", f"Lab {lab_no} not found in the database.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    window = TimetableManager()
    window.show()
    app.exec()