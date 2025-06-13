from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
import subprocess
import sys

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timetable System")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #f5f7fa;")
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left side - Login Form
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: white;")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(80, 100, 80, 100)
        left_layout.setSpacing(25)

        title = QLabel("Sign In")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #333333;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Welcome! Please enter your details.")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #777777;")

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.set_lineedit_style(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.set_lineedit_style(self.pass_input)

        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(45)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6F61;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FF6F61;
            }
        """)
        login_btn.clicked.connect(self.check_login)

        left_layout.addWidget(title)
        left_layout.addWidget(subtitle)
        left_layout.addSpacing(20)
        left_layout.addWidget(self.user_input)
        left_layout.addWidget(self.pass_input)
        left_layout.addSpacing(10)
        left_layout.addWidget(login_btn)
        left_layout.addSpacing(20)

        # Right side - Branding or image
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #FF6F61;")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_text = QLabel("Welcome to Timetable Generator")
        welcome_text.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        welcome_text.setStyleSheet("color: white;")
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel("Manage your time with ease.\nPlan smart. Achieve more.")
        description.setFont(QFont("Segoe UI", 12))
        description.setStyleSheet("color: #eeeeee;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(welcome_text)
        right_layout.addSpacing(20)
        right_layout.addWidget(description)

        main_layout.addWidget(left_frame, stretch=3)
        main_layout.addWidget(right_frame, stretch=2)

    def set_lineedit_style(self, lineedit):
        lineedit.setFixedHeight(45)
        lineedit.setFont(QFont("Segoe UI", 11))
        lineedit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border: 1.5px solid #FF6F61;
                background-color: #fafafa;
            }
        """)

    def check_login(self):
        user = self.user_input.text()
        password = self.pass_input.text()
        if user == "admin" and password == "1234":
            # QMessageBox.information(self, "Login Successful", "Welcome!")  # Removed as per request
            self.close()
            subprocess.Popen(["python", "Main.py"])
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid credentials")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
