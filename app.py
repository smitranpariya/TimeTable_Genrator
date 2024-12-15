import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt


class TimetableForm(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Timetable Management")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("background-color: #FFFFFF;")

        # Main Layout
        self.main_layout = QHBoxLayout(self)

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
        self.update_sidebar_styles()

        # Connect signal to update styles on selection change
        self.sidebar.currentRowChanged.connect(self.load_form)

        # Form Container
        self.form_container = QFrame()
        self.form_container.setStyleSheet("background-color: #D3CFCF; border-radius: 10px;")
        self.form_layout = QVBoxLayout(self.form_container)

        # Load the initial form
        self.load_form(0)

        # Add Sidebar and Form Container to Main Layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.form_container)

    def update_sidebar_styles(self):
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            if i == self.sidebar.currentRow():
                item.setBackground(Qt.GlobalColor.lightGray)
                item.setForeground(Qt.GlobalColor.black)
            else:
                item.setBackground(Qt.GlobalColor.darkGray)
                item.setForeground(Qt.GlobalColor.white)

    def load_form(self, index):
        section_name = self.sidebar.item(index).text()

        # Clear the current layout
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if section_name == "General Info.":
            self.load_general_info_form()
        elif section_name == "Classroom Details":
            self.load_classroom_details_form()

    def load_general_info_form(self):
        title_label = QLabel("General Info.")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        self.form_layout.addWidget(title_label)

        fields = [
            ("Academic Year", "e.g., 2023-2024"),
            ("Semester", "1st Semester"),
            ("Class Name/Section", "e.g., B.Tech CSE - A"),
            ("Start and End Time", "e.g., 9:00 AM - 5:00 PM")
        ]

        for label_text, placeholder in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            self.form_layout.addWidget(label)

            if label_text == "Semester":
                combo_box = QComboBox()
                combo_box.addItems(["1st Semester", "2nd Semester", "3rd Semester", "4th Semester"])
                combo_box.setStyleSheet("""
                    QComboBox {
                        border: 1px solid #A0A0A0;
                        padding: 5px;
                        background-color: #FFFFFF;
                        border-radius: 5px;
                    }
                """)
                self.form_layout.addWidget(combo_box)
            else:
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
                self.form_layout.addWidget(line_edit)

        save_button = QPushButton("Save and Next")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        save_button.clicked.connect(lambda: self.sidebar.setCurrentRow(1))
        self.form_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)

    def load_classroom_details_form(self):
        title_label = QLabel("Classroom Details")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        self.form_layout.addWidget(title_label)

        fields = [
            ("Number of Classrooms", "e.g., 5"),
            ("Classroom Numbers", "e.g., Room 101, Room 102"),
            ("Lab Details", "e.g., Room 101, Room 102"),
            ("Classroom Capacity", "e.g., 30")
        ]

        for label_text, placeholder in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            self.form_layout.addWidget(label)

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
            self.form_layout.addWidget(line_edit)

        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self.sidebar.setCurrentRow(0))
        self.form_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        save_button = QPushButton("Save and Next")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.form_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimetableForm()
    window.show()
    sys.exit(app.exec())
