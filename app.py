import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt

class TimetableForm(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Timetable Management")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("background-color: #FFFFFF;")

        # Main Layout
        main_layout = QHBoxLayout(self)

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
        self.sidebar.currentRowChanged.connect(self.update_sidebar_styles)

        # Form Container
        form_container = QFrame()
        form_container.setStyleSheet("background-color: #D3CFCF; border-radius: 10px;")
        form_layout = QVBoxLayout(form_container)

        # Title
        title_label = QLabel("General Info.")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        form_layout.addWidget(title_label)

        # Input Fields
        fields = [
            ("Academic Year", "e.g., 2023-2024"),
            ("Semester", "1st Semester"),
            ("Class Name/Section", "e.g., B.Tech CSE - A"),
            ("Start and End Time", "e.g., 9:00 AM - 5:00 PM")
        ]

        for label_text, placeholder in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333333; margin-top: 10px;")
            form_layout.addWidget(label)

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
                form_layout.addWidget(combo_box)
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
                form_layout.addWidget(line_edit)

        # Spacer to Push Save Button to Bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        form_layout.addItem(spacer)

        # Save Button
        save_button = QPushButton("Save And Next")
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
        form_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Add Sidebar and Form Container to Main Layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(form_container)

    def update_sidebar_styles(self):
        """Update sidebar styles to set only the selected item with the specific color."""
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            if i == self.sidebar.currentRow():
                item.setBackground(Qt.GlobalColor.lightGray)
                item.setForeground(Qt.GlobalColor.black)
            else:
                item.setBackground(Qt.GlobalColor.darkGray)
                item.setForeground(Qt.GlobalColor.white)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimetableForm()
    window.show()
    sys.exit(app.exec())
