from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QCheckBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QLabel,
    QAbstractItemView, QMenu, QAction
)
from PyQt6.QtCore import Qt

class SubjectTab(QWidget):
    def __init__(self, subject_collection):
        super().__init__()
        self.subject_collection = subject_collection
        self.subject_tab = QWidget()
        self.setupSubjectTab()

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

    def updateSubject(self):
        # This method is removed as it's now handled within editSubject
        pass