from ortools.sat.python import cp_model
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel
)


class TimetableGenerator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Timetable Generator")
        self.resize(800, 400)

        layout = QVBoxLayout()

        self.title_label = QLabel("Generated Timetable", self)
        layout.addWidget(self.title_label)

        self.table = QTableWidget(self)
        layout.addWidget(self.table)

        self.generate_button = QPushButton("Generate Timetable")
        self.generate_button.clicked.connect(self.generate_timetable)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)

    def generate_timetable(self):
        """ Generate timetable using OR-Tools Constraint Programming (CP-SAT) Model """
        model = cp_model.CpModel()

        # Example Data
        subjects = ["Math", "Physics", "Chemistry", "English", "Biology"]
        teachers = ["T1", "T2", "T3", "T4", "T5"]
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        time_slots = ["9:00-10:00", "10:00-11:00", "11:00-12:00", "1:00-2:00", "2:00-3:00"]
        num_classes = 3  # Number of sections

        # Decision Variables: Assign (Day, Time Slot, Class) to a Subject
        timetable = {}
        for c in range(num_classes):
            for d in days:
                for t in time_slots:
                    timetable[(c, d, t)] = model.NewIntVar(0, len(subjects) - 1, f"class{c}_{d}_{t}")

        # Constraints:
        # 1. Each class gets different subjects throughout the day
        for c in range(num_classes):
            for d in days:
                model.AddAllDifferent([timetable[(c, d, t)] for t in time_slots])

        # 2. A teacher should not be assigned to multiple classes at the same time
        for d in days:
            for t in time_slots:
                model.AddAllDifferent([timetable[(c, d, t)] for c in range(num_classes)])

        # Solve the problem
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            self.populate_table(solver, timetable, subjects, days, time_slots, num_classes)
        else:
            self.title_label.setText("No feasible timetable found.")

    def populate_table(self, solver, timetable, subjects, days, time_slots, num_classes):
        """ Display timetable data in a QTableWidget """
        self.table.setColumnCount(len(time_slots) + 1)  # Add 1 for the "Day" column
        self.table.setRowCount(len(days) * num_classes)
        self.table.setHorizontalHeaderLabels(["Day/Time"] + time_slots)

        row = 0
        for c in range(num_classes):
            for d in days:
                self.table.setItem(row, 0, QTableWidgetItem(f"Class {c + 1} - {d}"))
                for t_idx, t in enumerate(time_slots):
                    subject_index = solver.Value(timetable[(c, d, t)])
                    self.table.setItem(row, t_idx + 1, QTableWidgetItem(subjects[subject_index]))
                row += 1


if __name__ == "__main__":
    app = QApplication([])
    window = TimetableGenerator()
    window.show()
    app.exec()
