from PyQt6.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtCore import Qt
import sys

class Timetable(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("College Timetable")
        self.setGeometry(100, 100, 900, 500)

        layout = QVBoxLayout()

        # Title
        title = QLabel("D.Y. Patil International University, Akurdi, Pune\nSchool Of Computer Science Engineering And Application\nFINAL YEAR (B.Tech) - Section CS - SEM VII - Room No: 533")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: black; text-align: center;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Timetable Table
        self.table = QTableWidget()
        self.table.setRowCount(9)  # Rows for different time slots
        self.table.setColumnCount(7)  # 7 Days (Mon-Sat)
        self.table.setHorizontalHeaderLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        self.table.setVerticalHeaderLabels(["9:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30", "12:30 - 1:30 (Lunch)", "1:30 - 2:30", "2:30 - 3:30", "3:30 - 4:30", "4:30 - 5:30"])

        self.populate_table()

        layout.addWidget(self.table)
        self.setLayout(layout)

    def populate_table(self):
        """Fill the table with sample data (Can be modified to fetch from DB)"""
        sample_data = {
            (0, 0): "OFFICE HOUR",
            (1, 1): "TC-7",
            (2, 3): "TC-6/CS544",
            (4, 4): "TC-6-TUT",
            (6, 2): "OFFICE HOUR"
        }

        for (row, col), text in sample_data.items():
            self.set_cell(row, col, text)

    def set_cell(self, row, col, text):
        """Helper function to set cell text and style"""
        item = QTableWidgetItem(text)
        item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        if "OFFICE HOUR" in text:
            item.setBackground(QBrush(QColor("#F4A460")))  # Light Orange
        elif "TC-" in text:
            item.setBackground(QBrush(QColor("#DDA0DD")))  # Purple
        else:
            item.setBackground(QBrush(QColor("#ADD8E6")))  # Light Blue
        
        self.table.setItem(row, col, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Timetable()
    window.show()
    sys.exit(app.exec())
