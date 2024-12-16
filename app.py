import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem,QStackedWidget, QFrame,QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

from db_helper import DatabaseHelper


class TimetableForm(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Timetable Management")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("background-color: #FFFFFF;")

        # Main Layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.db = DatabaseHelper() 

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #E5E5E5;
                border: none;
                border-radius: 10px;
            }
            QListWidget::item {
                background-color: #3A3A3A;
                color: white;
                font-size: 14px;
                margin: 5px;
                padding: 10px;
                border-radius: 5px;
            }
            QListWidget::item:selected { 
                background-color: #BAA5A5;
                color: black;
                border: none;
            }
        """)

        # Sidebar Items
        sections = [
            "General Info.",
            "Classroom Details",
            "Faculty Info",
            "Subject Details",
            "Student Batches",
            "Breaks",
            "Constraints"
        ]
        for section in sections:
            item = QListWidgetItem(section)
            self.sidebar.addItem(item)

        # Default select "General Info."
        self.sidebar.setCurrentRow(0)
        # Form Container (Stacked Widget)
        self.form_container = QStackedWidget()

        # Add Forms to the Stacked Widget
        self.general_info_form = self.load_general_info_form()
        self.classroom_details_form = self.load_classroom_details_form()
        self.faculty_info_form = self.create_faculty_info_form()
        self.subject_details_form = self.create_subject_details_form()
        self.student_batches_form = self.create_student_batches_form()
        self.breaks_form = self.create_breaks_form()
        self.constraints_form = self.create_constraints_form()
        self.form_container.addWidget(self.general_info_form)
        self.form_container.addWidget(self.classroom_details_form)
        self.form_container.addWidget(self.faculty_info_form)
        self.form_container.addWidget(self.subject_details_form)
        self.form_container.addWidget(self.student_batches_form)
        self.form_container.addWidget(self.breaks_form)
        self.form_container.addWidget(self.constraints_form)

        # Add Sidebar and Form Container to Main Layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.form_container)

        # Connect sidebar selection change to form change
        self.sidebar.currentRowChanged.connect(self.change_form)

    def change_form(self, index):
        self.form_container.setCurrentIndex(index)

    def load_form(self, index):
        section_name = self.sidebar.item(index).text()

        # Clear the current layout
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if section_name == "General Info.":
            self.load_general_info_form()
        elif section_name == "Classroom Details":
            self.load_classroom_details_form()

    def load_general_info_form(self):
        form = QFrame()
        form.setStyleSheet("background-color: #D3CFCF; border-radius: 10px;")
        layout = QVBoxLayout(form)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top content
        top_content_layout = QVBoxLayout()
        title_label = QLabel("General Info")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        top_content_layout.addWidget(title_label)

        # Fields
        fields = [
            "Academic Year",
            "Semester",
            "Class Name/Section"
        ]

        self.form_inputs = {}  # Initialize the dictionary to store input fields

        for label_text in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            top_content_layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Enter {label_text.lower()}")  # Add placeholder dynamically
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #A0A0A0;
                    padding: 5px;
                    background-color: #FFFFFF;
                    border-radius: 5px;
                }
            """)
            self.form_inputs[label_text] = line_edit  # Map the field to the input
            top_content_layout.addWidget(line_edit)

        layout.addLayout(top_content_layout)

        # Add stretch before buttons
        layout.addStretch()

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        save_button = QPushButton("Save and Next")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        save_button.clicked.connect(self.save_general_info)
        button_layout.addWidget(save_button)

        # Align button to the center
        button_layout.addStretch()

        layout.addLayout(button_layout)

        return form


    def save_general_info(self):
        try:
            # Extract and validate input values
            academic_year = self.form_inputs["Academic Year"].text().strip()
            semester = self.form_inputs["Semester"].text().strip()
            class_name = self.form_inputs["Class Name/Section"].text().strip()

            # Check for empty fields
            if not all([academic_year, semester, class_name]):
                QMessageBox.warning(self, "Error", "Please fill in all the fields.")
                return

            # Insert data into the database
            self.db.insert_general_info(academic_year, semester, class_name)

            # Move to the next form
            QMessageBox.information(self, "Success", "General information saved successfully.")
            self.sidebar.setCurrentRow(1)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")



    def load_classroom_details_form(self):
        form = QFrame()
        form.setStyleSheet("background-color: #D3CFCF; border-radius: 10px;")
        layout = QVBoxLayout(form)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top content
        top_content_layout = QVBoxLayout()
        title_label = QLabel("Classroom Details")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        top_content_layout.addWidget(title_label)

        # Fields
        fields = [
            ("Number of Classrooms", ""),
            ("Classroom Numbers", ""),
            ("Lab Details", ""),
            ("Classroom Capacity", "")
        ]

        self.classroom_fields = {}

        for label_text, placeholder in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            top_content_layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder)
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #A0A0A0;
                    padding: 5px;
                    background-color: #FFFFFF;
                    border-radius: 5px;
                }
            """)
            if label_text in ["Number of Classrooms", "Classroom Capacity"]:
                line_edit.setValidator(QIntValidator(0, 1000))  # Restrict to integers

            top_content_layout.addWidget(line_edit)
            self.classroom_fields[label_text] = line_edit  # Store reference to the field

        layout.addLayout(top_content_layout)

        # Add stretch before buttons
        layout.addStretch()

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        back_button.clicked.connect(lambda: self.sidebar.setCurrentRow(0))  # Navigate to General Info
        button_layout.addWidget(back_button)

        save_button = QPushButton("Save and Next")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        save_button.clicked.connect(self.save_classroom_details)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        return form

    def save_classroom_details(self):
        try:
            # Extract input values
            num_classrooms = self.classroom_fields["Number of Classrooms"].text().strip()
            classroom_numbers = self.classroom_fields["Classroom Numbers"].text().strip()
            lab_details = self.classroom_fields["Lab Details"].text().strip()
            classroom_capacity = self.classroom_fields["Classroom Capacity"].text().strip()

            # Check for empty fields
            if not all([num_classrooms, classroom_numbers, lab_details, classroom_capacity]):
                QMessageBox.warning(self, "Error", "Please fill in all the fields.")
                return

            # Convert numeric fields
            try:
                num_classrooms = int(num_classrooms)
                classroom_capacity = int(classroom_capacity)
            except ValueError:
                QMessageBox.warning(self, "Error", "Number of Classrooms and Classroom Capacity must be integers.")
                return

            # Insert data into the database
            self.db.insert_classroom_details(num_classrooms, classroom_numbers, lab_details, classroom_capacity)

            # Navigate to the next form
            QMessageBox.information(self, "Success", "Classroom details saved successfully.")
            self.sidebar.setCurrentRow(2)

        except KeyError as e:
            QMessageBox.critical(self, "Error", f"Missing field: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")



    # Start Faculty info form
    def create_faculty_info_form(self):  
        form = QFrame()
        form.setStyleSheet("background-color: #D3CFCF; border-radius: 10px;")
        layout = QVBoxLayout(form)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top content
        top_content_layout = QVBoxLayout()
        title_label = QLabel("Faculty Information")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        top_content_layout.addWidget(title_label)

        # Fields with updated second field
        fields = [
            ("Faculty Name", "e.g., Dr. Rahul Sharma"),
            ("Department", "e.g., AI Ethics"),  # Updated second part
            ("Availability", "e.g., Monday to Thursday")
        ]

        for label_text, placeholder in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            top_content_layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder)
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #A0A0A0;
                    padding: 5px;
                    background-color: #FFFFFF;
                    border-radius: 5px;
                }
            """)
            top_content_layout.addWidget(line_edit)

        layout.addLayout(top_content_layout)

        # Add stretch before buttons
        layout.addStretch()

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        back_button.clicked.connect(lambda: self.sidebar.setCurrentRow(1))  # Back to "Classroom Details"
        button_layout.addWidget(back_button)

        save_button = QPushButton("Save and Next")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        save_button.clicked.connect(lambda: self.sidebar.setCurrentRow(3))  # Move to the next section
        button_layout.addWidget(save_button)

        # Set fixed button widths
        back_button.setFixedWidth(form.width() // 2)
        save_button.setFixedWidth(form.width() // 2)

        layout.addLayout(button_layout)

        return form  
    #faculty form completed
    
    #Subject Details form start
    def create_subject_details_form(self):  # Start
        form = QFrame()
        form.setStyleSheet("background-color: #D3CFCF; border-radius: 10px;")
        layout = QVBoxLayout(form)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top content
        top_content_layout = QVBoxLayout()
        title_label = QLabel("Subject Details")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        top_content_layout.addWidget(title_label)

        # Fields for subject details
        fields = [
            ("Subject Name", "e.g., Mathematics"),
            ("Subject Code", "e.g., MATH101"),
            ("Faculty Assigned", "e.g., Dr. John Doe"),
            ("Credits", "e.g., 3"),
    
        ]

        for label_text, placeholder in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            top_content_layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder)
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #A0A0A0;
                    padding: 5px;
                    background-color: #FFFFFF;
                    border-radius: 5px;
                }
            """)
            top_content_layout.addWidget(line_edit)

        layout.addLayout(top_content_layout)

        # Add stretch before buttons
        layout.addStretch()

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        back_button.clicked.connect(lambda: self.sidebar.setCurrentRow(2))  # Back to the previous section
        button_layout.addWidget(back_button)

        save_button = QPushButton("Save and Next")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        save_button.clicked.connect(lambda: self.sidebar.setCurrentRow(4))  # Move to the next section
        button_layout.addWidget(save_button)

        # Set fixed button widths
        back_button.setFixedWidth(form.width() // 2)
        save_button.setFixedWidth(form.width() // 2)

        layout.addLayout(button_layout)

        return form
    #end subject details form

    #start student batches form
    def create_student_batches_form(self):  # Start
        form = QFrame()
        form.setStyleSheet("background-color: #D3CFCF; border-radius: 10px;")
        layout = QVBoxLayout(form)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top content
        top_content_layout = QVBoxLayout()
        title_label = QLabel("Student Batches")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        top_content_layout.addWidget(title_label)

        # Fields for student batches
        fields = [
            ("Batch Name", "e.g., Batch A"),
            ("Batch Strength", "e.g., 90"),
            ("Special Batch Preferences", "e.g., Batch A prefers morning labs")
        ]

        for label_text, placeholder in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            top_content_layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder)
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #A0A0A0;
                    padding: 5px;
                    background-color: #FFFFFF;
                    border-radius: 5px;
                }
            """)
            top_content_layout.addWidget(line_edit)

        layout.addLayout(top_content_layout)

        # Add stretch before buttons
        layout.addStretch()

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        back_button.clicked.connect(lambda: self.sidebar.setCurrentRow(3))  
        button_layout.addWidget(back_button)

        save_button = QPushButton("Save and Next")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        save_button.clicked.connect(lambda: self.sidebar.setCurrentRow(5))  
        button_layout.addWidget(save_button)

        # Set fixed button widths
        back_button.setFixedWidth(form.width() // 2)
        save_button.setFixedWidth(form.width() // 2)

        layout.addLayout(button_layout)

        return form
    
    #end student details form

    #start breaks form
    def create_breaks_form(self):  # Start
        form = QFrame()
        form.setStyleSheet("background-color: #D3CFCF; border-radius: 10px;")
        layout = QVBoxLayout(form)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top content
        top_content_layout = QVBoxLayout()
        title_label = QLabel("Break Details")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        top_content_layout.addWidget(title_label)

        # Fields for breaks
        fields = [
            ("Break Name", "e.g., Morning Break"),
            ("Start Time", "e.g., 12:30 AM"),
            ("End Time", "e.g., 1:30 AM"),
            ("Duration", "e.g., 60 minutes")
        ]

        for label_text, placeholder in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            top_content_layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder)
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #A0A0A0;
                    padding: 5px;
                    background-color: #FFFFFF;
                    border-radius: 5px;
                }
            """)
            top_content_layout.addWidget(line_edit)

        layout.addLayout(top_content_layout)

        # Add stretch before buttons
        layout.addStretch()

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        back_button.clicked.connect(lambda: self.sidebar.setCurrentRow(4))  # Back to "Student Batches"
        button_layout.addWidget(back_button)

        save_button = QPushButton("Save and Next")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        save_button.clicked.connect(lambda: self.sidebar.setCurrentRow(6))  # Move to the next section
        button_layout.addWidget(save_button)

        # Set fixed button widths
        back_button.setFixedWidth(form.width() // 2)
        save_button.setFixedWidth(form.width() // 2)

        layout.addLayout(button_layout)

        return form
    
    #end breaks form 

    #start Constraints form
    def create_constraints_form(self):  # Start
        form = QFrame()
        form.setStyleSheet("background-color: #D3CFCF; border-radius: 10px;")
        layout = QVBoxLayout(form)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top content
        top_content_layout = QVBoxLayout()
        title_label = QLabel("Constraints Details")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        top_content_layout.addWidget(title_label)

        # Fields for constraints
        fields = [
            ("Constraint Name", "e.g., No classes on weekends"),
            ("Description", "e.g., Classes cannot be scheduled on Saturday or Sunday"),
            ("Priority", "e.g., High, Medium, Low"),
            ("Applicable Days", "e.g., Monday to Friday")
        ]

        for label_text, placeholder in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            top_content_layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder)
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #A0A0A0;
                    padding: 5px;
                    background-color: #FFFFFF;
                    border-radius: 5px;
                }
            """)
            top_content_layout.addWidget(line_edit)

        layout.addLayout(top_content_layout)

        # Add stretch before buttons
        layout.addStretch()

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        back_button.clicked.connect(lambda: self.sidebar.setCurrentRow(5))  # Back to "Break Details"
        button_layout.addWidget(back_button)

        save_button = QPushButton("Save and Next")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)

        # Function to show success popup
        def show_success_popup():
            # Create a message box to show success
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Information)  # Corrected for PyQt6
            msg_box.setText("Information saved successfully!")
            msg_box.setWindowTitle("Success")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)  # Corrected for PyQt6
            msg_box.exec()

        # Connect the save button to show success popup
        save_button.clicked.connect(show_success_popup)
        button_layout.addWidget(save_button)

        # Set fixed button width
        back_button.setFixedWidth(form.width() // 2)
        save_button.setFixedWidth(form.width() // 2)

        layout.addLayout(button_layout)

        return form
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimetableForm()
    window.show()
    sys.exit(app.exec())
